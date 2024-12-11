
from flask import Flask, render_template, g, request, redirect, url_for, session, make_response
import logging, psycopg2, bcrypt
import base64, hashlib, os
from dotenv import load_dotenv

load_dotenv()

def db_connection():
    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )
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
    
    message = "The authentication failed. Wrong credentials."
    
    if not results:
        return render_template("part1.html",messages=message, message_type="error")
    
    username_d, password_d, salt_d = results[0]
    
    if bcrypt.checkpw(password.encode(), password_d.encode()):
        message = "You were successfully authenticated."
        
        if remember == "on":
            session.permanent = True
        else:
            session.permanent = False
        
        session['username'] = username
        return render_template("part1.html",messages=message, message_type="success")
    else:
        return render_template("part1.html", messages=message,message_type="error")
