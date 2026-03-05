// Spielfeld
let brett = ['', '', '', '', '', '', '', '', ''];
let spielAktiv = true;
let spielerDran = true;
let difficultyNow = 'easy';
let history_list = [];

// Gewinnoptionen
const gewinnKombinationen = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Horizontal
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Vertikal
    [0, 4, 8], [2, 4, 6]             // Diagonal
];

// Schwierigkeitsgrad
function difficulty(level) {
    difficultyNow = level;
    
    let anzeigeText = level
    document.querySelector('.dropbtn').innerText = "Difficulty: " + anzeigeText;

    neustart(); 
}

// Spieler
function macheZug(feldIndex) {
    if (brett[feldIndex] !== '' || !spielAktiv || !spielerDran) {
        return; 
    }

    brett[feldIndex] = 'X';
    history_list.push("X" + feldIndex);

    document.getElementById('feld-' + feldIndex).innerText = 'X';
    document.getElementById('feld-' + feldIndex).style.color = '#007bff';

    if (prüfeGewinner('X')) {
        beendeSpiel("Gewonnen!", "#007bff");
        return;
    }

    if (!brett.includes('')) {
        beendeSpiel("Unentschieden!", "white");
        return;
    }

    document.getElementById('status-text').innerText = "KI ist am Zug...";
    document.getElementById('status-text').style.color = '#ff8400';
    
    spielerDran = false;
    setTimeout(kiZug, 500);

}

// KI
function kiZug() {
    if (!spielAktiv) return;

    let leereFelder = [];
    for (let i = 0; i < brett.length; i++) {
        if (brett[i] === '') leereFelder.push(i);
    }

    let kiWahl;

    // Wählen des Algorithmus für die konkrete Schwierigkeit
    if (difficultyNow === 'easy') {
        let zufallsIndex = Math.floor(Math.random() * leereFelder.length);
        kiWahl = leereFelder[zufallsIndex];

    } 
    else if (difficultyNow === 'medium') {
        if (Math.random() > 0.7) {
            kiWahl = minimax(brett, 'O').index;
        } else {
            let zufallsIndex = Math.floor(Math.random() * leereFelder.length);
            kiWahl = leereFelder[zufallsIndex];
        }

    } 
    else if (difficultyNow === 'hard') {
        kiWahl = minimax(brett, 'O').index;
    }

    // Zug ausführen
    brett[kiWahl] = 'O';
    document.getElementById('feld-' + kiWahl).innerText = 'O';
    document.getElementById('feld-' + kiWahl).style.color = '#ff8400';

    // Anzeige nach Gewinnerprüfung
    if (prüfeGewinner('O')) {
        beendeSpiel("Verloren!", "#ff8400");
        return;
    }

    if (!brett.includes('')) {
        beendeSpiel("Unentschieden!", "white");
        return;
    }

    // Anzeige für den Spielerzug laden
    document.getElementById('status-text').innerText = "Du bist dran (X)";
    document.getElementById('status-text').style.color = '#007bff';

    // Spieler kann seinen Zug machen
    spielerDran = true;
    history_list.push("O" + kiWahl);
}

// MiniMax
function minimax(neuesBrett, spieler) {
    let leereFelder = [];
    for (let i = 0; i < neuesBrett.length; i++) {
        if (neuesBrett[i] === '') leereFelder.push(i);
    }

    // Simulation
    if (prüfeGewinner('X', neuesBrett)) {
        return { score: -10 };
    } else if (prüfeGewinner('O', neuesBrett)) {
        return { score: 10 };
    } else if (leereFelder.length === 0) {
        return { score: 0 };
    }

    let züge = [];

    for (let i = 0; i < leereFelder.length; i++) {
        let zug = {};
        zug.index = leereFelder[i];
        
        neuesBrett[leereFelder[i]] = spieler;

        if (spieler === 'O') {
            let result = minimax(neuesBrett, 'X');
            zug.score = result.score;
        } else {
            let result = minimax(neuesBrett, 'O');
            zug.score = result.score;
        }
        // Undo-Simulation
        neuesBrett[leereFelder[i]] = '';
        züge.push(zug);
    }

    // Strebt nach bestem Score für die KI und schlechtestem Score für den Spieler
    let besterZugIndex;
    if (spieler === 'O') {
        let bestScore = -10000;
        for (let i = 0; i < züge.length; i++) {
            if (züge[i].score > bestScore) {
                bestScore = züge[i].score;
                besterZugIndex = i;
            }
        }
    } else {
        let bestScore = 10000;
        for (let i = 0; i < züge.length; i++) {
            if (züge[i].score < bestScore) {
                bestScore = züge[i].score;
                besterZugIndex = i;
            }
        }
    }

    return züge[besterZugIndex];
}

// Prüfe GEwinner
function prüfeGewinner(spieler, testBrett = brett) {
    for (let i = 0; i < gewinnKombinationen.length; i++) {
        let kombi = gewinnKombinationen[i];
        let a = kombi[0];
        let b = kombi[1];
        let c = kombi[2];
        
        // Prüfe alle Kominationen und schaue ob gewonnen hat
        if (testBrett[a] === spieler && testBrett[b] === spieler && testBrett[c] === spieler) {
            return true;
        }
    }
    return false;
}

// Spiel beenden
function beendeSpiel(nachricht, farbe) {
    // Deaktivieren
    spielAktiv = false;
    
    // Anzeige
    document.getElementById('status-text').innerText = nachricht;
    document.getElementById('status-text').style.color = farbe;

    // Liste erstellen
    let historyDaten = history_list.join(','); 
    let formElement = document.getElementById('history-form');
    let Url = formElement.action || window.location.href;

    // Formular erstellen und Liste reinschreiben
    let formData = new FormData();
    formData.append('history', historyDaten);

    // Formular abschicken
    fetch(Url, {
        method: 'POST',
        body: formData
    })
}

// Neustart
function neustart() {
    brett = ['', '', '', '', '', '', '', '', ''];
    history_list = [];
    spielAktiv = true;
    
    // Brett leeren
    for (let i = 0; i < 9; i++) {
        document.getElementById('feld-' + i).innerText = '';
    }

    // Spieler kann Zug machen
    spielerDran = true;

    // Status Text anzeige
    document.getElementById('status-text').innerText = "Du bist dran (X)";
    document.getElementById('status-text').style.color = '#007bff';
}