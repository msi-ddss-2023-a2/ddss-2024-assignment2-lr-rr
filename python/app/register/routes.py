from flask import Flask, render_template, g, request, redirect, url_for,  make_response,  render_template_string
import psycopg2, hashlib, os
from base64 import b64encode
# Route for showing the registration page
def register_html():
    return render_template("register.html")

def db_connection():
    conn = psycopg2.connect(user = "ddss-database-assignment-2",
                password = "ddss-database-assignment-2",
                host = "db",
                port = "5432",
                database = "ddss-database-assignment-2")
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

# Route for handling the registration process
def register():
   

    if request.method == 'GET':
        password = request.args.get('v_password') 
        username = request.args.get('v_username') 
    else:
        password = request.form['v_password']
        username = request.form['v_username']
    #Verificar se o utilizador ou password nao tem codigo la pelo meio
    verif_user = sanitize_input(username)
    if verif_user == -1:
        message = "Username not permitted"
        return render_template("register.html",message=message)
    verif_password = sanitize_input(password)
    if verif_password == -1:
        message = "Password not permitted"
        return render_template("register.html",message=message)
    #Verificar se o utilizador existe        
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()  
    query = "SELECT username,password,salt FROM users WHERE username = %s"
    cursor.execute(query, (username,)) 
    results = cursor.fetchall() 
    conn.commit()
    conn.close()
    if results:
        message = "The user exist in the database" 
        return render_template("register.html", message=message)
    
    #Criar o utilizador
    salt = os.urandom(64)
    hash_object = hashlib.sha256()
    hash_object.update(salt + password.encode())
    hash_password = hash_object.hexdigest()
    salted_s = b64encode(salt).decode('utf-8')
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    sql = """ INSERT INTO users
                       (username, password, salt) VALUES (%s,%s,%s)"""
    tuple1 = (username,hash_password, salted_s)
    cursor.execute(sql, tuple1)  
    conn.commit()
    conn.close()
    message = "The user created successfly" 
    return render_template("register.html", message=message)