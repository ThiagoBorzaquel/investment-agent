# Robô de conteúdo para Instagram

## Dashboard Admin

No dashboard (`admin_dashboard.py`) existem **3 campos principais** com suporte a **editar, adicionar e apagar** itens:

1. Lista de URLs
2. Prompt de geração do post
3. Prompt de geração da imagem

Cada um aceita múltiplas entradas. O robô escolhe aleatoriamente uma URL e também pode sortear prompts da lista.

### Executar dashboard

```bash
python admin_dashboard.py
```

Acesse `http://localhost:8080`.

## Robô

```bash
python social_automation.py
```

As configurações são salvas em `.bot_config.json`.

## Campos adicionais no dashboard

- `instagram_user_id`
- `instagram_access_token`
- `instagram_image_url`
- `openai_api_key`
- `openai_text_model`
- `openai_image_model`
- `schedule_times`
- `timezone`
