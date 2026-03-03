from flask import Flask, render_template, request
from datetime import date
import sqlite3
import bcrypt               #zum verschlüsseln/ hashen der Passwörter


app = Flask(__name__)

con = sqlite3.connect("DBPixelPenguin.db", check_same_thread = False)   #connected zur Datenbank
cur = con.cursor()                                                  #ermöglicht Interaktion mit DB

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
            return render_template("main.html")
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
            return render_template("registrierung.html", exists = False)
        
        stored_hash = row[0]
        username = row[1]
        
        #überprüft ob das passwort mit dem gespeicherten Passwort übereinstimmt
        if bcrypt.checkpw(password_bytes, stored_hash):
            return render_template("main.html")
        else:
            return render_template("login.html", check = True)
    return render_template("login.html")

@app.route("/main", methods = ['GET', 'POST'])
def main(): 
    return render_template("main.html")



@app.route("/tictactoe")
def ttt():
    return render_template("tictactoe.html")

if __name__ == "__main__":
    app.run(debug = True)
