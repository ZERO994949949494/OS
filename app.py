import re
import secrets
from pathlib import Path

from flask import Flask, jsonify, request, send_file, url_for


BASE_DIR = Path(__file__).resolve().parent
BUILD_DIR = BASE_DIR / "builds"
PROTOTYPE_FILE = BUILD_DIR / "prototype.zip"  # Укажите точное имя файла

app = Flask(__name__)

# Демонстрационное хранилище: при перезапуске приложения данные исчезнут.
# Для реального сервиса замените его на базу данных.
prototype_tokens = {}


def is_valid_email(email: str) -> bool:
    """Базовая проверка email для демонстрационной формы."""
    if not isinstance(email, str) or len(email) > 254:
        return False

    email = email.strip()
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.fullmatch(pattern, email))


@app.get("/")
def index():
    """Отдаёт лендинг."""
    return send_file(BASE_DIR / "index.html")


@app.post("/api/request")
def create_request():
    """Создаёт уникальную ссылку на прототип."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")

    if not is_valid_email(email):
        return jsonify({
            "error": "Введите корректный email."
        }), 400

    email = email.strip().lower()

    # token_urlsafe создаёт трудноугадываемый URL-safe код.
    token = secrets.token_urlsafe(24)
    prototype_tokens[token] = {
        "email": email
    }

    prototype_url = request.url_root.rstrip("/") + url_for(
        "prototype",
        token=token
    )

    # Отправки письма здесь нет — это демонстрационная форма.
    return jsonify({
        "ok": True,
        "email_sent": False,
        "message": "Заявка зарегистрирована в демонстрационном режиме.",
        "prototype_url": prototype_url
    })


@app.get("/prototype/<token>")
def prototype(token):
    if token not in prototype_tokens:
        return "Ссылка недействительна или устарела.", 404

    if not PROTOTYPE_FILE.is_file():
        app.logger.error("Файл прототипа не найден: %s", PROTOTYPE_FILE)
        return "Файл прототипа пока недоступен.", 404

    return send_file(
        PROTOTYPE_FILE,
        as_attachment=True,
        download_name=PROTOTYPE_FILE.name
    )

if __name__ == "__main__":
    # Для локальной разработки. В рабочей среде debug следует выключить.
    app.run(debug=True)
