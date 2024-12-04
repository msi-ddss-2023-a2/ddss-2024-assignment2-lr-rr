#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, g, request, redirect, url_for, session, make_response
import logging, psycopg2
from register.routes import register_html, register
from part1.routesv import part1_vulnerable
from part1.deletesession import delete_session
from part1.routesc import part1_correct
from datetime import timedelta, datetime
from markupsafe import escape
from flask_talisman import Talisman

app = Flask(__name__, static_folder='templates/static/')
Talisman(app)

@app.before_request
def redirect_to_https():
    # Check if the request is not secure
    if not request.is_secure:
        # Redirect to HTTPS with the correct host and path
        return redirect(f"https://{request.host}{request.path}", code=301)    

@app.route("/")
def home():
    return render_template("index.html")

# Register routes for registration
@app.route("/register.html")
def register_page():
    return register_html()

@app.route("/register", methods=["POST", "GET"])
def register_action():
    return register()

@app.route('/target')
def target():
    return render_template('index.html')

@app.route("/part1.html", methods=['GET'])
def login():
    return render_template("part1.html");

@app.route("/part1_vulnerable", methods=['GET', 'POST'])
def part1_vulnerable_app():
    return part1_vulnerable()

@app.route("/part1_correct", methods=['GET', 'POST'])
def part1_correct_app():
    
    return part1_correct()

@app.route('/logout')
def delete_session_app():
    return delete_session()


@app.route("/part2.html", methods=["GET", "POST"])
def part2():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        # Form submission handling
        form_source = request.form.get("form_source")
        author = session.get("username", "anonymous")
        message = request.form.get("text", "")

        if form_source == "vulnerable":
            # Append a marker to the vulnerable message
            message_with_marker = f"{message} [Vulnerable]"
        elif form_source == "correct":
            # Sanitize the input and append a marker for correct messages
            message_with_marker = f"{escape(message)} [Correct]"
        else:
            message_with_marker = ""

        if message_with_marker:
            cur.execute(
                "INSERT INTO messages (author, message) VALUES (%s, %s)",
                (author, message_with_marker),
            )
            conn.commit()

    # Fetch all messages for display
    cur.execute("SELECT author, message FROM messages ORDER BY message_id DESC")
    messages = cur.fetchall()
    conn.close()

    return render_template("part2.html", messages=messages)


@app.route("/part2.html", methods=["GET", "POST"])
def part2_page():  # Renamed to avoid conflicts
    conn = get_db()
    cur = conn.cursor()

    # Fetch all messages
    cur.execute("SELECT text, is_vulnerable FROM messages ORDER BY id DESC")
    messages = cur.fetchall()
    conn.close()

    return render_template("part2.html", messages=messages)

@app.route("/part2_vulnerable", methods=["GET", "POST"])
def part2_vulnerable():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        author = session.get("username", "anonymous")
        message = request.form["v_text"]

        # Append "[Vulnerable]" marker to the message
        message_with_marker = f"{message} [Vulnerable]"

        cur.execute(
            "INSERT INTO messages (author, message) VALUES (%s, %s)",
            (author, message_with_marker),
        )
        conn.commit()

    # Fetch all messages for display
    cur.execute("SELECT author, message FROM messages ORDER BY message_id DESC")
    messages = cur.fetchall()
    conn.close()

    return render_template("part2.html", messages=messages)


@app.route("/part2_correct", methods=["GET", "POST"])
def part2_correct():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        author = escape(session.get("username", "anonymous"))  # Sanitize session input
        message = escape(request.form["c_text"])  # Sanitize input

        # Append "[Correct]" marker to the message
        message_with_marker = f"{message} [Correct]"

        # Correct parameterized query for psycopg2
        cur.execute(
            "INSERT INTO messages (author, message) VALUES (%s, %s)",
            (author, message_with_marker),
        )
        conn.commit()

    # Fetch all messages for display
    cur.execute("SELECT author, message FROM messages ORDER BY message_id DESC")
    messages = cur.fetchall()
    conn.close()

    return render_template("part2.html", messages=messages)

@app.route("/insert_book", methods=["POST"])
def insert_book():
    try:
        # Get form data
        title = request.form["title"]
        authors = request.form["authors"]
        category = request.form["category"]
        price = request.form["price"]
        book_date = request.form["book_date"]
        description = request.form["description"]
        keywords = request.form["keywords"]
        notes = request.form["notes"]
        recommendation = request.form["recommendation"]

        # Insert into the database
        conn = get_db()
        cur = conn.cursor()

        query = """
        INSERT INTO books (title, authors, category, price, book_date, description, keywords, notes, recomendation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (title, authors, category, price, book_date, description, keywords, notes, recommendation))

        conn.commit()
        cur.close()
        conn.close()

        return "Book has been successfully added to the database.", 200
    except Exception as e:
        return f"Failed to add the book: {str(e)}", 500

@app.route("/part3.html", methods=['GET'])
def part3():
    return render_template("part3.html");


@app.route("/part3_vulnerable", methods=["GET", "POST"])
def part3_vulnerable():
    results = None
    error = None
    if request.method == "POST":
        try:
            # Get form inputs
            title = request.form.get("title", "")
            authors = request.form.get("authors", "")
            category = request.form.get("category", "")
            keywords = request.form.get("keywords", "")

            # Vulnerable SQL query
            query = f"""
            SELECT * FROM books
            WHERE title LIKE '%{title}%'
              AND authors LIKE '%{authors}%'
              AND category LIKE '%{category}%'
              AND keywords LIKE '%{keywords}%'
            """
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query)
            results = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            error = str(e)

    return render_template("part3.html", results=results, error=error)

@app.route("/part3_correct", methods=["GET", "POST"])
def part3_correct():
    results = None
    error = None
    if request.method == "POST":
        try:
            # Get form inputs
            title = request.form.get("title", "")
            authors = request.form.get("authors", "")
            category = request.form.get("category", "")
            keywords = request.form.get("keywords", "")

            # Secure SQL query with parameterized inputs
            query = """
            SELECT * FROM books
            WHERE title LIKE %s
              AND authors LIKE %s
              AND category LIKE %s
              AND keywords LIKE %s
            """
            params = (
                f"%{title}%",
                f"%{authors}%",
                f"%{category}%",
                f"%{keywords}%",
            )
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            error = str(e)

    return render_template("part3.html", results=results, error=error)

##########################################################
## DATABASE ACCESS
##########################################################

def get_db():
    db = psycopg2.connect(user = "ddss-database-assignment-2",
                password = "ddss-database-assignment-2",
                host = "db",
                port = "5432",
                database = "ddss-database-assignment-2")
    return db

##########################################################
## MAIN
##########################################################
if __name__ == "__main__":
    logging.basicConfig(filename="log_file.log")

    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
     
    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s:  %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.info("\n---------------------\n\n")

    #app.run(debug=False)  # Disable debug mode in production    
    ####################################
    #TODO:Falar com o Rui sobre isto
    app.secret_key = 'super secret key'
    ####################################
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, ssl_context=('certificates/cert.pem', 'certificates/key.pem'))  # Enable debug mode for development






