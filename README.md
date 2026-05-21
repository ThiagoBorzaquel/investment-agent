# Robô de conteúdo para Instagram

## Segurança do Admin

O painel agora exige autenticação com:

- cadastro com **email + senha**
- login
- recuperação de senha (token)
- **2FA (TOTP)** na etapa de login

### Fluxo

1. Acesse `/register` para criar usuário admin.
2. Guarde a chave 2FA exibida no cadastro e cadastre no app autenticador.
3. Faça login em `/login` e valide o código em `/verify-2fa`.
4. Se esquecer a senha, use `/forgot-password` e depois `/reset-password`.

## Dashboard Admin

Após login, no dashboard (`/`) você configura:

1. Lista de URLs (adicionar/editar/apagar)
2. Prompt de geração do post (adicionar/editar/apagar)
3. Prompt de geração da imagem (adicionar/editar/apagar)

## Agendamento e aprovação

- Modo de postagem: automático ou com aprovação.
- Tipo de agendamento: horários fixos (`schedule_times`) ou intervalo (`interval_minutes`).

Com aprovação, o post pendente fica em `generated/pending_post.json` e deve ser aprovado no botão do dashboard.

## Executar

```bash
python admin_dashboard.py
```

Acesse `http://localhost:8080`.
