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

# Route for handling the registration process
def register():
   

    if request.method == 'GET':
        password = request.args.get('v_password') 
        username = request.args.get('v_username') 
    else:
        password = request.form['v_password']
        username = request.form['v_username']
    
    #Verificar se o utilizador existe        
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()  
    sql = "SELECT username,password FROM users where username = '" + username + "';" 
    cursor.execute(sql) 
    results = cursor.fetchall() 
    conn.commit()
    conn.close()
    if results:
        message = "The user exist in the database" 
        return render_template("register.html", message=message)
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()  
    sql = "SELECT username,password FROM users where username = '" + username + "';" 
    cursor.execute(sql) 
    results = cursor.fetchall() 
    conn.commit()
    conn.close()
    
    #Criar o utilizador
    salt = os.urandom(64)
    hash_object = hashlib.sha256()
    hash_object.update(salt + password.encode())
    hash_password = hash_object.hexdigest()
    salted_s = b64encode(salt).decode('utf-8')
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()  
    sql = "INSERT INTO users (username, password, salt) VALUES ('" + username + "','" + hash_password + "','" + salted_s + "');" 
    cursor.execute(sql)  
    conn.commit()
    conn.close()
    return render_template("register.html")