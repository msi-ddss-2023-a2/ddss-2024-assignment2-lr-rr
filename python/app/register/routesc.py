from flask import Flask, render_template, g, request, redirect, url_for,  make_response,  render_template_string
import psycopg2, hashlib, os,re
from base64 import b64encode
# Route for showing the registration page

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


# Route for handling the registration process
def register():
   

    if request.method == 'GET':
        password = request.args.get('c_password') 
        username = request.args.get('c_username')
        phonenumber =  request.args.get('c_phonenumber')
    else:
        password = request.form['c_password']
        username = request.form['c_username']
        phonenumber =  request.args.get('c_phonenumber')
    #Verificar se o utilizador ou password nao tem codigo la pelo meio
    verif_user = sanitize_input(username)
    if verif_user == -1:
        message = "Username not permitted"
        return render_template("register.html",messages=message, message_type="error")
    verif_password = sanitize_input(password)
    if verif_password == -1:
        message = "Password not permitted"
        return render_template("register.html",messages=message, message_type="error")
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
        return render_template("register.html", messages=message,message_type="error")
     #Check password strength
    #password_feedback = is_password_strong(password)
    #if password_feedback:
    #    return render_template("register.html", messages=password_feedback, message_type="error") 
    #Verificar o numero de telemovel
    if not phonenumber.isnumeric():
        message = "Input only numbers"
        return render_template("register.html", messages=message, message_type="error")
    if not len(phonenumber) == 9:
        message = "Input nine numbers"
        return render_template("register.html", messages=message, message_type="error")
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
                       (username, password, salt,phonenumber) VALUES (%s,%s,%s,%s)"""
    tuple1 = (username,hash_password, salted_s,phonenumber)
    cursor.execute(sql, tuple1)  
    conn.commit()
    conn.close()
    message = "The user created successfly" 
    return render_template("register.html", messages=message, message_type="success") 