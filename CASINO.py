import streamlit as st  # Libreria per creare interfacce web semplici
import pandas as pd  # Libreria per gestire tabelle di dati
import random  # Libreria per generare numeri casuali
import time  # Libreria per creare pause e ritardi
from datetime import datetime  # Libreria per gestire date e orari

# ============== CONFIGURAZIONE INIZIALE ==============
# Questa parte configura l'aspetto generale della pagina web

# Imposta il titolo della pagina, l'icona e il layout a schermo intero
st.set_page_config(page_title="Casino GSOM - Roulette", page_icon="🎰", layout="wide")

# ============== INIZIALIZZAZIONE VARIABILI ==============
# Qui vengono create le variabili che mantengono lo stato dell'applicazione
# tra un'interazione e l'altra

# Inizializza il portafoglio del giocatore a 1000€ se non esiste già
if 'saldo' not in st.session_state:
    # session_state permette di salvare dati tra diverse esecuzioni del programma
    st.session_state.saldo = 1000  # Inizia con 1000€

# Crea una tabella vuota per tenere traccia delle partite giocate
if 'storico_partite' not in st.session_state:
    # Definiamo le colonne della tabella
    st.session_state.storico_partite = pd.DataFrame(
        columns=[
            'Timestamp',   # Data e ora della partita
            'Gioco',       # Nome del gioco (Roulette)
            'Scommessa',   # Su cosa hai scommesso (es. "rosso", "19")
            'Importo',     # Quanto hai scommesso (€)
            'Risultato',   # Risultato della partita (numero uscito)
            'Vincita'      # Quanto hai vinto o perso (€)
        ]
    )

# ============== FUNZIONI DI RESET ==============
# Queste funzioni permettono di ripristinare il gioco

def ripristina_budget():
    """
    Questa funzione riporta il saldo a 1000€, come all'inizio del gioco.
    È come ricevere nuovi gettoni al casinò.
    """
    # Reimposta il saldo a 1000€
    st.session_state.saldo = 1000
    # Mostra un messaggio di conferma all'utente
    st.success("Budget ripristinato a €1000")

def ripristina_statistiche():
    """
    Questa funzione cancella tutta la storia delle partite giocate.
    È come iniziare un nuovo registro nel casinò.
    """
    # Crea una nuova tabella vuota per le partite
    st.session_state.storico_partite = pd.DataFrame(
        columns=['Timestamp', 'Gioco', 'Scommessa', 'Importo', 'Risultato', 'Vincita']
    )
    # Mostra un messaggio di conferma all'utente
    st.success("Statistiche e storico partite azzerati")

# ============== FUNZIONI PRINCIPALI ==============

def aggiorna_storico(gioco, scommessa, importo, risultato, vincita):
    """
    Questa funzione registra una partita giocata nel registro storico e aggiorna il saldo.
    
    Funziona come il registro di un casinò che tiene traccia di ogni puntata.
    
    Parametri:
    - gioco: nome del gioco (es. "Roulette")
    - scommessa: su cosa hai scommesso (es. "rosso" o "17")
    - importo: quanto hai scommesso (€)
    - risultato: risultato della partita (es. "23")
    - vincita: quanto hai vinto (negativo se hai perso) (€)
    """
    # Crea un nuovo record per questa partita
    nuova_partita = pd.DataFrame({
        'Timestamp': [datetime.now()],  # Ora attuale
        'Gioco': [gioco],               # Nome del gioco
        'Scommessa': [scommessa],       # Su cosa hai scommesso
        'Importo': [importo],           # Quanto hai scommesso
        'Risultato': [risultato],       # Risultato della partita
        'Vincita': [vincita]            # Quanto hai vinto o perso
    })
    
    # Aggiungi questa partita allo storico (in fondo alla tabella)
    st.session_state.storico_partite = pd.concat(
        [st.session_state.storico_partite, nuova_partita], 
        ignore_index=True  # Questo fa sì che le righe siano numerate correttamente
    )
    
    # Aggiorna il saldo del giocatore
    # Se vincita è positiva, il saldo aumenta; se è negativa, il saldo diminuisce
    st.session_state.saldo += vincita

# ============== FUNZIONE DELLA ROULETTE ==============

def gioca_roulette():
    """
    Questa funzione gestisce il gioco della roulette.
    Mostra l'interfaccia, raccoglie le scommesse e calcola i risultati.
    """
    # Mostra il titolo del gioco
    st.subheader("🎡 Roulette")
    
    # Crea un contenitore vuoto per mostrare il saldo, che può essere aggiornato dinamicamente
    saldo_container = st.empty()
    saldo_container.write(f"Saldo attuale: €{st.session_state.saldo}")
    
    # Dividi lo schermo in due colonne: una per i controlli di gioco, una per le regole
    col1, col2 = st.columns([1, 2])  # La seconda colonna è il doppio della prima
    
    # Prima colonna: controlli di gioco
    with col1:
        # Controllo se l'utente ha soldi sufficienti per giocare
        if st.session_state.saldo <= 0:
            # Se non ha soldi, mostra un messaggio di errore
            st.error("Non hai più soldi per scommettere! Ripristina il budget per continuare a giocare.")
            importo = 0  # Imposta l'importo a zero (non può scommettere)
        else:
            # Se ha soldi, mostra l'input per la scommessa con un semplice campo di testo
            importo_testo = st.text_input(
                "Importo della scommessa (€):",
                value="10"
            )
            
            # Convertiamo il testo in numero, con validazione
            try:
                importo = int(importo_testo)
                if importo < 1:
                    st.warning("L'importo minimo è 1€")
                    importo = 1
                elif importo > st.session_state.saldo:
                    st.warning(f"Non puoi scommettere più di {st.session_state.saldo}€")
                    importo = st.session_state.saldo
            except ValueError:
                st.error("Inserisci un numero valido")
                importo = 10
        
        # Opzioni di scommessa disponibili nella roulette
        opzioni_scommessa = [
            "rosso", "nero",  # Colori
            "pari", "dispari",  # Parità del numero
            "1-18", "19-36",  # Intervalli di numeri
            "1a dozzina", "2a dozzina", "3a dozzina"  # Dozzine
        ] + [str(i) for i in range(0, 37)]  # Aggiungi tutti i numeri da 0 a 36
        
        # Menu a tendina per scegliere su cosa scommettere
        scommessa = st.selectbox("Scegli su cosa scommettere", opzioni_scommessa)
        
        # Pulsante per girare la ruota
        if st.button("Gira la Ruota"):
            # Mostra un'animazione di caricamento mentre "gira la ruota"
            with st.spinner("La ruota gira..."):
                # Crea un momento di suspense (1 secondo)
                time.sleep(1)
                
                # ======== ESTRAZIONE E CALCOLO VINCITA ========
                
                # Estrai un numero casuale tra 0 e 36
                numero_estratto = random.randint(0, 36)
                # Converti in stringa per il display
                risultato = str(numero_estratto)
                
                # Di default, perdi l'importo scommesso
                vincita = -importo
                
                # Definisci i numeri rossi e neri della roulette
                # (questi sono i numeri standard della roulette europea)
                numeri_rossi = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
                numeri_neri = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
                
                # Controlla il tipo di scommessa e calcola la vincita
                # Scommessa sul rosso
                if scommessa == "rosso" and numero_estratto in numeri_rossi:
                    vincita = importo  # Vincita 1:1 (raddoppi la scommessa)
                
                # Scommessa sul nero
                elif scommessa == "nero" and numero_estratto in numeri_neri:
                    vincita = importo  # Vincita 1:1
                
                # Scommessa sui numeri pari (lo 0 non è considerato pari nella roulette)
                elif scommessa == "pari" and numero_estratto % 2 == 0 and numero_estratto != 0:
                    vincita = importo  # Vincita 1:1
                
                # Scommessa sui numeri dispari
                elif scommessa == "dispari" and numero_estratto % 2 == 1:
                    vincita = importo  # Vincita 1:1
                
                # Scommessa sui numeri da 1 a 18
                elif scommessa == "1-18" and 1 <= numero_estratto <= 18:
                    vincita = importo  # Vincita 1:1
                
                # Scommessa sui numeri da 19 a 36
                elif scommessa == "19-36" and 19 <= numero_estratto <= 36:
                    vincita = importo  # Vincita 1:1
                
                # Scommessa sulla prima dozzina (1-12)
                elif scommessa == "1a dozzina" and 1 <= numero_estratto <= 12:
                    vincita = importo * 2  # Vincita 2:1 (triplichi la scommessa)
                
                # Scommessa sulla seconda dozzina (13-24)
                elif scommessa == "2a dozzina" and 13 <= numero_estratto <= 24:
                    vincita = importo * 2  # Vincita 2:1
                
                # Scommessa sulla terza dozzina (25-36)
                elif scommessa == "3a dozzina" and 25 <= numero_estratto <= 36:
                    vincita = importo * 2  # Vincita 2:1
                
                # Scommessa su un numero specifico
                elif scommessa.isdigit() and int(scommessa) == numero_estratto:
                    vincita = importo * 35  # Vincita 35:1 (36 volte la scommessa)
                
                # ======== AGGIORNAMENTO STATO GIOCO ========
                
                # Registra la partita nello storico
                aggiorna_storico("Roulette", scommessa, importo, risultato, vincita)
                
                # Aggiorna i saldi mostrati (sia nella sezione roulette che nell'intestazione)
                saldo_container.write(f"Saldo attuale: €{st.session_state.saldo}")
                if 'saldo_header' in st.session_state:
                    st.session_state.saldo_header.header(f"Saldo: €{st.session_state.saldo}")
                
                # Mostra il risultato
                st.success(f"Numero estratto: {risultato}")
                
                # Mostra un messaggio diverso se hai vinto o perso
                if vincita > 0:
                    # Mostra palloncini per festeggiare
                    st.balloons()
                    st.success(f"Hai vinto €{vincita}!")
                else:
                    st.error(f"Hai perso €{abs(vincita)}.")
    
    # Seconda colonna: spiegazioni sulla roulette
    with col2:
        # Mostra le regole della roulette in formato Markdown (testo formattato)
        st.markdown("""
        ### Come funziona la Roulette:
        - La ruota ha numeri da 0 a 36
        - I numeri rossi sono: 1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36
        - I numeri neri sono: 2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35
        - Lo zero (0) è verde
        
        Le vincite dipendono dal tipo di scommessa:
        - Numero singolo: 35:1 (vinci 35 volte la scommessa)
        - Rosso/Nero, Pari/Dispari, 1-18/19-36: 1:1 (vinci lo stesso importo della scommessa)
        - Dozzine: 2:1 (vinci il doppio della scommessa)
        """)

# ============== FUNZIONE DELLE STATISTICHE ==============

def visualizza_statistiche():
    """
    Questa funzione mostra le statistiche delle partite giocate.
    Include grafici e analisi dei risultati.
    """
    # Mostra il titolo della sezione
    st.subheader("📊 Statistiche e Probabilità")
    
    # Se non ci sono partite registrate, mostra un messaggio e termina
    if len(st.session_state.storico_partite) == 0:
        st.info("Gioca alcune partite per vedere le statistiche!")
        return  # Esci dalla funzione
    
    # ===== STATISTICHE GENERALI =====
    st.write("### Statistiche Generali")
    
    # Classifica ogni partita come Vittoria, Perdita o Pareggio
    # in base al valore della vincita
    risultati = st.session_state.storico_partite['Vincita'].apply(
        lambda x: 'Vittoria' if x > 0 else ('Pareggio' if x == 0 else 'Perdita')
    )
    
    # Conta quante vittorie, perdite e pareggi ci sono stati
    conteggio_risultati = risultati.value_counts()
    
    # Crea tre colonne per mostrare i conteggi
    col1, col2, col3 = st.columns(3)
    
    # Mostra i contatori in ciascuna colonna
    with col1:
        st.metric("Vittorie", conteggio_risultati.get('Vittoria', 0))
    
    with col2:
        st.metric("Perdite", conteggio_risultati.get('Perdita', 0))
    
    with col3:
        st.metric("Pareggi", conteggio_risultati.get('Pareggio', 0))
    
    # Calcola e mostra il profitto totale
    profitto_totale = st.session_state.storico_partite['Vincita'].sum()
    st.metric("Profitto Totale", f"€{profitto_totale}")
    
    # ===== GRAFICO DELL'ANDAMENTO DEL BUDGET =====
    st.write("### Andamento del Budget")
    
    # Prepara i dati per il grafico
    df_budget = st.session_state.storico_partite.copy()
    # Calcola il saldo progressivo a partire dal saldo iniziale di 1000€
    df_budget['Saldo_Progressivo'] = 1000 + df_budget['Vincita'].cumsum()
    # Aggiungi una colonna con il numero della partita
    df_budget['Numero_Partita'] = range(1, len(df_budget) + 1)
    
    # Crea i dati per il grafico
    chart_data = pd.DataFrame({
        'Numero_Partita': df_budget['Numero_Partita'],
        'Saldo': df_budget['Saldo_Progressivo']
    })
    
    # Mostra il grafico a linea dell'andamento del budget
    st.line_chart(
        chart_data.set_index('Numero_Partita')['Saldo'],
        use_container_width=True  # Usa tutta la larghezza disponibile
    )
    
    # ===== BARRE COLORATE PER LA DISTRIBUZIONE RISULTATI =====
    st.write("### Distribuzione Risultati")
    
    # Calcola percentuali di vittorie, perdite e pareggi
    totale_partite = len(st.session_state.storico_partite)
    vittorie = len(st.session_state.storico_partite[st.session_state.storico_partite['Vincita'] > 0])
    perdite = len(st.session_state.storico_partite[st.session_state.storico_partite['Vincita'] < 0])
    pareggi = len(st.session_state.storico_partite[st.session_state.storico_partite['Vincita'] == 0])
    
    # Calcola le percentuali (evita divisione per zero se non ci sono partite)
    perc_vittorie = (vittorie / totale_partite) * 100 if totale_partite > 0 else 0
    perc_perdite = (perdite / totale_partite) * 100 if totale_partite > 0 else 0
    perc_pareggi = (pareggi / totale_partite) * 100 if totale_partite > 0 else 0
    
    # Crea due colonne: una per le barre e una per le percentuali
    col1, col2 = st.columns([3, 1])
    
    # Nella prima colonna, mostra le barre colorate
    with col1:
        # Barra verde per le vittorie
        st.write("Vittorie:")
        # Crea una barra personalizzata usando HTML
        st.markdown(f"""
        <div style="width:100%; height:20px; background-color:#E0E0E0; border-radius:3px;">
            <div style="width:{perc_vittorie}%; height:20px; background-color:#2ECC71; border-radius:3px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra rossa per le perdite
        st.write("Perdite:")
        st.markdown(f"""
        <div style="width:100%; height:20px; background-color:#E0E0E0; border-radius:3px;">
            <div style="width:{perc_perdite}%; height:20px; background-color:#E74C3C; border-radius:3px;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra blu per i pareggi
        st.write("Pareggi:")
        st.markdown(f"""
        <div style="width:100%; height:20px; background-color:#E0E0E0; border-radius:3px;">
            <div style="width:{perc_pareggi}%; height:20px; background-color:#3498DB; border-radius:3px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Nella seconda colonna, mostra le percentuali numeriche
    with col2:
        st.write(f"{perc_vittorie:.1f}%")  # Mostra con 1 decimale
        st.write(f"{perc_perdite:.1f}%")
        st.write(f"{perc_pareggi:.1f}%")

# ============== INTERFACCIA PRINCIPALE ==============

def main():
    """
    Funzione principale dell'applicazione.
    Definisce la struttura dell'interfaccia e controlla il flusso dell'applicazione.
    """
    # Mostra il titolo principale dell'applicazione
    st.title("🎰 Il Casino GSOM 🎰")
    
    # Crea un contenitore vuoto per il saldo principale, che può essere aggiornato dinamicamente
    saldo_header = st.empty()
    saldo_header.header(f"Saldo: €{st.session_state.saldo}")
    
    # Crea due colonne per i pulsanti di reset
    col1, col2 = st.columns(2)
    
    # Pulsante per ripristinare il budget
    with col1:
        if st.button("🔄 Ripristina Budget", help="Riporta il saldo a €1000"):
            ripristina_budget()
            # Aggiorna il saldo principale subito dopo il ripristino
            saldo_header.header(f"Saldo: €{st.session_state.saldo}")
    
    # Pulsante per azzerare le statistiche
    with col2:
        if st.button("🗑️ Azzera Statistiche", help="Cancella tutto lo storico delle partite"):
            ripristina_statistiche()
    
    # Salva un riferimento al contenitore del saldo principale per usarlo nelle schede
    if 'saldo_header' not in st.session_state:
        st.session_state.saldo_header = saldo_header
    
    # Crea le schede (tabs) per navigare tra giochi e statistiche
    tab1, tab2 = st.tabs(["🎮 Gioca", "📊 Statistiche"])
    
    # Contenuto della scheda Gioca
    with tab1:
        gioca_roulette()
    
    # Contenuto della scheda Statistiche
    with tab2:
        visualizza_statistiche()

# ============== AVVIO DELL'APPLICAZIONE ==============
# Questa parte viene eseguita quando il file viene avviato direttamente

# Se questo file è il programma principale (non importato da altri)
if __name__ == "__main__":
    # Avvia la funzione principale
    main()
