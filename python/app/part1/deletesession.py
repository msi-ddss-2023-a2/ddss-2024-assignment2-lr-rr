from flask import Flask, render_template, session
def delete_session():
    session.clear()
    return render_template("part1.html")