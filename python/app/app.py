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
        title = request.form.get("title", "").strip()
        authors = request.form.get("authors", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        book_date = request.form.get("book_date", "").strip()
        description = request.form.get("description", "").strip()
        keywords = request.form.get("keywords", "").strip()
        notes = request.form.get("notes", "").strip()
        recommendation = request.form.get("recommendation", "").strip()

        # Validate required fields
        if not title or not authors or not category or not price or not book_date:
            return render_template("part1.html", message="Missing required fields.", message_type="error")

        # Validate price
        try:
            price = float(price)
            if price <= 0:
                return render_template("part1.html", message="Price must be a positive number.", message_type="error")
        except ValueError:
            return render_template("part1.html", message="Invalid price format.", message_type="error")

        # Validate date
        try:
            # Ensure the date is in the correct format
            book_date = datetime.strptime(book_date, "%Y-%m-%d")
        except ValueError:
            return render_template("part1.html", message="Invalid date format. Use YYYY-MM-DD.", message_type="error")

        # Ensure the date is not in the future
        if book_date > datetime.today():
            return render_template("part1.html", message="The book date cannot be in the future.", message_type="error")

        # Optional length validation
        if len(title) > 255 or len(authors) > 255 or len(category) > 100:
            return render_template("part1.html", message="One or more fields exceed allowed length.", message_type="error")

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

        return render_template("part1.html", message="Book has been successfully added to the database.", message_type="success")
    except Exception as e:
        return render_template("part1.html", message=f"Failed to add the book: {str(e)}", message_type="error")


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
            v_radio_match = request.form.get("v_radio_match", "any")
            v_sp_date_range = request.form.get("v_sp_date_range", "-1")
            v_sp_start_month = request.form.get("v_sp_start_month", "0")
            v_sp_start_day = request.form.get("v_sp_start_day", "0")
            v_sp_start_year = request.form.get("v_sp_start_year", "")
            v_sp_end_month = request.form.get("v_sp_end_month", "0")
            v_sp_end_day = request.form.get("v_sp_end_day", "0")
            v_sp_end_year = request.form.get("v_sp_end_year", "")

            # Start building the SQL query
            query = "SELECT * FROM books WHERE 1=1"
            conditions = []

            # Add conditions for title, author, and category
            if v_name:
                conditions.append(f"title ILIKE '%{v_name}%'")
            if v_author:
                conditions.append(f"authors ILIKE '%{v_author}%'")
            if v_category_id:
                conditions.append(f"category = '{v_category_id}'")

            # Add conditions for price range
            if v_pricemin:
                conditions.append(f"price >= {v_pricemin}")
            if v_pricemax:
                conditions.append(f"price <= {v_pricemax}")

            # Add advanced search input condition
            if v_search_input:
                if v_radio_match == "any":
                    operator = " OR "
                elif v_radio_match == "all":
                    operator = " AND "
                else:  # Exact phrase
                    operator = ""

                if v_search_field == "any":
                    search_fields = ["title", "authors", "description", "keywords", "notes"]
                else:
                    search_fields = [v_search_field]

                search_conditions = [f"{field} ILIKE '%{v_search_input}%'" for field in search_fields]
                if operator:
                    conditions.append(f"({operator.join(search_conditions)})")
                else:
                    conditions.append(search_conditions[0])

             # Add date range conditions
            if v_sp_date_range != "-1":
                conditions.append(f"book_date >= NOW() - INTERVAL '{v_sp_date_range} days'")
            elif v_sp_start_year and not v_sp_end_year:
                # Search within a specific year
                start_date = f"{v_sp_start_year}-01-01"
                end_date = f"{v_sp_start_year}-12-31"
                conditions.append(f"book_date BETWEEN '{start_date}' AND '{end_date}'")
            elif v_sp_start_year and v_sp_end_year:
                # Search within a specified range
                start_date = f"{v_sp_start_year}-01-01"
                end_date = f"{v_sp_end_year}-12-31"
                conditions.append(f"book_date BETWEEN '{start_date}' AND '{end_date}'")


            # Combine conditions
            if conditions:
                query += " AND " + " AND ".join(conditions)

            # Execute the vulnerable query
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query)  # Vulnerable to SQL injection
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
            # Collect form inputs
            v_name = request.form.get("v_name", "")
            v_author = request.form.get("v_author", "")
            v_category_id = request.form.get("v_category_id", "")
            v_pricemin = request.form.get("v_pricemin", None)
            v_pricemax = request.form.get("v_pricemax", None)
            v_search_input = request.form.get("v_search_input", "")
            v_search_field = request.form.get("v_search_field", "any")
            v_radio_match = request.form.get("v_radio_match", "any")
            v_sp_date_range = request.form.get("v_sp_date_range", "-1")
            v_sp_start_month = request.form.get("v_sp_start_month", "0")
            v_sp_start_day = request.form.get("v_sp_start_day", "0")
            v_sp_start_year = request.form.get("v_sp_start_year", "")
            v_sp_end_month = request.form.get("v_sp_end_month", "0")
            v_sp_end_day = request.form.get("v_sp_end_day", "0")
            v_sp_end_year = request.form.get("v_sp_end_year", "")

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
                query += " AND price >= %s"
                params.append(v_pricemin)
            if v_pricemax:
                query += " AND price <= %s"
                params.append(v_pricemax)

            # Add advanced search input condition
            if v_search_input:
                if v_radio_match == "any":
                    operator = " OR "
                elif v_radio_match == "all":
                    operator = " AND "
                else:  # Exact phrase
                    operator = ""

                if v_search_field == "any":
                    search_fields = ["title", "authors", "description", "keywords", "notes"]
                else:
                    search_fields = [v_search_field]

                search_conditions = [f"{field} ILIKE %s" for field in search_fields]
                params.extend([f"%{v_search_input}%"] * len(search_fields))
                if operator:
                    query += f" AND ({operator.join(search_conditions)})"
                else:
                    query += f" AND {search_conditions[0]}"

            # Add date range conditions
            if v_sp_date_range != "-1":
                query += " AND book_date >= NOW() - INTERVAL %s"
                params.append(f"{v_sp_date_range} days")
            elif v_sp_start_year and v_sp_end_year:
                try:
                    start_date = f"{int(v_sp_start_year)}-{int(v_sp_start_month):02}-{int(v_sp_start_day):02}"
                    end_date = f"{int(v_sp_end_year)}-{int(v_sp_end_month):02}-{int(v_sp_end_day):02}"
                    query += " AND book_date BETWEEN %s AND %s"
                    params.extend([start_date, end_date])
                except ValueError:
                    raise ValueError("Invalid date format provided.")

            # Execute the secure query
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






