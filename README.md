# Robô de conteúdo para Instagram

## Dashboard Admin

No dashboard (`admin_dashboard.py`) você configura:

1. Lista de URLs (adicionar/editar/apagar)
2. Prompt de geração do post (adicionar/editar/apagar)
3. Prompt de geração da imagem (adicionar/editar/apagar)

## Agendamento e aprovação

O dashboard tem uma caixa de configuração para:

- **Modo de postagem**
  - `Postar automaticamente`
  - `Postar com aprovação no dashboard`
- **Tipo de agendamento**
  - `Horários pré-programados` (campo `schedule_times`)
  - `Intervalo de tempo` (campo `interval_minutes`)

Quando `posting_mode=approval`, o robô gera conteúdo e salva pendente em `generated/pending_post.json`.
Depois você usa o botão **Aprovar e publicar post pendente** no dashboard.

## Executar

```bash
python admin_dashboard.py
```

Acesse `http://localhost:8080`.

Para rodar apenas o scheduler:

```bash
python social_automation.py
```
