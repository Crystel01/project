from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

con = sqlite3.connect("messages.db", check_same_thread = False)
cur = con.cursor()


@app.route("/<name>", methods = ['GET', 'POST'])
def main(chat_id):
    # get result from SELECT-Statement as list of lists
    name = request.args['name']
    if request.method == 'POST':
        #name = request.form['name']
        new_message = request.form['new_message']
        print(name, new_message)

        cur.execute('''
            INSERT INTO Messages (name, text, time, chat_id)
            VALUES (?, ?, ?, datetime('now'))
                    ''', [name, new_message, chat_id])
        con.commit()
    
    return render_template("chat.html",  name = name, chat_id = chat_id)

@app.route("/login", methods = ['GET', 'POST'])
def login():
    
    return render_template("login.html")
        


if __name__ == "__main__":
    app.run(debug = True)