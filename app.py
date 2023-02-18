from flask import Flask
from flask import render_template, request, g
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_message_db():
    try:
            return g.message_db
    except:
            g.message_db = sqlite3.connect("messages_db.sqlite")
            # Create new database in g attribute if not exist. 
            # See: https://www.sqlitetutorial.net/sqlite-python/creating-tables/
            cmd = \
            f"""CREATE TABLE IF NOT EXISTS messages(
                id integer,
                handle text,
                message text
                );""" 
            cursor = g.message_db.cursor()
            cursor.execute(cmd)
            return g.message_db


def insert_message(request):
    # Get submission variables from submit.html
    message = request.form["message"]
    name = request.form["name"]
    
    conn = g.message_db
    cursor = conn.cursor()
    # Get the length of database, and let the number be the next ID. (ID starts from zero)
    ID = pd.read_sql("SELECT COUNT(*) FROM messages", conn).iloc[0][0]
    cmd = f''' INSERT INTO messages(id,handle,message)
              VALUES('{ID}','{name}','{message}') '''
    cursor.execute(cmd)
    conn.commit()
    conn.close()


def random_messages(n):
    conn = get_message_db()
    random_messages = pd.read_sql(f"SELECT * FROM messages ORDER BY RANDOM() LIMIT {n}", conn)
    conn.close()
    return random_messages


@app.route("/", methods = ["POST","GET"])
def submit():
    get_message_db()
    if request.method == "GET":
        return render_template("submit.html")
    else:
        insert_message(request=request)
        return render_template("submit.html", name = request.form["name"])


@app.route("/view")
def view():
    # Display 5 random messages
    m = random_messages(5)
    return render_template("view.html", messages = m)