from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

con = sqlite3.connect("Passwörter.db", check_same_thread = False)
cur = con.cursor()

@app.route("/")
def start():
     return render_template("start.html")

@app.route("/registrierung", methods = ["GET", "POST"])
def registrierung():

    if request.method == "POST":
        email = request.form["EMail"]

        cur.execute('''
            SELECT EXISTS(
            SELECT 1 FROM Passwörter
            WHERE EMail = ?)
            ''', [email,])
        exists = cur.fetchone()[0]

        if exists == 1:
            print("Ihre E-Mail existiert bereits")
            return render_template("login.html", exists = True)
        else:
            username = request.form["username"]
            password = request.form["password"]
            
            cur.execute('''
                INSERT INTO Passwörter (username, passwort, EMail)
                VALUES (?, ?, ?)
                ''', [username, password, email])
            con.commit()
            return render_template("main.html", username = username)
    return render_template("registrierung.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():  
    if request.method == 'POST': 
        email = request.form["email"]
        password = request.form["password"]

        cur.execute('''
            SELECT EXISTS(SELECT 1 FROM Passwörter
            WHERE EMail = ? and Passwort = ?)
            ''', [email, password])
        check = cur.fetchone()[0]

        cur.execute('''
            SELECT Username FROM Passwörter
            WHERE EMail = ?
        ''', [email,])
        username = cur.fetchone()[0]
        
        if check == 1:
            return render_template("main.html", username = username)
        else: 
            return render_template("login.html", check = False)
    return render_template("login.html")

@app.route("/main", methods = ['GET', 'POST'])
def main(username): 
    return render_template("main.html", username = username)

if __name__ == "__main__":
    app.run(debug = True)
