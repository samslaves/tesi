# Domande per il relatore — quantum simulation (Trotter) sul dimero

Domande aperte sul nuovo task (simulare $e^{-iHt}$ sull'Hamiltoniana del
dimero, non su Ising), da porre a Prof. Chiesa al prossimo incontro.

---

## 1. Serve un qubit di supporto per le correlazioni nel tempo?

Nel notebook di esempio che ho usato come riferimento (quello sul modello di
Ising), oltre ai qubit che rappresentano i due spin fisici ne viene usato un
**terzo, aggiuntivo**, che non rappresenta nessuno spin reale del sistema:
serve solo come "strumento di misura indiretto" per calcolare quantità che
altrimenti non sarebbero accessibili direttamente, tipo la correlazione tra
uno spin al tempo $t$ e l'altro al tempo $0$, $\langle s_{x1}(t)s_{x2}\rangle$.

**Domanda:** per il task che mi ha chiesto (evoluzione temporale
dell'Hamiltoniana del dimero, non del modello di Ising), mi serve anche a me
questo qubit aggiuntivo, oppure per ora mi basta guardare l'evoluzione di
osservabili "semplici" (es. la magnetizzazione $M_z(t)$), senza calcolare
correlazioni a due tempi?

## 2. Implemento entrambi i casi, D=0 e D≠0?

Dagli appunti risulta che lei ha già impostato il calcolo per entrambi i
casi: con $D=0$ i due pezzi dell'Hamiltoniana (campo $b$ e scambio $J$)
commutano e l'evoluzione si scrive in modo **esatto**; con $D\neq0$ no, e
serve una decomposizione approssimata (Trotter), con un errore che dipende
dal numero di passi usati.

**Domanda:** vuole che implementi e mostri **entrambi** i casi in sequenza
(prima $D=0$ come verifica esatta del metodo, poi $D\neq0$ con Trotter e
studio dell'errore al variare del numero di passi), oppure il caso $D=0$ è
solo un passaggio di controllo da tenere sott'occhio e il risultato da
presentare è direttamente quello con $D\neq0$?

## 3. Dove va collocato questo blocco nella tesi?

**Domanda:** questa simulazione temporale è una sotto-sezione della Parte 1
(sistema chiuso), oppure la immagina come una sezione a sé, magari come ponte
verso la Parte 2 (sistema aperto/rumore)?

## 4. Range di parametri e condizioni iniziali

**Domanda:** c'è un valore di riferimento per $b/J$ e $D$ da usare (es. gli
stessi usati nel resto della tesi per il dimero), e uno stato iniziale
specifico da cui far partire l'evoluzione (es. $|\!\uparrow\uparrow\rangle$,
oppure lo stato fondamentale trovato con il VQE)?

---

## Risposte ricevute (19/07/2026)

1. **Ancilla:** serve solo per osservabili a due corpi (correlazioni
   dinamiche). Per ora si parte con soli 2 qubit, usando $S_z$ totale come
   osservabile al posto delle correlazioni.
2. **D=0 vs D≠0:** si va direttamente con $D\neq0$.
3. **Collocazione in tesi:** per ora solo sistema chiuso.
4. **Parametri/stato iniziale:** provare $J=2B$, $D=B/3$; esplorare diversi
   set di parametri con la dinamica esatta per trovare oscillazioni di $S_z$
   non banali (non monocromatiche). Stato iniziale: $|00\rangle$.

**Nota del relatore per una fase successiva (da discutere a voce):**
aggiungere un qubit, partire dal ground state VQE invece di $|00\rangle$, e
calcolare correlazioni dinamiche come in Crippa et al. — rimandato a call.

**Call:** richiesta per lunedì 20/07/2026, tarda mattinata — in attesa di
conferma orario.

---

## 5. Correlazioni dinamiche: quale osservabile? (fase successiva, avviata)

Il relatore ha confermato di procedere con la fase rimandata al punto 1:
ground state via VQE (parametri del test 2 della relazione, $b/J=0.35$,
$D/J=0.80$) seguito dal calcolo di correlazioni dinamiche. Restano da
definire due aspetti dell'osservabile prima di poter disegnare il circuito
con l'ancilla (Hadamard test).

**Domanda:**
1. **Quale coppia di siti:** $\langle\psi_0|\,\sigma_z^{(1)}(t)\,\sigma_z^{(1)}(0)\,|\psi_0\rangle$
   (stesso spin, autocorrelazione locale) oppure
   $\langle\psi_0|\,\sigma_z^{(1)}(t)\,\sigma_z^{(2)}(0)\,|\psi_0\rangle$
   (spin diversi)?
2. **Quale componente:** solo $S_zS_z$, oppure anche $S_xS_x$/$S_yS_y$ come
   in Crippa et al.?

Il circuito con l'ancilla cambia a seconda della risposta, quindi serve
saperlo prima di implementare lo stage 3 (dopo VQE e verifica classica del
segnale).

**Risposta ricevuta:**

> Sono tutti casi interessanti, sia auto-correlazione (stesso sito) che tra
> spin diversi. Alcune combinazioni saranno nulle per simmetria dell'ham,
> vale la pena provarne varie.

**Lettura:** nessuna restrizione a priori — sia $\sigma^{(1)}(t)\sigma^{(1)}(0)$
(stesso sito) sia $\sigma^{(1)}(t)\sigma^{(2)}(0)$ (siti diversi) sono da
esplorare, e per entrambi i casi vale la pena provare più componenti
($S_zS_z$, $S_xS_x$, $S_yS_y$, eventualmente incrociate). Il relatore
segnala esplicitamente che **alcune combinazioni si annulleranno per
simmetria** — non è un errore di implementazione, è atteso: va verificato
*a priori* con un argomento di simmetria dell'Hamiltoniana (es. parità
rispetto allo scambio $1\leftrightarrow2$, o conservazione di $M$ residua)
quali combinazioni sono candidate a dare zero, prima di lanciarsi
nell'implementazione del circuito per tutte.

**Piano operativo:** costruire il circuito con l'ancilla (Hadamard test)
in forma **parametrica** rispetto a (a) quale coppia di siti e (b) quale
coppia di componenti di Pauli, così da poter scandire le combinazioni
senza riscrivere il circuito ogni volta. Prima di tutto, un controllo
classico (matrice) di quali combinazioni sono strutturalmente nulle per
simmetria a $(b/J,D/J)=(0.35,0.80)$, per non sprecare tempo implementando
casi banali.

## 6. Osservazioni sulla misura via circuito (relazione inviata)

Circuito con l'ancilla derivato da zero (non lo schizzo del punto 5,
mai verificato), validato, ed eseguito su tutte le 36 combinazioni
$C_{ij}^{\alpha\beta}(t)$ al punto del test 2 — nessuna risulta
strutturalmente nulla per ogni $t$ (solo 4 si annullano a $t=0$, siti
diversi con una sola componente $y$). Relazione inviata al relatore
(`relazione_correlazioni.docx`), con due osservazioni in attesa di
risposta:

1. Il correlatore indicato dal relatore come esempio
   ($\langle\sigma_{x2}(t)\sigma_{x1}(0)\rangle$, cioè $C_{2,1}^{xx}$) non
   è fra i più "ricchi" per criterio spettrale ($a_2/a_1$): è 27° su 36.
   Tenuto comunque come priorità per rilevanza fisica, non per qualità del
   segnale — le due cose non coincidono, segnalato esplicitamente invece
   di scegliere senza dirlo.
2. Pattern trovato negli spettri: tutte le combinazioni "ricche" (una
   componente $x$, una $y$) condividono lo stesso spettro esatto (canali
   $k=1,3$); tutte le "piatte" $ZZ$ condividono anch'esse lo stesso
   spettro esatto (canale $k=2$). $C_{1,1}^{zy}$ è un terzo caso a sé
   (canale $k=1$ dominante). Non c'è ancora una spiegazione fisica del
   perché la coppia di componenti fissi così rigidamente quale livello
   eccitato viene raggiunto — ipotesi non verificata: collegato all'asse
   del campo Zeeman ($z$) e alla struttura del DM ($x,z$). Chiesto un
   parere diretto al relatore prima di investigare da soli.

**Stato:** in attesa di risposta.

---

# Domande per il relatore — trimero N=3, triangolo isoscele

Domande aperte sulla nuova estensione (teoria esatta del triangolo isoscele,
completata in autonomia), da porre a Prof. Chiesa quando si passa al VQE.

## 7. Isoscele basta, o serve anche lo scaleno?

La teoria esatta in forma chiusa vale solo per il caso isoscele ($J'_{23}=J'_{31}$),
grazie alla simmetria di scambio $1\leftrightarrow2$. Il caso scaleno
($J'_{23}\neq J'_{31}$) rompe questa simmetria e richiederebbe la
diagonalizzazione numerica dell'$8\times8$ (nessuna forma chiusa).

**Domanda:** per la tesi è sufficiente il caso isoscele (con l'equilatero
come caso particolare), o vuole che si tratti anche lo scaleno per
completezza/generalità?

## 8. Priorità: catena aperta o VQE sul triangolo?

Con la teoria del triangolo isoscele completa, restano due filoni aperti per
N=3: la teoria della catena aperta (non ancora iniziata) e il VQE sul
triangolo isoscele (usando la teoria esatta appena fatta come benchmark).

**Domanda:** quale priorità, vista la scadenza di settembre — completare
prima il quadro teorico (catena aperta) o passare subito al VQE sul
triangolo?

## 9. Trattazione quantitativa del DM sul triangolo: necessaria?

Il ruolo del termine DM nell'aprire il gap agli incroci di livello è stato
discusso solo qualitativamente (analogo al dimero: serve un termine con
$\Delta M\neq0$). Una trattazione quantitativa richiederebbe abbandonare la
forma chiusa e diagonalizzare l'$8\times8$ completo con DM acceso.

**Domanda:** serve quantificare il gap aperto dal DM sul triangolo (analogo
a quanto già fatto per il dimero), o per la tesi basta il livello qualitativo
già raggiunto, dando priorità al VQE?

## 10. Valori di riferimento per $(J,J',b)$ sul triangolo

Per il dimero è stato usato un punto di riferimento concordato (parametri
del "test 2", $b/J=0.35$, $D/J=0.80$). Per il triangolo isoscele non c'è
ancora un punto di riferimento analogo.

**Domanda:** ci sono valori di $(J,J')$ di suo interesse per il triangolo
isoscele (es. un rapporto $J'/J$ specifico, magari motivato da un composto
reale), o si può scegliere liberamente un punto rappresentativo (es. uno dei
casi già usati nella teoria: $J{=}1,J'{=}0.4$ nella regione C) come punto di
partenza per il VQE?

## Aggiornamento — domande 8 e 9 risolte nei fatti

**Domanda 8 (priorità catena aperta vs VQE triangolo)**: risolta —
entrambe completate. Teoria della catena aperta e VQE (senza DM) per
entrambe le topologie sono stati fatti, non è stato necessario scegliere.

**Domanda 9 (DM quantitativo sul triangolo)**: risolta — quantificato in
`analisi_dm_trimero.pdf`. Solo l'Opzione B (DM su tutti e tre i legami,
proporzionale a $J$) apre realmente il gap all'incrocio, per una ragione
di simmetria esatta (regola di non-incrocio di von Neumann–Wigner
applicata a $S_{12}^2$), non per una coincidenza numerica. L'Opzione A
(simmetrica, coerente con la teoria in forma chiusa) non lo apre mai.

## 11. Priorità: Fase 5 (VQE con DM) per la catena, o Trotter/correlazioni per N=3?

Con VQE senza DM completo per entrambe le topologie e VQE con DM completo
per l'anello, restano due filoni aperti: estendere la Fase 5 (VQE con DM)
anche alla catena aperta, oppure aprire il fronte Trotter e correlazioni
dinamiche per N=3 (anticipato come complicato dalla condivisione di qubit
fra i tre bond nell'anello).

**Domanda:** quale priorità, vista la scadenza di settembre — chiudere
prima il parallelismo anello/catena sul VQE con DM, o passare subito a
Trotter/correlazioni su N=3?

## Aggiornamento — domanda 11 risolta nei fatti: fatti entrambi sull'anello

Non è stato necessario scegliere: per l'anello sono stati completati sia
il VQE con DM (Fase 5) sia Trotter e correlazioni dinamiche — il filone
anello è ora chiuso a tutti i livelli (teoria esatta, VQE senza/con DM,
Trotter, correlazioni). Vedi `scheda_progetto_tesi.md` e
`log_decisioni.md` per il dettaglio.

**Domanda aperta residua, per la catena aperta:** replicare lo stesso
percorso completo (Fase 5 con DM, poi Trotter, poi correlazioni
dinamiche) usato per l'anello — non ci sono più alternative di priorità
da chiedere al relatore, è l'ultimo filone rimasto per chiudere N=3 con lo
stesso livello di completezza. Un solo punto tecnico da confermare (non
al relatore, ma come primo checkpoint della prossima sessione): il punto
di lavoro $(b,D)$ per la Fase 5 della catena, dato che la struttura del
termine DM ($D_{12}=-D_{23}$, forzata dalla riflessione $P_{13}$) è già
nota e non richiede una scelta fra opzioni come per l'anello. Vedi
`prompt_nuova_chat_trimero_catena.md`.

---

# Domande per il relatore — Parte 2 (rumore sul dimero)

## 12. Dove attaccare il rumore, come interpretare la percentuale, quale piattaforma, readout simmetrico o no

Aperta la Parte 2. Scope confermato dal relatore: solo errori di gate (1q/2q)
e di readout, $T_1$/$T_2$ esclusi. Prima di scrivere codice, quattro punti
verificati come non banali (vedi `log_decisioni.md`, sezione "apertura Parte
2") e posti in una mail:

a) dove attaccare l'errore di gate — sui gate logici del modello (RXX, RYY,
   RZZ) o su un circuito transpilato in base hardware; se transpilato, con
   quale livello di ottimizzazione (verificato un fattore $\sim3.3$ fra
   default e ottimo: 10 CNOT vs 3 CNOT per passo di Trotter del dimero);
b) come interpretare la percentuale fornita: come errore medio di gate
   $\varepsilon$ (richiede conversione esplicita al parametro $\lambda$ di
   Aer, $\lambda=2\varepsilon$ a 1 qubit, $\lambda=\tfrac43\varepsilon$ a 2
   qubit) o come $\lambda$ direttamente;
c) piattaforma hardware di riferimento per i valori di calibrazione reali;
d) readout simmetrico (come nella slide 17 del corso) o asimmetrico (più
   realistico).

**Risposta ricevuta (02/09/2026):**

> Confermo che usiamo solo errori di gate e di misura.
> 1. Farei prima la transpilazione, aiuterà a ridurre i gate quindi va
>    fatto.
> 2. Riscala come dici
> 3. Usa dei valori tipici che prendi guardando i valori di qualche chip di
>    riferimento.
> In generale rifarei il conto per vari valori dei parametri di errore.
> Sull'errore di misura, parti simmetrico. Poi vedi se hai tempo di fare un
> test asimmetrico, ma senza perderci troppo tempo.

**Lettura operativa:**

- (a) **Transpilare**, motivato esplicitamente da "aiuterà a ridurre i
  gate" — quindi il livello di ottimizzazione va scelto per **minimizzare**
  il conteggio, non lasciato al default. Per il passo di Trotter del dimero
  questo significa `optimization_level>=2` (3 CNOT), non il default (10
  CNOT). Estensione diretta a trimero anello/catena quando si aprirà quella
  fase: usare lo stesso criterio (livello che minimizza), non assumere che
  il numero di CNOT sia lo stesso del dimero.
- (b) **Confermata la conversione** $\varepsilon\to\lambda$ di Aer già
  derivata — nessuna sorpresa, procedere come pianificato.
- (c) **Nessuna piattaforma imposta**: scegliere un chip reale rappresentativo
  e citarne i dati di calibrazione pubblicati. Aggiunta esplicita non
  richiesta in precedenza: **il relatore chiede uno scan sui parametri di
  errore** ("rifarei il conto per vari valori"), non un solo punto —
  implica una griglia $(\varepsilon_{1q},\varepsilon_{2q},p_\text{readout})$
  o almeno una scansione 1D attorno al valore tipico, non un singolo
  risultato a percentuali fisse.
- (d) **Readout simmetrico come primo passo**, obbligatorio; l'asimmetrico è
  **opzionale**, da fare solo se il tempo lo consente e senza investirci
  sforzo eccessivo — non un requisito per la consegna.

**Stato:** tutte le domande aperte sulla Parte 2 risolte. Prossimo passo:
ricerca dei valori di calibrazione reali (fonti citabili), poi
implementazione con transpilazione ottimizzata e scan sui parametri di
errore.

Non è stato necessario scegliere: per l'anello sono stati completati sia
il VQE con DM (Fase 5) sia Trotter e correlazioni dinamiche — il filone
anello è ora chiuso a tutti i livelli (teoria esatta, VQE senza/con DM,
Trotter, correlazioni). Vedi `scheda_progetto_tesi.md` e
`log_decisioni.md` per il dettaglio.

**Domanda aperta residua, per la catena aperta:** replicare lo stesso
percorso completo (Fase 5 con DM, poi Trotter, poi correlazioni
dinamiche) usato per l'anello — non ci sono più alternative di priorità
da chiedere al relatore, è l'ultimo filone rimasto per chiudere N=3 con lo
stesso livello di completezza. Un solo punto tecnico da confermare (non
al relatore, ma come primo checkpoint della prossima sessione): il punto
di lavoro $(b,D)$ per la Fase 5 della catena, dato che la struttura del
termine DM ($D_{12}=-D_{23}$, forzata dalla riflessione $P_{13}$) è già
nota e non richiede una scelta fra opzioni come per l'anello. Vedi
`prompt_nuova_chat_trimero_catena.md`.

## Nota informativa (non una domanda) — due scelte implementative per la Parte 2

Da segnalare al relatore nel prossimo scambio, non da porre come domanda
aperta: due dettagli implementativi emersi verificando la pipeline prima di
introdurre il rumore.

1. **Transpilazione per blocco, non sull'intero circuito.** La direttiva
   "transpilare per minimizzare i gate" va applicata al singolo passo di
   Trotter, compilato una volta e ripetuto $N$ volte — transpilando l'intero
   circuito a un livello di ottimizzazione alto, Qiskit collassa gli $N$
   passi identici in un circuito a costo costante, eliminando la dipendenza
   da $N$ che serve allo scan sui parametri di errore.
2. **VQE reale come preparazione di default sotto rumore**, non le ampiezze
   esatte: verificato numericamente che il contributo della preparazione
   all'errore totale è una costante additiva, indipendente da $N$, che non
   sposta il numero di passi ottimale $N^*$ ma ne fissa il pavimento minimo
   raggiungibile.

Entrambe rientrano nello scope già confermato il 02/09/2026 (sez. 12); non
richiedono una risposta, solo una comunicazione a valle.

## Nota informativa (non una domanda) — Parte 2 completata sul dimero

Da comunicare al relatore, non una domanda aperta: tutti e cinque i passi
della pipeline di Parte 2 (rumore sul dimero) sono completi, con lo scan
sui parametri di errore che rispondeva esplicitamente alla sua richiesta
del 02/09/2026 ("rifarei il conto per vari valori dei parametri di
errore... vedere come si sposta $N^*$").

Due risultati che potrebbero interessargli in particolare:
1. **$N^*$ non dipende dall'errore di lettura**, per un readout
   simmetrico — risultato analitico (la correzione di readout è un
   fattore costante in $N$), non solo empirico.
2. Al punto di calibrazione scelto (`ibm_torino`), $N^*=8$ sulla fedeltà
   di Trotter e $N^*=5$ sui correlatori dinamici: il numero ottimale di
   passi dipende dall'osservabile che si sta calcolando, non solo dal
   livello di rumore del dispositivo.

Non richiede una risposta; utile per orientare la discussione quando si
passerà alla stesura del capitolo finale.
