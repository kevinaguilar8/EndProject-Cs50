import os
import json
import requests

from flask import Flask, session, render_template, url_for, request, redirect, flash
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from loginRequired import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not request.form.get("username"):
            flash("INGRESE USUARIO", "succes")
            return render_template("login.html")
        elif not request.form.get("password"):
            flash("INGRESE CONTRASEÑA", "succes")
            return render_template("login.html")
        
        Vuser = text("SELECT * FROM users WHERE usuario=:username")
        cons = db.execute(Vuser, {'username': username})
        print(cons)
        users = cons.fetchone()
        print(users)
        db.commit()
        db.close()
        
        if users and check_password_hash(users[2], password):
            flash("Sesión Iniciada", "success")
            session["id"]=users[0]
            return render_template("articulos.html")
        else:
            flash("USUARIO Y CONTRASEÑA INCORRECTOS", "error")
            return render_template("login.html")
    else:
        return render_template("login.html")
    
@app.route("/logout")
@login_required
def logout():
    session.clear()

    flash("Hasta luego", "info")
    return redirect("/")


@app.route("/register",methods=['GET', 'POST'])
def register():
    #Formulario para registro
   if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not request.form.get("username"):
            flash("INGRESE USUARIO", "warning")
            return render_template("register.html")
        elif not request.form.get("password"):
            flash("INGRESE CONTRASEÑA", "warning")
            return render_template("register.html")
        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("CONFIRMAR CONTRASEÑA", "warning")
            return render_template("register.html")
        #insert Bd tables users
        contraseña = generate_password_hash(request.form.get("password"))
        consulta = text(
        "Insert into users(usuario, password) values(:usuario,:password)"
        )
        db.execute(consulta, {'usuario': username, 'password': contraseña})
        db.commit()
        
        session["usuario"] = request.form.get("username")
        flash("REGISTRO EXITOSO","success")
        return render_template('login.html')
   else:
        return render_template('register.html')

@app.route("/articulos",methods=['GET', 'POST'])
@login_required
def articulos():
    return render_template("articulos.html")

#pagina no encontrada
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404