from flask import Flask, render_template, g, request, redirect, url_for,  make_response,  render_template_string
import psycopg2, hashlib, os,re
from base64 import b64encode
import pyotp
import qrcode
from io import BytesIO
# Route for showing the registration page

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

def sanitize_input(user_input):
    dangerous_terms = {"eval", "exec", "execfile", "input", "compile", "open", "os.system"}
    
    # Convert input to lowercase for case-insensitive comparison
    user_input = user_input.lower()
    
    # Check if any dangerous term is in the input
    if any(term in user_input for term in dangerous_terms):
        return -1
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
        passwordv =  request.args.get('c_passwordv')
        username = request.args.get('c_username')
        
    else:
        password = request.form['c_password']
        username = request.form['c_username']
        passwordv =  request.args.get('c_passwordv')
    
    #Verificar se a password e igual
    if password != passwordv:
        message="Passwords not correspond"
        return render_template("register.html",messages=message, message_type="error")
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
    password_feedback = is_password_strong(password)
    if password_feedback:
        return render_template("register.html", messages=password_feedback, message_type="error") 
    
    #Criar o utilizador
    salt = os.urandom(64)
    hash_object = hashlib.sha512()
    hash_object.update(salt + password.encode())
    hash_password = hash_object.hexdigest()
    salted_s = b64encode(salt).decode('utf-8')
    
    
    # Generate an MFA secret
    mfa_secret = pyotp.random_base32()

    # Create QR Code
    totp = pyotp.TOTP(mfa_secret)
    provisioning_uri = totp.provisioning_uri(name=username, issuer_name="CDSS-A2-MFA")
    qr = qrcode.make(provisioning_uri)

    # Save QR Code as a base64 string for the template
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = b64encode(buffer.getvalue()).decode('utf-8')

    # Save user to the database
    conn = db_connection()
    conn.autocommit = True
    cursor = conn.cursor()
    sql = """ INSERT INTO users
                       (username, password, salt, mfa_secret) VALUES (%s,%s,%s,%s)"""
    tuple1 = (username,hash_password, salted_s, mfa_secret)
    cursor.execute(sql, tuple1)  
    conn.commit()
    conn.close()
    
    message = "The user was created successfully. Scan the QR code with Google Authenticator."
    
    return render_template("register.html", messages=message, message_type="success", qr_code=qr_base64,
        mfa_secret=mfa_secret) 