# Robô de conteúdo para Instagram

Agora o projeto tem um **dashboard admin** para cadastrar credenciais do ChatGPT/OpenAI e Instagram.

## O que o robô faz

1. Lê uma lista de URLs e escolhe 1 URL aleatória por execução;
2. Extrai conteúdo e tickers sem repetição;
3. Gera legenda com prompt de engajamento + aviso de não recomendação;
4. Gera imagem para Instagram;
5. Publica via Instagram Graph API nos horários configurados.

## Dashboard Admin

Arquivo: `admin_dashboard.py`

No dashboard você pode configurar:
- URLs do site
- `instagram_user_id`
- `instagram_access_token`
- `instagram_image_url`
- `openai_api_key`
- modelos de texto/imagem
- horários de postagem e timezone

### Rodar dashboard

```bash
python admin_dashboard.py
```

Acesse: `http://localhost:8080`

As configurações são salvas em `.bot_config.json`.

## Rodar robô (modo scheduler)

```bash
python social_automation.py
```

## Variáveis de ambiente (opcional override)

```bash
export SITE_URLS="https://seusite.com/pagina-1,https://seusite.com/pagina-2"
export IG_USER_ID="seu_ig_user_id"
export IG_ACCESS_TOKEN="seu_token"
export INSTAGRAM_IMAGE_URL="https://cdn.seudominio.com/posts/post_hoje.png"
export OPENAI_API_KEY="sua_chave"
export SCHEDULE_TIMES="09:00,13:30,18:00"
export BOT_TIMEZONE="America/Sao_Paulo"
export RUN_IMMEDIATELY="true"
```

## Prompts usados

### Prompt de legenda

```text
Pegas as informações dessa URL cria um post usando a foto e nome dos ticker para postar no Instagram e gera engajamento.
Não esqueça do avisa que não e recomendação.
Sem repetir ticker ou empresa.

Exemplos:
• “acesse o site e veja o ranking completo”
• “Siga para receber ações baratas todos os dias”
• “Eu posto oportunidades escondidas diariamente”
• “Segue que amanhã tem outra melhor”
```

### Prompt de imagem

```text
Agora crie uma imagem usando o logo e o ticker com formato para postar no Instagram.
```
