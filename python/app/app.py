#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, g, request, redirect, url_for, session, make_response
import logging, psycopg2
from register.register import register

from part1.routesv import part1_vulnerable
from part1.deletesession import delete_session
from part1.routesc import part1_correct
from datetime import timedelta, datetime
from markupsafe import escape
#from flask_talisman import Talisman
import os
from dotenv import load_dotenv

#Load environment variables from a .env file
load_dotenv() 
app = Flask(__name__, static_folder='templates/static/')
#Talisman(app)


@app.route("/")
def home():
    return render_template("index.html")

#Register routes for registration
@app.route("/register.html")
def register_page():
    return render_template("register.html")

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



@app.route("/mfa_verification.html", methods=['GET', 'POST'])
def mfa_verification_func():
    return render_template("mfa_verification.html")

@app.route("/part1_correct", methods=['GET', 'POST'])
def part1_correct_app():
    
    return part1_correct()

@app.route('/logout')
def delete_session_app():
    return delete_session()


@app.route("/part2.html", methods=["GET"])
def part2():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "GET":
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


@app.route("/part2_vulnerable", methods=["POST"])
def part2_vulnerable():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        author = session.get("username", "anonymous")
        message = request.form["v_text"]

        # Truncate the message to 256 characters if it's too long (adjust for the marker length)
        max_message_length = 256 - len(" [Vulnerable]")
        if len(message) > max_message_length:
            message = message[:max_message_length]

        # Escape single quotes in the message to avoid SQL syntax errors
        message_with_marker = f"{message} [Vulnerable]".replace("'", "''")

        # Vulnerable SQL query without parameterization
        cur.execute(
            f"INSERT INTO messages (author, message) VALUES ('{author}', '{message_with_marker}')"
        )
        conn.commit()

    # Fetch all messages for display
    cur.execute("SELECT author, message FROM messages ORDER BY message_id DESC")
    conn.close()

    return redirect("part2.html")


@app.route("/part2_correct", methods=["GET", "POST"])
def part2_correct():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        author = escape(session.get("username", "anonymous"))  # Sanitize session input
        message = escape(request.form["c_text"])  # Sanitize input

        # Truncate the message to 256 characters if it's too long (adjust for the marker length)
        max_message_length = 256 - len(" [Correct]")
        if len(message) > max_message_length:
            message = message[:max_message_length]

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

    return redirect("part2.html")

@app.route("/insert_book", methods=["POST"])
def insert_book():
    try:
        # Get form data
        title = request.form.get("title", "").strip()
        authors = request.form.get("authors", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        book_date = request.form.get("book_date", "").strip()
        description = request.form.get("description", "").strip()
        keywords = request.form.get("keywords", "").strip()
        notes = request.form.get("notes", "").strip()
        recomendation = request.form.get("recomendation", "").strip()

        # Validate required fields
        if not title or not authors or not category or not price or not book_date:
            return render_template("part1.html", messages="Missing required fields.", message_type="error")

        # Validate category selection
        valid_categories = {"1": "Programming", "2": "Databases", "3": "HTML & Web design"}
        if category not in valid_categories:
            return render_template("part1.html", messages="You must submit a category!", message_type="error")

        # Validate price
        try:
            price = float(price)
            if price <= 0:
                return render_template("part1.html", messages="Price must be a positive number.", message_type="error")
        except ValueError:
            return render_template("part1.html", messages="Invalid price format.", message_type="error")

        # Validate date
        try:
            # Ensure the date is in the correct format
            book_date = datetime.strptime(book_date, "%Y-%m-%d")
        except ValueError:
            return render_template("part1.html", messages="Invalid date format. Use YYYY-MM-DD.", message_type="error")

        # Ensure the date is not in the future
        if book_date > datetime.today():
            return render_template("part1.html", messages="The book date cannot be in the future.", message_type="error")

        # Optional length validation
        if len(title) > 255 or len(authors) > 255 or len(category) > 100:
            return render_template("part1.html", messages="One or more fields exceed allowed length.", message_type="error")

        # Database interaction
        conn = get_db()
        cur = conn.cursor()

        query = """
        INSERT INTO books (title, authors, category, price, book_date, description, keywords, notes, recomendation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (title, authors, category, price, book_date.strftime("%Y-%m-%d"), description, keywords, notes, recomendation))

        conn.commit()
        cur.close()
        conn.close()

        return render_template("part1.html", messages="Book has been successfully added to the database.", message_type="success")
    except Exception as e:
        return render_template("part1.html", messages=f"Failed to add the book: {str(e)}", message_type="error")


@app.route("/part3.html", methods=['GET'])
def part3():
    return render_template("part3.html");


@app.route("/part3_vulnerable", methods=["POST"])
def part3_vulnerable():
    results = None
    error = None
    if request.method == "POST":
        try:
            # Collect form inputs without any sanitization
            v_name = request.form.get("v_name", "")
            v_author = request.form.get("v_author", "")
            v_category_id = request.form.get("v_category_id", "")
            v_pricemin = request.form.get("v_pricemin", "")
            v_pricemax = request.form.get("v_pricemax", "")
            v_search_input = request.form.get("v_search_input", "")
            v_search_field = request.form.get("v_search_field", "any")
            v_radio_match = request.form.get("v_radio_match", "any")
            v_sp_start_date = request.form.get("v_sp_start_date", "")
            v_sp_end_date = request.form.get("v_sp_end_date", "")
            sort_by = request.form.get("v_sp_s", "0")

            # Start building the SQL query with direct user input interpolation
            query = "SELECT * FROM books WHERE 1=1"

            # Add conditions for title, author, and category
            if v_name:
                query += f" AND title ILIKE '%{v_name}%'"
            if v_author:
                query += f" AND authors ILIKE '%{v_author}%'"
            if v_category_id:
                query += f" AND category = '{v_category_id}'"

            # Add conditions for price range
            if v_pricemin:
                query += f" AND price >= {v_pricemin}"
            if v_pricemax:
                query += f" AND price <= {v_pricemax}"

            # Add conditions for date range
            if v_sp_start_date:
                query += f" AND book_date >= '{v_sp_start_date}'"
            if v_sp_end_date:
                query += f" AND book_date <= '{v_sp_end_date}'"

            # Add advanced search input condition
            if v_search_input:
                if v_search_field == "any":
                    search_fields = ["title", "authors", "description", "keywords", "notes"]
                else:
                    search_fields = [v_search_field]

                if v_radio_match == "any":
                    search_conditions = " OR ".join([f"{field} ILIKE '%{v_search_input}%'" for field in search_fields])
                elif v_radio_match == "all":
                    search_conditions = " AND ".join([f"{field} ILIKE '%{v_search_input}%'" for field in search_fields])
                else:  # Exact match
                    search_conditions = f"{search_fields[0]} ILIKE '%{v_search_input}%'"

                query += f" AND ({search_conditions})"

            # Add sorting condition
            if sort_by == "0":  # Sort by recommendation
                query += " ORDER BY recomendation DESC"
            else:  # Default: sort by book_date
                query += " ORDER BY book_date DESC"

            # Execute the vulnerable query
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query)  # Directly using query without parameters
            results = cur.fetchall()
            cur.close()
            conn.close()

        except Exception as e:
            error = str(e)

    return render_template("part3.html", results=results, error=error)


@app.route("/part3_correct", methods=["POST"])
def part3_correct():
    results = None
    error = None
    if request.method == "POST":
        try:
            # Collect form inputs and sanitize them
            c_name = escape(request.form.get("c_name", "").strip())
            c_author = escape(request.form.get("c_author", "").strip())
            c_category_id = escape(request.form.get("c_category_id", "").strip())
            c_pricemin = request.form.get("c_pricemin", None)
            c_pricemax = request.form.get("c_pricemax", None)
            c_search_input = escape(request.form.get("c_search_input", "").strip())
            c_search_field = escape(request.form.get("c_search_field", "any").strip())
            c_radio_match = escape(request.form.get("c_radio_match", "any").strip())
            c_sp_start_date = escape(request.form.get("c_sp_start_date", "").strip())
            c_sp_end_date = escape(request.form.get("c_sp_end_date", "").strip())
            sort_by = escape(request.form.get("c_sp_s", "0").strip())

            # Start building the SQL query
            query = "SELECT * FROM books WHERE 1=1"
            params = []

            # Add conditions for title, author, and category
            if c_name:
                query += " AND title ILIKE %s"
                params.append(f"%{c_name}%")
            if c_author:
                query += " AND authors ILIKE %s"
                params.append(f"%{c_author}%")
            if c_category_id:
                query += " AND category = %s"
                params.append(c_category_id)

            # Add conditions for price range
            if c_pricemin:
                try:
                    c_pricemin = float(c_pricemin)
                    query += " AND price >= %s"
                    params.append(c_pricemin)
                except ValueError:
                    error = "Invalid minimum price. Please enter a valid number."
                    return render_template("part3.html", results=None, error=error)
            if c_pricemax:
                try:
                    c_pricemax = float(c_pricemax)
                    query += " AND price <= %s"
                    params.append(c_pricemax)
                except ValueError:
                    error = "Invalid maximum price. Please enter a valid number."
                    return render_template("part3.html", results=None, error=error)

            # Add conditions for date range
            if c_sp_start_date or c_sp_end_date:
                try:
                    if c_sp_start_date:
                        start_date = datetime.strptime(c_sp_start_date, "%Y-%m-%d")
                    else:
                        start_date = None

                    if c_sp_end_date:
                        end_date = datetime.strptime(c_sp_end_date, "%Y-%m-%d")
                    else:
                        end_date = None

                    if start_date and end_date and start_date > end_date:
                        error = "Start date cannot be greater than end date."
                        return render_template("part3.html", results=None, error=error)

                    if start_date:
                        query += " AND book_date >= %s"
                        params.append(start_date)
                    if end_date:
                        query += " AND book_date <= %s"
                        params.append(end_date)

                except ValueError:
                    error = "Invalid date format. Please use YYYY-MM-DD."
                    return render_template("part3.html", results=None, error=error)

            # Add advanced search input condition
            if c_search_input:
                valid_search_fields = ["title", "authors", "description", "keywords", "notes"]
                if c_search_field == "any":
                    search_fields = valid_search_fields
                elif c_search_field in valid_search_fields:
                    search_fields = [c_search_field]
                else:
                    error = "Invalid search field specified."
                    return render_template("part3.html", results=None, error=error)

                search_conditions = [f"{field} ILIKE %s" for field in search_fields]
                if c_radio_match == "any":
                    query += " AND (" + " OR ".join(search_conditions) + ")"
                elif c_radio_match == "all":
                    query += " AND (" + " AND ".join(search_conditions) + ")"
                else:
                    error = "Invalid match type specified."
                    return render_template("part3.html", results=None, error=error)
                params.extend([f"%{c_search_input}%"] * len(search_fields))

            # Add sorting condition
            if sort_by == "1":  # Sort by recommendation
                query += " ORDER BY recomendation DESC"
            elif sort_by == "0":  # Sort by book_date
                query += " ORDER BY book_date DESC"
            else:
                error = "Invalid sorting option specified."
                return render_template("part3.html", results=None, error=error)

            # Execute the query safely
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
            conn.close()

        except Exception as e:
            error = "An unexpected error occurred. Please try again later."

    return render_template("part3.html", results=results, error=error)

##########################################################
## DATABASE ACCESS
##########################################################

def get_db():
    try:
        db = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),  # Default to localhost
            port=os.getenv("DB_PORT", "5432"),       # Default to 5432
            database=os.getenv("DB_NAME")
        )
        return db
    except psycopg2.OperationalError as e:
        logging.error("Database connection failed: %s", e)
        raise

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
    #Use environment variable for SSL context (optional for production)
    cert_path = os.getenv("SSL_CERT_PATH", "certificates/cert.pem")
    key_path = os.getenv("SSL_KEY_PATH", "certificates/key.pem")

    #Use environment variable for Flask secret key
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, ssl_context=(cert_path, key_path))  # Enable debug mode for development
    






