let brett = ['', '', '', '', '', '', '', '', ''];
let spielAktiv = true;
let meinSymbol = GAME_DATA.symbol;
let istMeinZug = (meinSymbol === "X")

if (istMeinZug) {
    document.getElementById('status-text').innerText = "Du bist dran (X)";
    document.getElementById('status-text').style.color = '#007bff';
} else {
    document.getElementById('status-text').innerText = "Auf Gegner warten...";
    document.getElementById('status-text').style.color = '#ffffff';
}

// Gewinnoptionen
const gewinnKombinationen = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Horizontal
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Vertikal
    [0, 4, 8], [2, 4, 6]             // Diagonal
];

function macheZug(feldIndex) {
    if (brett[feldIndex] !== '' || !spielAktiv || !istMeinZug) {
        console.log("Zug nicht möglich!");
        return; 
    }

    brett[feldIndex] = meinSymbol;
    let feldElement = document.getElementById('feld-' + feldIndex);
    feldElement.innerText = meinSymbol;
    feldElement.style.color = (meinSymbol === 'X') ? '#007bff' : '#ff8400';

    let zugString = meinSymbol + feldIndex;
    
    istMeinZug = false;
    document.getElementById('status-text').innerText = "Auf Gegner warten...";
    document.getElementById('status-text').style.color = '#ffffff';

    if (prüfeGewinner(meinSymbol)) {
        beendeSpiel("Gewonnen!", (meinSymbol === 'X') ? '#007bff' : '#ff8400');
    }

    sendeZugAnServer(zugString);
}

function sendeZugAnServer(zugDaten) {
    // Formular erstellen
    let formData = new FormData();
    
    // Zug ins Formular
    formData.append("history", zugDaten);

    // Formular senden
    fetch('/tictactoe/make_move', { 
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        console.log("gesendet, Server sagt:", data);
    })
    .catch(error => console.error("fehler beim senden", error));
}


let pollingIntervall;

// Server nachfragen ob der Gegner einen Zug gemacht hat, damit das Spiel synchron ist
function startePolling() {
    pollingIntervall = setInterval(frageNachGegnerZug, 2000);
}

function frageNachGegnerZug() {
    if (!spielAktiv || istMeinZug) return;

    fetch('/tictactoe/get_moves') 
    .then(response => response.text())
    .then(textDaten => {
        // Nur Text
        let zugText = textDaten.trim(); 
        
        // Prüfe ob es ein Zug ist
        if (zugText.length === 2 && zugText !== "ERROR") {
            let symbol = zugText.charAt(0); 
            let feldIndex = parseInt(zugText.charAt(1)); 

            // Prüfe ob das Feld frei ist
            if (brett[feldIndex] === '' && symbol !== meinSymbol) {
                verarbeiteGegnerZug(feldIndex, symbol);
            }
        }
    })
    .catch(error => console.error("Fehler", error));
}

function verarbeiteGegnerZug(feldIndex, symbol) {
    brett[feldIndex] = symbol;
    
    let feldElement = document.getElementById('feld-' + feldIndex);
    feldElement.innerText = symbol;
    feldElement.style.color = (symbol === 'X') ? '#007bff' : '#ff8400';

    if (prüfeGewinner(symbol)) {
        beendeSpiel("Verloren!", (symbol === 'X') ? '#007bff' : '#ff8400');
        return;
    }

    if (!brett.includes('')) {
        beendeSpiel("Unentschieden!", "white");
        return;
    }

    istMeinZug = true;
    document.getElementById('status-text').innerText = "Du bist dran!";
    document.getElementById('status-text').style.color = (meinSymbol === 'X') ? '#007bff' : '#ff8400';
}

//Gewinner Symbol absenden
function sendeGewinner(){
    let formData = new FormData();
    formData.append("winner_symbol", meinSymbol);

    fetch('/tictactoe/game_won', {
        method: 'POST',
        body: formData
    })
    
}



// Spiel beenden
function beendeSpiel(nachricht, farbe) {
    // Deaktivieren
    spielAktiv = false;

    // Status Text Anzeige
    document.getElementById('status-text').innerText = nachricht;
    document.getElementById('status-text').style.color = farbe;

    if (nachricht === 'Gewonnen!'){
        sendeGewinner()
    }


    // Polling stoppen
    clearInterval(pollingIntervall);
}

// Prüfe Gewinner
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

// Polling starten
startePolling();