#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, g, request, redirect, url_for, session, make_response
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

        # Vulnerable SQL query without parameterization
        cur.execute(
            f"INSERT INTO messages (author, message) VALUES ('{author}', '{message_with_marker}')"
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
        title = request.form.get("title", "").strip()
        authors = request.form.get("authors", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        book_date = request.form.get("book_date", "").strip()
        description = request.form.get("description", "").strip()
        keywords = request.form.get("keywords", "").strip()
        notes = request.form.get("notes", "").strip()
        recommendation = request.form.get("recomendation", "").strip()

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
        cur.execute(query, (title, authors, category, price, book_date.strftime("%Y-%m-%d"), description, keywords, notes, recommendation))

        conn.commit()
        cur.close()
        conn.close()

        return render_template("part1.html", messages="Book has been successfully added to the database.", message_type="success")
    except Exception as e:
        return render_template("part1.html", messages=f"Failed to add the book: {str(e)}", message_type="error")


@app.route("/part3.html", methods=['GET'])
def part3():
    return render_template("part3.html");


@app.route("/part3_vulnerable", methods=["GET", "POST"])
def part3_vulnerable():
    results = None
    error = None
    if request.method == "POST":
        try:
            # Collect form inputs
            v_name = request.form.get("v_name", "")
            v_author = request.form.get("v_author", "")
            v_category_id = request.form.get("v_category_id", "")
            v_pricemin = request.form.get("v_pricemin", None)
            v_pricemax = request.form.get("v_pricemax", None)
            v_search_input = request.form.get("v_search_input", "")
            v_search_field = request.form.get("v_search_field", "any")
            v_radio_match = request.form.get("v_radio_match", "any").strip()
            v_sp_start_date = request.form.get("v_sp_start_date", "").strip()
            v_sp_end_date = request.form.get("v_sp_end_date", "").strip()
            sort_by = request.form.get("v_sp_s", "0")

            # Start building the SQL query
            query = "SELECT * FROM books WHERE 1=1"
            params = []

            # Add conditions for title, author, and category
            if v_name:
                query += " AND title ILIKE %s"
                params.append(f"%{v_name}%")
            if v_author:
                query += " AND authors ILIKE %s"
                params.append(f"%{v_author}%")
            if v_category_id:
                query += " AND category = %s"
                params.append(v_category_id)

            # Add conditions for price range
            if v_pricemin:
                try:
                    v_pricemin = float(v_pricemin)
                    query += " AND price >= %s"
                    params.append(v_pricemin)
                except ValueError:
                    error = "Invalid minimum price."
                    return render_template("part3.html", results=None, error=error)
            if v_pricemax:
                try:
                    v_pricemax = float(v_pricemax)
                    query += " AND price <= %s"
                    params.append(v_pricemax)
                except ValueError:
                    error = "Invalid maximum price."
                    return render_template("part3.html", results=None, error=error)

            # Add conditions for date range
            if v_sp_start_date or v_sp_end_date:
                try:
                    if v_sp_start_date:
                        start_date = datetime.strptime(v_sp_start_date, "%Y-%m-%d")
                    else:
                        start_date = None

                    if v_sp_end_date:
                        end_date = datetime.strptime(v_sp_end_date, "%Y-%m-%d")
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
                    error = "Invalid date format. Use YYYY-MM-DD."
                    return render_template("part3.html", results=None, error=error)

            # Add advanced search input condition
            if v_search_input:
                if v_search_field == "any":
                    search_fields = ["title", "authors", "description", "keywords", "notes"]
                else:
                    search_fields = [v_search_field]

                search_conditions = [f"{field} ILIKE %s" for field in search_fields]
                if v_radio_match == "any":
                    query += " AND (" + " OR ".join(search_conditions) + ")"
                elif v_radio_match == "all":
                    query += " AND (" + " AND ".join(search_conditions) + ")"
                else:  # Exact phrase
                    query += " AND (" + search_conditions[0] + ")"
                params.extend([f"%{v_search_input}%"] * len(search_fields))

            # Add sorting condition
            if sort_by == "0":  # Sort by recommendation
                query += " ORDER BY recomendation DESC"
            else:  # Default: sort by book_date
                query += " ORDER BY book_date DESC"

            # Execute the query
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query, params)
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






