from flask import Flask, render_template, request, session, redirect, url_for
from datetime import date
import sqlite3
import bcrypt               #zum verschlüsseln/ hashen der Passwörter
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

#nötig, damit nicht auf den aktuellen Arbeistspeicher zugegriffeen werden muss
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   #guckt wo die Py Datei liegt, definiert als absoluten Pfad und gibt den den Ornder an
db_path = os.path.join(BASE_DIR, "DBPixelPenguin.db")   #verbindet Ordner und DB in Abhängigkeit vom OS 

con = sqlite3.connect(db_path, check_same_thread=False)     #connected zur Datenbank
cur = con.cursor()                                          #ermöglicht Interaktion mit DB
cur.execute("PRAGMA foreign_keys = ON")                     #falls User gelöscht wird automatisch Player, games und Moves gelöscht

#Startseite, auswählen zwischen registrieren und Login
@app.route("/")
def start():
     return render_template("start.html")

#Registrierung mit Umleitung zu main oder login (Email schon vorhanden)
@app.route("/registrierung", methods = ["GET", "POST"])
def registrierung():
    
    if request.method == "POST":
        #wählt EMails aus, welche mit der eingegebenen identisch sind
        email = request.form["email"]
        cur.execute('''
            SELECT Passwort, Username FROM User
            WHERE EMail = ? 
            ''', [email,])
        row = cur.fetchone()
        #falls es schon eine EMail mit dem eingegebenen Namen gibt 
        #wird man zum Login geleitet mit der Hinweis, das sie schon existiert
        if row is not None: 
            return render_template("login.html", exists = True)
        else:
            username = request.form["username"]
            password = request.form["password"]
            #bscrypt braucht eine Folge an Bytes um diese zu verschlüssln
            password_bytes = password.encode('utf-8')
            #generiert random Salt(Schlüssel) fürn hash
            hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt())  
            cur_date = date.today()

            cur.execute('''
                INSERT INTO User (Username, Passwort, EMail, created_at)
                VALUES (?, ?, ?, ?)
                ''', [username, hash, email, cur_date])
            con.commit()

            session["user"] = username
            return redirect(url_for("main"))
    return render_template("registrierung.html")

#Login mit Umleitung zu main oder Registrierung (falls email nicht vorhanden) 
#oder Login (Passwort falsch)
@app.route("/login", methods = ['GET', 'POST'])
def login():  
    if request.method == 'POST': 
        email = request.form["email"]
        password = request.form["password"]
        password_bytes = password.encode('utf-8')

        cur.execute('''
            SELECT Passwort, Username FROM User
            WHERE EMail = ? 
            ''', [email,])
        row = cur.fetchone()

        #falls email nicht existiert gehe zur Registrierung und gebe das an
        if row is None: 
            return render_template("registrierung.html", exists = True)
        
        stored_hash = row[0]
        username = row[1]
        
        #überprüft ob das passwort mit dem gespeicherten Passwort übereinstimmt
        if bcrypt.checkpw(password_bytes, stored_hash):
            session["user"] = username
            return redirect(url_for("main"))
        else:
            return render_template("login.html", check = True)
    return render_template("login.html")

@app.route("/main", methods = ['GET', 'POST'])
def main(): 
    #falls User nicht eingeloggt existiert er nicht im Wörterbuch -> zurück zum Login
    if "user" not in session:
        return redirect(url_for("login"))
    
    #übergeben des Usernamen
    username = session["user"]
    return render_template("main.html", username = username)

#redirected zu start und beendet die Session
@app.route("/logout", )
def logout():
    session.pop("user", None)
    return redirect("/")

#tictactoe Seite
@app.route("/tictactoe")
def ttt():
    if "user" not in session:
        return redirect(url_for("login"))
    
    if "player_id" not in session:
        username = session["user"]
        cur.execute("SELECT id FROM User WHERE Username = ?", (username,))
        user_row = cur.fetchone()
        if user_row:
            user_id = user_row[0]

            cur.execute("INSERT INTO Player (user_id, role) VALUES (?, ?)", (user_id, "X"))
            player_id = cur.lastrowid
            session["player_id"] = player_id
            con.commit()
    else: 
        return redirect(url_for("login"))

    return render_template("tictactoe.html")

if __name__ == "__main__":
    app.run(debug = True)
