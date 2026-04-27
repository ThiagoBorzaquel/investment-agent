import os
import secrets
import sqlite3
from functools import wraps

import pyotp
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from social_automation import ContentAutomationBot, build_bot_config, load_runtime_settings, save_runtime_settings

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-me-secret")
DB_PATH = "admin_users.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                totp_secret TEXT NOT NULL,
                reset_token TEXT
            )
            """
        )


def get_user_by_email(email: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def _clean_list(values):
    return [v.strip() for v in values if v and v.strip()]


def _form_to_settings(form):
    return {
        "site_urls": _clean_list(form.getlist("site_urls")),
        "post_prompts": _clean_list(form.getlist("post_prompts")),
        "image_prompts": _clean_list(form.getlist("image_prompts")),
        "instagram_user_id": form.get("instagram_user_id", "").strip(),
        "instagram_access_token": form.get("instagram_access_token", "").strip(),
        "instagram_image_url": form.get("instagram_image_url", "").strip(),
        "schedule_times": _clean_list(form.get("schedule_times", "09:00").split(",")),
        "schedule_mode": form.get("schedule_mode", "fixed").strip(),
        "interval_minutes": int(form.get("interval_minutes", "60") or "60"),
        "posting_mode": form.get("posting_mode", "auto").strip(),
        "timezone": form.get("timezone", "America/Sao_Paulo").strip(),
        "openai_api_key": form.get("openai_api_key", "").strip(),
        "openai_text_model": form.get("openai_text_model", "gpt-4.1-mini").strip(),
        "openai_image_model": form.get("openai_image_model", "gpt-image-1").strip(),
    }


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Preencha email e senha.", "error")
            return redirect(url_for("register"))
        if get_user_by_email(email):
            flash("Email já cadastrado.", "error")
            return redirect(url_for("register"))

        totp_secret = pyotp.random_base32()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (email, password_hash, totp_secret) VALUES (?, ?, ?)",
                (email, generate_password_hash(password), totp_secret),
            )
        flash(f"Cadastro concluído. Guarde sua chave 2FA: {totp_secret}", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Credenciais inválidas.", "error")
            return redirect(url_for("login"))
        session["pending_2fa_user"] = user["id"]
        return redirect(url_for("verify_2fa"))

    return render_template("login.html")


@app.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    user_id = session.get("pending_2fa_user")
    if not user_id:
        return redirect(url_for("login"))

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if pyotp.TOTP(user["totp_secret"]).verify(code, valid_window=1):
            session.pop("pending_2fa_user", None)
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            return redirect(url_for("index"))
        flash("Código 2FA inválido.", "error")

    return render_template("verify_2fa.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    token = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = get_user_by_email(email)
        if user:
            token = secrets.token_urlsafe(16)
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE users SET reset_token = ? WHERE id = ?", (token, user["id"]))
        flash("Se o email existir, um token de recuperação foi gerado.", "success")
    return render_template("forgot_password.html", token=token)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        token = request.form.get("token", "").strip()
        new_password = request.form.get("new_password", "")
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute("SELECT * FROM users WHERE reset_token = ?", (token,)).fetchone()
            if not user:
                flash("Token inválido.", "error")
                return redirect(url_for("reset_password"))
            conn.execute(
                "UPDATE users SET password_hash = ?, reset_token = NULL WHERE id = ?",
                (generate_password_hash(new_password), user["id"]),
            )
        flash("Senha redefinida com sucesso.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        settings = _form_to_settings(request.form)
        path = save_runtime_settings(settings)
        flash(f"Configurações salvas em {path}", "success")
        return redirect(url_for("index"))

    settings = load_runtime_settings()
    return render_template("admin.html", settings=settings, email=session.get("email"))


@app.post("/run-now")
@login_required
def run_now():
    try:
        bot = ContentAutomationBot(build_bot_config(load_runtime_settings()))
        bot.run_once()
        flash("Processo executado com sucesso.", "success")
    except Exception as exc:
        flash(f"Erro ao executar: {exc}", "error")
    return redirect(url_for("index"))


@app.post("/approve-post")
@login_required
def approve_post():
    try:
        bot = ContentAutomationBot(build_bot_config(load_runtime_settings()))
        bot.approve_pending_post()
        flash("Post pendente aprovado e publicado.", "success")
    except Exception as exc:
        flash(f"Erro ao aprovar post: {exc}", "error")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
