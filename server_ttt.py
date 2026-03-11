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

#redirected zu start und beendet die Session
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

#Hauptseite mit Auswahl, falls vom Singleplayer aufgerufen wird, wird die Gesamthisotie gespeichert
@app.route("/main", methods = ['GET', 'POST'])
def main(): 
    #falls User nicht eingeloggt existiert er nicht im Wörterbuch -> zurück zum Login
    if "user" not in session:
        return redirect(url_for("login"))
    
    username = session["user"]
    
    #falls noch game offen ist und von eigenem User erstellt wurde, so wird Spiel gelöscht
    #P.S.: inner join ist wie normales Kreuprodukt (User, Player, Games), bloß effektiver und dahinter wird mit 'on' gefiltert
    cur.execute(''' SELECT Games.ID FROM User INNER JOIN Player on User.ID = Player.user_id 
                                        INNER JOIN Games on Player.ID = Games.playerID_X
                where Games.active = 'waiting' 
                AND User.Username = ?
                AND Games.playerID_X IS NOT NULL
                AND Games.playerID_O IS NULL
    ''', [username,])
    row = cur.fetchone()
    if row is not None:
        temp_game_id = row[0]
        cur.execute(''' DELETE FROM Games WHERE ID = ? ''', [temp_game_id,])
        con.commit()

    #bei beenden TTT wird Game gespeichert
    if request.method == "POST":
        player_id = session["player_id"]
        game_id = session["game_id"]
        game_history = request.form["history"]
        cur.execute('''INSERT INTO Move (game_history, game_id, player_id, created_at) 
                    VALUES (?, ?, ?, DATE('now'))''', [game_history, game_id, player_id])
        con.commit()
        session.pop("game_id", None)

    return render_template("main.html", username = username)

#tictactoe Seite für Ki
@app.route("/tictactoe/singleplayer", methods = ["GET", "POST"])
def tictactoe():
    if "user" not in session:
        return redirect(url_for("login"))
    
    #bei neustart wird Game gespeichert
    if request.method == "POST":
        player_id = session["player_id"]
        game_id = session["game_id"]
        game_history = request.form["history"]
        cur.execute('''INSERT INTO Move (game_history, game_id, player_id, created_at) 
                    VALUES (?, ?, ?, DATE('now'))''', [game_history, game_id, player_id])
        con.commit()
        # winner_id = request.form
        # cur.execute('''INSERT INTO Games (winner_id) VALUES (?)''', [winner_id,])
        # con.commit
        session.pop("game_id", None)
    
    username = session["user"]
    cur.execute("SELECT id FROM User WHERE Username = ?", (username,))
    user_row = cur.fetchone()
    user_id = user_row[0]

    #prüfe ob player schon existiert
    cur.execute("SELECT id FROM Player WHERE user_id = ?", [user_id,])
    player_row = cur.fetchone()

    #falls existiert wird kein neuer Player angelegt
    if player_row:
        player_id = player_row[0]
    else: 
        cur.execute("INSERT INTO Player (user_id, role) VALUES (?, ?)", (user_id, "X"))
        player_id = cur.lastrowid
        con.commit()
    
    session["player_id"] = player_id

    #kreiert neues Game, speichert in Game Tabelle
    cur.execute("""
    INSERT INTO Games (playerID_X, created_at, game_type)
    VALUES (?, DATE('now'), 'ttt_singleplayer')
    """, (player_id,))

    game_id = cur.lastrowid
    session["game_id"] = game_id
    con.commit()
    return render_template("tictactoe.html")

#tictactoe Anzeige für Multiplayer
@app.route("/tictactoe/multiplayer", methods = ["GET", "POST"])
def tictactoe_multiplayer():
    if "user" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("main"))

#checkt, ob es schon Spiele gibt, die kreiert wurden und entscheidet ob kreiert werden muss oder join
@app.route("/tictactoe/check_for_players")
def player_check():
    if "user" not in session:
        return redirect(url_for("login"))
    cur.execute('''
    SELECT COUNT(*) FROM Games WHERE playerID_X IS NOT NULL AND playerID_O IS NULL 
                AND game_type = "ttt_multiplayer" AND active = 'waiting'
    ''')
    count = cur.fetchone()
    
    username = session["user"]
    cur.execute("SELECT id FROM User WHERE Username = ?", (username,))
    user_row = cur.fetchone()
    user_id = user_row[0]

    #prüfe ob player schon existiert
    cur.execute("SELECT id FROM Player WHERE user_id = ?", [user_id,])
    player_row = cur.fetchone()

    #falls existiert wird kein neuer Player angelegt
    if player_row:
        player_id = player_row[0]
    else: 
        cur.execute("INSERT INTO Player (user_id, role) VALUES (?, ?)", (user_id, "X"))
        player_id = cur.lastrowid
        con.commit()
    
    session["player_id"] = player_id
    
    if count[0] >= 1:
        cur.execute("SELECT ID FROM Games WHERE playerID_X IS NOT NULL AND playerID_O IS NULL " \
        "AND game_type = 'ttt_multiplayer' AND active = 'waiting'")
        row = cur.fetchone()
        game_id = row[0]
        session["game_id"] = game_id
        return redirect(url_for("join_game", game_id = game_id))
    else: 
        return redirect(url_for("create_game"))

#erstellt neues Spiel und leitet an Wartezimmer weiter
@app.route("/tictactoe/create_game")
def create_game():
    if "user" not in session:
        return redirect(url_for("login"))
    player_id = session["player_id"]
    cur.execute("""
    INSERT INTO Games (playerID_X, game_type, created_at, active)
    VALUES (?, 'ttt_multiplayer', DATE('now'), 'waiting')
    """, (player_id,))

    game_id = cur.lastrowid
    con.commit()
    session["game_id"] = game_id
    return redirect(url_for("waiting_room"))

#Wartezimmer, html refresht alle 5s, ob Spieler gejoint ist
@app.route("/tictactoe/waiting_for_player")
def waiting_room():     #zurück Knopf macht Probleme, wenn Spiel gefunden noch keine Weiterleitung (HTML erstellen, ändern)
    if "user" not in session:
        return redirect(url_for("login"))
    game_id = session["game_id"]
    cur.execute("""
    SELECT playerID_O
    FROM Games
    WHERE id = ?
    """, (game_id,))

    row = cur.fetchone()

    if row[0] is not None:
        return redirect(url_for("tictactoe_multiplayer"))
    
    return render_template("waiting.html")
     
#Spiel existiert, -> joinen
@app.route("/tictactoe/join_game")
def join_game():
    if "user" not in session:
        return redirect(url_for("login"))
    player_id = session["player_id"]
    game_id = session["game_id"]
    cur.execute(" UPDATE Games SET playerID_O = ? AND active = 'found' WHERE ID = ?", [player_id, game_id])
    con.commit()
    
    return redirect(url_for("tictactoe_multiplayer"))

# @app.route("/tictactoe/multiplayer", methods = ["GET", "POST"])
# def tttm():
    if "user" not in session:
        return redirect(url_for("login"))

#Zustand, wenn Spieler an der Reihe ist
@app.route("/tictactoe/make_move", methods = ["POST"])
def make_move():
    if "user" not in session:
        return redirect(url_for("login"))
    game_id = session["game_id"]
    player_id = session["player_id"]
    position = request.form["history"]

    cur.execute("INSERT INTO Move (game_id, player_id, game_history) VALUES (?, ?, ?)", [game_id, player_id, position])
    con.commit()

    return render_template("tictactoe.html")

#warten auf den Zug des Gegenspielers, übergibt alle moves als 'history'
@app.route("/tictactoe/get_moves")
def get_moves():
    if "user" not in session:
        return redirect(url_for("login"))
    
    game_id = session["game_id"]
    
    cur.execute("""
    SELECT position, player_id
    FROM Move
    WHERE game_id = ?
    """, (game_id,))

    moves = cur.fetchall()

    return render_template("tictactoe.html", history = moves)

if __name__ == "__main__":
    app.run(debug = True)
