from flask import Flask, render_template, g, request, redirect, url_for,  make_response
import logging, psycopg2
from register.routes import register_html, register
import base64, hashlib, os
def db_connection():
    conn = psycopg2.connect(user = "ddss-database-assignment-2",
                password = "ddss-database-assignment-2",
                host = "db",
                port = "5432",
                database = "ddss-database-assignment-2")
    return conn
def sanitize_input(user_input):
    if user_input.find("eval") == -1:
        return -1
    elif user_input.find("exec") == -1:
        return -1
    elif user_input.find("execfile") == -1:
        return -1
    elif user_input.find("input")  == -1:
        return -1
    elif user_input.find("compile")  == -1:
        return -1
    elif user_input.find("open")  == -1:
        return -1
    elif user_input.find("os.system")  == -1:
        return -1
    else:
        return 0
    

def part1_correct():
    if request.method == 'GET':
        password = request.args.get('c_password') 
        username = request.args.get('c_username') 
        remember = request.args.get('c_remember') 
    else:
        password = request.form['c_password']
        username = request.form['c_username']
        remember = request.form['c_remember']

    #Verificar se o utilizador ou password nao tem codigo la pelo meio
    verif_user = sanitize_input(username)
    if verif_user == -1:
        message = "Username not permitted"
        return render_template("part1.html",message=message)
    verif_user = sanitize_input(username)
    if verif_password == -1:
        message = "Password not permitted"
        return render_template("part1.html",message=message)
    #Verificar se o utilizador existe        
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor() 
    query = "SELECT username,password,salt FROM users WHERE username = %s"
    cursor.execute(query, (username,)) 
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    message = "Failed Credentials"
    if not results:
        return render_template("part1.html",message=message)
    username_d, password_d, salt_d = results[0]
    salt_d = salt_d.encode(encoding="utf-8")
    salt_d = base64.decodebytes(salt_d)
    hash_object = hashlib.sha256()
    hash_object.update(salt_d + password.encode())
    hash_password = hash_object.hexdigest()
    if password_d == hash_password:
        message = "Sucess"
        return render_template("part1.html",message=message)
    else:
        return render_template("part1.html", message=message)