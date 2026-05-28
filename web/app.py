import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.users import Users
from database.db import Database

app = Flask(__name__)
app.secret_key = "super_secret_key"

db_path = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite')
db = Database(db_path)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    user = Users.find_by_username(db, username)

    if user is None:
        return render_template("login.html", error="Пользователь не найден")

    if not check_password_hash(user.Password, password):
        return render_template("login.html", error="Неверный пароль")

    session["user_id"] = user.ID
    session["username"] = user.Username

    return redirect(url_for("mainpage"))


@app.route("/")
def mainpage():
    username = session.get("username")
    return render_template("main.html", username=username)


@app.route("/user/<int:id>")
def get_user(id: int):
    if "username" not in session:
        return redirect(url_for("login"))

    try:
        user = Users(db, ID=id)
    except ValueError:
        return "Пользователь не найден", 404

    return f"User ID: {user.ID}, Username: {user.Username}"


@app.route("/user/config", methods=["GET", "POST"])
def user_config():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session.get("username")

    if request.method == "GET":
        return f"Страница конфигурации пользователя {username}"

    return f"Конфигурация пользователя {username} обновлена"


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("mainpage"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")

    if password != password_confirm:
        return render_template("register.html", error="Пароли не совпадают")

    existing_user = Users.find_by_username(db, username)
    if existing_user is not None:
        return render_template("register.html", error="Такой пользователь уже существует")

    hashed_password = generate_password_hash(password)

    new_user = Users(db)
    new_user.Username = username
    new_user.Password = hashed_password
    new_user.HashType = "pbkdf2:sha256"
    new_user.Author = "system"
    new_user.Change_cnt = 0
    new_user.dbInsert()

    session["user_id"] = new_user.ID
    session["username"] = new_user.Username

    return redirect(url_for("mainpage"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)