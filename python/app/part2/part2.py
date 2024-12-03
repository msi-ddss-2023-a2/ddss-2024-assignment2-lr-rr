from flask import Blueprint, request, redirect, url_for, session, escape, render_template
import sqlite3

part2_bp = Blueprint('part2', __name__, template_folder='../templates')

# Route for the vulnerable form
@part2_bp.route('/vulnerable', methods=['POST'])
def vulnerable_form():
    if 'username' not in session:
        return redirect(url_for('login'))
    text = request.form['v_text']
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (text, sanitized) VALUES (?, ?)', (text, 0))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# Route for the correct form
@part2_bp.route('/correct', methods=['POST'])
def correct_form():
    if 'username' not in session:
        return redirect(url_for('login'))
    text = request.form['c_text']
    sanitized_text = escape(text)  # Sanitize user input to prevent XSS
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (text, sanitized) VALUES (?, ?)', (sanitized_text, 1))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))
