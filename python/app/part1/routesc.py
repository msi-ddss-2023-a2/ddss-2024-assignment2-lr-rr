from flask import Flask, render_template, g, request, redirect, url_for, session, make_response, app
import logging, psycopg2
import base64, hashlib, os
import datetime
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

#@app.route('/mfa_verification', methods=['GET', 'POST'])
#def mfa_verification():
    #if 'username' not in session:
     #   return redirect(url_for('register'))
    
    #if request.method == 'POST':
        # Simulate MFA verification (e.g., verify OTP)
    #    otp = request.form['otp']
    #    if otp == "123456":  # Replace with actual OTP validation logic
    #        return render_template("success.html", messages="MFA completed successfully! User registration finalized.", message_type="success")
    #    else:
    #        return render_template("mfa_verification.html", messages="Invalid OTP. Please try again.", message_type="error")
    
    # Render MFA verification page
 #   return render_template("mfa_verification.html")

def sanitize_input(user_input):
    dangerous_terms = {"eval", "exec", "execfile", "input", "compile", "open", "os.system"}
    
    # Convert input to lowercase for case-insensitive comparison
    user_input = user_input.lower()
    
    # Check if any dangerous term is in the input
    if any(term in user_input for term in dangerous_terms):
        return -1
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
    
   
    
    username_d, password_d, salt_d = results[0]
    salt_d = salt_d.encode(encoding="utf-8")
    salt_d = base64.decodebytes(salt_d)
    hash_object = hashlib.sha256()
    hash_object.update(salt_d + password.encode())
    hash_password = hash_object.hexdigest()
    
    if password_d == hash_password:
        # Password is correct; set temporary session flag for MFA verification
        session.clear()  # Clear session to avoid bypass
        session['temp_username'] = username  # Temporary session variable for MFA
        session.permanent = remember == "on"
        return redirect(url_for('mfa_verification'))
    else:
        return render_template("part1.html", messages="Failed Credentials", message_type="error")

