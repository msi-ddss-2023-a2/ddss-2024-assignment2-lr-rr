from flask import Flask, render_template, g, request, redirect, url_for, session, make_response, app
import logging, psycopg2
import base64, hashlib, os
import datetime
from dotenv import load_dotenv

#Password validation function
def is_password_strong(password):
    # Minimum 8 characters, maximum 64
    if len(password) < 8 or len(password) > 64:
        return "Password must be between 8 and 64 characters long."

    #Must include at least one uppercase, one lowercase, one number, and one special character
    if not re.search(r'[A-Z]', password):
        return "Password must include at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must include at least one lowercase letter."
    if not re.search(r'\d', password):
        return "Password must include at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must include at least one special character."

    #No spaces allowed
    if ' ' in password:
        return "Password must not contain spaces."

    # All checks passed
    return None 

def db_connection():
    conn = psycopg2.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )
    return conn

def sanitize_input(user_input):
    if user_input.find("eval") != -1:
        return -1
    elif user_input.find("exec") != -1:
        return -1
    elif user_input.find("execfile") != -1:
        return -1
    elif user_input.find("input")  != -1:
        return -1
    elif user_input.find("compile")  != -1:
        return -1
    elif user_input.find("open")  != -1:
        return -1
    elif user_input.find("os.system")  != -1:
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
        return render_template("part1.html",messages=message, message_type="error")
    verif_password = sanitize_input(password)
    if verif_password == -1:
        message = "Password not permitted"
        return render_template("part1.html",messages=message, message_type="error")
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
        return render_template("part1.html",messages=message, message_type="error")
    
    #Check password strength
    #password_feedback = is_password_strong(password)
    #if password_feedback:
    #    return render_template("register.html", messages=password_feedback, message_type="error") 
    
    username_d, password_d, salt_d = results[0]
    salt_d = salt_d.encode(encoding="utf-8")
    salt_d = base64.decodebytes(salt_d)
    hash_object = hashlib.sha256()
    hash_object.update(salt_d + password.encode())
    hash_password = hash_object.hexdigest()
    if password_d == hash_password:

        message = "Sucess"
        if remember == "on":
            session.permanent = True
        else:
            session.permanent = False
        session['username'] = username
        return render_template("part1.html",messages=message,message_type="success")
    else:
        return render_template("part1.html", messages=message,message_type="error")