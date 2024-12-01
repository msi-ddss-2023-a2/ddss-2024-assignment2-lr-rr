
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


def part1_vulnerable():
    if request.method == 'GET':
        password = request.args.get('v_password') 
        username = request.args.get('v_username') 
        remember = request.args.get('v_remember') 
    else:
        password = request.form['v_password']
        username = request.form['v_username']
        remember = request.form['v_remember']
    #Verificar se o utilizador existe        
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()  
    sql = "SELECT username,password,salt FROM users where username = '" + username + "';" 
    cursor.execute(sql) 
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
