import base64
import datetime as dt
import json
import os
import random
import re
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

DEFAULT_POST_PROMPT = textwrap.dedent(
    """
    Pegas as informações dessa URL cria um post usando a foto e nome dos ticker para postar no Instagram e gera engajamento.
    Não esqueça do avisa que não e recomendação.
    Sem repetir ticker ou empresa.

    Exemplos:
    • “acesse o site e veja o ranking completo”
    • “Siga para receber ações baratas todos os dias”
    • “Eu posto oportunidades escondidas diariamente”
    • “Segue que amanhã tem outra melhor”

    URL selecionada: {url}
    Tickers únicos: {tickers}
    Conteúdo extraído:
    {content}
    """
).strip()
DEFAULT_IMAGE_PROMPT = "Agora crie uma imagem usando o logo e o ticker com formato para postar no Instagram. Ticker principal: {ticker}."


@dataclass
class BotConfig:
    site_urls: List[str]
    instagram_user_id: str
    instagram_access_token: str
    instagram_image_url: str
    schedule_times: List[str]
    post_prompts: List[str]
    image_prompts: List[str]
    posting_mode: str  # auto | approval
    schedule_mode: str  # fixed | interval
    interval_minutes: int
    timezone: str = "America/Sao_Paulo"
    output_dir: Path = Path("generated")
    openai_api_key: str = ""
    openai_text_model: str = "gpt-4.1-mini"
    openai_image_model: str = "gpt-image-1"


class ContentAutomationBot:
    def __init__(self, config: BotConfig):
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.pending_file = self.config.output_dir / "pending_post.json"

    def run_once(self) -> None:
        selected_url, raw_content = self._collect_random_page_content(self.config.site_urls)
        tickers = self._extract_unique_tickers(raw_content)

        post_prompt = self._build_post_prompt(selected_url, raw_content, tickers)
        caption = self._generate_caption(post_prompt, tickers)
        image_prompt = self._build_image_prompt(tickers)
        image_path = self._generate_image(image_prompt, caption)

        if self.config.posting_mode == "approval":
            self._save_pending_post(caption=caption, image_path=str(image_path), selected_url=selected_url)
            return

        self._publish_caption(caption)

    def approve_pending_post(self) -> None:
        if not self.pending_file.exists():
            raise RuntimeError("Não há post pendente para aprovação.")
        pending = json.loads(self.pending_file.read_text(encoding="utf-8"))
        caption = pending.get("caption", "")
        if not caption:
            raise RuntimeError("Post pendente inválido: sem legenda.")
        self._publish_caption(caption)
        self.pending_file.unlink(missing_ok=True)

    def _save_pending_post(self, caption: str, image_path: str, selected_url: str) -> None:
        payload = {
            "created_at": dt.datetime.now().isoformat(),
            "caption": caption,
            "image_path": image_path,
            "source_url": selected_url,
            "status": "pending_approval",
        }
        self.pending_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _publish_caption(self, caption: str) -> None:
        if not self.config.instagram_image_url:
            raise RuntimeError("Defina INSTAGRAM_IMAGE_URL no dashboard ou ambiente.")
        creation_id = self._create_instagram_media(caption, self.config.instagram_image_url)
        self._publish_instagram_media(creation_id)

    def _collect_random_page_content(self, urls: List[str]) -> tuple[str, str]:
        selected_url = random.choice(urls)
        response = requests.get(selected_url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = (soup.title.string or "Sem título").strip() if soup.title else "Sem título"
        body_text = " ".join([p.get_text(" ", strip=True) for p in soup.select("p") if p.get_text(strip=True)])
        body_text = textwrap.shorten(body_text, width=1400, placeholder="...")
        return selected_url, f"Título: {title}\nResumo: {body_text}"

    def _extract_unique_tickers(self, content: str) -> List[str]:
        found = re.findall(r"\b[A-Z]{4}\d{1,2}\b", content)
        unique: List[str] = []
        for t in found:
            if t not in unique:
                unique.append(t)
        return unique[:10]

    def _build_post_prompt(self, url: str, content: str, tickers: List[str]) -> str:
        template = random.choice(self.config.post_prompts) if self.config.post_prompts else DEFAULT_POST_PROMPT
        ticker_text = ", ".join(tickers) if tickers else "Não identificado"
        try:
            return template.format(url=url, tickers=ticker_text, content=content)
        except KeyError:
            return f"{template}\n\nURL: {url}\nTickers: {ticker_text}\nConteúdo:\n{content}"

    def _build_image_prompt(self, tickers: List[str]) -> str:
        template = random.choice(self.config.image_prompts) if self.config.image_prompts else DEFAULT_IMAGE_PROMPT
        ticker = tickers[0] if tickers else "TICKER"
        try:
            return template.format(ticker=ticker)
        except KeyError:
            return f"{template}\nTicker: {ticker}"

    def _request_openai_with_retry(
        self,
        url: str,
        payload: Dict[str, Any],
        timeout: int,
        max_attempts: int = 5,
    ) -> requests.Response:
        headers = {
            "Authorization": f"Bearer {self.config.openai_api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(1, max_attempts + 1):
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code != 429:
                response.raise_for_status()
                return response

            if attempt == max_attempts:
                response.raise_for_status()

            retry_after = response.headers.get("retry-after")
            if retry_after and retry_after.isdigit():
                wait_seconds = int(retry_after)
            else:
                wait_seconds = min(2 ** attempt, 30)

            time.sleep(wait_seconds)

        raise RuntimeError("Erro inesperado ao chamar OpenAI.")

    def _generate_caption(self, post_prompt: str, tickers: List[str]) -> str:
        if self.config.openai_api_key:
            try:
                return self._generate_caption_with_openai(post_prompt)[:2200]
            except requests.HTTPError as exc:
                if exc.response is None or exc.response.status_code != 429:
                    raise
            except requests.RequestException:
                pass
        return f"📈 Radar de hoje\n\nDestaques: {', '.join(tickers) if tickers else 'ticker não identificado'}.\nNão é recomendação de investimento."[:2200]

    def _generate_caption_with_openai(self, post_prompt: str) -> str:
        response = self._request_openai_with_retry(
            url="https://api.openai.com/v1/responses",
            payload={"model": self.config.openai_text_model, "input": post_prompt},
            timeout=60,
        )
        output = response.json().get("output_text", "").strip()
        if not output:
            raise RuntimeError("Resposta inválida ao gerar legenda.")
        return output

    def _generate_image(self, image_prompt: str, fallback_caption: str) -> Path:
        if self.config.openai_api_key:
            try:
                return self._generate_image_with_openai(image_prompt)
            except requests.HTTPError as exc:
                if exc.response is None or exc.response.status_code != 429:
                    raise
            except requests.RequestException:
                pass
        image = Image.new("RGB", (1080, 1080), color=(20, 24, 36))
        draw = ImageDraw.Draw(image)
        try:
            title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 64)
            body_font = ImageFont.truetype("DejaVuSans.ttf", 38)
        except OSError:
            title_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
        draw.text((80, 120), "Post automático", fill=(255, 255, 255), font=title_font)
        draw.text((80, 260), textwrap.fill(fallback_caption[:320], width=34), fill=(200, 216, 255), font=body_font)
        output = self.config.output_dir / f"post_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(output)
        return output

    def _generate_image_with_openai(self, image_prompt: str) -> Path:
        response = self._request_openai_with_retry(
            url="https://api.openai.com/v1/images/generations",
            payload={"model": self.config.openai_image_model, "prompt": image_prompt, "size": "1024x1024", "response_format": "b64_json"},
            timeout=90,
        )
        b64_data = response.json().get("data", [{}])[0].get("b64_json")
        if not b64_data:
            raise RuntimeError("Falha ao gerar imagem com OpenAI.")
        output = self.config.output_dir / f"post_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        output.write_bytes(base64.b64decode(b64_data))
        return output

    def _create_instagram_media(self, caption: str, image_url: str) -> str:
        endpoint = f"https://graph.facebook.com/v22.0/{self.config.instagram_user_id}/media"
        response = requests.post(endpoint, data={"image_url": image_url, "caption": caption, "access_token": self.config.instagram_access_token}, timeout=30)
        response.raise_for_status()
        media_id = response.json().get("id")
        if not media_id:
            raise RuntimeError("Falha ao criar mídia no Instagram.")
        return media_id

    def _publish_instagram_media(self, creation_id: str) -> None:
        endpoint = f"https://graph.facebook.com/v22.0/{self.config.instagram_user_id}/media_publish"
        response = requests.post(endpoint, data={"creation_id": creation_id, "access_token": self.config.instagram_access_token}, timeout=30)
        response.raise_for_status()


def load_runtime_settings(config_file: str | None = None) -> Dict[str, Any]:
    file_path = Path(config_file or os.getenv("BOT_CONFIG_FILE", ".bot_config.json"))
    data: Dict[str, Any] = json.loads(file_path.read_text(encoding="utf-8")) if file_path.exists() else {}

    def env_list(name: str) -> List[str]:
        return [x.strip() for x in os.getenv(name, "").split(",") if x.strip()]

    overrides: Dict[str, Any] = {
        "site_urls": env_list("SITE_URLS"),
        "instagram_user_id": os.getenv("IG_USER_ID", ""),
        "instagram_access_token": os.getenv("IG_ACCESS_TOKEN", ""),
        "instagram_image_url": os.getenv("INSTAGRAM_IMAGE_URL", ""),
        "schedule_times": env_list("SCHEDULE_TIMES"),
        "post_prompts": env_list("POST_PROMPTS"),
        "image_prompts": env_list("IMAGE_PROMPTS"),
        "posting_mode": os.getenv("POSTING_MODE", ""),
        "schedule_mode": os.getenv("SCHEDULE_MODE", ""),
        "interval_minutes": os.getenv("INTERVAL_MINUTES", ""),
        "timezone": os.getenv("BOT_TIMEZONE", ""),
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "openai_text_model": os.getenv("OPENAI_TEXT_MODEL", ""),
        "openai_image_model": os.getenv("OPENAI_IMAGE_MODEL", ""),
    }
    for key, value in overrides.items():
        if value:
            data[key] = value

    data.setdefault("schedule_times", ["09:00"])
    data.setdefault("post_prompts", [DEFAULT_POST_PROMPT])
    data.setdefault("image_prompts", [DEFAULT_IMAGE_PROMPT])
    data.setdefault("posting_mode", "auto")
    data.setdefault("schedule_mode", "fixed")
    data.setdefault("interval_minutes", 60)
    data.setdefault("timezone", "America/Sao_Paulo")
    data.setdefault("openai_text_model", "gpt-4.1-mini")
    data.setdefault("openai_image_model", "gpt-image-1")
    return data


def save_runtime_settings(settings: Dict[str, Any], config_file: str | None = None) -> Path:
    file_path = Path(config_file or os.getenv("BOT_CONFIG_FILE", ".bot_config.json"))
    file_path.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    return file_path


def build_bot_config(settings: Dict[str, Any]) -> BotConfig:
    site_urls = settings.get("site_urls", [])
    if not site_urls:
        raise RuntimeError("Adicione pelo menos uma URL da lista.")
    user_id = settings.get("instagram_user_id", "")
    token = settings.get("instagram_access_token", "")
    if not user_id or not token:
        raise RuntimeError("Defina IG_USER_ID e IG_ACCESS_TOKEN.")

    return BotConfig(
        site_urls=site_urls,
        instagram_user_id=user_id,
        instagram_access_token=token,
        instagram_image_url=settings.get("instagram_image_url", ""),
        schedule_times=settings.get("schedule_times", ["09:00"]),
        post_prompts=settings.get("post_prompts", [DEFAULT_POST_PROMPT]),
        image_prompts=settings.get("image_prompts", [DEFAULT_IMAGE_PROMPT]),
        posting_mode=str(settings.get("posting_mode", "auto")),
        schedule_mode=str(settings.get("schedule_mode", "fixed")),
        interval_minutes=int(settings.get("interval_minutes", 60)),
        timezone=settings.get("timezone", "America/Sao_Paulo"),
        openai_api_key=settings.get("openai_api_key", ""),
        openai_text_model=settings.get("openai_text_model", "gpt-4.1-mini"),
        openai_image_model=settings.get("openai_image_model", "gpt-image-1"),
    )


def main() -> None:
    config = build_bot_config(load_runtime_settings())
    bot = ContentAutomationBot(config)

    if os.getenv("RUN_IMMEDIATELY", "true").lower() == "true":
        bot.run_once()

    scheduler = BlockingScheduler(timezone=config.timezone)
    if config.schedule_mode == "interval":
        scheduler.add_job(bot.run_once, trigger="interval", minutes=config.interval_minutes, id="post_interval", replace_existing=True)
    else:
        for schedule in config.schedule_times:
            hour, minute = schedule.split(":", 1)
            scheduler.add_job(bot.run_once, trigger="cron", hour=int(hour), minute=int(minute), id=f"post_{hour}_{minute}", replace_existing=True)

    scheduler.start()


if __name__ == "__main__":
    main()
