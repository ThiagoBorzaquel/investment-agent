from flask import Flask, redirect, render_template, request, url_for, flash

from social_automation import (
    ContentAutomationBot,
    build_bot_config,
    load_runtime_settings,
    save_runtime_settings,
)

app = Flask(__name__)
app.secret_key = "admin-dashboard-secret"


def _form_to_settings(form):
    return {
        "site_urls": [u.strip() for u in form.get("site_urls", "").splitlines() if u.strip()],
        "instagram_user_id": form.get("instagram_user_id", "").strip(),
        "instagram_access_token": form.get("instagram_access_token", "").strip(),
        "instagram_image_url": form.get("instagram_image_url", "").strip(),
        "schedule_times": [t.strip() for t in form.get("schedule_times", "09:00").split(",") if t.strip()],
        "timezone": form.get("timezone", "America/Sao_Paulo").strip(),
        "openai_api_key": form.get("openai_api_key", "").strip(),
        "openai_text_model": form.get("openai_text_model", "gpt-4.1-mini").strip(),
        "openai_image_model": form.get("openai_image_model", "gpt-image-1").strip(),
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        settings = _form_to_settings(request.form)
        path = save_runtime_settings(settings)
        flash(f"Configurações salvas em {path}", "success")
        return redirect(url_for("index"))

    settings = load_runtime_settings()
    return render_template("admin.html", settings=settings)


@app.post("/run-now")
def run_now():
    try:
        settings = load_runtime_settings()
        config = build_bot_config(settings)
        bot = ContentAutomationBot(config)
        bot.run_once()
        flash("Post executado com sucesso.", "success")
    except Exception as exc:
        flash(f"Erro ao executar post: {exc}", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
