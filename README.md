# Robô de conteúdo para Instagram

Este projeto inclui um robô que:

1. Lê uma lista de URLs e escolhe **1 URL aleatória** por execução;
2. Extrai conteúdo da URL e identifica tickers sem repetição;
3. Gera legenda usando o prompt de engajamento (incluindo aviso de não recomendação);
4. Gera imagem 1080x1080 usando prompt de imagem (logo + ticker);
5. Publica no Instagram via Graph API nos horários configurados.

## Arquivo principal

- `social_automation.py`

## Instalação

```bash
pip install -r requirements.txt
```

## Variáveis de ambiente

```bash
export SITE_URLS="https://seusite.com/pagina-1,https://seusite.com/pagina-2"
export IG_USER_ID="seu_ig_user_id"
export IG_ACCESS_TOKEN="seu_token"
export SCHEDULE_TIMES="09:00,13:30,18:00"
export BOT_TIMEZONE="America/Sao_Paulo"

# obrigatório para publicar no Instagram (URL pública da imagem final)
export INSTAGRAM_IMAGE_URL="https://cdn.seudominio.com/posts/post_hoje.png"

# opcional: usa OpenAI para gerar legenda e imagem com os prompts solicitados
export OPENAI_API_KEY="sua_chave"
export OPENAI_TEXT_MODEL="gpt-4.1-mini"
export OPENAI_IMAGE_MODEL="gpt-image-1"

# opcional: roda imediatamente ao iniciar
export RUN_IMMEDIATELY="true"
```

## Executar

```bash
python social_automation.py
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

## Observação importante

A API do Instagram exige `image_url` público no endpoint `/media`.
O script salva uma cópia local da imagem em `generated/`, mas a publicação usa a URL definida em `INSTAGRAM_IMAGE_URL`.
