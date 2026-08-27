# Log delle decisioni — Tesi triennale

Registro delle scelte metodologiche e del loro *perché*. Da aggiornare man mano.
Le voci aperte sono marcate con [ ], quelle decise con [x].

---

## Esito call con il relatore (Prof. Chiesa)
- [x] **Modello:** sistemi di spin-1/2 (di tipo Heisenberg).
- [x] **Struttura della tesi in due parti:**
      Parte 1 = sistema CHIUSO (no rumore, vettore di stato, Schrödinger);
      Parte 2 = sistema APERTO (rumore approssimato in Qiskit, operatore densità,
      decoerenza).
- [x] **Punto di partenza Parte 1:** esempio "VQE on a spin dimer" (N=2),
      6-Applications.pdf slide 19–21, da **estendere a N=3**.
- [x] **Reti neurali (NQS): FUORI SCOPE.**
- [x] **Topologia N=3: ENTRAMBI i casi** (catena aperta e anello/triangolo), a
      confronto. Confermato dal relatore. Topologia gestita come parametro nel
      codice (presenza/assenza del legame di chiusura 3-1).
- [x] **Sessione di laurea: SETTEMBRE** (luglio non fattibile nei tempi).

## Hamiltoniana del dimero (letta da 6-Applications.pdf, slide 19–21)
$$H = J_x X_1X_2 + J_y Y_1Y_2 + J_z Z_1Z_2 + b(Z_1+Z_2)$$
Caso isotropo $J_x=J_y=J_z=J$, risolubile in forma chiusa:
- $H_1=J(XX+YY+ZZ)=2J(S^2-s_1^2-s_2^2)$, $H_2=b(Z_1+Z_2)=2bS_z$, $[H_1,H_2]=0$.
- Autovalori: $E(S,M)=2bM+2JS(S+1)-3J$.
  - $S=0$: $E=-3J$ (singoletto, GS a campo basso)
  - $S=1$: $E=J+2b,\,J,\,J-2b$ (tripletto)
- Incrocio del GS a $b/J=2$ (singoletto → $|\!\downarrow\downarrow\rangle$).
- USO: spettro analitico = riferimento esatto per validare il VQE.

## Nuova richiesta del relatore — quantum simulation (Trotter) sull'Hamiltoniana del dimero
- [ ] **Richiesta (18/07/2026):** il relatore chiede di provare, sul dimero, una
      *quantum simulation* con decomposizione $e^{-iHt}$ — MA usando l'**Hamiltoniana
      VQE del dimero** (Heisenberg isotropo + campo $b$ + termine DM), **non**
      l'Hamiltoniana di Ising trasverso (TIM) usata nel notebook di esempio
      `Quantum_simulation_TIM_noiseless.ipynb`.
- **Materiale di riferimento fornito dal relatore:** `quantum_simulation_notes.jpg`.
  Notazione con spin operators $s_i=\sigma_i/2$ (convenzione Crippa, vedi nota sotto
  su $J_{code}$ vs $J_{Crippa}$):
  $$H = b(s_{z1}+s_{z2}) + J\,\vec s_1\!\cdot\!\vec s_2 + D(s_{x1}s_{z2}-s_{z1}s_{x2}) = H_1+H_2$$
  con $H_1=b(s_{z1}+s_{z2})$ (campo) e $H_2 = J\vec s_1\!\cdot\!\vec s_2$ (scambio isotropo);
  il termine DM è scritto a parte, sommato dentro $H_2$ quando $D\neq0$.
  - **In generale $[H_1,H_2]\neq0$.**
  - **Caso $D=0$:** $H_1$ e $J\vec s_1\!\cdot\!\vec s_2$ **commutano** →
    $e^{-iHt}=R_z^{(1)}(bt)\,R_z^{(2)}(bt)\,U_J$ **esatto**, nessun errore di
    Trotter (decomposizione esatta in tre blocchi in sequenza, non serve
    approssimare).
  - **Caso $D\neq0$:** $[H_1,H_2]\neq0$ → serve **Suzuki-Trotter**:
    $$e^{-i(H_1+H_2)t}\approx\left(e^{-iH_1 t/N}e^{-iH_2 t/N}\right)^N + O\!\left((t/N)^2\right)$$
- **Obiettivo del nuovo task:** NON è VQE (ricerca variazionale del ground state),
  ma **simulazione dinamica in tempo reale** $e^{-iHt}$ dell'Hamiltoniana del
  dimero già usata in Parte 1, riusando l'approccio del notebook TIM come
  *template* metodologico (decomposizione in gate, confronto Trotter vs esatto,
  eventuale ancilla per funzioni di correlazione dinamiche) ma con
  l'Hamiltoniana giusta (dimero VQE, non Ising).
- **Stato:** ~~NON ancora iniziato. Solo presa visione e pianificazione per ora,
  su richiesta esplicita di Samuele ("per ora non fare nulla").~~ **SUPERATO —
  task completato, vedi "Aggiornamento — quantum simulation Trotter del
  dimero: completata" più sotto.**
- **Da chiarire con il relatore/in autonomia:**
  - dove collocare questo blocco nella tesi (sotto-sezione di Parte 1? sezione
    a sé stante prima della Parte 2, come ponte verso la dinamica?);
  - se il termine DM va incluso da subito o si parte prima dal caso $D=0$
    (esatto, senza errore di Trotter) per poi introdurre $D\neq0$;
  - se servono le funzioni di correlazione dinamiche (richiedono ancilla, vedi
    notebook TIM) o solo l'evoluzione di osservabili locali (es. $M_z(t)$).

## Domande ancora aperte
- [ ] Parte 2: quale modello di rumore (da backend IBM reale? rumore uniforme
      approssimato? quali canali: depolarizzante, damping, bit-flip?).
- [ ] Parte 2: ottimizzatore — passare a SPSA (più robusto al rumore)?
- [ ] Collocazione del nuovo task di quantum simulation (Trotter sul dimero
      VQE) nella struttura della tesi — vedi sezione dedicata sopra.

## Scelte di metodo (VQE) — Parte 1
- [x] Backend: simulatore statevector (sistema chiuso, esatto).
- [x] Validazione: confronto con autovalori esatti + fidelity
      $\mathcal{F}=|\langle\psi_0|\psi(\tilde\theta)\rangle|$ + osservabili (es. $M_z$).
- [x] **Ansatz (N=2): definiti e confrontati.** HA (`n_local`, Ry+CZ, 6 parametri,
      generico, robusto a $D\neq0$) e famiglia PMA (Crippa et al., basato su
      simmetrie). Il PMA di base (1 parametro, $M$-conservante) è efficientissimo
      a $D=0$ (precisione macchina) ma degrada a $D\neq0$ vicino a $B/J=2$
      (rottura di $M$). Esteso con rotazioni reali aggiuntive in due famiglie:
      **PMA-1q** (1,2,4,6 parametri) e **PMA-2q** (1,3,5,7 parametri).
      **`PMA-2q·3` è l'ansatz raccomandato** per il seguito (N=3): raggiunge
      $\mathcal F=1$ con il minimo numero di parametri (3, pari ai gradi di
      libertà fisici $S^3$), marcato `PMA_RECOMMENDED` nel codice.
- [x] **Ottimizzatore:** L-BFGS-B (in `vqe_dimer.py`, 3 restart) per il confronto
      HA/PMA base; **multistart con $R=6$ restart, reinizializzazione casuale
      ad ogni ciclo esterno** (non ad ogni iterazione COBYLA) per il confronto
      esteso in `confronto_ansatz_entangler.ipynb` — è la metodologia da
      portare avanti su N=3, come da indicazione del relatore.

## Stato di avanzamento
- [x] Caricato paper di riferimento (Crippa et al. 2021).
- [x] Caricato notebook Qiskit di partenza.
- [x] Caricato 6-Applications.pdf (esempio spin dimer).
- [x] Call di inquadramento con il relatore: struttura definita.
- [x] Letto e annotato l'esempio "VQE on a spin dimer" (N=2): Hamiltoniana e
      spettro analitico sopra.
- [x] **Implementato/riprodotto il dimero (N=2) via VQE su statevector.**
      Modulo `dimer_exact.py` (benchmark: formula chiusa + `eigh`, self-test
      $8.88\times10^{-16}$) + `vqe_dimer.py` (VQE con ansatz HA e PMA) +
      `confronto_ansatz_entangler.ipynb` (4 ansatz reali A–D + famiglie
      PMA-1q/PMA-2q) + `analisi_rotazioni_PMA.ipynb` (derivazione di quali
      rotazioni servono per rompere $M$). Dettagli completi in fondo al file.
- [x] **Trimero N=3, triangolo (anello) isoscele: teoria esatta completa.**
      Base $J$, lati $J'$ ($J\neq J'$), risolubile in forma chiusa via
      decomposizione di Kambe (Casimir $S_{12}^2,S^2,S_z$) — nessuna
      diagonalizzazione numerica necessaria. Dettagli completi in fondo al
      file.
- [ ] Trimero N=3, catena aperta: teoria non ancora iniziata.
- [ ] VQE N=3 (entrambe le topologie, catena e anello): non ancora iniziato
      — teoria esatta dell'anello isoscele disponibile come benchmark.
- [ ] Introdotto il modello di rumore / operatore densità (Parte 2).
- [x] Caricato `Quantum_simulation_TIM_noiseless.ipynb` (esempio Trotter/TIM,
      da riusare come template metodologico, NON come Hamiltoniana da tenere).
- [x] Caricati appunti del relatore `quantum_simulation_notes.jpg` (schema
      Trotter per $H=H_1+H_2$ del dimero, casi $D=0$ esatto e $D\neq0$ Suzuki-Trotter).
- [x] Implementata la quantum simulation ($e^{-iHt}$, Trotter) sull'Hamiltoniana
      VQE del dimero — completata, usata come base per il circuito delle
      correlazioni. Vedi "Aggiornamento — quantum simulation Trotter del
      dimero: completata".
- [x] **Notebook `Quantum_simulation_TIM_noiseless.ipynb` eseguito per intero
      da Samuele, senza errori, con la sua installazione Qiskit 2.x.**
      Unica modifica necessaria: commentata la riga
      `from qiskit_ibm_runtime import *` (pacchetto non essenziale, non usato
      nel resto del notebook, non serve per la simulazione locale). Nessun'altra
      API risultata deprecata o incompatibile. Il notebook TIM è quindi
      confermato utilizzabile come *template* metodologico per il nuovo task.

## Note / ragionamenti
- Convenzione: 6-Applications.pdf usa $b$ (campo) e $J$ davanti a $(XX+YY+ZZ)$;
  Crippa usa $2J\sum\mathbf{s}_i\cdot\mathbf{s}_{i+1}+B\sum s_i^z$. Stesso modello a meno
  di fattori 2. Usare la convenzione di 6-Applications.pdf come operativa.
- Lo stato fondamentale NON è una singola configurazione: il termine di scambio
  $X_iX_j+Y_iY_j$ è fuori diagonale e mescola le configurazioni → sovrapposizione.
  La minimizzazione VQE è nello spazio dei parametri $\theta$, non nelle config.
- Parte 1 vs Parte 2 = sistema chiuso vs aperto. Chiuso: stato puro $|\psi\rangle$,
  evoluzione unitaria. Aperto: stato misto, operatore densità $\rho$, dinamica non
  unitaria (decoerenza).
- N=3 dispari → caso fisicamente interessante (frustrazione del triangolo se
  anello; effetti di taglia/parità). Da sfruttare se il relatore lo conferma.

## Risorse di studio
- **VQE — tutorial IBM** (inquadramento "Hamiltoniana = somma di Pauli", il caso
  nostro): https://learning.quantum.ibm.com/tutorial/variational-quantum-eigensolver
- **VQE — corso "Quantum chemistry with VQE"** per la meccanica (ansatz, Estimator,
  Qiskit patterns): https://learning.quantum.ibm.com/course/quantum-chem-with-vqe
  > Ignorare la parte fermionica/struttura elettronica: il nostro è un modello di
  > spin che si mappa direttamente sui qubit.
- **Corso teorico Watrous** (Qiskit): Lesson 3 (circuiti) utile; Lesson 1-2 ripasso
  veloce; **Lesson 9 (matrici densità), 10 (canali quantistici), 12 (fidelity)
  UTILI per la Parte 2** (rumore, operatore densità). Saltare il resto.

## Aggiornamento 18/07/2026 — Hamiltoniana Trotter del dimero (versione confermata)

Trascrizione finale e confermata degli appunti del relatore
(`quantum_simulation_notes.jpg`), vedi anche il file dedicato
`trascrizione_appunti.md` caricato a parte:

$$H = b(s_{z1}+s_{z2}) + J\,\vec s_1\cdot\vec s_2 + D(s_{x1}s_{z2}-s_{z1}s_{x2}) = H_1+H_2$$

- $H_1 = b(s_{z1}+s_{z2}) + J\,\vec s_1\cdot\vec s_2$ (campo + scambio, **fisso**,
  non dipende da $D$).
- $H_2 = D(s_{x1}s_{z2}-s_{z1}s_{x2})$ (**solo** DM; è $H_2$, non $H_1$, ad
  annullarsi quando $D=0$).
- $[H_1,H_2]\neq0$ quando $D\neq0$.
- **$D=0$:** $H=H_1$, decomposizione **esatta**:
  $|\psi(t)\rangle = R_z^{(1)}(bt)\,R_z^{(2)}(bt)\,U_J\,|\psi(0)\rangle$.
- **$D\neq0$:** serve Suzuki-Trotter,
  $e^{-i(H_1+H_2)t}\approx(e^{-iH_1t/N}e^{-iH_2t/N})^N$, errore $O((t/N)^2)$
  per passo (nessun termine oltre l'$O(\cdot)$, confermato dal foglio originale).
  Riferimenti bibliografici del risultato: Trotter (1959), Suzuki (1985),
  Lloyd (1996) — vedi conversazione per le citazioni complete.

**Stato:** trascrizione confermata dal relatore/da Samuele; notebook TIM
eseguito con successo come template metodologico. Prossimo passo: implementare
la stessa logica (evoluzione esatta per $D=0$, Trotter per $D\neq0$) usando
l'Hamiltoniana del dimero al posto di quella di Ising.

**File da ricaricare nella project knowledge per rendere ufficiale questo
aggiornamento:** `log_decisioni.md` (questa versione), `scheda_progetto_tesi.md`
(aggiornata), `trascrizione_appunti.md` (nuovo), notebook TIM eseguito e
salvato da Samuele (nuovo, sostituisce/affianca l'originale).

## Aggiornamento 18/07/2026 — Risultati completi N=2 (dimero), da file caricati

Riepilogo di quanto già prodotto e verificato su N=2, dai file:
`dimer_exact.py`, `dimer_exact_spiegato.ipynb` (+ note), `vqe_dimer.py`,
`vqe_dimer_spiegato.ipynb` (+ note), `confronto_ansatz_entangler.ipynb`
(+ note), `analisi_rotazioni_PMA.ipynb`.

### Benchmark esatto (`dimer_exact.py`)
- `analytic_eigenvalues`: formula chiusa $E(S,M)=2JS(S+1)-3J+2bM$, valida solo
  per $D=0$ (simmetrie $[H,S^2]=[H,S_z]=0$).
- `exact_sweep` (via `eigh`): diagonalizzazione numerica, valida per $D$
  qualunque; è il riferimento usato ovunque nel progetto.
- Self-test: $\max|E_\text{num}-E_\text{analitico}| = 8.88\times10^{-16}$
  (precisione macchina, nessuna discrepanza fisica).
- Con $D=0.2$: level crossing in $B/J=2$ diventa **anticrossing** (gap minimo
  $\Delta\simeq0.57$); magnetizzazione passa da salto netto a crossover liscio.

### VQE dimero — HA vs PMA (`vqe_dimer.py`)
| ansatz | $D$ | parametri | $\Delta E$ | fidelity |
|---|---|---|---|---|
| HA | 0 | 6 | $\sim10^{-13}$ | $1.000$ ovunque |
| HA | 0.2 | 6 | $\sim10^{-13}$ | $1.000$ ovunque (anche sull'anticrossing) |
| PMA | 0 | 1 | $\sim10^{-16}$ | $1.000$ ovunque |
| PMA | 0.2 | 1 | fino a $\sim0.2$ a $B/J=2$ | scende a $\sim0.82$ a $B/J=2$ |

Causa della degradazione del PMA base a $D\neq0$: il PMA conserva $M$ per
costruzione (blocco $W_{01}(\theta)$ diagonale a blocchi nei settori $M=0$ e
$M=\pm1$, **stessa** rotazione su entrambi, mai li mescola), ma con $D\neq0$ il
vero ground state a $B/J=2$ è una miscela singoletto/tripletto **senza $M$
definito** — irraggiungibile per un ansatz $M$-conservante.

### Confronto esteso, 6 ansatz reali + isolamento della causa (`confronto_ansatz_entangler.ipynb`)
- Ansatz A–D (Ry + entangler non/poco parametrico): tutti raggiungono
  $\mathcal F=1$ **ovunque**, anche a $D\neq0$ — confermano che il GS resta
  reale (H è reale simmetrica) e che la rottura di simmetria $M$, non la
  complessità dello stato, è la sola causa del fallimento del PMA base.
- Blocco RBS unico e riusato ovunque: $G(\varphi)$, rotazione di Givens reale
  nel settore $M=0$, implementato come $(H\otimes H)\,\mathrm{CZ}\,(R_y(\varphi)\otimes R_y(-\varphi))\,\mathrm{CZ}\,(H\otimes H)$,
  self-test errore $\sim10^{-16}$.
- **PMA-1q** (1,2,4,6 parametri, $R_y$ su un solo qubit): recupera $\mathcal
  F=1$ da **4** parametri.
- **PMA-2q** (1,3,5,7 parametri, $R_y$ indipendenti su entrambi i qubit):
  recupera $\mathcal F=1$ già da **3** parametri (minimo teorico, $S^3$).
  **`PMA-2q·3` = ansatz raccomandato per N=3** (`PMA_RECOMMENDED` nel codice).
- Multistart: $R=6$ restart, reinizializzazione casuale nel ciclo **esterno**
  (mai dentro le iterazioni di COBYLA) — mandato dal relatore.
- Fidelity robusta alla degenerazione (a $B/J=2$, $D=0$): proiettore sul
  sottospazio fondamentale $\mathcal G$, non su un singolo autovettore.

### Perché serve un parametro indipendente per qubit (`analisi_rotazioni_PMA.ipynb`)
Derivazione esplicita: dopo il blocco RBS lo stato è $a|01\rangle+b|10\rangle$
(settore $M=0$). Applicando $R_y(\varphi)$ su entrambi i qubit:
- **stesso segno** $R_y(\varphi)\otimes R_y(\varphi)$: i coefficienti generati
  nei settori $M=\pm1$ sono entrambi $\propto(a+b)$ — **fallisce** (fidelity
  max $\simeq0.74$, indipendente da quanti blocchi si impilano);
- **segno opposto** $R_y(\varphi)\otimes R_y(-\varphi)$: entrambi $\propto(a-b)$
  — **satura** a $n=2$ (un solo grado di libertà reale, solo orientato
  diversamente);
- **parametri indipendenti** $R_y(\alpha)\otimes R_y(\beta)$, $\alpha\neq\beta$:
  due gradi di libertà reali indipendenti — **funziona**, $\mathcal F=1$ da
  $n=3$.

### Convenzione DM usata nel codice
$D(X_1Z_2-Z_1X_2)$ (reale, rompe $M$) — distinta dalla DM "canonica"
$D(X_1Y_2-Y_1X_2)$ (immaginaria, non usata qui). L'intera Hamiltoniana
$H=J(XX+YY+ZZ)+b(Z_1+Z_2)+D(XZ-ZX)$ è reale simmetrica → il ground state può
sempre essere scelto reale (teorema spettrale), verificato numericamente nel
notebook: ansatz a sole $R_y$ sono sufficienti anche a $D\neq0$, nessuna
necessità di $R_z$/fasi complesse.

**Stato N=2: sostanzialmente completo e validato.** Prossimo passo naturale:
estendere `PMA-2q` e il benchmark esatto a N=3 (catena e triangolo), più il
task separato di quantum simulation Trotter (vedi sezioni precedenti).

## Aggiornamento 19/07/2026 — Risposte del relatore (task quantum simulation dimero)

Prof. Chiesa ha risposto (19/07/2026, di domenica) alle 4 domande inviate.
Risposte:

1. **Ancilla:** serve solo per osservabili a due corpi (funzioni di
   correlazione dinamica). **Per ora si parte con soli 2 qubit**, usando
   un'altra osservabile — **$S_z$ totale** — al posto delle correlazioni.
2. **D=0 vs D≠0:** si va **direttamente con $D\neq0$**, non serve passare
   prima per $D=0$.
3. **Collocazione in tesi:** **per ora solo sistema chiuso** (quindi non
   ancora deciso se sotto-sezione di Parte 1 o ponte verso Parte 2 — resta
   comunque nell'ambito del sistema chiuso).
4. **Parametri/stato iniziale:** nessun valore a priori noto; il relatore
   suggerisce di **provare $J=2B$, $D=B/3$** come punto di partenza, e di
   **esplorare vari set di parametri con la dinamica esatta** per trovare
   un regime con **oscillazioni di $S_z$ non banali (non monocromatiche)**.
   **Stato iniziale: $|00\rangle$.**

**Sviluppo successivo (non ora, da discutere a voce):** in un secondo
momento si può aggiungere un qubit, partire dal ground state trovato via
VQE (non da $|00\rangle$) e calcolare correlazioni dinamiche, come in
Crippa et al. (Magnetochemistry). Rimandato a call.

**Call con il relatore:** richiesta per lunedì 20/07/2026, in tarda mattinata
(vincolo di Samuele: call di lavoro al mattino). Da confermare orario esatto.

**Piano operativo aggiornato per il task (nessuna ambiguità residua per
iniziare a lavorare):**
- 2 qubit, $D\neq0$ diretto (niente caso $D=0$ separato).
- Parametri di partenza: $J=2B$, $D=B/3$; esplorare la griglia con la
  dinamica esatta ($\texttt{scipy.linalg.expm}$, come nel notebook TIM) per
  trovare un regime con oscillazioni di $S_z$ non monocromatiche.
- Osservabile: $S_z$ totale (non correlazioni a due corpi — quelle sono
  rimandate a una fase successiva, con ancilla e stato iniziale da VQE).
- Stato iniziale: $|00\rangle$.
- Suzuki-Trotter per l'evoluzione (nessuna decomposizione esatta disponibile
  con $D\neq0$).

## Aggiornamento — VQE ground state al punto del test 2, completato

Fase VQE → ground state → correlazioni dinamiche, primo stadio completato.
Punto di lavoro: parametri del test 2 (`relazione_test_parametri.md`),
$b/J=0.35$, $D/J=0.80$, $J=1$. File: `vqe_test2.py`,
`vqe_ground_state_test2.ipynb`, `risultati_vqe_test2.md`.

- Riuso totale di Hamiltoniana (`dimer_exact.py`) e ansatz+metodologia
  (PMA-2q·3, multistart $R=6$, `confronto_ansatz_entangler.ipynb`): nessuna
  scelta nuova.
- Aggiunta: polish L-BFGS-B dopo COBYLA, per scendere da $\mathcal
  O(10^{-5})$ a precisione macchina in energia — necessario perché questo
  stato diventa input di un circuito a valle (un residuo non trascurabile
  propagherebbe errore sistematico nelle correlazioni).
- Risultato: $E_0=-3.57321145$, $\mathcal F=1$ (a precisione macchina),
  $\langle M_z\rangle\simeq-0.035$. Stato dominato dalla combinazione
  $|01\rangle-|10\rangle$ (vicino al singoletto, deformato dal DM).
- Stato salvato in `ground_state_test2.npz` (vettore + parametri ottimali
  dell'ansatz), pronto per la preparazione nel circuito con l'ancilla.

## Aggiornamento — Risposta del relatore sull'osservabile di correlazione

Prof. Chiesa ha risposto alla domanda 5 di `domande_relatore.md`:

> Sono tutti casi interessanti, sia auto-correlazione (stesso sito) che tra
> spin diversi. Alcune combinazioni saranno nulle per simmetria dell'ham,
> vale la pena provarne varie.

**Decisione operativa:**
- Nessuna restrizione a priori su sito (stesso spin / spin diversi) né su
  componente ($S_z,S_x,S_y$): si esplorano più combinazioni.
- **Prima** di implementare il circuito con l'ancilla: controllo classico
  (matrice, `numpy`) di quali combinazioni $\langle\psi_0|\sigma_i^\alpha(t)\sigma_j^\beta(0)|\psi_0\rangle$
  sono strutturalmente nulle per simmetria dell'Hamiltoniana al punto del
  test 2 — così da non implementare inutilmente casi banali e da poter
  spiegare *perché* si annullano (non solo verificarlo numericamente).
- **Poi:** circuito Hadamard test in forma parametrica rispetto a (coppia
  di siti, coppia di componenti), riusando lo stato $|\psi_0^\text{VQE}\rangle$
  (o i parametri dell'ansatz PMA-2q·3) da `ground_state_test2.npz` come
  stato di preparazione, sullo schema del notebook TIM.

## Domande ancora aperte (aggiornato)
- [x] ~~Quali combinazioni (sito, componente) sono nulle per simmetria al
      punto del test 2~~ — **risposta: nessuna, 0 su 36** strutturalmente
      nulle per ogni $t$ (verificato sia per via classica sia rimisurando
      via circuito). 4 combinazioni nulle solo a $t=0$ (siti diversi, una
      sola componente $y$), non per ogni $t$ — vedi aggiornamento sotto.
- [ ] Osservazioni della relazione inviata al relatore (vedi
      `domande_relatore.md`, punto 6): in attesa di risposta.
- [ ] Parte 2: quale modello di rumore.
- [ ] Parte 2: ottimizzatore — SPSA?
- [ ] Collocazione definitiva in tesi del blocco di quantum simulation
      (Trotter + correlazioni) — ancora "sistema chiuso, non meglio
      specificato" per indicazione del relatore.
- [ ] Rumore di **gate** reale sul circuito delle correlazioni (finora
      solo rumore statistico su simulazione ideale) — da affrontare
      insieme alla Parte 2.

## Aggiornamento — due appunti manoscritti del relatore (immagini caricate)

Due foto di appunti del relatore, caricate nel progetto come
`correlazioni_dinamiche.jpg` e un secondo file (schizzo circuito).

### 1. Schizzo di circuito per un correlatore concreto — NON verificato

Il relatore fornisce un primo esempio esplicito di correlatore da provare:

$$\langle V^\dagger(t)\,W(0)\rangle = \langle\psi_0|\,e^{iHt/\hbar}\,V^\dagger\,e^{-iHt/\hbar}\,W\,|\psi_0\rangle,
\qquad W=\sigma_{x1},\ \ V=\sigma_{x2}$$

cioè $\langle\sigma_{x2}(t)\,\sigma_{x1}(0)\rangle$ — correlazione fra siti
diversi, componente $S_x$. **La formula è solida** e va tenuta come primo
caso concreto da calcolare (in aggiunta all'esplorazione più ampia già
pianificata sopra).

Lo schizzo include anche un circuito con ancilla (Hadamard test,
controlled-$W$/controlled-$V$ attorno a un blocco $U(t)$ non controllato,
stato di preparazione esplicitamente il "ground state VQE"). **Il relatore
stesso non era sicuro della correttezza di questo circuito** — Samuele lo
conferma. Il circuito va quindi considerato solo **indicativo**, non un
riferimento da implementare così com'è: **da ri-derivare da zero** (schema
standard del Hadamard test per $\mathrm{Re}/\mathrm{Im}\langle
V^\dagger(t)W(0)\rangle$, verificato contro la formula sopra) prima di
qualunque implementazione.

### 2. Formalismo Kraus/Lindblad — materiale per la Parte 2

Nonostante l'intestazione "correlazioni dinamiche", il contenuto è la
derivazione standard per sistemi aperti, pertinente alla **Parte 2** (non
al circuito di correlazione del punto 1):

- stato puro → Schrödinger → $|\psi(t)\rangle=U(t,t_0)|\psi(t_0)\rangle$;
- passaggio a stato misto: ensemble $\{|\psi_k\rangle,p_k\}$ →
  $\rho=\sum_k p_k|\psi_k\rangle\langle\psi_k|$;
- equazione di Lindblad $\dot\rho = -\frac{i}{\hbar}[H,\rho] + \mathcal
  D[\rho]$, con $\mathcal D[\rho]$ (dissipatore, rumore) evidenziato;
- rappresentazione di Kraus equivalente, $\rho_t=\sum_k
  E_k\rho_0E_k^\dagger$, $\sum_k E_k^\dagger E_k=\mathbb I$;
- esempio concreto, canale bit-flip: $E_0=\sqrt{1-p}\,\mathbb I$,
  $E_1=\sqrt p\,X$ → $\rho_t=(1-p)\rho_0+pX\rho_0X$, con $p\sim0.1$–$1\%$
  (ordine di grandezza realistico di un errore di gate).

**Stato:** materiale preparatorio per la Parte 2, non ancora iniziata.
Nessuna azione immediata richiesta; da riprendere quando si apre quel
blocco della tesi.

## Aggiornamento — circuito con l'ancilla: derivazione, validazione, due bug corretti

Fase circuito (successiva al VQE ground state al test 2) completata fino
alla misura di tutte le 36 combinazioni e all'invio della relazione al
relatore.

**Derivazione del circuito.** Lo schizzo del relatore (punto 1 della
sezione precedente, non verificato, lui stesso non ne era sicuro) non è
stato usato come riferimento diretto. Circuito ri-derivato da zero
(Hadamard test standard: $H$ sull'ancilla, controlled-$W$ prima di
$U(t)$, $U(t)$ non controllato, anti-controlled-$V$ dopo, rotazione
finale + misura per $\mathrm{Re}/\mathrm{Im}$), verificato contro due
fonti indipendenti in letteratura: Crippa et al. (*Magnetochemistry* 7,
117, 2021, eq. 12 — il riferimento primario della tesi) e Tacchino,
Chiesa, Carretta, Gerace (*Adv. Quantum Technol.* 3, 1900052, 2020, Fig.
3/Sez. 3.6) — struttura identica in entrambe, coerente con il circuito
ri-derivato.

**Due bug trovati e corretti**, entrambi mascherati per coincidenza sui
primi due correlatori validati ($C_{2,1}^{xx}$, $C_{2,1}^{xy}$) grazie
alla simmetria $U$, e diventati visibili solo scansionando
sistematicamente tutte le 36 combinazioni:

1. **Formula spettrale del correlatore classico** (usata come riferimento
   per la validazione): mancava un coniugato complesso —
   $C(t)=\sum_k e^{i(E_0-E_k)t}\overline{a_k}b_k$, non $a_kb_k$. Invisibile
   per $\alpha=x,z$ (matrici reali, $a_k$ reale); ribalta il segno quando
   $\alpha=y$ (matrice immaginaria). Non ha invalidato nessuna conclusione
   qualitativa già tratta (tutte basate su moduli/rapporti, insensibili al
   segno), ma falsava il confronto diretto circuito-vs-classico.
2. **Mappatura sito→qubit nel circuito**: `site_to_qubit={1:0,2:1}` era
   invertita rispetto alla convenzione già stabilita (sito1 = indice qubit
   1 di $|\psi_0\rangle$, sito2 = indice 0). Il circuito costruiva quindi
   sempre il correlatore con i siti scambiati — invisibile per
   $C_{2,1}^{xx}$ e $C_{2,1}^{xy}$ perché $\eta_\alpha\eta_\beta=+1$ per
   queste coppie (la simmetria $U$ garantisce
   $C_{12}=\eta_\alpha\eta_\beta C_{21}$).

Entrambi corretti in tutti e tre i notebook coinvolti; rieseguiti e
riverificati dopo la correzione.

**File prodotti:**
- `correlazioni_dimero_esplorazione.ipynb` (principale) e
  `correlazioni_dimero_simmetria_U.ipynb` (secondario, sincronizzato) —
  derivazione completa, scan a 36 combinazioni, validazione, shot finiti.
- `circuito_correlazioni_tutte.ipynb` — versione snella: misura diretta
  (non dedotta) di tutte le 36 via circuito, selettore interattivo,
  spettro $|a_kb_k|$ per ciascuna, analisi.
- `simmetrie_correlatori_dimero.pdf` — teoria delle simmetrie (derivazione
  completa, non solo verifica numerica).
- `circuito_correlatori_spiegato.pdf` + `interferometro.html` — spiegazione
  pedagogica completa del circuito (prodotti di Pauli, rappresentazione di
  Heisenberg, misura), verificata passo per passo.
- `circuito_compatto_risposta.pdf` — risposta alla domanda del relatore
  sul circuito compatto a 3 CNOT: dove si applica (misura di $C(t)$ a $t$
  fissato) e dove no (studio Trotter-vs-rumore, preparazione dello stato).
  Deliverable a sé, non ancora applicato al circuito delle correlazioni.
- `relazione_correlazioni.docx`/`.md` — relazione inviata al relatore,
  due osservazioni in attesa di risposta (vedi `domande_relatore.md`,
  punto 6).

## Aggiornamento — Trimero N=3, triangolo (anello) isoscele: teoria esatta completa

Prima estensione di Parte 1 a N=3, topologia anello/triangolo. Generalizzazione
del caso equilatero (frustrato) al caso **isoscele**: base $J$ fra i siti
$1,2$, lati $J'$ fra $2,3$ e $3,1$ ($J\neq J'$, con $J'=J$ come caso
particolare che recupera l'equilatero). Obiettivo: capire per quali segni e
rapporti di $J,J'$ esiste un incrocio di livello del fondamentale al variare
del campo $b$, come base teorica prima di passare al VQE.

### Perché l'isoscele (e non subito lo scaleno)

Con i due lati uguali, l'Hamiltoniana ha una simmetria di scambio $1\leftrightarrow2$
($P_{12}$) che si traduce nella conservazione di $\mathbf S_{12}^2$ (spin
della sola coppia di base) oltre a $\mathbf S^2,S_z$ — dimostrato esplicitamente
via coniugazione $P_{12}HP_{12}^\dagger$, non solo per analogia. Questo rende
il problema **risolubile in forma chiusa** (decomposizione di Kambe): lo
spettro esce per sola sostituzione algebrica, senza diagonalizzare l'$8\times8$.
Con lati diversi ($J'_{23}\neq J'_{31}$, caso scaleno) questa simmetria si
rompe e serve la diagonalizzazione numerica — rimandato, non necessario per
la fase attuale.

### Risultato centrale: tre multipletti, spettro chiuso

$$H = J\,\boldsymbol\sigma_1\cdot\boldsymbol\sigma_2 + J'(\boldsymbol\sigma_2\cdot\boldsymbol\sigma_3+\boldsymbol\sigma_3\cdot\boldsymbol\sigma_1) + b\sum_i Z_i$$

(convenzione operativa di Pauli, coerente con 6-Applications.pdf). Tre blocchi:

| blocco | $S_{12}$ | $S$ | dim. | $E(b{=}0)$ |
|---|---|---|---|---|
| A | 1 | 3/2 | 4 | $J+2J'$ |
| B | 1 | 1/2 | 2 | $J-4J'$ |
| C | 0 | 1/2 | 2 | $-3J$ |

Limite dimero ($J'\to0$): $E_A,E_B\to J$, $E_C\to-3J$ — coincide esattamente
con singoletto/tripletto del dimero già validato in Parte 1 (buon controllo
di coerenza fra le due estensioni).

### Campo critico e mappa dei segni

Per $b>0$ il fondamentale è C o B (a $b=0$) fino a un campo critico $b_c$
dove interseca A (quadrupletto saturato):
$$b_c = 2J+J' \ \ (\text{se il fondamentale a }b{=}0\text{ è C}), \qquad b_c=3J' \ \ (\text{se è B}).$$
Limite $J'\to0$: $b_c\to2J$, esattamente il campo critico $b/J=2$ del
dimero — secondo controllo di coerenza indipendente.

**Mappa completa nel piano $(J,J')$, con segni** (non solo il quadrante
$J,J'>0$): esiste sempre un crossing tranne quando $J<0$ e $J'<0$ (ferromagnete
già saturo a $b=0$) o quando $J>0,J'<-2J$ (oltre quella soglia A è già
fondamentale a $b=0$). Il caso $J>0,J'<0$ è degno di nota: il campo critico
$2J+J'$ decresce e si annulla esattamente a $J'=-2J$, dove il fondamentale è
degenere $2+4=6$ volte già a $b=0$ — punto limite utile come stress test per
un futuro ansatz VQE.

**Tutti gli incroci trovati sono veri incroci** (gap esattamente nullo, non
anticrossing): dimostrato dalla regola di selezione $\bra{S_{12},S,M}H\ket{S_{12}',S',M'}=0$
se i numeri quantici differiscono, conseguenza diretta della costruzione di
$H$ come combinazione lineare dei soli Casimir. Per aprire il gap servirebbe
un termine con $\Delta M\neq0$ (es. il DM già usato nel dimero) — discusso
solo qualitativamente, **non quantificato**: richiederebbe abbandonare la
forma chiusa e diagonalizzare l'$8\times8$ completo. Rimandato a una fase
successiva se necessario per il VQE.

### Errore trovato e corretto durante la stesura

Nella prima esposizione (chat) le pendenze delle otto rette $E(b)$ erano state
indicate erroneamente come $\pm2,\pm6$; il valore corretto (derivato e usato
ovunque nei calcoli, incluso $b_c$) è $\pm1,\pm3$ (pendenza $=2M$, non $4M$).
Le formule finali di $b_c$ erano comunque corrette; solo la frase descrittiva
andava sistemata — fatto, verificato che non si propagasse altrove.

### Verifica numerica indipendente

Script `verifica.py`: diagonalizzazione esatta dell'$8\times8$ (NumPy) contro
tutte le formule chiuse — spettro completo (400 configurazioni casuali di
$(J,J',b)$, errore massimo $\sim10^{-14}$), campo critico (10 casi, scansione
del salto di $\langle S_z\rangle$ del ground state), mappa dei segni (14640
punti sulla griglia, zero disaccordi genuini — i soli "mismatch" iniziali
erano artefatti di floating point sulla retta di degenerazione $J'=-2J$, non
errori), identità operatoriali ($\boldsymbol\sigma_1\cdot\boldsymbol\sigma_2=2P_{12}-\mathbb I$,
$\mathbf S_{12}^2=\mathbb I+P_{12}$), condizione di isoscele ($\|[H,\mathbf
S_{12}^2]\|=0$ se e solo se $J'_{23}=J'_{31}$, verificato anche per
sbilanciamenti minimi).

### File prodotti

- `teoria_trimero_isoscele.pdf` (20 pagine) — derivazione completa senza
  passaggi impliciti: algebra di scambio, decomposizione di Kambe (col metodo
  esplicito del conteggio per $M$, non solo citazione di Clebsch-Gordan),
  simmetria $C_2$ dimostrata via coniugazione, spettro nei Casimir, campo
  critico, mappa dei segni, regola di selezione, conseguenze per il VQE.
  Include: figura della geometria, figura della mappa dei segni $(J,J')$,
  figura ad albero della decomposizione $\tfrac12^{\otimes3}\to$ A,B,C,
  figura della struttura diagonale $8\times8$ di $H$ (a $b=0$ e $b\neq0$),
  quattro grafici dello spettro in campo nei casi rappresentativi.
- `animazione_trimero_isoscele.html` — esplorazione interattiva standalone
  (nessuna dipendenza esterna): slider su $J,J'$ (con segno) e sul campo
  osservato, triangolo con legami colorati per segno (AFM/FM) e spessore
  proporzionale al modulo, mini-mappa di fase con posizione corrente, stato
  istantaneo (fondamentale, gap, magnetizzazione) aggiornato dal vivo.
- `verifica.py` — batteria di test sopra descritta, riusabile per controlli
  futuri (es. dopo l'estensione allo scaleno o all'introduzione del DM).

### Metodologia di lavoro (nuova, degna di nota per il seguito)

L'intera derivazione è stata costruita a domande: ogni passaggio lasciato
inizialmente implicito (es. perché gli autovalori di $P_{12}$ sono $\pm1$,
perché $v\propto(1,1)$ diventa $\ket{t_0}=\tfrac1{\sqrt2}(\ket{01}+\ket{10})$,
le regole di commutazione $[s_i^a,s_j^b]$, perché $\mathbf S^2$ si chiama
"Casimir", perché il conteggio dà tre multipletti A,B,C invece di due) è
stato reso esplicito su richiesta e poi integrato nel PDF in un secondo
momento, con verifica di non aver perso né semplificato nulla (controllo
riga-per-riga di ogni occorrenza terminologica prima di applicare rinomine,
es. "singoletto" usato correttamente per la sola coppia di base ma
fuorviante se riferito al blocco C intero — corretto in tre punti precisi,
non con una sostituzione generica).

### Prossimo passo

Catena aperta N=3 (teoria esatta, stesso livello di dettaglio) per completare
il quadro Parte 1; oppure VQE per il triangolo isoscele (PMA-2q·3 esteso a 3
qubit) usando questa teoria come benchmark. Nessuna decisione ancora presa
su quale priorità — vedi `scheda_progetto_tesi.md`.

## Aggiornamento — quantum simulation Trotter del dimero: completata

Implementato il task richiesto dal relatore il 18/07/2026 (simulazione dinamica
reale $e^{-iHt}$ dell'Hamiltoniana VQE del dimero, non del TIM), seguendo le
risposte del 19/07 (2 qubit, $D\neq0$ diretto, stato iniziale $\ket{00}$,
osservabile $S_z$ totale, Suzuki-Trotter al 1° ordine).

**Punto di partenza per la dimostrazione Trotter:** il regime **R0**
($b/J=0.5$, $D/J=1/6$, cioè $J=2b$, $D=b/3$) è **esattamente il
suggerimento originale del relatore** del 19/07/2026 (vedi risposta 4
sopra), usato come primo caso e come controllo "quasi monocromatico"; da lì
derivato **R1** ($b/J=-0.18$, $D/J=1$, non monocromatico). Sono i punti
adottati **per questo sotto-task specifico** (dimostrare convergenza di
Trotter, costo in gate, comportamento monocromatico vs non), un filone
esplorativo a sé.

**Punto adottato per la pipeline principale (ground state → correlazioni):**
resta il "test 2" ($b/J=0.35$, $D/J=0.80$, `parametri_scelti.json`) — è lì
che il ground state trovato via VQE viene effettivamente usato come stato
iniziale nel circuito con l'ancilla per le correlazioni dinamiche (vedi
sezioni precedenti). **I due punti non si sovrappongono e non sono in
competizione**: R0/R1 non sono mai stati portati alla pipeline
ground-state/correlazioni, e il test2 non è mai stato usato per la
dimostrazione di convergenza di Trotter (**corretto rispetto a una prima
stesura di questa voce**, che indicava erroneamente il test 2 come punto di
partenza anche per la dimostrazione Trotter).

### Selezione del regime dimostrativo

Per trovare "oscillazioni di $S_z$ non banali (non monocromatiche)" come
richiesto, sviluppato un criterio a due indicatori calcolati dalla dinamica
esatta: **escursione** picco-picco di $\langle S_z\rangle(t)$ (deve superare
il rumore statistico di campionamento) e **$a_2/a_1$**, rapporto fra le
ampiezze dei due modi spettrali dominanti ($\to0$ monocromatico, $\to1$
bilanciato). Servono entrambi: un segnale ricco ma minuscolo, o grande ma
monocromatico, non soddisfano la richiesta.

Storia della selezione (utile per la difesa): un primo criterio (entropia
spettrale pesata $A\cdot S$) è stato scartato — non riconducibile ad alcuna
fonte (proposta originale non richiesta dal corso) e poco robusto (scarto
1°–5° classificato del 4%, un criterio alternativo rimescolava la
graduatoria). Il criterio a due indicatori attuale è più semplice e
verificabile a mano dal relatore.

Due regimi identificati: **R0** ($b/J=0.5,\,D/J=1/6$, quasi monocromatico,
usato come controllo) e **R1** ($b/J\approx-0.18,\,D/J=1$, non
monocromatico, $a_2/a_1=0.995$) — quest'ultimo derivato dalla struttura a V
dell'Hamiltoniana (ampiezza da formula di Rabi, numero di frequenze dai
detuning $\Delta_\pm=J\pm b$) con due scan 1D indipendenti, non da scan
automatico o brute-force.

> ✅ **Discrepanza R1 risolta (era falso allarme di versione):** il notebook
> definisce esplicitamente `R1 = dict(b=-0.18, J=1.0, D=1.0)  # punto
> adottato` e lo usa coerentemente ovunque, incluse le etichette dei grafici
> nella versione attuale del notebook (`R1: $b/J=-0.18,\ D/J=1$`). Il
> grafico con l'etichetta $-0.15$ mostrato durante la revisione era una
> **figura non aggiornata** rispetto al notebook corrente — nessuna
> discrepanza reale nel codice, $-0.18$ è il valore definitivo su tutta la
> linea (derivazione, tabelle, circuito, grafici).

### Risultato analitico trovato durante l'analisi

Lo stato $\ket{t_0}=(\ket{01}+\ket{10})/\sqrt2$ risulta **esattamente
disaccoppiato** dall'intera dinamica: autostato di $H_1$ (energia $J/4$),
annichilito da $H_2$ ($H_2\ket{t_0}=0$ esatto — i contributi del DM su
$\ket{01}$ e $\ket{10}$ si cancellano per interferenza distruttiva esatta),
ortogonale a $\ket{00}$, non contribuisce a $S_z$. Tutte e tre le proprietà
verificate a scarto numericamente zero. Conseguenza: lo spazio efficace è a
3 livelli (non 4), quindi al più 2 frequenze **indipendenti** (non 3: vincolo
$\Delta_{03}=\Delta_{01}+\Delta_{13}$) nell'evoluzione di $\langle
S_z\rangle(t)$ — verificato su tutti i regimi testati.

### Verifica quantitativa dell'errore di Trotter

Scaling misurato a $t=10$: infedeltà $1-\mathcal F$ scala con pendenza
$-2.11$ (log-log), norma operatoriale $\|\Delta U\|_2$ con pendenza $-1.06$
— coerenti con la teoria (Trotter al 1° ordine: errore per passo
$O((t/N)^2)$, quindi $\|\Delta U\|\sim O(1/N)$ a $t$ fissato e $1-\mathcal
F\sim O(1/N^2)$, essendo l'infedeltà quadratica nell'errore d'operatore).
Confrontato anche il circuito con shot finiti (8192 shot, $N=20$) contro la
dinamica esatta — buon accordo.

### Costo in gate (`costo_gate_trotter.md`)

Due codifiche a confronto per passo di Trotter:

| | `cx`-`rz`-`cx` esplicito | `RZZ` nativo |
|---|---|---|
| gate/passo | 17 (8 a 2 qubit) | 11 (5 a 2 qubit) |
| profondità/passo | 15 | 9 |

A $N=20$ ($t=30$, il caso eseguito su circuito): 340 vs 220 gate totali, 160
vs 100 a due qubit. Nota: `RZZGate` di Qiskit non è primitivo indipendente,
la sua `.definition` è esattamente la stessa decomposizione `cx-rz-cx` — la
differenza è solo il livello di astrazione a cui si conta, rilevante per la
Parte 2 (rumore di gate reale).

> ✅ **Verificato sul codice, non solo sull'intestazione (in risposta a
> domanda diretta di Samuele):** `trotter_dimero.py` scrive $H$ in
> **convenzione di spin** ($s_i=\sigma_i/2$, coefficienti $b/2$, $J/4$,
> $D/4$ — è la notazione con cui il relatore stesso ha posto il task in
> `quantum_simulation_notes.jpg`) con la propria convenzione sito1→qubit0.
> Il circuito delle correlazioni (`circuito_correlazioni_tutte.ipynb`)
> costruisce $H$ **in modo completamente indipendente**, con la propria
> funzione `dimer_hamiltonian` in **convenzione di Pauli diretta** (nessun
> fattore $1/2,1/4$ — la stessa di `vqe_test2.py`/6-Applications.pdf) e con
> `site_to_qubit={1:1, 2:0}`. **Nessun import fra i due file** (verificato
> a colpo di script sul notebook: zero occorrenze di `trotter_dimero`).
> Controllando l'algebra con entrambe le convenzioni tracciate insieme
> (sito **e** normalizzazione, non una sola delle due), i due moduli
> risultano **entrambi corretti e a vicenda coerenti** per la stessa fisica
> $D(s_{x1}s_{z2}-s_{z1}s_{x2})$ — non c'è un segno sbagliato nascosto.
> **Non è quindi un bug attivo**, ma resta un punto da tenere a mente: le
> due convenzioni (spin vs Pauli) differiscono per un fattore $2$ su $b$ e
> $4$ su $J,D$ (lo stesso tipo di dizionario $J_\text{Heisenberg}=4J_\text{code}$
> già noto nel progetto) — se in futuro si vorranno riusare gli stessi
> valori numerici fra il blocco Trotter e il blocco VQE/correlazioni, va
> applicata la conversione esplicita, **sito e normalizzazione insieme**
> (convertirne solo una delle due, isolatamente, introdurrebbe davvero un
> segno sbagliato).

### Collegamento con le correlazioni

Il circuito con l'ancilla (Hadamard test) usa $U(t)$ come blocco non
controllato fra controlled-$W$ e anti-controlled-$V$. **Verificato**: $U(t)$
nel circuito delle correlazioni **non** è quella di `trotter_dimero.py` — è
costruita in proprio nel notebook delle correlazioni, come prodotto Trotter
($e^{-iH_2\tau}e^{-iH_1\tau}$, con $H_1,H_2$ dalla convenzione di Pauli
locale del notebook) applicato $N$ volte come gate unitario esplicito
(`UnitaryGate`, non decomposto in porte elementari). Il filone Trotter di
`trotter_dimero.py` resta quindi **dimostrativo a sé** (focalizzato su
convergenza, costo in gate, regimi R0/R1) e non condivide codice con le
correlazioni — ciascuno dei due usa la propria costruzione di $U(t)$,
internamente coerente (vedi discrepanza sopra, chiarita).

### File prodotti

`trotter_dimero.py`, `quantum_simulation_dimero_trotter.ipynb`,
`quantum_simulation_dimero_trotter_semplificato.ipynb`,
`quantum_simulation_dimero_trotter_note.md`,
`quantum_simulation_relazione_domande_tecniche.md`, `costo_gate_trotter.md`,
`parametri_scelti.json`.

**Stato:** completato. Le due discrepanze inizialmente segnalate sono state
entrambe verificate e chiuse (R1: falso allarme di figura non aggiornata;
convenzioni spin/Pauli e sito/qubit: diverse ma internamente coerenti in
ciascun modulo, nessun bug attivo, nessun import incrociato) — vedi ✅
sopra. Punto da tenere a mente per il seguito, non un errore: se si
vorranno mai riusare gli stessi valori numerici $(b,J,D)$ fra il blocco
Trotter (convenzione di spin) e il blocco VQE/correlazioni (convenzione di
Pauli), va applicata la conversione $b_\text{Pauli}=b_\text{spin}/2$,
$J_\text{Pauli}=J_\text{spin}/4$, $D_\text{Pauli}=D_\text{spin}/4$ — sito e
normalizzazione insieme, non separatamente.

## Aggiornamento — N=3: teoria della catena aperta, VQE (senza e con DM) per anello e catena, ristrutturazione documentale

### Teoria della catena aperta

Stessa decomposizione di Kambe già usata per il triangolo isoscele, applicata
alla catena 1–2–3 (legami fisici $(1,2)$ e $(2,3)$, nessun legame $(3,1)$).
Simmetria di **riflessione** $1\leftrightarrow3$ (sulla coppia *non legata*,
non quella legata come nell'anello) — Casimir $S_{13}^2$, tre multipletti
$A$ ($S_{13}{=}1,S{=}3/2$), $B$ ($S_{13}{=}1,S{=}1/2$), $C$ ($S_{13}{=}0,S{=}1/2$),
campo critico $b_c=3J$ (esiste solo per $J>0$). Per $J>0$ il fondamentale a
basso campo è **sempre** il blocco $B$ — mai serve il confronto $E_B$ vs $E_C$
che serve invece nell'anello, perché $E_B=-4J<E_C=0$ indipendentemente da
$J$: una semplificazione reale, non solo una topologia più povera.

**Complicazione trovata nella derivazione degli stati**: la coppia di
classificazione $(1,3)$ non è adiacente nel registro fisico
$|q_1q_2q_3\rangle$ — la derivazione richiede una gestione esplicita del
riordino che nell'anello (coppia $(1,2)$, adiacente) non serve. Il blocco
$B$ risultante **non è banale** (pesi $1/\sqrt6,1/\sqrt6,-\sqrt{2/3}$) — a
differenza del blocco a basso campo del punto di lavoro standard
dell'anello (blocco $C$, singoletto banale). Conseguenza diretta per il
VQE: nella catena non esiste una derivazione a mano semplice
($X,H,\mathrm{CX},X$) per lo stato iniziale a basso campo, serve
`prepare_state` fin da subito.

**File prodotti:** `trimer_chain_exact.py`, `teoria_trimero_catena_aperta.pdf`,
`derivazione_stati_kambe_trimero_catena.pdf`, `verifica_catena.py` (ex
`verifica_catena_preliminare.py`), `animazione_trimero_catena_aperta.html`.

### VQE senza DM — anello e catena, struttura parallela completa

Per entrambe le topologie: un ansatz PMA con branching e blocco RBS
(produzione principale), lo stesso con blocco $W$ (mirror dell'ansatz
"originale" del dimero), un ansatz PMA senza branching, due notebook
"spiegato". Per l'anello: `vqe_trimer_ring.py`, `vqe_trimer_ring_W.py`,
`vqe_trimer_ring_nobranch.py`, i due `_spiegato.ipynb`. Per la catena, lo
stesso mirror: `vqe_trimer_chain.py`, `vqe_trimer_chain_W.py`,
`vqe_trimer_chain_nobranch.py`, i due `_spiegato.ipynb`.

> ✅ **Due problemi reali trovati e corretti durante la costruzione, non
> solo teorici:**
> 1. `vqe_trimer_chain_nobranch.py` — conteggio dei parametri per ciclo
>    sbagliato ($4K$ invece di $5K$), causava un `IndexError` immediato.
>    Dopo la correzione: a $b=1.0$ (sotto $b_c$), $K=1$ resta vicino al
>    tetto strutturale $\approx5/6$ già noto per la famiglia "esatta", ma
>    $K=2$ (RBS ripetuto due volte) lo supera, $\mathcal F=1$ esatto —
>    stesso pattern già visto per l'anello sotto DM (PMA-2qC.K2 batte K1).
> 2. `vqe_trimer_chain_spiegato.ipynb` — due celle mostravano
>    $\mathcal F=0.826612$ invece di $1.000000$, non per un limite
>    strutturale ma per un minimo locale specifico del seed di default
>    (42): con $R=8$ o con qualunque altro seed, converge subito
>    all'esatto. Esempio concreto della distinzione "limite di
>    espressività" vs "artefatto di ottimizzazione" già tenuta ferma dal
>    dimero — qui il rischio si è materializzato davvero, non solo in
>    teoria.

> ✅ **Correzione anche su `trimer_ring_exact.py`:** $\langle M_z\rangle$
> a $b=0$ (fondamentale degenere) veniva calcolato su un singolo
> autovettore restituito da `numpy.linalg.eigh`, scelto arbitrariamente
> fra quelli del sottospazio degenere — un salto apparente osservato in una
> vecchia figura era un artefatto numerico, non fisico. Corretto: media sul
> sottospazio degenere. Il salto vero (fisico) resta solo a $b_c$.

### VQE con DM — anello (Fase 5), catena non ancora affrontata

Due notebook, stesso schema indagine-mirata → confronto-sistematico già
usato per il dimero:
- `analisi_espressivita_PMA_anello.ipynb` — quale famiglia PMA (RBS o $W$)
  regge meglio sotto DM, testata al campo critico teorico $b_c=2.4$.
- `confronto_ansatz_entangler_trimero_anello.ipynb` — 15 ansatz (10 RBS,
  5 $W$), sweep completo su griglia in $b$, sia $D=0$ sia DM Opzione B.

> ✅ **Scoperta centrale, verificata con 60 restart e ottimizzazione
> diretta della fidelity (non dell'energia)**: la famiglia RBS-2q ha un
> **tetto strutturale vero** sotto DM ($\mathcal F\approx0.9999$,
> identico per tre varianti indipendenti indipendentemente dal numero di
> parametri), mentre la famiglia $W$-2q raggiunge $\mathcal F=1$ esatto.
> Candidato canonico per il seguito sotto DM: **`W-2q.6`** — meno
> parametri e meno gate di RBS-2q, fidelity esatta dove RBS-2q resta
> bloccata. Risultato controintuitivo rispetto al caso $D=0$, dove RBS-2q
> è sempre la famiglia più efficiente.

**File obsoleto trovato**: `plateau_dm_ring_cache.json` — formato di
chiave incompatibile con la cache effettivamente usata dal notebook finale
(`espressivita_anello_cache.json`), zero sovrapposizione di chiavi,
verificato esplicitamente. Artefatto di una versione precedente del
notebook. Candidato per l'eliminazione dalla cartella di lavoro.

**Non ancora fatto**: Fase 5 (VQE con DM) per la catena aperta — il
notebook di confronto attuale (`confronto_ansatz_entangler_trimero_catena.ipynb`)
resta $D=0$-only, non ancora esteso agli ansatz $W$ né al DM.

### Ristrutturazione documentale — dimero, anello, catena allineati

Tutta la documentazione tex/pdf riorganizzata per fase e per topologia,
mirror strutturale in tutte e tre: `trimero_anello_exact.pdf`,
`trimero_catena_exact.pdf`, `dimero_exact.pdf` (Fase esatto);
`trimero_anello_vqe.pdf`, `trimero_catena_vqe.pdf`, `dimero_vqe.pdf` (VQE
senza DM — per il dimero, dove il DM non è mai stato separato in una fase
a sé, il documento copre l'intera fase, dichiarato esplicitamente);
`trimero_anello_vqe_dm.pdf` (VQE con DM, solo anello per ora);
`trimero_anello_verifiche.pdf`, `trimero_catena_verifiche.pdf` (script di
controllo indipendenti — spettro/campo critico da un lato, stati di Kambe
espliciti dall'altro, per ciascuna topologia).

Ogni documento include, per i moduli `.py`, l'elenco delle funzioni
interne e come si usa il file — non solo descrizione/verifiche/conclusione.

**Stato attuale in una riga:** teoria completa per entrambe le topologie
N=3; VQE senza DM completo per entrambe; VQE con DM completo solo per
l'anello. Trotter e correlazioni dinamiche per N=3 restano il prossimo
fronte, per entrambe le topologie.

## Aggiornamento — decisione metodologica: Trotter interno per H_ex (trimero)

Per estendere Trotter dal dimero al trimero (anello), H0 = b·S_z^tot + H_ex
fattorizza esattamente come nel dimero (S_z^tot commuta con H_ex). Ma H_ex
= J σ1·σ2 + J'σ2·σ3 + J'σ3·σ1 non è un blocco singolo esponenziabile: i
legami 12 e 23 condividono il qubit 2, [σ1·σ2, σ2·σ3] ≠ 0.

Decisione: procedere con Trotter interno (strategia (a)) — spezzare H_ex
nei tre legami, ciascuno esponenziabile come nel dimero via RXX+RYY+RZZ —
invece della sintesi numerica dell'unitaria 8x8 (strategia (b), scartata
per coerenza con l'approccio "gate sempre fisicamente etichettati" già
seguito nel dimero). Introduce una SECONDA fonte di errore di Trotter,
annidata e distinta da quella fra H0 e H_DM — da trattare esplicitamente
in tesi come due livelli separati.

Aperto: quale opzione DM (A o B) usare per la dimostrazione di Trotter
(diverso dalla scelta già chiusa per il VQE, dove B è obbligata dalla
fisica del gap); punto di lavoro/stato iniziale per la dinamica (J=1,
J'=0.4 zona C è ottimizzato per il ground state statico, non garantisce
oscillazioni non banali di ⟨S_z⟩(t)). In attesa di risposta del relatore
(mail inviata).

## Aggiornamento — risposta del relatore e assunzione operativa (DM per Trotter trimero)

**Risposta del relatore alla mail sulle priorità:** conferma implicitamente
la priorità Trotter+correlazioni su N=3 (risponde nel merito tecnico invece
di indicare un'altra priorità) e concorda esplicitamente sulla seconda
fonte di errore di Trotter dovuta alla divisione dei bond 1-2 e 2-3.
Richiesta esplicita: testare quanti step $N$ sono necessari per una buona
riproduzione della dinamica — analisi di convergenza (fidelity/osservabili
vs $N$) da includere fin da subito nel task.

**Nota importante:** la risposta del relatore riguarda SOLO la divisione
dei bond in $H_{\rm ex}$, non specifica quale opzione DM usare per questo
task — non va confusa con una conferma sull'opzione DM.

**Assunzione operativa presa in autonomia (non confermata esplicitamente
dal relatore, da segnalare nel prossimo report):** si procede con **DM
Opzione B**, per coerenza con tutta la sezione VQE trimero già validata su
B (apertura del gap, ansatz W-2q.6 testato proprio sotto B) — evita di
introdurre una seconda variante di $H_{\rm DM}$ nel codice senza un motivo
fisico per farlo. Punto di lavoro: si parte da $J=1$, $J'=0.4$ (zona C,
punto VQE), poi si esplora la dinamica esatta per trovare un regime con
oscillazioni non banali di $\langle S_z\rangle(t)$ — stesso pattern
R0→R1 già usato nel dimero.

## Aggiornamento — Trotter trimero anello: modulo validato, punto provvisorio, due note aperte per il seguito

**Modulo `trotter_trimero_anello.py`** completato e validato: self-test a
precisione macchina sul circuito Qiskit reale (non solo a matrice numpy).
Struttura a **tre livelli** confermata numericamente (non due, come
inizialmente ipotizzato): $H_0=bS_z^{tot}+H_{ex}$ fattorizza esattamente;
$H_{ex}$ e **anche** $H_{DM}$ (Opzione B) richiedono ciascuno un Trotter
interno sui 3 bond, condividendo qubit. Il livello nuovo ($H_{DM}$
bond-split) non è trascurabile: al punto di lavoro adottato pesa un
fattore $\sim4.4$ sull'infedeltà totale rispetto a un'ipotetica (irrealizzabile)
versione con $H_{DM}$ trattato come blocco esatto.

**Convenzione**: modulo scritto in convenzione Pauli diretta (coerente con
`trimer_ring_exact.py`, VQE trimero), NON in convenzione a spin come
`trotter_dimero.py` — angoli dei gate ri-derivati da zero, non copiati.
Convenzione sito↔qubit identica a `trimer_ring_exact.py` (site1→qubit2,
site2→qubit1, site3→qubit0).

**Punto di lavoro adottato: $R_0$ (trimero)** — $J{=}1,J'{=}0.4$ (VQE),
$b{=}0.05,D{=}1.93$. Scelto da uno scan $(b,D)$ con lo stesso criterio
picco-picco + $a_2/a_1$ di R0/R1 del dimero, poi verificato robusto a
piccole perturbazioni. **Provvisorio**, non da una derivazione principiata.
Convergenza in $N$ misurata: infedeltà $<1\%$ a $N\simeq325$, $<0.1\%$ a
$N\simeq1025$, $<0.01\%$ a $N\simeq3250$ — sensibilmente più alto del
dimero (dove $N=80$ bastava per $\sim10^{-5}$), atteso per via dei due
livelli di bond-splitting e di $D/J\simeq1.9$ non piccolo.

- [ ] **APERTO**: derivazione analoga a quella di R1 (struttura degli 8
      livelli del trimero, condizioni indipendenti su ampiezza/detuning)
      per sostituire $R_0$ con un punto derivato, non solo scansionato.
      Prossimo notebook dedicato.
- [ ] **APERTO (per la Parte 2, rumore)**: costo in gate del circuito
      Trotter — 30 gate a 1-2 qubit per passo esterno (12 H, 9 RZZ, 3 RXX,
      3 RYY, 3 RZ), $N\simeq300$–$1000$ per soglie di infedeltà 1%–0.01% al
      punto $R_0$. Aggancio diretto con il vantaggio di gate già
      documentato per RBS vs $W$ nel VQE (`scelta_ansatz_RBS_vs_W.pdf`):
      meno gate per bond = meno canali di rumore da modellare quando si
      introduce Kraus/Lindblad. Da riprendere esplicitamente quando si
      apre quel blocco della tesi.

## Aggiornamento — circuito compatto per il trimero anello: verifica empirica, stessa conclusione del dimero (rafforzata)

Ripetuto per il trimero l'esperimento già fatto per il dimero
(`circuito_compatto_teoria_e_limiti.pdf`): comprimere il circuito Trotter
via sintesi numerica (`transpile`, `optimization_level=3`) invece di usare
i gate fisicamente etichettati.

**Differenza di partenza rispetto al dimero**: per 2 qubit esiste un
teorema chiuso (Cartan/camera di Weyl, $SU(4)$): ogni unitaria si
realizza con al più 3 CNOT. Per 3 qubit ($SU(8)$) non esiste un
risultato altrettanto chiuso — non reperita né verificata alcuna formula
analoga. La verifica qui è quindi **empirica** (quello che il transpiler
trova), non un minimo dimostrato — differenza dichiarata esplicitamente
nel documento.

**Risultati**: un singolo passo (15 gate a due qubit nativi) si comprime
a 18 CNOT, fedeltà $1.0$. Il fenomeno interessante è sull'**intero
prodotto a $N$ passi**: si stabilizza a $\sim19$ CNOT
**indipendentemente da $N$** già da $N=2$ (verificato fino a $N=100$) —
stesso fenomeno del dimero (lì 3 CNOT fissi), qui più marcato in valore
assoluto: con gli $N\simeq300$–$1000$ che servono per la convergenza al
punto $R_0$, il circuito esplicito avrebbe $4500$–$15000$ gate a due
qubit contro i $\sim19$ del compresso.

**Conclusione**: invariata rispetto al dimero, riconfermata e rafforzata
— non usare il circuito compresso per lo studio Trotter-vs-rumore della
Parte 2 (farebbe sparire la scalata in $N$ del costo in gate, il
fenomeno stesso da studiare, e lo farebbe in modo ancora più ingannevole
data la maggiore distanza fra $N$ reale e conteggio compresso fisso);
legittimo solo per la domanda separata "costo minimo per *questa*
evoluzione a un $t$ fissato".

**File prodotto**: `trimero_anello_circuito_compatto.tex` (compilato e
verificato, 3 pagine, nessun errore).

## Aggiornamento — documentazione completa della fase Trotter trimero anello; prossimo passo: correlazioni dinamiche

Completata la documentazione della fase di quantum simulation (Trotter) per il
trimero anello, in parallelo a quanto già esiste per il dimero. File prodotti
da allora:

- **`quantum_simulation_trimero_anello_teoria.tex`** — derivazione teorica
  completa. Contributo originale: l'operatore di **chiralità di spin
  scalare** $\chi=\vec\sigma_1\cdot(\vec\sigma_2\times\vec\sigma_3)$
  (Wen–Wilczek–Zee 1989, citazione verificata) identifica esattamente il
  commutatore che rende necessario il Trotter interno di $H_{ex}$; identità
  analoga (ma strutturalmente diversa, non collassa a un solo operatore) per
  i legami DM. Formula chiusa per l'errore di livello 1:
  $i\tau^2J'^2\chi+O(\tau^3)$ — il prodotto incrociato $JJ'$ si cancella
  esattamente, dipende solo dai lati uguali $J'$.
- **`quantum_simulation_trimero_anello_applicazione.tex`** — applica la
  teoria all'implementazione: cronologia della scoperta del livello 2,
  ricerca del punto di lavoro, risultati di convergenza e separazione errori,
  riepilogo compattezza.
- **`quantum_simulation_trimero_anello_trotter_spiegato.tex`** — il notebook
  spiegato cella per cella. Include la dimostrazione (verificata,
  $2.2\times10^{-16}$) che $\ket{000}$ è autostato esatto di $H_{ex}$ e di
  $H_0$: per $D=0$, $\langle S_z^{tot}\rangle(t)$ è **costante** qualunque
  siano $J,J',b$ — il DM non è un dettaglio, è l'unica sorgente di dinamica
  osservabile da questo stato iniziale.
- **`trimero_anello_frustrazione_e_chiralita.tex`** — nota di chiarimento:
  la frustrazione energetica (ciclo dispari) non richiede l'equilatero; la
  non-commutatività algebrica (operatore $\chi$) vale per qualunque $J,J'$;
  le due cose si toccano solo nel limite $J'\to0$ (errore di livello 1 → 0,
  coerente col ritorno al caso dimero). Il nostro punto di lavoro
  ($J\neq J'$) non è nel regime degenere/chirale del paper citato.
- **`trimero_anello_quantum_simulation.tex`** — documento di catalogazione
  di tutta la fase (stile `trimero_anello_vqe_dm.pdf`), un riferimento unico
  per ritrovare rapidamente cosa fa ciascun file.

**Notebook (`quantum_simulation_trimero_anello_trotter.ipynb`) esteso**:
convergenza in $N$ e separazione dei livelli di errore ripetute su tre punti
robusti (non solo $R_0$) — risultato notevole: la scala di $N$ richiesta
varia molto da punto a punto (da $N\simeq30$ a $N\simeq325$ per l'1\% di
infedeltà), ma lo scaling $O(1/N^2)$ è confermato su tutti e tre; il peso
del livello 2 varia da quasi trascurabile ($\times1.04$) a dominante
($\times4.4$, a $R_0$) — non un fattore universale. Aggiunto anche lo
spettro (ampiezza dei modi di Bohr vs $\Delta_{kl}$) accanto a ogni
traiettoria, e una sezione di esplorazione a parametri liberi (funzione
`esplora(J,Jp,b,D)`, 4 pannelli: segnale, spettro, convergenza, peso
livello 2).

**Nota su `ipywidgets`**: tre tentativi di controlli interattivi
(`FloatSlider`+`interact`, `FloatSlider`+`interact_manual`,
`Dropdown`+`interact` sullo schema di `circuito_correlazioni_tutte.ipynb`)
non hanno dato un risultato affidabile nell'ambiente reale (blocco di
minuti, poi errore di rendering specifico di VS Code —
`jupyter-ipywidget-renderer`/`ipywidgetsKernel`, bug noto dell'estensione,
non del codice). **Adottata la versione a chiamata diretta** (parametri
modificati a mano nel codice): nessuna dipendenza fragile.

**Punti aggiuntivi trovati con l'esplorazione libera — accantonati per
ora, non promossi a punto di lavoro**: $J{=}1,J'{=}0.3,b{=}0.2,D{=}1.1$
(dove il rapporto $V_2/V_1$ attraversa $1$ fra $N=640$ e $N=1280$ — i due
errori di livello sono quasi della stessa taglia a questo punto, un
comportamento qualitativamente diverso dagli altri) e una riconferma
numerica di $R_0$. Decisione esplicita: **restare focalizzati su $R_0$**
come punto di lavoro principale; questi punti aggiuntivi restano
documentati ma non adottati, eventualmente da riprendere in futuro.

**Prossimo passo (decisione presa, in chat separata)**: estendere il
circuito con l'ancilla per le **correlazioni dinamiche** su $N=3$ — l'altra
metà della richiesta originale del relatore ("Trotter e correlazioni
dinamiche"), non ancora iniziata per il trimero. La derivazione
principiata stile $R_1$ del punto di lavoro resta rimandata (priorità più
bassa), non abbandonata.

## Aggiornamento — correlazioni dinamiche trimero anello: simmetria residua derivata, punto di lavoro confermato

Primo passo della fase correlazioni dinamiche per N=3 (mirror del dimero, questa
volta in una chat separata dedicata all'estensione N=3): analisi di simmetria
**prima** del circuito, per lezione esplicita imparata sul dimero (i due bug
del circuito dimero — coniugato complesso mancante, mappa sito↔qubit invertita
— erano entrambi mascherati dalla simmetria $U$ sui primi correlatori testati,
quindi qui l'analisi di simmetria viene fatta e verificata numericamente
**prima** di scrivere una riga di circuito, non dopo).

**Decisione preliminare sul punto di lavoro (discussa con Samuele).** Come per
il dimero (dove il punto "test2" per le correlazioni non fu scelto con uno scan
dedicato, ma riusato dal lavoro VQE già fatto, e la sua ricchezza verificata
*dopo*), si riusa il punto VQE-con-DM già validato per l'anello:
$J{=}1,\,J'{=}0.4,\,b{=}b_c{=}2.4,\,D{=}0.15$ (Opzione B), ansatz `W-2q.6`
(vedi `trimero_anello_vqe_dm.tex`) — invece di cercare un nuovo punto dedicato
o riusare i punti Trotter ($R_0$, $D\gg J$, regime scollegato dal VQE-con-DM
già validato). Motivazione fisica: $b_c$ è l'incrocio di livello che il DM
Opzione B apre in anticrossing (`analisi_dm_trimero_anello.tex`) — gap piccolo
fondamentale/primo eccitato, stesso meccanismo che nel dimero produceva $R_1$
(dinamica non monocromatica). Decisione condizionata a verifica classica
esplicita (fatta subito sotto), non assunta a priori.

**Simmetria unitaria residua — generalizzazione non banale del caso dimero.**
Sotto DM Opzione B, lo scambio puro $P_{12}$ resta rotto (il DM è dispari sotto
scambio, come nel dimero). La riparazione del dimero,
$U=\mathrm{SWAP}\cdot(R_z(\pi)\otimes R_z(\pi))$, **non si estende aggiungendo
banalmente l'identità sul terzo qubit**: verificato numericamente che quella
versione NON commuta con $H$ ($\|[U_\text{naive},H]\|\sim31$ su parametri
casuali — non un piccolo residuo, una rottura netta). La simmetria corretta
richiede $R_z(\pi)$ su **tutti e tre** i qubit:
$$U_\text{anello} = \mathrm{SWAP}_{12}\cdot\big(R_z(\pi)\big)^{\otimes 3}.$$
Verificato $[U_\text{anello},H]=0$ a precisione macchina (errore $=0$ esatto)
su 20 punti casuali $(J,J',b,D)$, per l'Hamiltoniana completa (scambio + campo
+ DM Opzione B). Differenza qualitativa dal dimero: $U_\text{anello}^2=-\mathbb
I$ (non è un'involuzione, ordine 4 e non 2, per via del terzo fattore $R_z(\pi)$
— $(-1)^3=-1$ invece di $(-1)^2=+1$) — non hermitiano, ma resta unitario con
autovalori di modulo 1 ($\pm i$), sufficiente per l'argomento sui correlatori
(stessa struttura di dimostrazione del dimero, non ripetuta qui in dettaglio).

**Lemma (verificato numericamente, errore $=0$):**
$U_\text{anello}\,\sigma_i^\alpha\,U_\text{anello}^\dagger=\eta_\alpha\,
\sigma_{\pi(i)}^\alpha$ per $i=1,2,3$, con $\pi=(1\,2)$ (fissa il sito 3),
$\eta_x=\eta_y=-1,\eta_z=+1$ — stessa struttura del dimero, estesa al sito
fisso $3$ (che riceve comunque il fattore $\eta_\alpha$ dalla propria $V$,
pur non essendo scambiato).

**Corollario nuovo, specifico di $N=3$ (non presente nel dimero: lì non
esisteva un sito fisso sotto lo scambio).** Poiché il sito 3 è punto fisso di
$\pi$: $C_{33}^{\alpha\beta}(t)=\eta_\alpha\eta_\beta\,C_{33}^{\alpha\beta}(t)$
per ogni $t$ — zero rigoroso **per ogni $t$** (non solo $t=0$) quando
$\eta_\alpha\eta_\beta=-1$:
$$C_{33}^{xz}(t)=C_{33}^{zx}(t)=C_{33}^{yz}(t)=C_{33}^{zy}(t)\equiv0\quad\forall t.$$
Verificato numericamente al punto di lavoro: $\max_k|a_kb_k|\sim10^{-17}$
(precisione macchina) per tutte e quattro.

**Simmetria di time-reversal $K$.** $H$ è reale in base computazionale per
ogni $J,J',b,D$ (verificato, $\max|\mathrm{Im}\,H|=0$ su 20 punti casuali) —
stesso argomento del dimero (Lemma "$KHK=H$"), generalizza senza modifiche a
$N$ siti qualunque (l'argomento non usa la struttura di scambio, solo la
realtà delle matrici di Pauli $X,Z$ e l'immaginarietà di $Y$). Zero rigoroso a
$t=0$ per ogni coppia $i\neq j$ con esattamente una componente $y$: verificate
tutte le $24$ combinazioni (3 coppie di siti ordinate $\times$ 2 ordini
$\times$ 4 combinazioni di componenti con un solo $y$) al punto di lavoro,
tutte esattamente zero a $t=0$.

**Controllo classico completo al punto proposto
($J{=}1,J'{=}0.4,b{=}b_c{=}2.4,D{=}0.15$, Opzione B).** Fondamentale non
degenere: gap $E_1-E_0=0.2547$ (coerente con $g_\text{min}\approx0.25$ già
riportato in `analisi_dm_trimero_anello.tex` per $D\approx0.148$-$0.15$).
Scan completo delle $81$ combinazioni $(i,j,\alpha,\beta)$ con $i,j\in\{1,2,3\}$:
**esattamente 4 nulle per ogni $t$** — le quattro predette dalla simmetria
$U_\text{anello}$ (autocorrelazione sito 3, $xz/zx/yz/zy$), nessuna zero
aggiuntivo non spiegato da simmetria. Le restanti 77 sono non banali, con
diverse combinazioni genuinamente ricche: es. $C_{11}^{yy},C_{12}^{yy},
C_{21}^{yy},C_{22}^{yy}$ con $|a_kb_k|_\text{max}\approx0.50$ e fino a 6 modi
spettrali rilevanti (soglia 5% del massimo) su un massimo possibile di 7;
$C_{33}^{yy},C_{33}^{xy},C_{33}^{yx},C_{33}^{xx}$ con $|a_kb_k|_\text{max}
\approx0.49$–$0.52$, 3 modi rilevanti. Alcune combinazioni residue sono
piccole ma non nulle (es. $C_{33}^{zz}\sim5\times10^{-4}$) — non protette da
alcuna simmetria trovata, semplicemente piccole a questo punto specifico.

**Decisione presa:** punto di lavoro **confermato**, verificato a posteriori
(non solo assunto) — nessuna ricerca di un punto dedicato è risultata
necessaria.

**Formalizzato in `.tex`:** `simmetrie_correlatori_trimero_anello.tex`
(compilato, verificato pagina per pagina, zero errori/overfull, 8 pagine) —
tutte le proposizioni/corollari sopra con dimostrazione completa, non solo
verifica numerica.

## Aggiornamento — circuito Hadamard test per le correlazioni trimero anello: implementato e validato

Secondo passo della fase correlazioni dinamiche per N=3: disegnato,
implementato e validato il circuito a 4 qubit (3 di registro + 1 ancilla),
mirror diretto del circuito già validato per il dimero
(`circuito_correlatori_spiegato.tex`), riusando `trotter_trimero_anello.py`
come blocco $U(t)$.

**Struttura del circuito** (`circuito_correlazioni_trimero_anello.py`,
funzioni `ground_state`, `build_correlator_circuit`,
`ancilla_z_expectation`, `correlator_from_circuit`): preparazione esatta
delle ampiezze del ground state (`prepare_state`, come stand-in per
l'ansatz VQE `W-2q.6`, stessa metodologia già usata per il dimero) sul
registro a 3 qubit; $H$ sull'ancilla; controlled-$W=\sigma_j^\beta$
(controllo pieno) prima di $U(t)$; $U(t)$ Trotter non controllato sul
registro; anti-controlled-$V=\sigma_i^\alpha$ dopo $U(t)$; rotazione di
base sull'ancilla ($H$ per Re, $R_x(\pi/2)$ per Im) e lettura di
$\langle\sigma_z^{anc}\rangle$ dallo statevector esatto (nessun rumore di
shot in questa fase — validazione della logica del circuito, non ancora
dello scenario sperimentale).

**Validazione** (`validate_circuito_correlazioni.py`): riferimento
classico calcolato **direttamente per esponenziale di matrice**
($\texttt{scipy.linalg.expm}$), deliberatamente **non** tramite la formula
spettrale $\sum_k a_kb_k$ — scelta per non poter reintrodurre per
disattenzione la stessa classe di bug del "coniugato complesso mancante"
già trovata nel dimero (qui il confronto è fra due calcoli
concettualmente indipendenti, non fra una formula e la sua stessa
riscrittura).

Al punto di lavoro confermato ($J{=}1,J'{=}0.4,b{=}b_c{=}2.4,D{=}0.15$,
Opzione B; gap $=0.2547$), risultati con $N=200$ passi di Trotter, $t\in\{0.5,1.3,2.7\}$:

- Tutti i correlatori testati ($C_{11}^{yy}$, $C_{33}^{yy}$, $C_{13}^{yy}$,
  $C_{33}^{xz}$, $C_{12}^{yy}$, $C_{21}^{yy}$) concordano col riferimento
  classico entro $|$residuo$|\sim10^{-4}$–$10^{-3}$, coerente con l'errore
  di Trotter atteso a $N=200$ per questo punto di lavoro (stesso ordine di
  grandezza già misurato per l'evoluzione da sola in
  `quantum_simulation_trimero_anello_trotter.tex`).
- **Zero strutturale del sito 3 confermato via circuito** (non solo
  classicamente): $C_{33}^{xz}(t)\approx0$ per tutti e tre i $t$ testati
  (valori $\sim10^{-4}$, compatibili con solo errore di Trotter, non con
  un residuo sistematico) — il Corollario del sito fisso è verificato
  anche a livello di circuito quantistico, non solo di algebra classica.
- **Relazione di simmetria $C_{12}^{yy}(t)=C_{21}^{yy}(t)$ confermata via
  circuito**: $\eta_y\eta_y=+1$ predice l'uguaglianza; il circuito la
  riproduce entro l'errore di Trotter a tutti e tre i $t$ (es. a $t=2.7$:
  $-0.3574+0.4338i$ classico vs $-0.3565+0.4337i$ / $-0.3564+0.4338i$
  circuito per le due permutazioni).
- **Convergenza in $N$** (caso singolo, $C_{11}^{yy}(t{=}1.3)$, $N\in\{10,
  20,40,80,160,320\}$): rapporto fra errori successivi $\to2.0$ raddoppiando
  $N$ (misurato: $2.35,2.14,2.05,2.02,2.01$) — errore sull'ampiezza
  $\sim O(1/N)$, coerente con Trotter al 1° ordine, in linea con la teoria
  già stabilita per il modulo Trotter (`quantum_simulation_trimero_anello_teoria.tex`).

**Nessun bug trovato in questa fase** (diversamente dal dimero, dove
l'implementazione del circuito aveva rivelato due bug reali solo dopo lo
scan sistematico): l'analisi di simmetria è stata fatta e verificata
**prima** di scrivere il circuito, e tutti i residui osservati sono
spiegabili quantitativamente come solo errore di Trotter — nessuna
discrepanza sistematica residua.

**File prodotti:** `circuito_correlazioni_trimero_anello.py`,
`validate_circuito_correlazioni.py` (più le copie locali di
`trimer_ring_exact.py` e `trotter_trimero_anello.py`, già esistenti come
file di progetto, riusate senza modifiche).

**Aperto per il seguito:**
- [x] ~~Documento `.tex` pedagogico che spieghi il circuito passo per passo~~
      — completato, vedi aggiornamento sotto.
- [ ] Validazione con rumore statistico a shot finiti (mirror di
      `circuito_correlazioni_tutte.ipynb` per il dimero) — finora solo
      statevector esatto.
- [ ] Scan sistematico delle 81 combinazioni via circuito effettivo (non
      solo classicamente) — finora solo 6 casi rappresentativi.
- [ ] Derivazione principiata (stile $R_1$) del punto Trotter dimostrativo
      $R_0$ del trimero — priorità più bassa, non abbandonata.
- [ ] Fase 5 (VQE con DM) per la catena aperta — non ancora affrontata.

## Aggiornamento — documento pedagogico del circuito delle correlazioni (trimero anello)

Terzo passo della fase correlazioni dinamiche per N=3: scritto
`circuito_correlazioni_trimero_anello_spiegato.tex`, mirror per N=3 di
`circuito_correlatori_spiegato.tex` (dimero) — spiegazione passo-passo del
circuito (stato di partenza, perché il correlatore non è misurabile
direttamente, costruzione stadio per stadio, dimostrazione che l'ancilla
legge l'overlap, i due punti delicati $U(t)$ non controllato e
anti-controllo su $V$, struttura del blocco Trotter, misura, validazione
finale), non solo verifica numerica come nello script già consegnato.

**Adattamento, non copia.** Dove la derivazione è indipendente dalla
dimensione del registro (lettura dell'ancilla, gate controllati/anti-
controllati, motivo per cui $U(t)$ non va controllato) il documento
richiama il risultato del dimero invece di ripeterlo. Due sezioni sono
riscritte da zero perché il salto a $N=3$ introduce differenze reali, non
solo di notazione:

1. **Il caso interessante: quando lo spalmamento non succede.** Invece di
   ripetere l'espansione di Heisenberg a breve tempo su tutti i $4^3=64$
   prodotti di Pauli (combinatoria che non aggiungerebbe comprensione, solo
   lunghezza), il documento usa come esempio guida lo zero strutturale del
   sito 3 per ogni $t$ (già dimostrato in
   `simmetrie_correlatori_trimero_anello.tex`): il sito 3, punto fisso della
   simmetria $U_\text{anello}$, non ha equivalente nel dimero (dove ogni
   sito viene scambiato) — un tipo di annullamento strutturale
   genuinamente nuovo per $N=3$, non solo "più della stessa cosa".
2. **Il blocco $U(t)$: Trotter a due livelli annidati.** Sezione nuova,
   assente nel dimero per costruzione: $H_{ex}$ e $H_{DM}$ (Opzione B),
   essendo ciascuno somma di tre legami che condividono qubit a due a due
   (i.e. la chiusura ad anello, non l'equilateralità o la frustrazione —
   punto già chiarito in `trimero_anello_frustrazione_e_chiralita.tex`),
   richiedono ciascuno un Trotter interno, oltre al Trotter esterno fra
   $H_0$ e $H_{DM}$ già presente nel dimero. Tre livelli di errore
   annidati invece di uno, richiamando la derivazione completa in
   `quantum_simulation_trimero_anello_teoria.tex` (operatore di chiralità
   di spin scalare, formula chiusa dell'errore di livello 1) invece di
   ripeterla.

**Figure prodotte** (generate da script Python dedicati, dati dalla
validazione già effettuata, non placeholder):
- diagramma schematico del circuito ($C_{12}^{yy}(t)$, $U(t)$ come box
  opaco, mirror del diagramma del dimero);
- convergenza Trotter $C_{11}^{yy}(t{=}1.3)$ vs $N$ (conferma visiva
  $\sim1/N$);
- validazione continua $C_{11}^{yy}(t)$ su un intervallo di $t$ (circuito
  vs esatto classico, Re e Im);
- zero strutturale del sito 3, $C_{33}^{xz}(t)$, su un intervallo continuo
  di $t$ (non solo nei tre punti già testati) — mostra visivamente che
  l'annullamento è per ogni $t$, non un caso isolato di $t=0$.

**Compilazione**: due passate `pdflatex`, zero errori, zero
overfull/underfull dopo correzioni (due spezzature di parola a metà
causate da `\seqsplit` su nomi di file lunghi — stesso tipo di problema
cosmetico già risolto altrove nel progetto — sostituite con interruzione
di riga manuale; un errore fatale di font expansion di `microtype` con
`tcolorbox`, risolto con `\microtypesetup{expansion=false}`). 10 pagine.

**File prodotti:** `circuito_correlazioni_trimero_anello_spiegato.tex`
(+ pdf compilato), `generate_figures_circuito_trimero_anello.py`,
`generate_circuit_fig_trimero_anello.py` (script di generazione figure,
riusabili se il punto di lavoro o i casi d'esempio cambiassero).

**Aperto per il seguito:** validazione a shot finiti; scan sistematico
delle 81 combinazioni via circuito effettivo; derivazione principiata del
punto Trotter $R_0$; Fase 5 (VQE con DM) per la catena aperta — invariato
rispetto a sopra.

## Aggiornamento — validazione a shot finiti del circuito delle correlazioni (trimero anello)

Quarto passo della fase correlazioni dinamiche per N=3: validazione a rumore
statistico finito, mirror per N=3 di `circuito_correlazioni_tutte.ipynb`
(dimero) — finora il circuito era stato validato solo su statevector esatto
(nessun rumore di shot).

**Metodologia.** `AerSimulator()` (shot-based, non statevector); stima
$\langle\sigma_z^{anc}\rangle=(n_0-n_1)/N_\text{shots}$ da conteggi, per le
due esecuzioni separate (Re e Im) di ciascun correlatore. Nota tecnica:
`AerSimulator.run()` su un circuito con `prepare_state` non transpilato
fallisce (`AerError: unknown instruction: state_preparation`) — richiede
`transpile(qc, backend)` prima dell'esecuzione. Cache di transpilazione
(`_TRANSPILE_CACHE`, chiave su tutti i parametri del circuito) per evitare
di ritranspilare l'intero circuito Trotter a $N=200$ passi a ogni chiamata
— porta il tempo totale dello script a $\sim44$ s.

**Punto di lavoro**: quello confermato per le correlazioni ($J{=}1,J'{=}0.4,
b{=}b_c{=}2.4,D{=}0.15$, Opzione B), $N=200$ passi di Trotter (stesso $N$
già usato per la validazione a statevector).

**Tre correlatori rappresentativi** (esatto classico / statevector $N=200$ /
shots $N=200$, $8192$ shots, seed fisso): $C_{11}^{yy}(t{=}1.3)$,
$C_{33}^{xz}(t{=}2.7)$ (atteso $\approx0$, zero strutturale del sito 3),
$C_{12}^{yy}(t{=}2.7)$ — tutti concordano entro l'ordine di grandezza atteso
dal rumore statistico a $8192$ shots.

**Risultato quantitativo centrale — separazione dei due errori (Trotter vs
statistico), stesso confronto già fatto per il dimero (R1):**

| quantità | valore |
|---|---|
| errore di Trotter ($N=200$, statevector vs esatto) | $7.08\times10^{-4}$ |
| soglia statistica nel caso peggiore, $1/\sqrt{8192}$ | $0.0110$ |
| rapporto (statistico / Trotter) | $\sim15.6\times$ |

**Conclusione, opposta a quella del dimero**: qui l'errore statistico
**domina** nettamente su quello di Trotter (fattore $\sim16$), l'esatto
contrario del regime R1 del dimero (dove il Trotter dominava di oltre
$30\times$). Non è una conferma dello stesso pattern, ma un risultato
distinto — a $N=200$ il Trotter è già ben oltre il punto di convergenza
necessario, mentre il rumore di campionamento a $8192$ shots resta il
collo di bottiglia. Implicazione pratica: con questo numero di shots, non
avrebbe senso spingere $N$ molto oltre 200 senza anche aumentare gli shots.

**Convergenza vs $N_\text{shots}$** (stesso correlatore, $256\to16384$
shots, $40$ ripetizioni indipendenti per punto): la deviazione standard
misurata segue l'andamento atteso $\sim1/\sqrt{N_\text{shots}}$ (es. a
$256$ shots: dev.std $=0.0523$ vs atteso $0.0625$; a $16384$: $0.0066$ vs
$0.0078$), con la media che converge visibilmente al valore esatto
classico ($+0.4521$) al crescere del numero di shots.

**File prodotti:** `validate_shot_noise_trimero_anello.py`,
`generate_figure_shotnoise.py` (produce `fig_shot_trimero.png`, grafico di
convergenza con barre d'errore e banda $\pm1/\sqrt{N_\text{shots}}$).

**Documento pedagogico aggiornato**: aggiunta la sottosezione "Validazione
a shot finiti: quale errore domina?" a
`circuito_correlazioni_trimero_anello_spiegato.tex` (tabella di confronto,
box con la conclusione opposta al dimero, nuova Fig. 4). Ricompilato,
zero errori, un solo underfull hbox cosmeticamente trascurabile
(badness 1735), 11 pagine.

**Aperto per il seguito:** scan sistematico delle 81 combinazioni via
circuito effettivo (ora estendibile sia a statevector sia a shot finiti);
derivazione principiata del punto Trotter $R_0$; Fase 5 (VQE con DM) per
la catena aperta — invariato rispetto a sopra, tolta la voce shot-noise
(completata qui).

## Aggiornamento — scan sistematico delle 81 combinazioni via circuito effettivo (trimero anello)

Quinto passo della fase correlazioni dinamiche per N=3: esteso a **tutte e
81** le combinazioni $(i,j,\alpha,\beta)$ lo scan finora fatto solo su 6
casi rappresentativi (statevector) e 3 casi (shot finiti) — misurando
ciascuna **via circuito vero e proprio** (non più solo classicamente),
sia a statevector esatto sia a shot finiti ($8192$ shots), allo stesso
punto di lavoro confermato ($J{=}1,J'{=}0.4,b{=}b_c{=}2.4,D{=}0.15$,
Opzione B), $t=1.3$, $N=200$.

**Nota sullo scan precedente**: lo scan delle 81 combinazioni era già
stato fatto in `simmetrie_correlatori_trimero_anello.tex`, ma **solo per
via classica** (algebra/`expm`), per identificare quali fossero
strutturalmente nulle. Questo è il primo scan completo che passa per il
circuito quantistico reale su tutte e 81, non solo su un sottoinsieme.

**Risultati principali:**
- **I quattro zeri strutturali** predetti dal Corollario del sito fisso
  ($C_{33}^{xz},C_{33}^{zx},C_{33}^{yz},C_{33}^{zy}$) sono confermati
  esattamente — né un quinto zero "spurio", né uno dei quattro previsti
  che risulti in realtà non nullo. Massimo $|C|$ misurato fra questi:
  $2.6\times10^{-3}$ a statevector (coerente con solo errore di Trotter),
  $2.2\times10^{-2}$ a shot finiti (coerente con solo rumore statistico).
- **Errori uniformemente piccoli su tutte le 81** (non solo sui 6/3 casi
  già visti): errore di Trotter medio $8.8\times10^{-4}$, massimo
  $2.6\times10^{-3}$; errore statistico medio $1.4\times10^{-2}$, massimo
  $3.7\times10^{-2}$ — nessun caso patologico isolato.
- **Risultato nuovo, non previsto dalla sola analisi di simmetria**:
  $C_{33}^{zz}(t{=}1.3)\approx0.9995$ — l'autocorrelazione
  $\langle\sigma_3^z(t)\sigma_3^z(0)\rangle$ è quasi congelata. Nessuna
  delle simmetrie derivate lo impone: è un fatto dinamico specifico del
  punto di lavoro (DM piccolo rispetto a scambio/campo, $\sigma_3^z$
  quasi conservato) — un'osservazione fisica ulteriore rispetto a
  quanto richiesto dalla sola validazione del circuito.
- Fra i correlatori non banali, i più intensi sono le coppie sito-1/sito-3
  ($|C_{31}^{zx}|,|C_{13}^{xz}|\approx0.663$), non le autocorrelazioni del
  sito 1 usate come esempio pedagogico principale nel documento.

**Figura prodotta**: heatmap $9\times9$ di $|C_{ij}^{\alpha\beta}(t{=}1.3)|$
(righe/colonne raggruppate per sito, separatori bianchi), con i quattro
zeri strutturali evidenziati da un riquadro rosso — visivamente confermano
di cadere esattamente nel blocco $(3,3)$ previsto.

**File prodotti:** `scan81_trimero_anello.py` (scan completo, cache di
transpilazione, $\sim4.5$ minuti di esecuzione per le 81 combinazioni×2
esecuzioni(statevector)+2 esecuzioni(shots)), `generate_figure_scan81.py`
(produce `fig_scan81_trimero.png`), `scan81_results.npz`/`.json` (risultati
completi salvati per riuso).

**Documento pedagogico aggiornato**: aggiunta la sottosezione "Scan
sistematico delle 81 combinazioni, via circuito effettivo" a
`circuito_correlazioni_trimero_anello_spiegato.tex` (Sez. 8.1), con
tabella degli errori aggregati e la nuova Fig. 6. Ricompilato, zero
errori, stesso unico underfull hbox cosmetico già presente prima
(badness 1735), 13 pagine.

**Aperto per il seguito:** derivazione principiata (stile $R_1$ del
dimero) del punto Trotter dimostrativo $R_0$ del trimero; rumore di gate
reale (Parte 2 della tesi); Fase 5 (VQE con DM) per la catena aperta —
tolta la voce "scan sistematico delle 81 combinazioni" (completata qui).

## Aggiornamento — tre notebook della fase correlazioni, trimero anello (mirror del dimero)

Sesto passo della fase correlazioni dinamiche per N=3: costruiti i tre
notebook Jupyter che mirrorano, per il trimero anello, la struttura già
usata per il dimero (`circuito_correlazioni_tutte.ipynb`) — eseguiti per
intero (non solo listati di codice), con output reali salvati nel file.
Su richiesta esplicita di Samuele, tutta la logica pesante è riusata per
import dai moduli `.py` già scritti e validati
(`circuito_correlazioni_trimero_anello.py`,
`validate_circuito_correlazioni.py`, `trotter_trimero_anello.py`,
`trimer_ring_exact.py`) invece di essere riscritta nei notebook.

**`correlazioni_trimero_anello_simmetria.ipynb`** — mirror computazionale
di `simmetrie_correlatori_trimero_anello.tex`: verifica passo per passo
(non solo teoria) che $S_z^{tot}$ non è conservato, che $U_\text{naive}$
fallisce, che $U_\text{anello}=\mathrm{SWAP}_{12}\cdot(R_z(\pi))^{\otimes3}$
commuta con $H$ (anche su 20 punti casuali), il Lemma sui 9 operatori di
sito, i quattro zeri strutturali a precisione macchina, gli zeri a $t=0$
da time-reversal, e lo scan completo delle 81 combinazioni via formula
spettrale (non via circuito — quello è nel terzo notebook).

**`correlazioni_trimero_anello_esplorazione.ipynb`** — mirror di
`circuito_correlazioni_tutte.ipynb` del dimero nella parte "circuito":
disegno del circuito, validazione su 6 casi rappresentativi (statevector
vs classico esatto), convergenza Trotter, un confronto shot-vs-Trotter.
Nessuna riderivazione delle simmetrie (rimanda al primo notebook e al
`.tex`).

**`circuito_correlazioni_trimero_anello_tutte.ipynb`** — mirror snello:
misura diretta (non dedotta per simmetria) di tutte le 81 combinazioni via
circuito a $t=1.3,N=200$, heatmap $9\times9$ con i quattro zeri
strutturali evidenziati, una vista d'insieme nel tempo (griglia
$9\times9$, deliberatamente ridotta a $N=100$/8 punti di $t$ per non
appesantire l'esecuzione — scelta dichiarata esplicitamente nel notebook,
non un limite nascosto), un selettore manuale (niente `ipywidgets`, bug di
rendering già noto in questo ambiente), l'analisi escursione/simmetria/
spettro, e un confronto finale con lo scan a shot finiti precomputato da
`scan81_trimero_anello.py` (non ricalcolato nel notebook, per evitare di
ripetere ~4-5 minuti di esecuzione).

**Bug incontrato e risolto durante la costruzione (degno di nota
metodologico).** Lo script generatore del terzo notebook costruisce il
testo delle celle dentro stringhe Python non-raw; una riga con `\beta` e
`\alpha` destinati a comparire letteralmente nel LaTeX della cella è stata
consumata come sequenza di escape Python (`\b`=backspace, `\a`=bell) **due
volte, in due punti distinti**: una volta nello script generatore
(backslash singolo invece di doppio, corretto raddoppiandolo) e una
seconda volta, indipendentemente, nel codice generato stesso — un
f-string non raw, `f"...\alpha\beta..."`, che il kernel Jupyter
reinterpreta come escape al momento dell'esecuzione della cella, non solo
in fase di scrittura del file (corretto rendendo la f-string raw,
`rf"..."`). Errore silenzioso — non un traceback all'origine ma un
`ParseException` di matplotlib mathtext a valle, con lettere mancanti nel
titolo del grafico (`lpha`, `eta` invece di `alpha`, `beta`) come unico
indizio: utile da ricordare per il seguito, ogni volta che si genera
codice Python contenente LaTeX via uno script wrapper.

**Esecuzione**: tutte e tre le celle eseguite senza errori (verificato
iterando su tutti gli output di tutte le celle), risultati numerici
coerenti con quanto già misurato negli script standalone (es. rapporti di
simmetria $C_{11}^{\alpha\beta}/C_{22}^{\alpha\beta}$ entro qualche punto
percentuale da $\eta_\alpha\eta_\beta=\pm1$, coerente col rumore della
griglia ridotta $N=100$/8 punti usata in quella sezione).

**Nota sulla consegna, valida da qui in avanti**: su richiesta di
Samuele, niente più compilazione PDF (solo sorgenti `.tex`, per non
consumare token) e i file testuali (`.tex`, `.py`, `.ipynb`) vengono
salvati nel Project (`project_write`, consultabili senza bisogno di
scaricarli) invece che solo allegati in chat, perché il download diretto
degli allegati non funziona dal suo client.

**File prodotti (salvati nel Project):**
`correlazioni_trimero_anello_simmetria.ipynb`,
`correlazioni_trimero_anello_esplorazione.ipynb`,
`circuito_correlazioni_trimero_anello_tutte.ipynb`.

**Problema di consegna file allegati (`.ipynb`/`.tex`/`.py`) — aperto,
non risolto, workaround rifiutato da Samuele.** Samuele riceve
"Impossibile aprire il file" scaricando notebook/`.py`/`.tex` da un
allegato in chat — problema comparso da quando (su sua stessa richiesta)
si è smesso di compilare i `.tex` in PDF: prima i documenti tex arrivavano
sempre anche come PDF compilato (che apriva senza problemi), i sorgenti
grezzi invece no. Primo tentativo: esportare ogni file anche in **HTML
autonomo** (`nbconvert`/`pandoc`/`pygments`, zero token — conversione
locale, non ricompilazione) — confermato apribile per i notebook, ma
**Samuele l'ha esplicitamente rifiutato come soluzione** ("non voglio gli
html") e ha chiesto di segnalare il problema "a chi di dovere" invece di
aggirarlo lato mio. **Nessun meccanismo disponibile per aprire un ticket
verso l'infrastruttura Anthropic per conto suo** — indicato a Samuele di
usare il pulsante di feedback (thumbs down) o support.claude.com per
segnalarlo direttamente lui.

**Decisione operativa, valida da qui in avanti**: niente più conversioni
HTML di cortesia non richieste. I file continuano a essere salvati nel
Project (fonte primaria, consultabile senza download) e/o allegati in
chat come `.tex`/`.py`/`.ipynb` grezzi come sempre fatto finora; Samuele
gestisce da sé, con copia-incolla, i casi in cui il download/apertura
dell'allegato non funziona.

**Aperto per il seguito:** derivazione principiata (stile $R_1$ del
dimero) del punto Trotter dimostrativo $R_0$ del trimero; rumore di gate
reale (Parte 2 della tesi); Fase 5 (VQE con DM) per la catena aperta —
invariato rispetto a sopra.

## Aggiornamento — documento di catalogazione della fase correlazioni (trimero anello)

Creato `trimero_anello_correlazioni.tex`, stesso stile di
`trimero_anello_quantum_simulation.tex` (un `\section*` per file: cosa fa,
funzioni interne, come si usa, verifiche, conclusione) — riferimento unico
per ritrovare rapidamente cosa fa ciascun file della fase correlazioni
dinamiche del trimero anello: `simmetrie_correlatori_trimero_anello.tex`,
`circuito_correlazioni_trimero_anello.py`,
`validate_circuito_correlazioni.py`,
`circuito_correlazioni_trimero_anello_spiegato.tex` (+ script figure),
`validate_shot_noise_trimero_anello.py` + `generate_figure_shotnoise.py`,
`scan81_trimero_anello.py` + `generate_figure_scan81.py`, e i tre notebook
(`correlazioni_trimero_anello_simmetria.ipynb`,
`correlazioni_trimero_anello_esplorazione.ipynb`,
`circuito_correlazioni_trimero_anello_tutte.ipynb`).

Non compilato in PDF (regola "solo `.tex`" tuttora valida) — solo sorgente,
salvato nel Project.

## Aggiornamento — bug percorso assoluto in `scan81_trimero_anello.py` (secondo giro)

Samuele ha eseguito lo script sulla propria macchina e ottenuto
`FileNotFoundError` su `np.savez('/home/claude/thesis_work/scan81_results.npz', ...)`
in fondo allo script — il calcolo numerico era corretto (valori coerenti
con quanto già noto), il crash era solo sul salvataggio finale. Causa:
la copia incollata da Samuele conteneva ancora il percorso assoluto del
mio sandbox (`/home/claude/thesis_work/...`), non valido sulla sua
macchina — bug già corretto una volta in questa sessione ma non ancora
recepito lato Samuele, che lavora per copia-incolla manuale (vedi sopra).
Corretto di nuovo, qui e nel Project, a percorsi relativi:
```
np.savez('scan81_results.npz', ...)
...
with open('scan81_results.json', 'w') as f:
```
Diff comunicato a Samuele in chiaro (le due righe, prima/dopo) per
permettergli di patchare la propria copia senza dover ricopiare tutto lo
script.

## Aggiornamento — VQE reale nel circuito dei correlatori (trimero anello)

Chiusa la pipeline VQE→correlazioni con il circuito effettivo, sostituendo
lo stand-in a ampiezze esatte (`prepare_state`) usato finora — mirror
dell'analoga chiusura già fatta per il dimero.

**Scoperta preliminare:** i file `vqe_trimer_ring_W.py` e affini, descritti
a lungo in `trimero_anello_vqe.tex`/`trimero_anello_vqe_dm.tex`, **non
esistono** come moduli separati nel Project (confermato da un
`project_read` fallito, con l'elenco completo dei doc disponibili in
risposta). Il codice reale dell'ansatz vive dentro due notebook,
`confronto_ansatz_entangler_trimero_anello.ipynb` e
`analisi_espressivita_PMA_anello.ipynb`. Creato quindi un modulo nuovo,
`vqe_w2q6_trimero_anello.py`, che isola la costruzione dell'ansatz
`W-2q.6` (`pma_2q_trimer_exact(6, w_block)`, blocco
`CNOT`–$R_y(\theta)$–`CNOT`, bond `BOND12=(2,1)`, `BOND23=(1,0)`,
`BOND31=(0,2)`) in un file riusabile, così da non dipendere da import di
notebook.

**Ottimizzazione VQE** (multistart COBYLA, 12 partenze casuali seed
fissato, + polish L-BFGS-B) al punto di lavoro confermato $J=1$, $J'=0.4$,
$b=b_c=2.4$, $D=0.15$ (Opzione B): tutte le 12 partenze convergono allo
stesso punto, $E_{vqe}=-5.53437001739340$ vs $E_{esatto}=-5.53437001739350$
($\Delta E=9.8\times10^{-14}$), fidelity $\mathcal F=0.99999999999961$ —
coerente con il valore già presente in
`trimer_ansatz_sweep_cache_v2.json` (voce `"DM|W-2q.6|2.4"`), che però
non conservava il vettore dei parametri ottimali (solo metriche
scalari) — da qui la necessità di rieseguire l'ottimizzazione. Parametri
salvati in `w2q6_params_optimal.npz`.

**Integrazione nel circuito.** Modificato
`circuito_correlazioni_trimero_anello.py`: `build_correlator_circuit` e
`correlator_from_circuit` accettano ora un argomento opzionale
`ansatz_params` — se `None` (default), preparazione invariata via
`prepare_state`; se fornito (i 6 parametri), preparazione via il circuito
reale `w2q6_circuit()` composto sul registro. Nessuna modifica al
comportamento di default (retrocompatibile con tutto il codice esistente:
`scan81_trimero_anello.py`, `validate_shot_noise_trimero_anello.py`,
i tre notebook).

**Validazione** (`validate_vqe_circuito_correlazioni.py`, nuovo file):
confronto sistematico delle 81 combinazioni $C_{ij}^{\alpha\beta}(t)$,
preparazione VQE reale vs preparazione esatta — errore medio
$3.0\times10^{-7}$, massimo $8.3\times10^{-7}$ (su $C_{21}^{zz}$), come
atteso dell'ordine di $\sqrt{1-\mathcal F}$. Nessuna discrepanza
anomala; la sostituzione è validata su tutte le combinazioni, non solo
su un sottoinsieme.

**Documentazione aggiornata:** rimosso il linguaggio "stand-in" da
`circuito_correlazioni_trimero_anello_spiegato.tex` (aggiunta la
sottosezione con risultato dell'ottimizzazione e della validazione) e da
`trimero_anello_correlazioni.tex` (nuova sezione per i due file nuovi,
conclusione generale aggiornata).

File nuovi di questa milestone: `vqe_w2q6_trimero_anello.py`,
`validate_vqe_circuito_correlazioni.py`, `w2q6_params_optimal.npz`
(quest'ultimo dato binario, non salvato nel Project — rigenerabile
eseguendo `vqe_w2q6_trimero_anello.py`).

**Aperto per il seguito:** derivazione principiata (stile $R_1$ del
dimero) del punto Trotter dimostrativo $R_0$ del trimero; rumore di gate
reale (Parte 2 della tesi); Fase 5 (VQE con DM) per la catena aperta —
invariato rispetto a sopra.

## Aggiornamento — manuali d'uso e quarto notebook (chiusura VQE reale, trimero anello)

Completata la documentazione pratica della milestone precedente (VQE reale
nel circuito dei correlatori), su richiesta esplicita di Samuele.

**Due manuali d'uso** (nuovi), uno per versione, entrambi `.tex`,
struttura: Scopo, Prerequisiti, Passi numerati con comandi/output attesi,
Problemi comuni, Riferimenti:
- `manuale_uso_correlazioni_trimero_anello_statevector.tex` — versione a
  preparazione esatta (`prepare_state`), invariata; copre i quattro script
  standalone della fase in ordine d'uso (validazione classica, shot noise,
  scan81, figure).
- `manuale_uso_correlazioni_trimero_anello_vqe.tex` — versione attuale
  (ansatz VQE reale `W-2q.6`); copre in più il passo di ottimizzazione
  (`vqe_w2q6_trimero_anello.py`, con l'avviso che i parametri vanno
  rigenerati se cambia il punto di lavoro $J,J',b,D$) e la validazione
  incrociata (`validate_vqe_circuito_correlazioni.py`); nota esplicita
  sulla retrocompatibilità (`ansatz_params=None` invariato).

**Quarto notebook** (nuovo), `circuito_correlazioni_trimero_anello_vqe.ipynb`
— Samuele ha fatto notare che le tre notebook esistenti della fase usano
tutte `prepare_state`, nessuna mostra la pipeline con l'ansatz VQE reale.
A differenza delle prime tre (mirror diretto delle notebook del dimero),
questo non ha un equivalente nel dimero: documenta specificamente la
chiusura VQE→correlazioni per il trimero anello. Contenuto: ottimizzazione
inline dell'ansatz `W-2q.6` (stessi 12 multistart + polish, stesso
risultato $\mathcal F=0.99999999999961$), le 81 correlazioni ricalcolate
con preparazione VQE vs esatta (stessi numeri di
`validate_vqe_circuito_correlazioni.py`: errore medio $3.0\times10^{-7}$,
massimo $8.3\times10^{-7}$), heatmap $9\times9$ del residuo in scala
logaritmica (verificata visivamente: range $\sim10^{-9}$--$10^{-6.5}$,
nessuna anomalia). 12 celle, eseguite senza errori.

`trimero_anello_correlazioni.tex` aggiornato di conseguenza (sezione
notebook rinominata "Quattro notebook...", nuovo paragrafo descrittivo,
"Come si usano"/"Verifiche"/"Conclusione" aggiornati).

**Aperto per il seguito:** invariato rispetto a sopra.

## Aggiornamento — quarto notebook esteso a mirror completo di "tutte" (trimero anello)

Samuele ha fatto notare che la versione precedente del quarto notebook (solo
ottimizzazione + confronto 81 combinazioni + un heatmap del residuo) non era
un vero equivalente di `circuito_correlazioni_trimero_anello_tutte.ipynb`:
mancavano heatmap di $|C|$, griglia $9\times9$ nel tempo, selettore,
simmetria, spettro, confronto shot noise. Confermato via
`AskUserQuestion` di rifare il mirror completo.

**`circuito_correlazioni_trimero_anello_vqe.ipynb` riscritto** (stesso
nome, contenuto sostituito): ora rispecchia tutte e otto le sezioni del
terzo notebook, con la preparazione VQE (`ansatz_params`) al posto di
`prepare_state` ovunque, precedute da una sezione 0 di ottimizzazione
dell'ansatz (stesso schema: 12 multistart COBYLA + polish, stesso
risultato $\mathcal F=0.99999999999961$). 28 celle, eseguite senza
errori. Risultati verificati: heatmap $|C|$ con gli stessi quattro zeri
strutturali evidenziati e la stessa cella $C_{33}^{zz}$ dominante;
griglia $9\times9$ nel tempo visivamente indistinguibile dalla versione
esatta; simmetria $C_{11}/C_{22}=\eta_\alpha\eta_\beta$ confermata entro
$\pm3\%$ su tutte e nove le coppie $(\alpha,\beta)$; spettro
ricco/piatto invariato (è teoria pura, indipendente dalla preparazione);
errore totale (Trotter+VQE) medio $8.81\times10^{-4}$, massimo
$2.64\times10^{-3}$ — indistinguibile da quello della versione a stato
esatto.

**File nuovo:** `scan81_vqe_trimero_anello.py` — mirror di
`scan81_trimero_anello.py` con preparazione VQE, richiesto dalla Sez. 7
del notebook (confronto con lo scan a shot finiti); richiede
`w2q6_params_optimal.npz` già presente. Eseguito una volta per generare
`scan81_vqe_results.npz`/`.json` (dati binari/derivati, non salvati nel
Project — rigenerabili eseguendo lo script). Errore statistico (shot vs
statevector) medio $1.33\times10^{-2}$, massimo $3.33\times10^{-2}$ —
stesso ordine di grandezza della versione a stato esatto, rumore
statistico ancora dominante sull'errore di Trotter e sul residuo VQE.

**Problema tecnico incontrato:** la prima versione del notebook riscritto
(736 KB, griglia $9\times9$ a `figsize=(11,11), dpi=70`) ha fatto
superare il tetto del Project (2.137M contro il limite di 2M) al momento
del salvataggio — lo stesso problema di dimensione già incontrato con le
prime tre notebook. Risolto riducendo la griglia a `figsize=(8,8),
dpi=45` (416 KB, verificato ancora leggibile) e ripetendo il pattern
`project_delete` + `project_write` per far scendere davvero il totale
sotto il tetto prima di aggiungere il nuovo file
`scan81_vqe_trimero_anello.py`.

`trimero_anello_correlazioni.tex` aggiornato di conseguenza (paragrafo
del quarto notebook riscritto per descrivere il mirror completo,
"Come si usano"/"Verifiche"/"Conclusione" aggiornati con i nuovi numeri).

**Aperto per il seguito:** invariato rispetto a sopra.

## Aggiornamento — manuale d'uso VQE allineato al quarto notebook completo

`manuale_uso_correlazioni_trimero_anello_vqe.tex` era rimasto fermo alla
versione precedente del quarto notebook: non citava
`scan81_vqe_trimero_anello.py` né il notebook esteso, e "Cosa NON cambia"
parlava ancora di "tre notebook". Aggiunto un Passo 4 (scan completo,
mirror del Passo 4 del manuale gemello) e una sezione "Come esplorare
tutto insieme" che rimanda al notebook come percorso rapido per farsi
un'idea complessiva senza lanciare gli script uno per uno; aggiornati
prerequisiti, problemi comuni (`FileNotFoundError` su
`scan81_vqe_results.npz`) e il riferimento ai "tre notebook" (ora
esplicitamente "i primi tre... che usano ancora `prepare_state`").

**Aperto per il seguito:** invariato rispetto a sopra.

## Aggiornamento — due relazioni .docx per il trimero anello (stile Samuele)

Samuele ha allegato due relazioni .docx già scritte per il dimero
(`relazione_test_parametri.docx`, `relazione_correlazioni.docx`) e ha
chiesto l'equivalente per il trimero, stesso font (Times New Roman),
stessa dimensione (corpo 11pt, didascalie 9.5pt corsivo centrato), stessa
impostazione (nessun titolo, testo giustificato, tono diretto in prima
persona da studente, non da relazione accademica formale).

Chiarito con l'utente quale contenuto abbinare (via AskUserQuestion, non
ovvio 1:1 col dimero): relazione 1 = ottimizzazione e test del circuito
VQE reale W-2q.6 (lavoro di questa sessione, dati e figure già pronti);
relazione 2 = correlazioni dinamiche trimero anello (mirror diretto di
`relazione_correlazioni.docx`, scan81/simmetrie/ricco-piatto/chiusura
VQE). Scartata l'alternativa (Trotter/ricerca del punto R0) perché le
figure originali di quella fase (Aug 22) non sono più disponibili — solo
il testo tex sopravvive, sul disco locale non c'erano i PNG.

**File prodotti** (consegnati via SendUserFile, non salvati nel Project
per non far esplodere il tetto di dimensione con le immagini incorporate):
- `relazione_vqe_trimero_anello.docx` — circuito dell'ansatz (versione
  scomposta CNOT-Ry-CNOT), ottimizzazione (12 multistart, tutti convergenti
  allo stesso minimo, F=0.99999999999961), tabella delle 5 combinazioni
  con residuo maggiore fra preparazione VQE ed esatta, heatmap del
  residuo log10 sulle 81 combinazioni, domanda aperta al relatore su
  se F=1 sia specifico di questo punto o generale nella regione DM.
- `relazione_correlazioni_trimero_anello.docx` — scan81 con esempi
  ricco/piatto (C_11^yy, C_33^zz con nota sulla scala verticale),
  heatmap |C| con i quattro zeri strutturali, griglia 9x9 nel tempo,
  scoperta C_33^zz≈0.9995, nota onesta sul residuo peggiore che cade su
  uno zero strutturale, chiusura VQE, domanda aperta al relatore su quale
  correlatore usare come primo banco di prova per il rumore (Parte 2).

**Metodo:** letti i due docx di riferimento con pandoc (testo) e ispezione
diretta di `word/document.xml`/`styles.xml` (font, dimensioni, spaziature,
bordi tabella) per replicare esattamente lo stile, non solo il tono.
Figure riusate da notebook già eseguiti in questa sessione dove possibile
(`circuito_correlazioni_trimero_anello_tutte.ipynb`) per evitare ricalcoli;
rigenerate solo le due mancanti (circuito ansatz, heatmap residuo VQE).
Documenti costruiti con `docx` (npm) via script Node, verificati
convertendoli in PDF/JPEG e ispezionando visivamente ogni pagina.

## Aggiornamento — correzione formattazione matematica nei due .docx del trimero

Samuele ha segnalato che le formule nei due report appena consegnati erano
scritte come testo ASCII semplice (es. la stringa letterale `C_ij^αβ(t)`)
invece che con la formattazione matematica reale di Word (corsivo sulle
lettere-variabile, apice/pedice veri), come nei documenti di riferimento
del dimero — non accettabile per un elaborato che deve leggersi come un
paper/libro di fisica.

**Causa:** gli script Node (`build_relazione_vqe.js`,
`build_relazione_correlazioni.js`) scrivevano ogni paragrafo come un unico
`TextRun` di testo piatto, senza mai usare le proprietà `italics`,
`subScript`, `superScript` del pacchetto `docx`.

**Convenzione estratta per confronto diretto dall'XML dei due riferimenti**
(`relazione_correlazioni.docx`, Calibri, uso estensivo di `w:vertAlign`;
`relazione_test_parametri.docx`, Times New Roman, zero formattazione
matematica — i suoi unici 6 tag `<w:i/>` sono le didascalie in corsivo,
non notazione fisica, coerente col fatto che quel report non contiene mai
indici/apici, solo rapporti semplici come b/J scritti in chiaro):
- lettera-variabile di base (C, a, b, D, J, N, t, k, E, F, σ, θ) → corsivo;
- indici in pedice (ij, 1, 2, k, c, anello, VQE, esatto) → pedice reale,
  non corsivo;
- componenti/esponenti in apice (αβ, xy, zz, vqe, esatto) → apice reale,
  non corsivo;
- lettere greche usate come etichette nude (α,β∈{...}) → testo semplice,
  non corsivo; i simboli dentro le graffe (x,y,z) restano corsivo in
  quanto valori rappresentativi della variabile;
- Δ maiuscolo → testo semplice, la lettera che segue (es. ΔE) → corsivo;
- numeri puri → testo semplice;
- nomi di gate (CNOT, Ry, RXX, RZZ) e identificatori di codice
  (`prepare_state`, nomi di file) → testo semplice, mai formule.

**Fix:** introdotto in entrambi gli script un mini-linguaggio di markup
(`*corsivo*`, `~pedice~`, `^apice^`, sequenziale non annidato) con un
parser (`parseMath`) che genera i `TextRun` corretti; applicato a ogni
formula nei paragrafi, nelle didascalie e nella tabella del report VQE
(intestazioni e valori di colonna *C*~ij~, αβ). Un solo conflitto di
delimitatore trovato e risolto: "~0.0015" (tilde come "circa") sostituito
con "≈0.0015" per non essere scambiato per un pedice.

Entrambi i file rigenerati, riconvertiti in PDF/JPEG e verificati
visivamente pagina per pagina (corsivo/pedice/apice ora corretti su tutte
le formule, tabella inclusa) prima di essere riconsegnati via SendUserFile.

## Aggiornamento — narrativa L-BFGS-B nella relazione VQE trimero anello: giustificazione numerica, letteratura, separazione tesi/riferimento personale

Su richiesta di Samuele, ripresa la menzione di L-BFGS-B in
`relazione_vqe_trimero_anello.docx` (già presente come nome nudo
dell'ottimizzatore) per motivarne l'uso in modo onesto: non solo
espandere l'acronimo, ma raccontare *cosa mancava*, *come la ricerca ha
portato alla soluzione*, e dichiarare esplicitamente l'uso di un
assistente AI per l'implementazione — mostrando comunque contezza del
problema fisico sottostante, verificato *prima* di cercare una soluzione.

### La domanda fisica: perché un residuo $\sim10^{-5}$ non è trascurabile

Richiesta esplicita di Samuele: una giustificazione numerica di come il
residuo di energia lasciato da COBYLA da solo ($\Delta E\sim10^{-5}$,
già documentato in `vqe_ground_state_test2.ipynb` per il dimero)
si propaghi come errore sulle osservabili a valle (i correlatori), non
solo un'affermazione qualitativa.

**Derivazione (bound spettrale + argomento di stazionarietà).** Per uno
stato variazionale $|\psi(\theta)\rangle=c_0|0\rangle+\sum_{n\geq1}c_n|n\rangle$
con fidelity $F=|c_0|^2$, il bound spettrale esatto è
$1-F\leq\Delta E/\Delta$, con $\Delta E=E(\theta)-E_0$ il residuo di
energia e $\Delta=E_1-E_0$ il gap al primo eccitato. Ponendo
$\varepsilon=\sqrt{1-F}$: l'errore sull'**energia** è $O(\varepsilon^2)$
(quadratico, per la stazionarietà variazionale — il gradiente dell'energia
si annulla al vero ground state), ma l'errore su un'osservabile
**generica** (come un correlatore di spin) è $O(\varepsilon)$ (lineare,
nessuna protezione da stazionarietà) — un residuo di energia "piccolo" può
quindi corrispondere a un errore molto più grande su qualunque altra
osservabile, che scala come la sua radice quadrata.

**Applicazione numerica al punto di lavoro** ($J=1,J'=0.4,b=b_c=2.4,D=0.15$,
Opzione B): gap vero $\Delta=0.2547$ (verificato indipendentemente in due
notebook del progetto — `correlazioni_trimero_anello_simmetria.ipynb` e
`correlazioni_trimero_anello_esplorazione.ipynb` — e derivabile anche da
`simmetrie_correlatori_trimero_anello.tex`). Con un residuo tipico
$\Delta E\approx10^{-5}$ lasciato da COBYLA da solo:
$1-F\leq4\times10^{-5}$, $\varepsilon\approx6\times10^{-3}$ — **tre ordini
di grandezza più grande** di $\Delta E$ stesso, e circa **4 volte più
grande** dell'ampiezza di oscillazione reale dell'autocorrelazione
$C_{33}^{zz}$ (circa 0.0015, dalla relazione sulle correlazioni): un
residuo di quella taglia coprirebbe completamente quel segnale fisico.

### Letteratura consultata per L-BFGS-B

- Byrd, Lu, Nocedal, Zhu (1995), *SIAM J. Sci. Comput.* 16(5), 1190–1208 —
  versione pubblicata di riferimento, **a pagamento**
  (epubs.siam.org/doi/10.1137/0916069).
- Zhu, Byrd, Lu, Nocedal (1997), *ACM TOMS* 23(4), 550–560 ("Algorithm
  778") — **a pagamento** (dl.acm.org/doi/10.1145/279232.279236).
- Un **preprint tecnico del 1994** (Argonne National Laboratory/
  Northwestern University), **liberamente leggibile** tramite un mirror
  Scispace — attenzione: ha **solo tre autori** (Byrd, Lu, Nocedal; Zhu si
  è aggiunto solo nella versione pubblicata del 1995/1997), quindi va
  citato come preprint preliminare, non come sostituto dell'articolo
  pubblicato.
- Pagina ufficiale del software L-BFGS-B di Nocedal: stesse referenze,
  nessun PDF libero, solo codice sorgente.

Distinzione dichiarata esplicitamente nel materiale di riferimento
personale (vedi sotto): il preprint gratuito e l'articolo pubblicato non
sono la stessa cosa (differiscono per autori e stato di revisione), onestà
bibliografica che vale la pena mantenere nella tesi.

### Decisione: dettagli implementativi fuori dalla tesi, dentro un riferimento personale

Su indicazione di Samuele ("eviterei di parlare di COBYLA, L-BFGS-B e
anche delle varie cache... sono dettagli implementativi e complicati per
una triennale"): la derivazione completa (bound spettrale, argomento
$O(\varepsilon)$ vs $O(\varepsilon^2)$, numeri, letteratura, nota di
disclosure sull'uso dell'AI, listato della funzione `vqe_multistart` reale)
è stata spostata in un documento **`.tex` a sé**,
`lbfgsb_giustificazione_teoria.tex` (compilato, 4 pagine, verificato
pagina per pagina) — dichiarato esplicitamente come **riferimento
personale e teoria di lavoro, non parte del testo della tesi**.

`relazione_vqe_trimero_anello.docx` è stato invece **semplificato**: tolta
ogni menzione di COBYLA, L-BFGS-B, cache o dettagli dell'ottimizzatore;
resta solo il risultato numerico finale (paragrafo sul multistart da punti
casuali, poi $E_\text{VQE}=-5.53437001739340$, $E_\text{esatto}
=-5.53437001739350$, $\Delta E=9.8\times10^{-14}$, $F=0.99999999999961$,
conclusione sulla robustezza della convergenza) — adatto al livello di una
triennale, senza perdere il risultato quantitativo.

**Due bug di formattazione trovati e corretti durante la QA visiva** (stesso
processo screenshot-per-pagina già usato per gli altri report): (1) un
trattino `~` usato nel testo per "circa" veniva interpretato dal parser
`parseMath` come delimitatore di pedice, comprimendo tutto il testo fra
due tilde in un unico pedice minuscolo — sostituito con "≈"/"circa"; (2)
il simbolo "≲" non è supportato dal font usato nel documento e ne
corrompeva silenziosamente il rendering (carattere e apice successivo
scomparsi) — sostituito con "≤" (già verificato renderizzare correttamente
altrove nello stesso documento).

### Nota sull'uso di un assistente AI (disclosure onesta)

Narrativa concordata con Samuele: prima ha derivato e verificato *lui
stesso* la propagazione dell'errore (il calcolo sopra, con i numeri del
proprio punto di lavoro), **poi** ha chiesto a un assistente AI se
esistesse una soluzione già pronta per il problema individuato — non il
contrario. L'implementazione dello stage L-BFGS-B (già presente nel
codice funzionante) è stata fatta implementare all'AI, ma la comprensione
del *perché* serva è di Samuele, verificabile dal calcolo sopra prima di
qualunque ricerca di soluzione. Disclosure di questo tipo inclusa nel
`.tex` di riferimento personale (non nella tesi, per lo stesso motivo di
livello sopra citato).

**File prodotti:** `lbfgsb_giustificazione_teoria.tex` (+ pdf compilato,
riferimento personale, non allegato alla tesi), `relazione_vqe_trimero_anello.docx`
(aggiornato/semplificato).

**Aperto per il seguito:** invariato rispetto a sopra.

## Aggiornamento — esplorazione interattiva "video e foto" del correlatore (trimero anello): due notebook + tool HTML standalone

Su richiesta di Samuele ("sarebbe molto interessante poter simulare il
video e la relativa foto: scelta con widgets della correlazione, scelta
del tempo t e vedere a lato la heatmap corrispondente... prova i widgets
come fatto per il dimero"), aggiunta un'esplorazione interattiva che lega
la curva $C_{ij}^{\alpha\beta}(t)$ nel tempo (il "video") alla heatmap
$9\times9$ a $t$ fissato (la "foto") già presenti separatamente nei
notebook del trimero anello (Sez. 4 e Sez. 3). Lavoro in due parti: prima
dentro i notebook Jupyter esistenti (via `ipywidgets`), poi — su richiesta
successiva di Samuele — anche come pagina HTML standalone indipendente da
Jupyter.

### Parte 1 — cella interattiva nei due notebook Jupyter

Aggiunta una nuova Sez. 5bis ("Video e foto insieme, interattivo") in
**entrambi** i notebook della fase (confermato via `AskUserQuestion`:
"Entrambi"): `circuito_correlazioni_trimero_anello_tutte.ipynb`
(preparazione esatta) e `circuito_correlazioni_trimero_anello_vqe.ipynb`
(preparazione VQE reale), inserita fra la Sez. 5 (selettore manuale) e la
Sez. 6 (analisi).

**Schema:** menu a tendina per le 81 combinazioni + slider per $t$, via
`ipywidgets.interactive_output` — schema **diverso** dai tre già
documentati come falliti in questo stesso progetto
(`FloatSlider`+`interact`, `FloatSlider`+`interact_manual`,
`Dropdown`+`interact`, bug noto dell'estensione VS Code
`jupyter-ipywidget-renderer`/`ipywidgetsKernel`), ripreso invece dal
pattern più difensivo già usato per il dimero in
`vqe_ground_state_test2.ipynb` (try/except sull'import, messaggio di
fallback). **Nessuna garanzia** che eviti lo stesso bug, mai confermato
risolto lato estensione — per questo la cella mostra sempre anche una
figura statica di esempio, e resta disponibile il fallback manuale
`_disegna_video_foto(combo_label, t)` per chiamata diretta. La heatmap si
ricalcola dal vivo con la formula **classica esatta** (`classical_exact`,
veloce), non con il circuito (troppo lento per seguire lo slider in tempo
reale).

**Validazione end-to-end con dati reali** (non stub), per entrambi i
notebook: eseguita l'intera pipeline in background (multi-minuto, incluso
il rilancio dell'ottimizzazione VQE per la seconda variante — fidelity
$\approx1$) e verificato che la nuova cella gira senza eccezioni e
produce output corretto (curve piatte sugli zeri strutturali, cella
$C_{33}^{zz}$ correttamente evidenziata). Entrambi i notebook aggiornati
salvati nel Project.

### Parte 2 — tool HTML standalone (`correlazioni_trimero_esplorazione.html`)

Samuele ha chiesto, in una richiesta successiva, di "mettere quella
esplorazione in un html" — una versione autonoma, non dipendente da
Jupyter/VS Code, per aggirare del tutto il rischio del bug `ipywidgets`
sopra. Confermato via `AskUserQuestion` di includere **entrambe** le
preparazioni (esatta e VQE) con un interruttore, non solo una.

**Design tecnico centrale:** la heatmap ("foto") non usa dati
precalcolati su una griglia fissa di $t$, ma **ricalcola dal vivo, nel
browser**, la formula classica esatta — un porting da zero in JavaScript
della piccola algebra lineare $8\times8$ complessa (prodotto di Kronecker
delle matrici di Pauli $2\times2$, evoluzione temporale via
autodecomposizione precalcolata in Python, $U(t)=V\,\mathrm{diag}
(e^{-iEt})\,V^\dagger$, embeddata come JSON). **Verificato** il porting
JS contro `classical_exact` di Python su più casi di test (incluso uno
zero strutturale e l'autocorrelazione quasi congelata): concordano a
precisione di macchina ($\sim10^{-15}$). La curva "video" è quindi anche
lei ricalcolata dal vivo per $t$ arbitrario, non su una griglia fissa;
solo i punti **misurati dal circuito reale** (Trotter, $N=100$, 16 punti
di $t$, per entrambe le preparazioni) restano precalcolati e sovrapposti
come riferimento, dato che simulare l'intero circuito quantistico nel
browser non sarebbe praticabile.

**Pipeline dati** (`compute_data.py`, $\sim15$ minuti di esecuzione):
ottimizzazione VQE (stesso schema a 12 restart + polish già validato) +
tutte le 81 correlazioni $\times$ 16 punti di $t$ $\times$ 2 preparazioni
via circuito reale, serializzate in `trimero_explore_data.json`
($\sim120$ KB) ed embeddate nella pagina.

**Design visivo** (seguendo le skill `artifact-design`/`dataviz` del
prodotto): palette dedicata (teal/ruggine per Re/Im, validata
CVD-sicura con lo script di validazione della skill dataviz — la coppia
teal/magenta usata nelle figure matplotlib esistenti falliva il check di
separazione per deuteranopia, ΔE 3.2 contro soglia 8; sostituita con
teal/ruggine, ΔE 11.0/9.3 a seconda del canale), accento oro "da
strumento" condiviso fra i controlli e l'evidenziazione della selezione
in heatmap, rampa sequenziale blu per il colore della heatmap, coppia
tipografica Newsreader/IBM Plex Sans/IBM Plex Mono, temi chiaro e scuro
entrambi progettati esplicitamente (non un'inversione automatica).

**Pubblicazione:** pagina pubblicata come Cowork Artifact (link
persistente, aggiornabile) e — dopo che Samuele ha segnalato di non avere
modo di scaricarla dall'artifact — consegnata anche come file `.html`
standalone via allegato, per garantire un download diretto indipendente
dall'artifact.

**Tre correzioni su segnalazione di Samuele, dopo la prima consegna:**
1. aggiunta l'ordinata (tacche numeriche + griglia orizzontale) al
   grafico "video", che prima mostrava solo l'asse dei tempi;
2. spostata la legenda della heatmap a lato invece che sotto, con
   l'aggiunta di una barra del gradiente colore (0→1) esplicita;
3. l'interruttore stato-esatto/VQE **funzionava già correttamente**, ma
   non c'era modo di vederlo: lo scarto fra le due preparazioni
   ($10^{-6}$–$10^{-7}$ per ogni correlatore) è troppo piccolo per
   spostare visibilmente la curva alla scala del grafico — è esattamente
   il punto fisico che il tool vuole dimostrare. Aggiunto un indicatore
   numerico dal vivo accanto all'interruttore (scarto massimo fra le due
   preparazioni per il correlatore scelto) così l'effetto del click resta
   verificabile quantitativamente anche quando non è visibile a occhio.

Entrambe le versioni (artifact e file scaricabile) rigenerate e risincronizzate
dopo le correzioni; verificate con screenshot automatizzati (Playwright) in
tema chiaro, scuro e a schermo stretto. Verificato anche, su richiesta
esplicita di Samuele prima di un possibile invio al relatore, che il file
non contenga alcun riferimento a "Claude"/"Anthropic"/tag di generazione
(controllo testuale su tutto il sorgente, nessuna occorrenza).

**File prodotti:** `correlazioni_trimero_esplorazione.html` (pagina
autonoma), `compute_data.py` (script di generazione dati, riusabile se il
punto di lavoro cambia), `trimero_explore_data.json` (dati serializzati).
Non salvati nel Project (file binari/derivati o non testuali secondo la
convenzione già in uso per questo tipo di output).

**Aperto per il seguito:** invariato rispetto a sopra (derivazione
principiata del punto Trotter $R_0$; rumore di gate reale, Parte 2; Fase 5
VQE con DM per la catena aperta).

## Aggiornamento — convenzione $J$ uniforme per la catena: già documentata, propagazione al DM da documentare

**Controllo fatto all'apertura della sessione catena/Fase 5.** Verificato che la
scelta di un **singolo $J$ uniforme** sui due legami della catena (contro
$(J,J')$ dell'anello isoscele) è già motivata in documentazione, non è una
convenzione implicita. Riferimenti puntuali, per non riscrivere quanto esiste:

- `teoria_trimero_catena_aperta.tex`, sez. Hamiltoniana (righe ~93–95):
  distinzione esplicita caso uniforme / caso generale $J_{12},J_{23}$.
- Idem, sez. "Simmetria di riflessione": Proposizione $J_{12}=J_{23}\Rightarrow
  [P_{13},H]=0$ con dimostrazione termine per termine e verifica numerica
  $8\times8$ nei due casi. Osservazione chiave: nella catena i due termini di
  scambio si scambiano *fra loro* sotto $P_{13}$ (nell'anello $P_{12}$ fissava
  la base e scambiava i laterali), quindi è proprio l'uguaglianza dei due
  coefficienti a rendere la somma invariante.
- Idem, righe ~176–183: il livello più profondo — con $J_{12}\neq J_{23}$ si può
  ancora raccogliere $\mathbf s_2\cdot(J_{12}\mathbf s_1+J_{23}\mathbf s_3)$, ma
  $J_{12}\mathbf s_1+J_{23}\mathbf s_3$ **non è un operatore di momento angolare
  con Casimir ben definito**: non si rompe solo una simmetria, viene a mancare
  l'oggetto su cui si costruisce la decomposizione di Kambe.
- Idem, sez. "Il caso non uniforme": $\|P_{13}HP_{13}^\dagger-H\|=0.8$ a
  $(J_{12},J_{23},b)=(0.9,0.5,0.4)$; nessuna forma chiusa, analogo diretto dello
  scaleno per l'anello, rimandato a fase successiva come da proposta al relatore.
- Idem, sez. "Campo critico", tabella comparativa: parametri liberi $(J,J')$ e
  mappa di fase 2D per l'anello, solo $J$ (segno) per la catena; $b_c=3J'$ vs $3J$.
- `trimero_catena_verifiche.tex`: test corrispondente, incluso
  `H_chain_nonuniform(J12, J23, b)` — verifica che $P_{13}$ **si rompa** nel caso
  non uniforme, non solo che valga in quello uniforme.

**Conclusione:** nessuna aggiunta necessaria ai `.tex` esistenti su questo punto.

### Cosa invece NON è ancora documentato: propagazione al termine DM

Il termine DM della catena eredita la stessa uniformità. La struttura
$D_{12}=-D_{23}\equiv D$ (unica compatibile con $P_{13}$, già verificata nei
self-test DM di `trimer_chain_exact.py`) ha **un solo modulo**, non due
indipendenti. Conseguenza operativa per la Fase 5 e per il Trotter:

> Il punto di lavoro della catena vive in **due** parametri $(b,D)$ a $J$ fissato,
> contro i **quattro** $(J,J',b,D)$ del punto $R_0$ dell'anello. Lo scan del
> punto di lavoro è quindi strutturalmente più semplice, non solo più rapido.

Da inserire in `analisi_dm_trimero_catena.tex` quando verrà scritto (Fase 5,
punto 3), non nei documenti di teoria esistenti — è una conseguenza della
struttura DM, non della teoria a $D=0$.

### Affermazione scartata (non documentare)

In discussione era emersa l'idea che "aggiungere un $J'$ alla catena non
aprirebbe comunque una vera mappa di fase come nell'anello, per assenza di
frustrazione". **Non verificata, non presente in alcun `.tex`, non da citare.**
L'argomento per assenza di frustrazione è plausibile ma non è una dimostrazione;
se e quando si aprirà il caso non uniforme, va verificato numericamente, non
assunto. Registrato qui solo per evitare che rientri per inerzia in un documento.

### Nota minore di igiene del codice

`trimer_chain_exact.py`, `_self_test_dm()` (righe ~441–449): variabile locale
`Jp = 1.0`. Non è un secondo accoppiamento — è un nome ereditato per copia dal
file dell'anello, dove `Jp` indicava davvero $J'$. Funzionalmente innocuo,
potenzialmente fuorviante a distanza di tempo. Da rinominare (`J_test`) alla
prossima modifica del file per la Fase 5.

## Aggiornamento — correzione di due file dell'anello: trappola di Kramers a $b=0$

**Origine.** Aprendo la Fase 5 della catena si è applicata alla lettera la ricetta
metodologica scritta in `analisi_dm_trimero_anello.tex` («minimo assoluto del gap su
tutto l'asse $b$») e si è ottenuto $g_\text{min}=0$ per ogni $D$, apparentemente
«il DM della catena non apre l'incrocio» — conclusione **falsa**. Il minimo cadeva
sempre a $b=0$.

**Diagnosi: teorema di Kramers.** A $b=0$ l'Hamiltoniana è invariante per inversione
temporale $T=(i\sigma_y)^{\otimes3}K$: scambio e DM sono entrambi $T$-pari (bilineari
in operatori di spin, ciascuno $T$-dispari), solo lo Zeeman è $T$-dispari. Con un
numero **dispari** di spin-$1/2$ lo spin totale è semi-intero, $T^2=-\mathbb{I}$, e
Kramers impone che ogni livello sia almeno doppiamente degenere a campo nullo. Quella
degenerazione **non è apribile da alcun DM**, per costruzione. Vale per entrambe le
topologie.

**Verifica numerica** (script `verifica_kramers.py`, prodotto in sessione):
$\|U_TU_T^\dagger-\mathbb{I}\|=0$; $\|T^2+\mathbb{I}\|=0$; $\|THT^{-1}-H\|=0$ esatto a
$b=0$ per anello (Opz. A e B) e catena, per $D=0,\,0.15,\,0.5,\,1.3$; $=14.4$ a
$b=2.4$ e $=3.0$ a $b=0.5$; scarto nei quattro doppietti a $b=0$ $\leq2.7\times10^{-15}$;
$|\langle\psi|T\psi\rangle|=0$ sui livelli $0,2,4,6$ (partner di Kramers ortogonale).

### ✅ I RISULTATI DELL'ANELLO SONO CORRETTI — nessun erratum

Punto verificato esplicitamente prima di toccare qualunque cosa, perché condizionava
la validità di quanto già comunicato al relatore. La tabella $g_\text{min}(D)$
pubblicata è stata **riprodotta da zero** rieseguendo `dm_min_gap`:

| $D$ | $g_\text{min}$ B ricalc. | pubbl. | $b$ ricalc. | pubbl. |
|---|---|---|---|---|
| 0.009 | 0.015273 | 0.0149 | 2.4000 | 2.4000 |
| 0.073 | 0.123857 | 0.1240 | 2.4017 | 2.4017 |
| 0.148 | 0.250930 | 0.2511 | 2.4068 | 2.4068 |
| 0.300 | 0.507215 | 0.5072 | 2.4275 | 2.4275 |

Opzione A ricalcolata: $10^{-8}$–$10^{-9}$, cioè zero a precisione numerica, come
pubblicato. Gap al punto di lavoro delle correlazioni: $0.254700$ ricalcolato contro
$0.2547$ nel log. **Nessun numero cambia, nessuna conclusione si ritira.**

Motivo per cui i risultati si sono salvati: `dm_min_gap` **nel codice** ha sempre
usato una finestra $[b_c-w,b_c+w]$ con $w=\max(1,0.6|b_c|)=1.44$, cioè $[0.96,3.84]$,
che esclude $b=0$. Era la **prosa** a descrivere una ricetta diversa da quella
eseguita. Controfattuale calcolato: applicando la ricetta come scritta su $[0,6]$,
entrambe le opzioni danno $\sim10^{-15}$ a $b=0$ — la distinzione A/B, cioè l'intero
risultato del documento, sarebbe evaporata.

Corroborazione indiretta: la catena, dove lo stesso Casimir è conservato ma
l'incrocio è **intra-settore**, dà l'esito opposto ($g_\text{min}=2\sqrt6\,D$). Due
topologie che si comportano in modo opposto nel modo previsto dalla regola di
von Neumann–Wigner rafforzano la conclusione dell'anello invece di incrinarla.

### 🔄 FILE MODIFICATI — DA SOSTITUIRE SUL PC E RICARICARE NEL PROGETTO

Modifiche prodotte in sessione, **solo sorgenti `.tex`, nessun PDF** (convenzione in
uso). Impronte per il controllo al prossimo caricamento:

| file | MD5 vecchio | MD5 nuovo | righe |
|---|---|---|---|
| `analisi_dm_trimero_anello.tex` | `79fca3a43146937bc495cd086d2885a7` | `ff4fbb64513ee2c3bfd51334f37821d9` | 281 → 400 |
| `trimer_ring_exact.py` | `e87dbbb4fb05f62f03e14f3e3cd3da27` | `ddb1fdf193d09f5f1bb46f4849dbc66e` | 565 → 582 |

> ⚠️ **Controllo da fare all'inizio della prossima sessione**: verificare con
> `md5sum` che i file presenti nel Project abbiano gli MD5 **nuovi**. Se compaiono
> ancora quelli vecchi, il caricamento non è avvenuto e la trappola di Kramers è
> ancora nella documentazione.

**Cosa è cambiato in `analisi_dm_trimero_anello.tex`** (+128 righe, −9; nessun
numero, nessuna conclusione, nessuna figura toccata):
1. Titolo sottosezione: «minimizzare il gap su tutto $b$» → «in un intorno di $b_c$».
2. Formula di $g_\text{min}$: esplicitato il dominio $\mathcal I=[b_c-w,b_c+w]$ e
   dichiarata la semiampiezza effettivamente usata dal codice.
3. **Nuova sottosezione** «Una seconda trappola: la degenerazione di Kramers a campo
   nullo» (`\label{sec:kramers}`): controfattuale, derivazione di $T$, tabella di
   verifica numerica, nota di generalità a qualunque numero dispari di spin-$1/2$, e
   nota storica sulla scoperta.
4. Conclusioni, punto 3: aggiunta la clausola sull'esclusione di $b=0$, con la
   simmetria fra le due trappole (una misura il gap dove non è più critico, l'altra
   dove è protetto da un'altra simmetria).
5. Preambolo: aggiunto `amsthm` + `\newtheorem*{osservazionekramers}`.

**Cosa è cambiato in `trimer_ring_exact.py`** (+23 righe, −6; nessuna modifica
funzionale, solo commenti):
1. Docstring di `dm_min_gap` riscritta: elenca **entrambi** gli errori da evitare
   (gap a $b_c$ fisso; estensione fino a $b=0$) con la ragione fisica del secondo.
2. Quattro riferimenti al nome file obsoleto `analisi_dm_trimero.pdf` →
   `analisi_dm_trimero_anello.tex`.

**Validazione delle modifiche:**
- `.tex` compilato due passate con `pdflatex`: **zero errori**, zero riferimenti
  indefiniti, 7 pagine. I tre `Underfull` residui sono alle righe 137–141, cioè nel
  testo preesistente, non nella parte aggiunta. Un `Overfull` introdotto dalla nuova
  tabella è stato corretto (tabella ristretta, nota spostata nel corpo). Il PDF è
  stato generato solo come controllo di sintassi e **non è stato consegnato**.
- `.py`: `_self_test()` e `_self_test_dm()` rieseguiti dopo la patch, tutti superati
  (incluso `[self-test DM 3]`, che dà ancora $2.26\times10^{-8}$ per A e $0.2543$ per B).
- `diff` riga per riga: le uniche righe rimosse/sostituite sono le 9 (`.tex`) e 6
  (`.py`) previste. Nessun contenuto perso.
- Terminatori CRLF e codifica UTF-8 preservati come negli originali.

### Nota metodologica per il seguito

`Kramers` non compariva da nessuna parte nel progetto prima di ora (controllato con
`grep` su tutti i `.tex`, `.py`, `.md`). L'esclusione di $b=0$ va ora considerata
parte della ricetta standard per qualunque ricerca di gap minimo in funzione del
campo su questi sistemi, catena inclusa.

## Aggiornamento — chiusura dei file della catena: funzioni DM aggiunte, documentazione riallineata

Prima di avviare lo sweep sistematico della Fase 5 (catena), chiusi i tre file che
risultavano indietro rispetto al modulo dell'anello o contenevano affermazioni
superate/errate.

### 🔄 FILE MODIFICATI — DA SOSTITUIRE SUL PC E RICARICARE NEL PROJECT

| file | MD5 vecchio | MD5 nuovo | righe |
|---|---|---|---|
| `trimer_chain_exact.py` | `4cf0e7dfc62d83251d4f3d90d726a4f8` | `ceec77022572c418a83f2dcadff8ba76` | 510 → 652 |
| `trimero_catena_exact.tex` | `a0798de9ab4549737197c66766ebf484` | `48c8fd06f35b78c28463f1b2482b1415` | 172 → 199 |

> ⚠️ Stesso controllo di sempre a inizio prossima sessione: verificare che i due file
> nel Project abbiano gli MD5 **nuovi**.

### `trimer_chain_exact.py` (+155/−13 righe)

1. **Tre funzioni nuove**, mirror di `trimer_ring_exact.py` ma con una correzione
   deliberata: `exact_sweep_dm(b_values, J, D)`, `ground_state_projector_dm(J, b, D,
   tol)`, `dm_min_gap(J, D, search_half_width)`.
   - `dm_min_gap` usa la stessa finestra $[b_c-w,b_c+w]$, $w=\max(1,0.6|b_c|)$,
     dell'anello — con la doppia motivazione ormai documentata (gap a $b_c$ fisso /
     Kramers a $b=0$) scritta per esteso nella docstring.
   - `exact_sweep_dm` **non è un mirror letterale** di quella dell'anello: include la
     media sul sottospazio degenere già usata in `exact_sweep` (D=0) di questo
     stesso file, che quella dell'anello non ha (vedi bug segnalato sotto).
2. **Due nuovi self-test** in `_self_test_dm()`: coerenza `exact_sweep_dm` ↔
   `ground_state_projector_dm` (mirror del self-test 5 dell'anello); linearità di
   $g_\text{min}(D)$ con pendenza $2\sqrt6\approx4.899$ (verifica diretta del
   risultato del checkpoint 1). Tredici self-test totali, tutti superati a
   precisione macchina dopo la patch.
3. **Rename** `Jp`→`J_test` nel self-test DM (mai stato un secondo accoppiamento,
   solo un nome ereditato per copia dall'anello — segnalato in precedenza).
4. **Intestazione della sezione DM riscritta**: da "STRUTTURA DISPONIBILE, NON
   USATA" a stato aggiornato, con la clausola esplicita che l'analogia con
   l'Opzione A dell'anello è *strutturale* (conserva $S_{13}^2$) ma *non di esito*
   (l'anello con A non apre mai il gap, qui il gap si apre, perché l'incrocio è
   intra-settore $S_{13}=1\to1$) — per evitare che un lettore futuro deduca la
   conclusione sbagliata dal solo nome "Opzione A".

**Validazione:** modulo rieseguito per intero dopo la patch — 8 self-test base + 5
self-test DM, tutti superati; sintassi Python verificata (`ast.parse`); `diff`
riga per riga conferma che le uniche 13 righe toccate sono le previste (intestazione
+ rename); CRLF preservato.

### `trimero_catena_exact.tex` (+35/−8 righe)

**Non è un aggiornamento di stato, è la correzione di un'affermazione falsa.** Il
paragrafo "Verifiche" affermava che il modulo includeva già *"il self-test
aggiuntivo di coerenza fra `exact_sweep_dm` e `ground_state_projector_dm`"* — quelle
due funzioni **non esistevano nel file** a inizio Fase 5 (solo `dm_term` e
`trimer_hamiltonian_dm`, etichettate esplicitamente "struttura disponibile, non
usata"). Il paragrafo è stato riscritto per dichiarare la correzione esplicitamente,
non solo per aggiornare silenziosamente il contenuto. L'elenco delle funzioni
interne è stato esteso con le tre funzioni nuove, inclusa la stessa clausola di
cautela sull'Opzione A (struttura sì, esito no).

**Validazione:** compilato due passate con `pdflatex`, zero errori, 4 pagine. Un
`Overfull` introdotto dalla nuova voce `dm_min_gap` (nome file lungo in `\texttt`
senza punti di sillababilità) è stato isolato con `\sloppy` locale al solo item
incriminato. Restano due `Overfull` (14.3pt, 18.5pt) **preesistenti nel documento
originale** (righe 107–110 e 126–132 prima della patch, stessa causa — nomi file
lunghi in `\texttt`): non nell'ambito di questa sessione, non toccati. Il PDF è
stato generato solo come controllo di sintassi, non consegnato.

### 🐛 Bug latente segnalato in `trimer_ring_exact.py` — NON corretto (fuori ambito)

Nello scrivere `exact_sweep_dm` per la catena, confrontando con la versione
dell'anello, confermato che `exact_sweep_dm` **dell'anello** non ha la correzione di
media sul sottospazio degenere presente invece nel suo stesso `exact_sweep` (D=0) e
in entrambe le `exact_sweep` della catena. Poiché a $b=0$ il fondamentale è un
doppietto di Kramers per *qualunque* $D$ (verificato ieri), `exact_sweep_dm`
dell'anello restituisce oggi un $\langle M_z\rangle$ dipendente dalla scelta
arbitraria di `numpy.linalg.eigh` in quel punto, anziché il valore fisico (atteso
0). **Non corretto in questa sessione**: era fuori dall'ambito concordato (solo file
della catena). Da correggere quando/se si riapre `trimer_ring_exact.py`.

## Aggiornamento — corretto il bug latente in `trimer_ring_exact.py::exact_sweep_dm`

Bug segnalato in precedenza (media sul sottospazio degenere assente in
`exact_sweep_dm`, presente invece in `exact_sweep` e in entrambe le `exact_sweep` di
`trimer_chain_exact.py`) ora corretto, su richiesta esplicita.

### 🔄 FILE MODIFICATO — DA SOSTITUIRE SUL PC E RICARICARE NEL PROJECT

| file | MD5 (versione con sole correzioni Kramers) | MD5 (con anche questa correzione) | righe |
|---|---|---|---|
| `trimer_ring_exact.py` | `ddb1fdf193d09f5f1bb46f4849dbc66e` | `60f3ebbfb8ff001151a7cc8434315275` | 582 → 613 |

> ⚠️ Questa è la **terza** versione di `trimer_ring_exact.py` prodotta in sessione
> (originale → correzione Kramers → correzione bug degenere). Al prossimo
> caricamento verificare che il Project abbia l'MD5 `60f3eb…5275`, non uno dei due
> precedenti.

### Cosa comportava il bug (richiesta esplicita di Samuele, verificata prima di
### correggere — vedi aggiornamento precedente)

Tracciati tutti i 15 file del progetto che importano da `trimer_ring_exact.py`.
Nessuno passa mai per $b=0$ attraverso `exact_sweep_dm` con lettura di `gs_mz`:
Trotter e correlazioni importano solo `trimer_hamiltonian(_dm)` (nessun contatto);
l'unico notebook che chiama `exact_sweep_dm`
(`confronto_ansatz_entangler_trimero_anello.ipynb`) legge solo `gs_energy` (non
affetta) su una griglia che parte da $b=0.05$; la fidelity nello stesso notebook usa
`ground_state_projector_dm`, funzione diversa e già corretta per costruzione.
**Nessun risultato consegnato al relatore era interessato.**

### Correzione applicata

`exact_sweep_dm` ora media $\langle M_z\rangle$, $\langle S_{12}^2\rangle$,
$\langle S^2\rangle$ sul sottospazio degenere (proiettore $V_0V_0^\dagger$/degenerazione),
esattamente come già fatto in `exact_sweep` — non un mirror indipendente, la stessa
logica copiata dalla funzione gemella dello stesso file.

**Controprova che il bug fosse reale** (calcolata prima di correggere, per non
correggere un problema immaginario): a $b=0$, $D=0.15$, il singolo autovettore
`v[:,0]` restituito da `eigh` dava $\langle M_z\rangle=-0.5$ (Opzione A) o $+0.484$
(Opzione B) — non zero, e dipendente arbitrariamente dalla base interna scelta da
`numpy.linalg.eigh`, non dalla fisica.

**Nuovo self-test DM 6**, aggiunto per non lasciare la correzione silenziosa:
verifica $\langle M_z\rangle(b{=}0)=0$ per Opzione A/B e $D=0,0.15,0.5,1.3$ — quello
che, senza la correzione, sarebbe fallito in modo intermittente a seconda
dell'implementazione di `eigh`. Tutti gli altri self-test (5 base + 6 DM, 14 totali)
rieseguiti e superati a precisione macchina dopo la correzione.

**Validazione:** `diff` contro la versione precedentemente consegnata conferma che
le uniche 4 righe toccate sono quelle del corpo di `exact_sweep_dm` (`g = v[:,0]` e
le tre append), come previsto; sintassi Python verificata; CRLF preservato.

## Aggiornamento — Fase 5 (catena), punti 1-2 completati: sweep sistematico + scoperta W-2qC.K2

### Punto 1 (quantificazione DM): confermato, checkpoint 1 chiuso in sessione precedente

Elemento di matrice $\langle B',-\tfrac12|H_{DM}|A',-\tfrac32\rangle=-\sqrt6\,D$
verificato ($4.4\times10^{-16}$); $g_\text{min}(D)=2\sqrt6\,D$ confermato su
griglia; punto di lavoro $(J,b,D)=(1,\,3.0,\,0.15)$ confermato da Samuele.
Formalizzato in `analisi_dm_trimero_catena.tex` (nuovo, vedi sotto).

### Punto 2 (sweep sistematico): completato — 300/300 punti, con una scoperta non
### assunta dall'anello

**File prodotti** (nessuno preesistente nel Project, tutti nuovi):

| file | contenuto |
|---|---|
| `ansatz_catena.py` | 15 famiglie di ansatz, mirror dell'anello adattato a 2 bond (conteggi $2+3k$ e $5K$, non $3+3k$/$6K$) |
| `sweep_catena_dm.py` | sweep sistematico: 15 ansatz × 10 $b$ × 2 condizioni (D0/DM) = 300 punti, cache incrementale |
| `trimer_chain_dm_sweep_cache.json` | i 300 risultati (energia, fidelity, parametri, degenerazione) |
| `indagine_catena_bc.py` | verifica dedicata a $b_c$ con 60-80 restart — non un secondo notebook, uno script mirato |
| `analisi_dm_trimero_catena.tex` | punto 1: derivazione, tabella $g_\text{min}(D)$, confronto con Opzione A dell'anello |
| `trimero_catena_vqe_dm.tex` | punto 2: catalogazione sweep, risultato W-2qC.K2, costo in gate |

**Validazione dei 300 punti:** nessuna fidelity fuori $[0,1]$; i valori a $D=0$
riproducono esattamente (stesse cifre) la cache preesistente
`trimer_chain_ansatz_sweep_cache.json` (nomenclatura `PMA-*`, stessi circuiti) —
conferma indipendente. Un'apparente anomalia (55/300 punti a fidelity $\approx0$)
risultata essere il limite strutturale **già noto e documentato** nel notebook
$D=0$ esistente (`PMA-1q` non raggiunge $\lvert111\rangle$ sulla catena, 2 bond
contro 3 — § 5.1 di `confronto_ansatz_entangler_trimero_catena.ipynb`): nessun bug,
confinata esattamente alle famiglie a bassa espressività già segnalate.

### 🔍 Scoperta: sulla catena servono DUE giri di blocchi per l'esatto, non uno

**Non un mirror dell'anello — verificato, non assunto, come da piano.** Sull'anello
un solo giro di $W$ (`W-2q.6`) bastava per $\mathcal F=1$ esatto sotto DM
(`analisi_espressivita_PMA_anello.ipynb`). Sulla catena, verificato con 60-80
restart su 3 seed indipendenti (stabile a $<10^{-10}$):

| famiglia | 1 giro | 2 giri (K2, 10 par) |
|---|---:|---:|
| RBS-2q | $0.9626275828$ | $1.0000000000$ |
| W-2q | $0.9936951715$ | $1.0000000000$ |
| W-1q.6 / .9 | $0.9999042461$ / $0.9999340062$ (tetto separato) | — |

La gerarchia $W>$RBS sotto DM si conferma in termini relativi, ma **né RBS né $W$
raggiungono l'esatto con un solo giro sulla catena** — serve `*-2qC.K2` (10
parametri, 2 giri completi) per entrambe le famiglie. Candidato canonico proposto:
**`W-2qC.K2`** (10 par, 8 gate a 2 qubit, 19 gate totali contro 39 di
`RBS-2qC.K2` a parità di parametri e gate a 2 qubit) — non l'analogo diretto di
`W-2q.6` dell'anello, che qui sarebbe insufficiente (tetto $0.9937$).

**Precisazione trovata sul risultato già comunicato dell'anello (nessun errore, solo
lettura più precisa).** Verificato che il notebook dedicato dell'anello
(`analisi_espressivita_PMA_anello.ipynb`, 20-60 restart) non ha mai testato
`RBS-2qC.K2`/`W-2qC.K2` (solo `.6`, `.9`, `K1` — varianti "un giro + Ry extra").
Controllato nello sweep sistematico dell'anello (`trimer_ansatz_sweep_cache_v2.json`):
`RBS-2qC.K2` vi raggiunge $\mathcal F=1$ esatto sotto DM, su tutta la griglia. La
frase nel log "RBS-2q ha un tetto strutturale vero... indipendentemente dal numero
di parametri" resta corretta per la famiglia effettivamente testata (un giro, $Ry$
extra non aiutano), ma va letta come tale — non come "per qualunque architettura
RBS". **Nessuna azione correttiva sui file dell'anello**: il risultato comunicato al
relatore resta valido, è solo la portata della frase a essere più stretta di quanto
una lettura letterale suggerirebbe. Segnalato qui per completezza, non richiede
modifica ai file già consegnati.

### Validazione LaTeX

Entrambi i `.tex` compilati due passate: **zero errori**. Un errore mio
(`\ket{...}` non definito in `trimero_catena_vqe_dm.tex`, che non carica lo stesso
preambolo di `analisi_dm_trimero_catena.tex`) corretto prima della consegna.
`analisi_dm_trimero_catena.tex`: 3 pagine, un `Overfull` di 4pt e un `Underfull`
sotto soglia — trascurabili, stessa tolleranza dei documenti già accettati.
`trimero_catena_vqe_dm.tex`: 3 pagine, zero overfull/underfull. PDF generati solo
come controllo di sintassi, non consegnati (convenzione: solo `.tex`).

### Prossimo passo

Punto 3 della Fase 5 tecnicamente già assorbito nei due documenti appena prodotti
(non serve un terzo file separato). Filone Fase 5 catena chiuso. Prossimo: Trotter
per la catena (derivazione da zero per la topologia a due bond, come da piano).

## Aggiornamento — due notebook interattivi per la Fase 5 (catena), con RBS e W

Su richiesta, prodotti due notebook con celle interattive (ipywidgets) che
rieseguono i calcoli localmente, in aggiunta agli script già consegnati (non in
sostituzione). Entrambi **eseguiti per intero in questa sessione** con un kernel
Jupyter reale (non solo verificati a livello di sintassi) — installato l'ambiente
necessario (`nbformat`, `nbclient`, `ipykernel`, `ipywidgets`) per poterlo fare.

### File consegnati

| file | contenuto |
|---|---|
| `confronto_ansatz_entangler_trimero_catena_dm.ipynb` | sweep sistematico interattivo: selettore circuiti, cella di sweep rilanciabile, tabelle, griglia di grafici fidelity vs $b$ |
| `indagine_bc_trimero_catena.ipynb` | verifica dedicata a $b_c$ con ricalcolo live (Dropdown ansatz + slider restart + pulsante) |
| `confronto_ansatz_trimero_catena_dm_grid.png` | figura generata dal primo notebook |
| `trimer_chain_dm_sweep_cache.json` | aggiornata a 320 punti (era 300: aggiunta `W-2qC.K2`, mancante dallo sweep originale) |
| `trimero_catena_vqe_dm.tex` | aggiornato con le due nuove sezioni di catalogazione |

### Pattern widget usato: Dropdown+observe, non FloatSlider+interact

Deliberatamente lo stesso pattern già validato con successo nell'anello
(`analisi_espressivita_PMA_anello.ipynb`: `ipywidgets.Dropdown` + `.observe()` +
`widgets.Output()`), non il pattern `FloatSlider`+`interact`/`interact_manual` che
aveva dato problemi di rendering in VS Code nel notebook Trotter dell'anello
(bug noto dell'estensione, documentato in precedenza nel log). Per il ricalcolo
live nel secondo notebook, `Button.on_click` invece di `interact_manual`, stessa
cautela.

### Esecuzione: due iterazioni per il timeout

Il tentativo iniziale (60 restart × 10 ansatz nella cella di riferimento del
secondo notebook) andava oltre il tempo disponibile per l'esecuzione automatica.
Ridotto a 15 restart, con dichiarazione esplicita nel testo del notebook (non un
silenzioso downgrade): la cella confrontata dà risultati **identici a 10 cifre
decimali** ai valori a 60-80 restart già in `indagine_catena_bc.py` — conferma
indipendente che il tetto trovato è vero, non dipendente dal numero di restart
oltre una soglia bassa.

### Verifica degli output dopo l'esecuzione

Ispezionati tutti gli output cella per cella: zero errori in entrambi i notebook;
i 15 restart riproducono esattamente $0.9626275828$ (RBS, 1 giro), $1.0$ (RBS/W,
2 giri, K2), $0.9936951715$ (W, 1 giro), $0.9999042461$/$0.9999340062$ (W-1q.6/.9)
— stessi valori del run a 60-80 restart eseguito in precedenza. Figura del primo
notebook (2080×910, ispezionata visivamente): otto pannelli, RBS-2qC.K2 e
W-2qC.K2 piatti a $1.0$ su tutta la griglia, coerenti con la tabella.

**Osservazione minore trovata durante l'ispezione, non un'anomalia**: a $D=0$ le
famiglie $W$-2q mostrano una lieve degradazione liscia e monotona sotto $b_c$
($0.9714\to0.9661$ per `W-2q.8`), non rumore — stessa direzione del limite più
severo di RBS-2q ma più mite. Segnalata nel `.tex` aggiornato, non richiede
correzione né cambia le conclusioni.

## Aggiornamento — Trotter per la catena aperta: derivazione dei livelli, note metodologiche

### 📐 Convenzione di norma matriciale — dichiarata esplicitamente

Ovunque nel progetto, `||M||` è la **norma di Frobenius**, cioè
`numpy.linalg.norm(M)` **senza** argomento `ord`. È la convenzione già in uso di
fatto in tutti i self-test di `trotter_trimero_anello.py`, `trimer_ring_exact.py` e
`trimer_chain_exact.py`, ma non era mai stata scritta da nessuna parte: Samuele ha
dovuto dedurla per tentativi nel riprodurre i valori di questa sessione. Da ora è
dichiarata in testa a `trotter_trimero_catena.py` e va dichiarata in ogni nuovo
documento che riporti norme numeriche. I valori riportati nel log **non** sono
confrontabili con una norma spettrale.

### ⚠️ Nota metodologica — non-sequitur nella docstring di `trotter_trimero_anello.py` (NESSUNA MODIFICA APPLICATA)

La docstring di `trotter_trimero_anello.py` giustifica il Trotter esterno dicendo che
l'errore è dovuto *solo* a $[S_z^{tot},H_{DM}]\neq0$ perché «$H_{ex}$ non contribuisce
all'errore esterno, commutando esattamente col campo».

**È un non-sequitur.** $[H_{ex},S_z^{tot}]=0$ e $[H_{ex},H_{DM}]=0$ sono condizioni
logicamente indipendenti: la prima non implica la seconda. Misura sulla catena a
$J=1$, $b=0.7$, $D=0.3$ (Frobenius):

| commutatore | norma |
|---|---|
| $\|[H_{ex},H_{DM}]\|$ | $10.182338$ |
| $\|[S_z^{tot},H_{DM}]\|$ | $3.394113$ |

$H_{ex}$ è il contributo **dominante** al mancato annullamento — circa il triplo del
campo — non trascurabile come la frase suggerisce. Verificato indipendentemente da
Samuele in chat parallela, con coincidenza esatta delle cifre.

**Stato: nessuna correzione applicata, per decisione esplicita.** Il filone anello è
chiuso e `trotter_trimero_anello.py` **non è stato toccato**. L'implementazione
dell'anello resta corretta: applica tre blocchi annidati in sequenza, non uno
splitting a due blocchi con $H_0$ trattato come esatto contro $H_{DM}$. È soltanto la
frase esplicativa a essere sbagliata. **Da non ricopiare** nella documentazione della
catena né altrove.

### Trotter catena — struttura a tre livelli, derivata da zero

**Livello 0 (esatto).** $e^{-i\tau(bS_z^{tot}+H_{ex})} = e^{-i\tau bS_z^{tot}}e^{-i\tau H_{ex}}$
**perché** $[S_z^{tot},H_{ex}]=0$ — verificato bond per bond, $\|[S_z^{tot},h_{12}]\| =
\|[S_z^{tot},h_{23}]\| = 0$ esatto. La proprietà si ferma alla coppia (campo, scambio) e
**non si estende a $H_{DM}$**.

**Livello 1.** Identità esatta (residuo $0.0$, non $10^{-16}$):
$$[\vec\sigma_1\!\cdot\!\vec\sigma_2,\ \vec\sigma_2\!\cdot\!\vec\sigma_3] = -2i\chi,
\qquad \chi=\vec\sigma_1\cdot(\vec\sigma_2\times\vec\sigma_3)$$
Con i bond applicati nell'ordine $(1,2)\to(2,3)$ (ordine del circuito):
$$e^{-i\tau Jh_{23}}e^{-i\tau Jh_{12}} = \exp\!\big[-i\tau(H_{ex}+\tau J^2\chi)+O(\tau^3)\big]$$
**Il segno dipende dall'ordine dei bond**: misurato $s=+1.000$ per $(1,2)\to(2,3)$ e
$s=-1.000$ per l'ordine invertito. Confronto con l'anello (dal log, non riverificato
qui): stessa forma con $J'^2\to J^2$, ma qui senza cancellazioni — c'è un solo
commutatore, non tre.

**Livello 2.** $[d_{12},-d_{23}] = -2i\Theta$ con $\Theta = X_1Y_2Z_3 - Z_1Y_2X_3$
(residuo $0.0$; decomposizione Pauli a due sole label). $\Theta$ è hermitiano e
**dispari** sotto $P_{13}$. **Non** è proporzionale a $\chi$: livelli 1 e 2 generano
strutture d'errore indipendenti, il livello 2 non è assorbibile in una ridefinizione
del livello 1.

### 🔍 Scoperta metodologica — `|000>` è cieco all'errore di livello 1

$|000\rangle$ è autostato di **ogni bond separatamente**: $h_{ij}|00\rangle = +|00\rangle$
(verificato, $\|h_{12}|000\rangle - |000\rangle\| = 0$). Tutti i fattori Trotter di
$H_{ex}$ agiscono su di esso come semplici fasi e commutano fra loro. Conseguenza: un
test di convergenza su $|000\rangle$ a $D=0$ dà infedeltà $\sim10^{-14}$ per
**qualunque** $N$ — è un test vuoto.

`trotter_trimero_anello.py` usa `PSI0 = |000>` nel suo self-test di convergenza: quel
test misura quindi il solo errore DM, non il livello 1. **Non corretto** (anello
chiuso), ma **non replicato**: i self-test della catena usano $|010\rangle$ e uno stato
random.

### 💡 Alternanza dell'ordine dei bond — risultato originale

Poiché il termine chirale cambia segno con l'ordine dei bond, alternare
$(1,2)\to(2,3)$ e $(2,3)\to(1,2)$ su passi consecutivi lo cancella al leading order,
**a parità esatta di gate** (nessun costo aggiuntivo). Misure su stato random, $t=2$:

| regime | fisso | alternato | guadagno a $N=80$ |
|---|---|---|---|
| $D=0$ | $O(1/N^2)$, rapporto $\times4.0$ | $O(1/N^4)$, rapporto $\times16.0$ | $34.5\times$, crescente come $N^2$ |
| $D=0.3$ | $O(1/N^2)$, $\times4.0$ | rapporto degrada $\times9.9\to\times5.1$ | $5.7\times$, in saturazione |

**Lettura onesta**: il guadagno di un ordine intero vale **solo** per il livello 1
isolato. Con DM acceso l'alternanza cancella il termine chirale ma lascia intatti il
livello 2 e i termini incrociati $H_{ex}/H_{DM}$ e $S_z^{tot}/H_{DM}$, che restano
$O(1/N^2)$ e tornano a dominare per $N$ grande. Il guadagno è reale ma parziale e
satura. Da non spacciare come risultato generale.

Rilevanza per la Parte 2: stesso numero di canali di rumore, meno passi per una data
accuratezza — vantaggio massimo nel regime a DM debole.

### File prodotto

`trotter_trimero_catena.py` (nuovo). Sette self-test, tutti superati. Convenzioni
dichiarate in testa, incluse le tre differenze da `trotter_trimero_anello.py`:
due bond invece di tre, un solo $J$, e soprattutto **$D$ assoluto** ($D_{12}=+D$,
$D_{23}=-D$) e non scalato per l'accoppiamento del bond come nell'anello
($D_{ij}=D\cdot J_{ij}$) — usare la convenzione dell'anello qui farebbe divergere
circuito e benchmark esatto di un fattore $J$.

### Aperto

Le tre domande di verifica poste a Samuele su $\chi$ (valore di attesa nel
fondamentale esatto; in che senso Trotter «accende» la chiralità; quale osservabile
usare per diagnosticare l'errore Trotter separandolo dalla decoerenza in Parte 2)
restano **senza risposta**. La terza è candidata a nota metodologica nella tesi.

## Aggiornamento — Documentazione e notebook Trotter catena (parallelo all'anello)

### File nuovi

| file | MD5 | righe |
|---|---|---|
| `trotter_trimero_catena.py` | `d866617bfa1e56327fb20f61f6b13f07` | 336 |
| `trimero_catena_quantum_simulation.tex` | `3ccb914d8e9d7e7b870655db5169ad00` | 208 |
| `quantum_simulation_trimero_catena_trotter.ipynb` | `b53cd62809debbf360917c00936eb32f` | — |

`trotter_trimero_catena.py` invariato rispetto alla versione già registrata in
questa sessione (stesso MD5): nessuna modifica al codice, solo aggiunta di
documentazione e notebook attorno ad esso.

### Punto di lavoro $S_0$ — trovato per scansione, provvisorio

Stesso criterio dell'anello: cercare più modi spettrali di ampiezza comparabile
nella decomposizione di Bohr di $\langle S_z^{tot}\rangle(t)$. Scansione attorno al
campo critico $b_c=3J$ (crossing esatto senza DM, teorema di Kramers): a $b=b_c$
fisso il rapporto $a_2/a_1\to1$ per ogni $D$ testato, ma il gap vero va cercato sul
minimo effettivo (funzione `dm_min_gap` di `trimer_chain_exact.py`), non su $b_c$
fisso — stesso errore metodologico già documentato per l'anello.

**Adottato**: $J=1$, $D=0.3$, $b=3.0073414$ (minimo vero del gap), gap
$=1.468777$. Due modi dominanti quasi degeneri in ampiezza ($a\approx2.0$, gap
$0.847$ e $1.469$): $\langle S_z^{tot}\rangle(t)$ mostra un battimento di periodo
$\approx10.1$, non un singolo coseno. **Provvisorio**, stesso status di $R_0$ per
l'anello — nessuna conferma del relatore.

### Convergenza a $S_0$ — riconferma su punto fisico, non solo su parametri casuali

Verificata su $|010\rangle$, $t=20$: infedeltà fissa $6.32\times10^{-6}$ a
$N=8000$ (scaling pulito $O(1/N^2)$); infedeltà alternata $2.51\times10^{-7}$,
guadagno $25.2\times$ ma rapporto ancora in crescita ($\times5.08$ all'ultimo
raddoppio, non $\times16$) — conferma su un punto fisico reale, non solo su
parametri casuali, che l'alternanza satura in presenza di DM (già registrato
nell'aggiornamento precedente).

### Documentazione compilata e verificata

`trimero_catena_quantum_simulation.tex`: due passate `pdflatex`, un solo overfull
residuo di $1.4$pt (invisibile, non corretto perché irrilevante). Corretto un
overfull iniziale di $26$pt (nome di funzione lungo senza `seqsplit`) e uno di
$7$pt (tabella troppo larga, ridotta con `\small`). **Errore trovato e corretto
durante la verifica**: tre riferimenti `\ref{sec:...}` a sezioni `\section*`
(non numerate) restituivano un riferimento vuoto in stampa — sostituiti con
richiami testuali diretti al titolo della sezione. Verificato pagina per pagina
(3 pagine): nessun testo sovrapposto a elementi grafici, nessun riferimento
vuoto residuo.

### Notebook

`quantum_simulation_trimero_catena_trotter.ipynb`: eseguito per intero via
`jupyter nbconvert --execute`, zero errori. Contiene self-test del modulo,
ricerca del punto $S_0$, traiettoria esatta, convergenza fisso/alternato,
disegno del circuito (21 gate nativi per un passo a $S_0$).

### Stato

Fase Trotter per la catena aperta chiusa a un livello di completezza analogo
all'anello: codice, teoria derivata da zero (non ricopiata), notebook eseguito,
documentazione compilata e verificata pagina per pagina. Prossimo passo:
Fase 5 (VQE+DM) per la catena e correlatori dinamici (`domande_relatore.md`).
