// Spielfeld
let brett = ['', '', '', '', '', '', '', '', ''];
let spielAktiv = true;
let spielerDran = true;

// Gewinnoptionen
const gewinnKombinationen = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Horizontal
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Vertikal
    [0, 4, 8], [2, 4, 6]             // Diagonal
];

// Felder
function macheZug(feldIndex) {
    if (brett[feldIndex] !== '' || !spielAktiv) {
        return; 
    }

    brett[feldIndex] = 'X';
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
    
    setTimeout(kiZug, 500); 
}

// KI
function kiZug() {
    if (!spielAktiv) return;

    let leereFelder = [];
    for (i = 0; i < brett.length; i++) {
        if (brett[i] === '') {
            leereFelder.push(i);
        }
    }

    let zufallsIndex = Math.floor(Math.random() * leereFelder.length);
    let kiWahl = leereFelder[zufallsIndex];

    brett[kiWahl] = 'O';
    document.getElementById('feld-' + kiWahl).innerText = 'O';
    document.getElementById('feld-' + kiWahl).style.color = '#ff8400';

    if (prüfeGewinner('O')) {
        beendeSpiel("Verloren!", "#ff8400");
        return;
    }

    if (!brett.includes('')) {
        beendeSpiel("Unentschieden!", "white");
        return;
    }

    document.getElementById('status-text').innerText = "Du bist dran (X)";
    document.getElementById('status-text').style.color = '#007bff';
}

// Prüfe GEwinner
function prüfeGewinner(spieler) {
    for (let i = 0; i < gewinnKombinationen.length; i++) {
        let kombi = gewinnKombinationen[i];
        let a = kombi[0];
        let b = kombi[1];
        let c = kombi[2];

        if (brett[a] === spieler && brett[b] === spieler && brett[c] === spieler) {
            return true;
        }
    }
    return false;
}

// Spiel beenden
function beendeSpiel(nachricht, farbe) {
    spielAktiv = false;
    document.getElementById('status-text').innerText = nachricht;
    document.getElementById('status-text').style.color = farbe;
}

// Neustart
function neustart() {
    brett = ['', '', '', '', '', '', '', '', ''];
    spielAktiv = true;
    
    for (let i = 0; i < 9; i++) {
        document.getElementById('feld-' + i).innerText = '';
    }

    document.getElementById('status-text').innerText = "Du bist dran (X)";
    document.getElementById('status-text').style.color = '#007bff';
}