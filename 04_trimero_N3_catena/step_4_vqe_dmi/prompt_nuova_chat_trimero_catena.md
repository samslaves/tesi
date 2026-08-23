Riprendo la tesi triennale (trimero di spin, catena aperta). Ho appena
aggiornato e ricaricato `log_decisioni.md`, `scheda_progetto_tesi.md` e
`domande_relatore.md` nel progetto: comincia leggendoli e dammi un
riepilogo dello stato confermato prima di implementare qualsiasi cosa.

**Contesto in breve**: per il trimero a catena aperta, la teoria esatta e
il VQE senza DM (Fase 4) sono completi e verificati — mirror strutturale
di quanto già fatto per l'anello (`trimer_chain_exact.py`,
`vqe_trimer_chain.py`/`_W.py`/`_nobranch.py`, due notebook "spiegato",
tutti eseguiti con successo in sessione). Per l'anello sono state
completate anche Fase 5 (VQE con DM), la simulazione quantistica
(Trotter) e le correlazioni dinamiche — l'intero filone anello è chiuso.
**Obiettivo di questa chat: concludere il filone catena aperta con lo
stesso livello di completezza**, in un'unica sessione di lavoro continua
(non tre chat separate come è successo per l'anello), sfruttando che la
metodologia è ormai consolidata.

**Pattern da ripetere identico, in ogni fase**: costruisci e valida ogni
pezzo (Trotter, circuito delle correlazioni) con `prepare_state` come
stand-in a ampiezze esatte; solo alla fine sostituisci con il circuito VQE
reale ottimizzato, verificando che il residuo introdotto sia trascurabile
rispetto agli altri errori già caratterizzati (Trotter, shot noise) — è lo
schema seguito ovunque sull'anello, non va abbandonato per la catena.

**Cosa manca, in ordine, per la catena aperta:**

## Fase 5 — VQE con DM

Correzione importante rispetto a com'era stata impostata la volta scorsa:
**la struttura del termine DM per la catena è già derivata**, non è un
punto aperto. `teoria_trimero_catena_aperta.tex` e `trimer_chain_exact.py`
mostrano che la simmetria di riflessione $P_{13}$ forza univocamente
$D_{12}=-D_{23}$ — a differenza dell'anello, qui **non c'è una scelta fra
Opzione A/B**: esiste un solo termine DM compatibile con la simmetria.
`trimer_chain_exact.py` ha già lo scaffolding (sezione DM inclusa "per
completezza strutturale", non ancora usata). Quello che manca è solo la
**quantificazione**:

1. Mirror snello di `analisi_dm_trimero_anello.tex`
   (→ `analisi_dm_trimero_catena.tex`): usando la struttura $D_{12}=-D_{23}$
   già nota, trovare $g_\text{min}(D)=\min_b[E_1(b;D)-E_0(b;D)]$ (minimo
   assoluto del gap su tutto $b$, non il gap a $b=3J$ fisso — stesso errore
   metodologico da evitare, già documentato per l'anello) e verificare che
   il DM apra davvero l'incrocio a $b_c=3J$. Dovrebbe essere più rapido
   dell'anello: un solo grado di libertà DM, non due opzioni da confrontare.

   **🛑 FERMATI QUI E CHIEDIMI CONFERMA**, prima di andare oltre: mostrami
   la tabella $g_\text{min}(D)$ (come quella fatta per l'anello) e il punto
   di lavoro $(b,D)$ che proponi di adottare per il resto della Fase 5 (e,
   salvo diversa indicazione al punto successivo, anche per le
   correlazioni). Non proseguire al confronto ansatz finché non confermo.

2. **Confronto ansatz sotto DM** (solo dopo la mia conferma sul punto di
   lavoro): invece delle due tappe separate usate per
   l'anello (indagine mirata poi confronto sistematico), fai **un solo
   sweep sistematico** che includa da subito sia RBS-2q sia $W$-2q, $D=0$ e
   DM acceso — i due notebook dell'anello restano il template diretto
   (`analisi_espressivita_PMA_anello.ipynb` +
   `confronto_ansatz_entangler_trimero_anello.ipynb`), ma non serve
   ripetere la stessa cautela in due stadi: l'ipotesi da testare (RBS ha un
   tetto strutturale sotto DM, $W$ no) è già nota dall'anello — verificala
   sui dati della catena senza assumerla, ma non serve un notebook
   esplorativo a parte prima del confronto completo.
3. Documentazione: `trimero_catena_vqe_dm.tex`, stessa struttura di
   `trimero_anello_vqe_dm.tex`.

## Simulazione quantistica (Trotter) — catena

Aperta H0 = b·S_z^tot + H_ex (2 bond, non 3): H_ex = J(σ1·σ2 + σ2·σ3)
fattorizza esattamente rispetto al campo, ma i bond 12 e 23 condividono il
qubit 2 → serve comunque un Trotter interno per H_ex, come per l'anello.
**Attenzione a non copiare la derivazione dell'anello senza controllo**:
lì l'operatore di chiralità $\chi=\vec\sigma_1\cdot(\vec\sigma_2\times
\vec\sigma_3)$ veniva dalla struttura ciclica a tre legami (identità del
prodotto misto); con solo due bond (nessun terzo legame, quindi nessuna
somma ciclica di tre commutatori) va verificato da zero se l'errore del
livello 1 ha una forma chiusa altrettanto semplice o se è strutturalmente
diverso — probabilmente più semplice, non più complicato (un solo
commutatore non nullo, $[\sigma_1\cdot\sigma_2,\sigma_2\cdot\sigma_3]$,
non tre). Stesso discorso per il Trotter interno di $H_{DM}$ una volta
quantificato sopra (due bond, $D_{12}=-D_{23}$, niente terzo termine).

Passi (mirror di `trotter_trimero_anello.py` +
`quantum_simulation_trimero_anello_teoria.tex`, ma con le derivazioni
riverificate per la topologia a due bond, non semplicemente riadattate):

1. Derivazione teorica del Trotter interno per $H_{ex}$ e $H_{DM}$ (catena).
2. Punto di lavoro dimostrativo (mirror $R_0$/$R_1$, **indipendente** dal
   punto VQE+DM del punto precedente — per l'anello erano regimi diversi
   apposta): esplorare $(b,D)$ con lo stesso criterio picco-picco +
   $a_2/a_1$.

   **🛑 FERMATI QUI E CHIEDIMI CONFERMA**, prima di andare oltre: mostrami
   il regime candidato (valori di $b,D$, escursione, $a_2/a_1$, eventuali
   alternative scartate) come è stato fatto per $R_0$/$R_1$ del dimero e
   dell'anello. Non proseguire all'implementazione del modulo Trotter
   finché non confermo il punto.

3. Modulo `trotter_trimero_catena.py` (solo dopo la mia conferma sul
   regime dimostrativo), self-test a precisione macchina sul
   circuito Qiskit reale, convergenza in $N$ (richiesta esplicita già fatta
   dal relatore per l'anello, verosimilmente valida anche qui: analisi di
   convergenza fidelity/osservabili vs $N$ fin da subito).
4. Documentazione (mirror `quantum_simulation_trimero_anello_teoria.tex` +
   `_applicazione.tex`).

## Correlazioni dinamiche — catena

Stessa sequenza già rodata sull'anello, con la simmetria giusta per questa
topologia (**non quella dell'anello**):

1. **Analisi di simmetria prima del circuito** (lezione imparata dai bug
   del dimero, poi confermata utile sull'anello: fatta prima ha evitato
   bug al primo colpo). Per la catena la simmetria è la **riflessione**
   $1\leftrightarrow3$ (sito 2 fisso), non la rotazione ciclica
   dell'anello — verificare se $P_{13}$ (o un suo analogo corretto con
   fattori $R_z(\pi)$, come è servito per l'anello) commuta con $H$
   completo di DM, derivare l'eventuale corollario di zero strutturale per
   $C_{22}^{\alpha\beta}$ (sito fisso, mirror del corollario sul sito 3
   dell'anello) — **da derivare e verificare numericamente da zero, non da
   assumere per analogia**.

   **🛑 FERMATI QUI E CHIEDIMI CONFERMA sul punto di lavoro per le
   correlazioni**, prima di costruire il circuito: per l'anello si è
   riusato direttamente il punto VQE-con-DM (verificandone *a posteriori*
   la ricchezza), invece di cercarne uno dedicato — proponimi se fare lo
   stesso per la catena (riuso del punto del punto 1 sopra) o se, alla
   luce della simmetria di riflessione appena derivata, conviene un punto
   diverso. Non proseguire al circuito finché non confermo.

2. Circuito Hadamard test (4 qubit: 3 registro + 1 ancilla), mirror diretto
   di `circuito_correlazioni_trimero_anello.py`, con `trotter_trimero_catena.py`
   come blocco $U(t)$.
3. Validazione (statevector, poi shot finiti), scan sistematico delle 81
   combinazioni, chiusura con VQE reale al posto di `prepare_state`.
4. Documentazione pedagogica + di catalogazione, stesso stile dell'anello.

## Come muoverti più rapidamente rispetto all'anello (senza perdere rigore)

- Riusa il codice delle famiglie di ansatz, la struttura del circuito
  Hadamard test e gli argomenti generali (perché $U(t)$ non va controllato,
  perché serve BCH per la fattorizzazione) **per citazione**, non per
  riderivazione — sono indipendenti dalla topologia.
- Rideriva da zero **solo** ciò che dipende genuinamente dalla topologia:
  simmetria (riflessione, non rotazione), struttura DM (un grado di
  libertà, non due opzioni), Trotter interno a due bond (non tre).
- Niente compilazione PDF (solo sorgenti `.tex`, convenzione già in uso);
  file salvati nel Project via `project_write`, non solo allegati in chat.
- **Checkpoint di conferma, solo dove contano**: uno iniziale sul piano
  generale, poi tre — segnalati sopra con 🛑 — sulle scelte che
  condizionano il resto del lavoro (punto di lavoro DM/VQE, regime
  dimostrativo Trotter, punto di lavoro per le correlazioni). Fuori da
  questi quattro punti, procedi senza fermarti a chiedere il permesso per
  ogni singolo script/notebook/verifica: dammi solo un aggiornamento
  quando una fase è completa, come già fatto molte volte sull'anello per
  le scelte minori (documentate nel log, non chieste prima).

Procedi con ordine: prima il riepilogo dello stato confermato (nota
esplicitamente la correzione sul DM già derivato), poi conferma il piano
con me, poi comincia a lavorare fermandoti solo sui quattro checkpoint
indicati (🛑) fra le tre fasi.
