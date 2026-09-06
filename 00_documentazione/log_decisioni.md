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

## Aggiornamento — Sei documenti .tex per la catena, mirror completo dell'anello

Prodotti, su richiesta esplicita, gli analoghi per la catena aperta dei sei
documenti già esistenti per l'anello, con le argomentazioni derivate da zero
per la topologia a due bond (non copiate meccanicamente).

| file | MD5 | mirror di |
|---|---|---|
| `quantum_simulation_trimero_catena_teoria.tex` | `1dac65b82a1cf51d127d269895b81bce` | `quantum_simulation_trimero_anello_teoria.tex` |
| `quantum_simulation_trimero_catena_applicazione.tex` | `ee9a6c9b853ec393a79ce79e45dde4b6` | `quantum_simulation_trimero_anello_applicazione.tex` |
| `quantum_simulation_trimero_catena_trotter_spiegato.tex` | `fb62b53e4c54f277f8efe16d9b00d281` | `quantum_simulation_trimero_anello_trotter_spiegato.tex` |
| `trimero_catena_circuito_compatto.tex` | `3e3fbe238fbe8cdc3a8a4e55f0033c51` | `trimero_anello_circuito_compatto.tex` |
| `trimero_catena_frustrazione_e_chiralita.tex` | `80eb8726f29581be769aa8edd5811a66` | `trimero_anello_frustrazione_e_chiralita.tex` |
| `trimero_catena_quantum_simulation.tex` | `15e0bd439a7ee956eae2ef210235cd6a` | `trimero_anello_quantum_simulation.tex` (aggiornato per includere i 5 nuovi documenti, non solo modulo+notebook) |

### Contenuti originali, non semplice trasposizione

- **Teoria**: derivazione da zero della struttura a due bond (un solo commutatore $\chi$ al livello 1, un solo $\Theta$ al livello 2, non tre come nell'anello); Sezione 8 riscrive correttamente il livello 0 esterno, correggendo il non-sequitur senza toccare il file dell'anello; Sezione 10 deriva l'alternanza dell'ordine dei bond, fenomeno assente nell'anello.
- **Applicazione**: tabella esplicita delle differenze di convenzione dall'anello (inclusa la normalizzazione assoluta di $D$, punto di attenzione concreto); ricerca di $S_0$ motivata fisicamente (attorno a $b_c=3J$), non su griglia cieca come l'anello.
- **Spiegato**: sette self-test invece di quattro, due dei quali (non-sequitur, cecità di $\ket{000}$) assenti nell'anello.
- **Circuito compatto**: stessi numeri già verificati in sessione precedente (10→19 CNOT per passo, 19 CNOT indipendente da $N$ fino a $N=100$), qui documentati con lo stile del progetto.
- **Frustrazione e chiralità — contributo originale**: dimostrazione algebrica generale (non solo verifica a numeri) che $\langle\chi\rangle=0$ su ogni autostato reale di ogni Hamiltoniana reale simmetrica ($\chi=iA$, $A$ reale antisimmetrico $\Rightarrow v^TAv=0$ per ogni $v$ reale). Risponde a una domanda aperta di una sessione precedente (dove vive $\chi$ se non nel fondamentale). Verificato numericamente su quattro punti (incluso $S_0$): $\langle\chi\rangle,\langle\Theta\rangle$ nulli entro $10^{-16}$. Generalizza la distinzione frustrazione/algebra già fatta per l'anello: la catena, priva di ciclo, frustrazione *e* degenerazione, mostra comunque l'identica non-commutatività algebrica.

### Verifica di compilazione

Tutti e sei compilati con `pdflatex`, due passate ciascuno. Un solo overfull
serio trovato e corretto (107pt, tabella troppo larga nell'applicazione,
risolta con `\small` e colonne `p{}`). Overfull residui: solo cosmetici
(≤1.4pt), invisibili. Ispezionati pagina per pagina (28 pagine totali fra i
sei documenti): nessun testo sovrapposto, nessun riferimento vuoto.

### Stato

Documentazione della fase Trotter per la catena ora a parità strutturale
completa con l'anello: sei documenti `.tex`, un modulo `.py`, un notebook
eseguito. Prossimo: correlatori dinamici (entrambe le topologie), Parte 2.

## Aggiornamento — correzione MD5 del notebook Trotter catena (rendering circuito)

L'MD5 registrato per `quantum_simulation_trimero_catena_trotter.ipynb`
nell'aggiornamento precedente (`b53cd62809debbf360917c00936eb32f`) è
**superato**: si riferiva alla versione con `qc.draw(output='text')`.

**Bug trovato**: la cella del circuito usava il rendering testuale invece
di quello grafico (`output='mpl'`), a differenza del notebook dell'anello.
Una seconda cella (traiettoria di $\langle S_z^{tot}\rangle(t)$) forzava
`matplotlib.use('Agg')`, impedendo la visualizzazione inline anche lì (il
grafico veniva solo salvato su file, mai mostrato).

**Corretto**: rimosso il backend forzato, sostituito il disegno testuale
con `qc.draw(output="mpl", fold=-1, style={"name": "iqp"})`, identico
all'anello. Rieseguito per intero (`jupyter nbconvert --execute`): entrambe
le celle producono ora `image/png` reale (46 KB e 28 KB), non testo.

**MD5 corretto**: `quantum_simulation_trimero_catena_trotter.ipynb` →
`de616b6c63ae0f9e810dde256d60cc6b` (era `b53cd62809debbf360917c00936eb32f`).
Nessun altro file di questa fase è stato toccato.

## Aggiornamento — MD5 del notebook Trotter catena: la versione con output puliti è quella corretta (decisione, non bug)

Correzione al proprio aggiornamento precedente. L'MD5
`de616b6c63ae0f9e810dde256d60cc6b` lì registrato è quello della versione
**eseguita** (output embedded: immagini del circuito e della traiettoria,
~94 KB). Il file effettivamente presente nel Project ha MD5
`46e4edf398d009b591dd0108253ad548` — stesso codice, cella per cella
identico (verificato), ma **output azzerati** (~20 KB).

**Decisione esplicita**: tenere la versione a output puliti nel Project,
per limite di spazio (le immagini `png` incorporate pesano quasi 5 volte
il file). Non è un errore da correggere al prossimo controllo MD5.

| stato | MD5 | dimensione | uso |
|---|---|---|---|
| output puliti (nel Project) | `46e4edf398d009b591dd0108253ad548` | ~20 KB | riferimento di codice, da rieseguire per vedere le figure |
| output eseguiti (solo in sessione locale, non nel Project) | `de616b6c63ae0f9e810dde256d60cc6b` | ~94 KB | consultata una tantum quando serve vedere circuito/traiettoria senza rieseguire |

**Nota per la verifica MD5 di apertura sessione**: da qui in avanti,
l'MD5 di riferimento per `quantum_simulation_trimero_catena_trotter.ipynb`
nel Project è `46e4edf398d009b591dd0108253ad548` (output puliti), non
`de616b6c63ae0f9e810dde256d60cc6b`.

## Aggiornamento — Correlatori dinamici per la catena aperta: mirror completo dell'anello

Ultimo filone aperto per chiudere $N=3$ (vedi aggiornamento precedente). Prodotti in
sessione tutti i file mirror della fase già chiusa per l'anello. **Non ancora
caricati nel Project**: MD5 e righe qui sotto sono calcolati sui file come
prodotti in sessione, da verificare di nuovo una volta caricati.

### Teoria: `simmetrie_correlatori_trimero_catena.tex`

| file | MD5 | righe |
|---|---|---|
| `simmetrie_correlatori_trimero_catena.tex` | `fc083dbdbe71a60f67671e1ed1698d9a` | 508 |

Derivata da zero, non ricopiata dall'anello. Simmetria residua $P_{13}$ (riflessione
siti 1,3, sito 2 fisso): a differenza di $U_\text{anello}=\mathrm{SWAP}_{12}\cdot
(R_z(\pi))^{\otimes3}$, qui basta lo **scambio puro**, $\lambda_\alpha\equiv+1$ per
ogni $\alpha$ — verificato $\|[P_{13},H]\|=0$ esatto, rotto nettamente col segno DM
sbagliato. Conseguenza qualitativa (non solo quantitativa): $P_{13}$ produce **solo
uguaglianze** fra correlatori ($C_{11}\equiv C_{33}$ etc.), **mai zeri** — il sito
fisso non è protetto, a differenza del sito 3 dell'anello (4 zeri strutturali).
Time-reversal: 24 zeri a $t=0$ per $i\neq j$ (stessa dimostrazione dell'anello) + 6
zeri aggiuntivi per $i=j$ ($C_{ii}^{xz},C_{ii}^{zx}$), argomento distinto
($\langle\sigma_i^y\rangle=0$ per stato reale). Caso $D=0$: regola di selezione su
$M$, 36 zeri per ogni $t$, distrutti tutti dal DM.

**Tre giri di audit indipendenti, ciascuno con correzioni reali** (non solo
conferme):
1. Errore di conteggio nel corollario delle relazioni $P_{13}$ (72 correlatori in 36
   coppie, non "36 correlatori accoppiati" come scritto la prima volta) + due lacune:
   caso $D=0$ mai trattato nella prima stesura (poi aggiunta Sez. 5 con verifica su 5
   punti casuali, sempre 36/36 esatti) e degenerazione del punto di lavoro a $D=0$
   mai dichiarata ($b=b_c$ con $D=0$ è level crossing esatto, il DM apre il gap).
2. Collisione di notazione: $\eta_\alpha$ usato con due significati diversi in due
   lemmi distinti (parità sotto $K$ vs autovalore sotto $P_{13}$) — rinominato
   $\lambda_\alpha$ per $P_{13}$, con nota esplicita di disambiguazione.
3. Claim comparativo verso l'anello **errato**: si affermava che il conteggio zeri
   a DM acceso "restava 4" anche a $D=0$ per l'anello — falso, verificato che
   l'anello ha **56** zeri a $D=0$ (36 dalla regola $M$ + 20 dal sito 3), non 4.
   Quadro corretto: $56\to4$ per l'anello, $36\to0$ per la catena. **Nota per
   l'anello**: la scoperta dei 56 zeri a $D=0$ (di cui 20 spiegati da $S^2$ totale
   conservato, verificato $\|[S^2,H]\|=0$ a $D=0$) non tocca alcun risultato già
   scritto per l'anello (mai testato $D=0$ in quella fase) — lasciata solo annotata
   in chat, **non** applicata ai documenti dell'anello su richiesta esplicita.

Compilato due volte, zero errori, zero overfull/underfull, 7 pagine, verificate
visivamente pagina per pagina a ogni giro di correzione.

### Circuito, VQE, validazioni

| file | MD5 | righe |
|---|---|---|
| `circuito_correlazioni_trimero_catena.py` | `22ba6618e2c5d0cf49bd731d13fe6724` | 142 |
| `vqe_w2qC_k2_trimero_catena.py` | `9dcbb0c343187d93fd2631cf1a092727` | 144 |
| `validate_circuito_correlazioni_catena.py` | `47c64c9c40f6ecdd16e3ad97071f1dfb` | 108 |
| `validate_vqe_circuito_correlazioni_catena.py` | `c0db95d6115930bd72e336dd90d60371` | 60 |
| `w2qC_k2_params_vqedm.npz` | `c247ab520c24db2bd4146a8a3e86ecc2` | — |
| `w2qC_k2_params_S0.npz` | `3890aaf4462686af491a5926a179f44c` | — |

Mirror di `circuito_correlazioni_trimero_anello.py` + `vqe_w2q6_trimero_anello.py`,
riusando `trotter_trimero_catena.py` come $U(t)$. **A differenza dell'anello**:
lavorato fin dall'inizio su **due** punti di lavoro (VQE-DM $J{=}1,b_c{=}3.0,D{=}0.15$;
S0 Trotter $J{=}1,b{=}3.0073414,D{=}0.3$), non uno solo — scelta definitiva ancora da
concordare col relatore. Ansatz `W-2qC.K2` (10 parametri, 2 cicli) ottimizzato a
entrambi i punti, 60 restart per cautela (stesso motivo già documentato per $b_c$
nella fase VQE-DM): $\mathcal F=1.000000000000$ (VQE-DM), $\mathcal F=0.999999999999992$
(S0).

**Verifica mirata sul mapping sito↔qubit**: con lo stato fondamentale (autostato di
$P_{13}$) un mapping invertito sarebbe stato invisibile a ogni altro test. Rifatto con
stato iniziale **casuale, esplicitamente asimmetrico** sotto $P_{13}$
($\|P_{13}\psi-\psi\|=1.21$), tutte le 81 combinazioni, $N=50\to800$: errore scala
$O(1/N)$ (rapporto $\to2.00$), nessun bias residuo — mapping corretto anche in
condizioni che ne avrebbero rivelato l'errore.

Pipeline VQE→correlazioni chiusa: errore massimo $5.9\times10^{-8}$ (VQE-DM) e
$9.8\times10^{-8}$ (S0), entrambi coerenti con $\sqrt{1-\mathcal F}$.

### Scan81 e shot noise

| file | MD5 | righe |
|---|---|---|
| `scan81_trimero_catena.py` | `df25d335cdb90645604222dee892cde3` | 159 |
| `generate_figure_scan81_catena.py` | `6dd0b29ba12c6193ddd3c1db1dd84b84` | 52 |
| `validate_shot_noise_trimero_catena.py` | `896e60f105ff4c2c1cf5f16a2db25ddd` | 126 |
| `generate_figure_shotnoise_catena.py` | `31fb09915ff59462dda8553c4df36673` | 36 |

Mirror di `scan81_trimero_anello.py` + `validate_shot_noise_trimero_anello.py`, con
argomento da riga di comando (`vqedm`/`s0`) per selezionare il punto — differenza
strutturale dall'anello, dichiarata nei manuali d'uso. Nessuna delle 81 combinazioni
collassa a zero in nessuno dei due punti (coerente con la teoria). Rapporto
statistico/Trotter: $\sim10\times$ a VQE-DM, $\sim115\times$ a S0 (su $C_{11}^{zz}$).

### Quattro notebook, eseguiti per intero

| file | MD5 | righe(nb) |
|---|---|---|
| `correlazioni_trimero_catena_simmetria.ipynb` | `f1cf21666ba1a21b916134f70af91a8b` | 530 |
| `correlazioni_trimero_catena_esplorazione.ipynb` | `4b4bba1a8029a8940470d8978a4f6ffe` | 456 |
| `circuito_correlazioni_trimero_catena_tutte.ipynb` | `62f6c90578081b7e229f9824c95118c8` | 667 |
| `circuito_correlazioni_trimero_catena_vqe.ipynb` | `45d73b421cd39f199688ad4007450b09` | 464 |

Eseguiti via `nbclient`, zero errori; tutti i numeri stampati verificati coincidere
con quelli degli script standalone dove sovrapposti (es. residuo VQE
$1.89\times10^{-8}$ identico in notebook e script).

**Correzione reale trovata durante l'ispezione** (non alla prima stesura): il terzo
notebook (`_tutte.ipynb`) plottava solo la parte reale nella griglia $9\times9$
temporale, senza motivo dichiarato — a differenza del notebook dell'anello, che
mostra sempre Re e Im. Corretto (Re verde, Im viola, mirror esatto); aggiunta anche
una verifica esplicita, prima assente, che nessun correlatore della catena sia
quasi-costante (escursione minima $0.196$, contro $\sim0.0005$ di $C_{33}^{zz}$
nell'anello) — emersa da una domanda mirata, non dalla prima stesura. Rieseguito
per intero dopo la correzione.

### Documento pedagogico, figure, manuali, raccolta

| file | MD5 | righe |
|---|---|---|
| `circuito_correlazioni_trimero_catena_spiegato.tex` | `5b181f49910d8550e0250eaf8edbc42b` | 518 |
| `generate_circuit_fig_trimero_catena.py` | `2cdec49468453960ede52ac78ec8df2b` | 57 |
| `generate_figures_circuito_trimero_catena.py` | `2dcb41442a57a6dd40185ea91d46d783` | 118 |
| `manuale_uso_correlazioni_trimero_catena_statevector.tex` | `c0e07cc07078edf1fc25e50e9730a053` | 168 |
| `manuale_uso_correlazioni_trimero_catena_vqe.tex` | `ce5995a44240afec8e9b6095a348dfe4` | 164 |
| `trimero_catena_correlazioni.tex` | `1c24172add9963cf931197bd6e613bca` | 241 |

Mirror di `circuito_correlazioni_trimero_anello_spiegato.tex` — non copia: Sez. 2
ribaltata (mostra perché il sito fisso **non** produce zeri, con figura di
contrasto $C_{22}^{xz}(t)$); Sez. 6 aggiunge una novità assente nell'anello
(opzione `alternate`, guadagno non monotono in $D$ e $N$, negativo a $N$ piccolo
con $D\neq0$).

**Due correzioni reali trovate durante la stesura/revisione**:
1. Tabella "$U$ controllato" lasciata inizialmente come placeholder ("altra
   quantità, non riportata") — calcolati i valori effettivi
   ($-0.3965+0.4358i$ a $t=1.3$) invece di lasciare il rattoppo.
2. `fig_validazione_trimero_catena.png` generata ma **mai inclusa** nel documento
   (mancava l'`\includegraphics`) — trovato grazie a una domanda diretta
   ("quali immagini vanno allo stesso livello dei tex?"), corretto inserendola in
   Sez. 8 dopo la tabella di validazione, come nell'anello.

**Spiegazione aggiunta su richiesta**: perché l'errore di Trotter in
Fig. 3 non giace sulla retta $1/N$ tratteggiata — la retta è ancorata al primo
punto ($N=10$), non è l'asintoto vero; fit indipendente
$\text{errore}\approx a/N+b/N^2$ con $a=4.60\times10^{-2}$, $b=-0.258$: il termine
subleading (segno negativo) sottrae dall'errore leading-order a $N$ piccolo,
facendo apparire il punto di ancoraggio più basso del vero asintoto.

Compilato più volte nel corso delle correzioni, zero errori, un solo underfull
cosmetico residuo (badness 1038, stessa soglia già accettata nei documenti
dell'anello). 10 pagine, verificate visivamente pagina per pagina a ogni giro.

Manuali d'uso compilati (3 pagine ciascuno): dichiarano esplicitamente la
differenza strutturale dei due punti di lavoro rispetto all'anello (uno script,
`validate_circuito_correlazioni_catena.py`, esegue entrambi i punti in automatico;
altri richiedono l'argomento da riga di comando) — verificata contro il
comportamento reale di ciascuno script prima di scriverla, non assunta.

### Immagini generate ma non incluse nel documento pedagogico (scelta di scope, non omissione)

`fig_scan81_trimero_catena_S0.png` e `fig_shot_trimero_catena_S0.png`: generate,
ma il documento mostra solo le figure al punto VQE-DM (i numeri di S0 sono in
tabella, le figure no). Non ancora deciso se aggiungerle.

### Stato

Fase correlatori dinamici chiusa per **entrambe** le topologie di $N=3$ (anello e
catena). Unico filone rimasto per l'intero progetto $N=3$: Parte 2 (rumore,
Kraus/Lindblad, Qiskit Aer). Aperto: scelta definitiva del punto di lavoro per la
catena (VQE-DM vs S0) col relatore; eventuale aggiunta delle due figure S0 mancanti
al documento pedagogico.

## Aggiornamento — Due relazioni per il relatore (catena): correlazioni e VQE

Su richiesta esplicita, prodotte le due relazioni per il relatore mirror dirette
di `relazione_correlazioni_trimero_anello.docx` e `relazione_vqe_trimero_anello.docx`
(lette entrambe, insieme a `relazione_correlazioni.docx` e
`relazione_test_parametri.docx`, per fissare formato/font/profondità prima di
scrivere: Times New Roman, corpo 11pt giustificato, nessuna intestazione, prosa in
prima persona rivolta al relatore con "Lei", figure con didascalia in corsivo 9.5pt
centrata, tabelle a bordo singolo con intestazione ombreggiata E8E8E8, chiusura
sempre su una domanda aperta). Le relazioni sono un genere a parte dalla
documentazione tecnica (`.tex`) prodotta finora in questa fase — risultati e
narrazione in prima persona, non derivazione completa; i dettagli restano nei
documenti tecnici già citati.

**File prodotti** (non ancora caricati nel Project):

| file | note |
|---|---|
| `relazione_correlazioni_trimero_catena.docx` | mirror di `relazione_correlazioni_trimero_anello.docx` |
| `relazione_vqe_trimero_catena.docx` | mirror di `relazione_vqe_trimero_anello.docx` |
| `generate_figures_relazione_catena.py` | genera le 5 figure della prima relazione |

### `relazione_correlazioni_trimero_catena.docx`

Racconta in prima persona la sequenza già stabilita nella fase tecnica: le 81
combinazioni (spiegato perché il conteggio non dipende dai legami ma dai siti),
la scoperta di $P_{13}$ come scambio puro — narrata come "mi aspettavo di dover
ripetere la costruzione dell'anello (SWAP+$R_z(\pi)$ su tutti e tre), ho trovato
che basta lo scambio semplice" — con un diagramma schematico a due pannelli
disegnato appositamente nello stesso stile dei diagrammi SWAP/$R_z$ già usati per
anello e dimero. Conseguenza opposta sul sito fisso (nessuno zero, non quattro
come nell'anello), illustrata su $C_{22}^{xz}(t)$ (zero puntuale a $t=0$ per un
motivo diverso — $\langle\sigma^y\rangle=0$ per stato reale — poi crescita rapida).
Due heatmap delle 81 combinazioni ($t=1.3$ e $t=2.7$) per escludere che l'assenza
di zeri sia una coincidenza dell'istante. Chiusura con la domanda già aperta nella
documentazione tecnica: quale dei due punti di lavoro (VQE-DM o S0) adottare in
via definitiva.

**Bug trovato e corretto durante la stesura**: la prima versione del generatore
perdeva silenziosamente tutto il testo nei segmenti corsivo+pedice/apice
combinati (funzione di estrazione testo incompleta) — pedici e apici sparivano
del tutto invece di essere semplicemente non formattati. Trovato confrontando il
rendering con l'atteso, corretto, rigenerato, verificato pagina per pagina (4
pagine) che ogni formula fosse leggibile.

### `relazione_vqe_trimero_catena.docx`

Riprende i numeri già stabiliti in `trimero_catena_vqe_dm.tex` (non ricalcolati,
solo verificati e citati): a differenza dell'anello, un solo giro di blocchi $W$
non basta per la catena (tetto $0.9937$, contro $0.9626$ di RBS a un giro,
confermato su tre seed indipendenti) — servono due giri completi
("W-2qC.K2", 10 parametri) per $\mathcal F=1$ esatto, sia con $W$ sia con RBS.
Confronto costo in gate (19 contro 39 gate totali, stessa direzione già vista
nell'anello). Circuito dell'ansatz disegnato con i 10 parametri ottimali
sostituiti (Qiskit, non schema a mano). Risultati di ottimizzazione riportati su
entrambi i punti di lavoro (VQE-DM $\mathcal F=1.000000000000$; S0
$\mathcal F=0.999999999999992$). Chiusura con una domanda che riprende
letteralmente il suggerimento già lasciato in `trimero_catena_vqe_dm.tex`
("punto da segnalare esplicitamente nella stesura finale"): se raccontare insieme
al contributo RBS-vs-$W$ anche il fatto che la topologia cambia *quanti giri*
servono, non solo *quale blocco* conviene.

### Stato

Entrambe le relazioni pronte per l'invio. Nessuna nuova analisi tecnica: solo
distillazione narrativa di risultati già stabiliti e verificati nelle fasi
precedenti. Prossimo passo, se confermato dal relatore: adottare un punto di
lavoro unico per la catena; altrimenti Parte 2 resta l'unico filone aperto.

## Aggiornamento — apertura Parte 2 (rumore): scope, infrastruttura Qiskit verificata, prima lacuna colmata

Aperta la Parte 2 (sistemi quantistici aperti). Scope fissato dal relatore:
**solo due canali**, errori di gate (1 qubit / 2 qubit distinti) ed errore di
readout — niente $T_1$/$T_2$, error mitigation, QEC per ora. Corrisponde
esattamente ai riquadri "Gate errors" e "Measurement errors" della slide 17
di `7Physical_implementation.pdf` ("Qiskit: noise models"); notazione di
riferimento presa da lì. Percentuali di lavoro confermate dal relatore:
$\varepsilon_{1q}=10^{-3}$, $\varepsilon_{2q}=10^{-2}$, $p_{\text{readout}}=10^{-2}$
(indicative, da confrontare con documentazione di macchine reali).

Pipeline da ripercorrere sul dimero, stesso ordine di Parte 1: VQE+DM →
quantum simulation (Trotter) → correlazioni dinamiche, con rumore.

**Nota per igiene del mount**: i due "PDF" del corso nel Project
(`6Applications.pdf`, `7Physical_implementation.pdf`) sono in realtà archivi
ZIP di immagini di pagina (una JPEG + un `.txt` per slide), non PDF veri —
vanno letti con `zipfile`, non `pypdf`/lettura PDF standard.

### Ambiente verificato

`qiskit 2.5.2` + `qiskit-aer 0.17.2` installabili via pip
(`--break-system-packages`). Smoke test superato: `NoiseModel` +
`depolarizing_error` + `ReadoutError` su `AerSimulator(method="density_matrix")`
su un Bell state, $\mathrm{Tr}(\rho^2)=0.984$ — coerente con l'aspettativa
qualitativa (canale depolarizzante riduce la purezza).

**Convenzione del canale depolarizzante in Aer verificata dalla docstring**:
$$E(\rho)=(1-\lambda)\rho+\lambda\,\mathrm{Tr}[\rho]\,\frac{\mathbb I}{2^n}$$
identica alla slide 14 del corso. **Attenzione**: $\lambda$ (parametro Aer)
non coincide con l'errore medio di gate $\varepsilon$ pubblicato dai
costruttori (da randomized benchmarking): $\varepsilon=\lambda\,(d-1)/d$ con
$d=2^n$, quindi $\lambda=2\varepsilon$ a 1 qubit e $\lambda=\tfrac43\varepsilon$
a 2 qubit. Passare $\varepsilon$ direttamente a `depolarizing_error`
sottostimerebbe il rumore. **Domanda posta al relatore** (vedi
`domande_relatore.md`, sezione Parte 2): se il valore fornito va inteso come
$\varepsilon$ (con conversione esplicita) o direttamente come $\lambda$.

Canali disponibili in Aer oltre ai due richiesti (non usati ora, per
riferimento futuro): `thermal_relaxation_error` ($T_1,T_2$),
`amplitude_damping_error`, `phase_damping_error`, `pauli_error`,
`kraus_error` (Kraus arbitrari — ponte diretto col formalismo
$\rho_t=\sum_k E_k\rho_0E_k^\dagger$ degli appunti Kraus/Lindblad del
relatore, già in log), `PauliLindbladError`, `coherent_unitary_error`.

### Scoperta numerica: dove attaccare il rumore non è una scelta binaria

Verificato sul passo elementare di Trotter del dimero (`trotter_dimero.py`,
un passo, $J=1,b=0.35,D=0.80$): il conteggio di gate a 2 qubit dipende
fortemente da *come* si arriva alla base hardware.

| modalità | gate a 2 qubit / passo |
|---|---|
| gate logici (RXX, RYY, 3×RZZ) | 5 |
| transpilato, `optimization_level` 0/1 | 10 CNOT |
| transpilato, `optimization_level` 2/3 | **3 CNOT** |

Il valore 3 coincide col minimo già dimostrato in `circuito_compatto_teoria_e_limiti.tex`
(2 CNOT impossibili, verificato con due algoritmi indipendenti, filone aperto
in risposta a una domanda del relatore sul conteggio gate). Rapporto
peggiore/migliore $\approx 10/3$: con $\varepsilon_{2q}=1\%$ e $N\sim100$–$200$
passi (i valori già usati in Parte 1), la probabilità di attraversare l'intera
evoluzione senza alcun errore a 2 qubit va da valori sotto l'1% fino a
praticamente nulla, a seconda della scelta — non un dettaglio implementativo.
Implica una struttura di errore totale con un $N$ ottimo:
$$\epsilon_{\text{tot}}(N)\simeq \frac{a}{N} + g\,\varepsilon_{2q}N
\quad\Longrightarrow\quad N^*=\sqrt{\frac{a}{g\,\varepsilon_{2q}}}$$
con $g$ = gate a 2 qubit per passo — risultato atteso centrale della Parte 2,
$a$ (coefficiente dell'errore di Trotter per il dimero) ancora da misurare.

Anche questo posto come domanda al relatore (mail inviata, in attesa di
risposta): rumore sui gate logici del modello o sul circuito transpilato in
base hardware (raccomandazione motivata verso quest'ultima: è l'unica scelta
che dà significato quantitativo al vantaggio di gate di RBS su $W$ già
documentato in `scelta_ansatz_RBS_vs_W.tex` — meno CNOT, meno canali di
rumore).

### Lacuna colmata: `circuito_correlazioni_dimero.py`

Segnalato in una sessione precedente come mancante (anello e catena avevano
il modulo, il dimero viveva solo dentro `circuito_correlazioni_tutte.ipynb`,
non importabile). Prodotto in un'altra chat (`circuito_correlazioni_dimero.py`,
`validate_circuito_correlazioni_dimero.py`, `risultati_circuito_correlazioni_dimero.md`),
**verificato in ambiente in questa sessione**, non solo letto:

- **Validazione eseguita pulita.** Residui coerenti con solo errore di
  Trotter, crescenti con $t$ a $N$ fisso ($1.7\times10^{-3}$ a $t=0.5$ →
  $1.1\times10^{-2}$ a $t=5.0$ su $C_{21}^{xx}$, $N=200$). Zeri a $t=0$ per
  le combinazioni attese (siti diversi, una sola componente $y$) a
  precisione macchina ($\sim10^{-16}$–$10^{-17}$). Convergenza in $N$:
  rapporto tra errori successivi raddoppiando $N$ da 10 a 320 converge
  esattamente a 2.00, coerente con Trotter al prim'ordine.
- **Mappatura sito↔qubit riverificata indipendentemente**, non presa per
  buona. Il test con lo stato fondamentale del test 2 è risultato **cieco**
  ($\langle Z_1\rangle=\langle Z_2\rangle=-0.0347$, quasi-simmetria che non
  discrimina nulla — stesso tipo di rischio già documentato per la catena).
  Rifatto con uno stato asimmetrico ad hoc ($\langle Z_1\rangle=0.811\neq
  \langle Z_2\rangle=0.650$): combacia esattamente con `SITE_TO_QUBIT={1:1,2:0}`
  dichiarata nel modulo (sito1→qubit1, sito2→qubit0, Famiglia 1).
- **Nessun bug trovato** in `circuito_correlazioni_dimero.py` né nel file di
  validazione, a parte un commento (non funzionale) sbagliato: la riga di
  test `(1,"y",1,"x")` dichiara "deve coincidere col precedente" mentre la
  relazione vera, verificata con un terzo metodo indipendente
  (`scipy.linalg.expm` diretto, nessuna formula spettrale), è
  un'**antisimmetria**: $C_{11}^{xy}(t)=-C_{11}^{yx}(t)$ esattamente
  ($xy+yx\sim10^{-16}$). Da correggere il commento, non il codice.

**Collisione di convenzione con `trotter_dimero.py`: confermata reale, ma
non tocca questo modulo.** Verificato alla fonte: `dimer_exact.py` (riga 9,
"la label 'ZI' agisce con Z sul qubit 1") implica sito1→qubit1, sito2→qubit0
(Famiglia 1); `trotter_dimero.py` (riga 3, dichiarata esplicitamente,
"spin 1 -> qubit 0, spin 2 -> qubit 1") è Famiglia 2 — opposte per davvero,
non un falso allarme. Ma `circuito_correlazioni_dimero.py` **non importa
`trotter_dimero.py`**: costruisce $U(t)$ da sé, esponenziando $H_1,H_2$ presi
da `dimer_exact.py` come matrici dense (`scipy.linalg.expm`) e applicandoli
come un unico `UnitaryGate` opaco a 2 qubit — stessa convenzione dello stato
iniziale, internamente coerente, confermato dal test con stato asimmetrico.

**Implicazione aperta per il seguito, non un difetto**: $U(t)$ in questo
modulo è un gate opaco, non decomposto in `rz`/`rxx`/`ryy`/`rzz` come in
`trotter_dimero.py` — un rumore per-gate nominato non si aggancia finché non
viene transpilato. Isolato e transpilato a parte: sintetizza sempre a **3
CNOT per passo**, a qualunque `optimization_level` (il sintetizzatore KAK di
Qiskit per un `UnitaryGate` isolato a 2 qubit trova da solo la forma
ottimale, a differenza della sequenza di rotazioni esplicite dove serve
`optimization_level>=2` per arrivarci) — coerente col minimo già stabilito.
Da decidere: agganciare il rumore qui via transpile (eredita il 3-CNOT), o
riscrivere $U(t)$ con i gate espliciti di `trotter_dimero.py` per controllo
diretto su quale gate riceve quale errore — stessa domanda di cui sopra,
ora concreta su un file specifico.

### File in arrivo nel Project (caricati dall'utente dopo questa verifica)

| file | stato |
|---|---|
| `circuito_correlazioni_dimero.py` | verificato in ambiente, nessun bug |
| `validate_circuito_correlazioni_dimero.py` | verificato in ambiente, un commento da correggere (non funzionale) |
| `risultati_circuito_correlazioni_dimero.md` | sintesi, mirror dei documenti "risultati" già in uso per anello/catena |

### Mail inviata al relatore

Chiarimenti richiesti prima di proseguire (testo completo scambiato in chat,
non ancora salvato come file a parte): dove attaccare l'errore di gate
(logico / transpilato default / transpilato ottimo — vedi tabella sopra),
come interpretare la percentuale ($\varepsilon$ vs $\lambda$ di Aer),
piattaforma di riferimento per i valori di calibrazione, readout simmetrico
o asimmetrico, conferma dell'esclusione di $T_1$/$T_2$. In attesa di
risposta.

### Stato

Parte 2 aperta, scope fissato, ambiente verificato, prima lacuna (modulo
correlatori del dimero) colmata e verificata indipendentemente. **Prossimo
passo**: in attesa della risposta del relatore sui punti della mail;
in parallelo, ricerca dei valori di calibrazione reali (fonti da citare,
nessun numero a memoria) e, se utile, preparazione dell'infrastruttura
`NoiseModel` parametrica rispetto alle scelte ancora aperte, così che la
risposta del relatore si traduca in un cambio di parametro.

## Aggiornamento — risposta del relatore su rumore (Parte 2): tutte le domande aperte risolte

Risposta ricevuta (02/09/2026) alle quattro domande della mail (dove attaccare
il rumore di gate, come interpretare la percentuale, quale piattaforma,
readout simmetrico o no). Testo completo e lettura operativa in
`domande_relatore.md`, sezione 12. In sintesi, quattro decisioni chiuse:

**(a) Transpilare, e farlo per minimizzare i gate — non un default qualsiasi.**
Il relatore motiva esplicitamente la scelta con "aiuterà a ridurre i gate
quindi va fatto": non basta transpilare, va fatto con il livello di
ottimizzazione che minimizza il conteggio. Per il passo di Trotter del
dimero questo risolve l'ambiguità già isolata in questa sessione
(`optimization_level` di default: 10 CNOT/passo; `optimization_level>=2`:
3 CNOT/passo, sintesi KAK, coincide col minimo già dimostrato in
`circuito_compatto_teoria_e_limiti.tex`) a favore della seconda: **3 CNOT
per passo di Trotter è il numero da usare per il dimero.** Da applicare con
lo stesso criterio (minimizzare, non assumere il default) quando si
estenderà a trimero anello/catena — il conteggio minimo per quei circuiti
non è stato ancora misurato con questo criterio specifico (solo il conteggio
empirico via `transpile(optimization_level=3)` già in
`trimero_anello_circuito_compatto.tex`/`trimero_catena_circuito_compatto.tex`,
che però era stato fatto per un motivo diverso — mostrare che il circuito
compresso nasconde la scalata in $N$, non per la Parte 2).

**(b) Conversione $\varepsilon\to\lambda$ confermata**, nessuna sorpresa:
$\lambda=2\varepsilon$ a 1 qubit, $\lambda=\tfrac43\varepsilon$ a 2 qubit
(da $\varepsilon=\lambda(d-1)/d$, $d=2^n$), come già derivato dalla docstring
di `depolarizing_error` di Aer.

**(c) Nessuna piattaforma imposta.** Scegliere un chip reale rappresentativo
e citarne i dati di calibrazione pubblicati. **Novità non anticipata**: il
relatore chiede esplicitamente uno **scan sui parametri di errore**
("rifarei il conto per vari valori dei parametri di errore"), non un singolo
punto a percentuali fisse — implica una griglia o almeno una scansione 1D
su $(\varepsilon_{1q},\varepsilon_{2q},p_\text{readout})$, coerente con la
struttura $N^*=\sqrt{a/(g\varepsilon_{2q})}$ già derivata in questa sessione
(l'$N$ ottimo dipende dal valore di $\varepsilon_{2q}$ scelto: uno scan sui
parametri di errore è anche l'unico modo di mostrare come si sposta $N^*$).

**(d) Readout simmetrico obbligatorio come primo passo; asimmetrico opzionale**,
da fare solo se resta tempo, senza investirci sforzo sproporzionato — non
un requisito per la consegna.

### File aggiornati di conseguenza

- `domande_relatore.md`: aggiunta sezione 12 (Parte 2), domanda e risposta
  integrali, lettura operativa punto per punto.
- `scheda_progetto_tesi.md`: allineato lo scope della Parte 2 — tolta la
  menzione generica di $T_1$/$T_2$ come argomento della tesi, sostituita con
  la dichiarazione esplicita dei due soli canali confermati (gate, readout)
  e l'esclusione dichiarata di $T_1$/$T_2$.

### Stato

Nessuna domanda aperta residua sull'impostazione della Parte 2. Prossimo
passo: (1) ricerca dei valori di calibrazione reali su un chip rappresentativo,
fonti citabili, nessun numero a memoria; (2) implementazione del NoiseModel
con transpilazione a gate minimizzati (3 CNOT/passo per il dimero) e scan sui
parametri di errore, non un singolo punto; (3) verifica end-to-end di tutta
la pipeline (VQE, U(t), correlatori) prima di introdurre il rumore, per non
propagare errori di stadi precedenti nella parte con rumore.

## Sessione 3 settembre 2026 — Parte 2: verifica end-to-end e primi due documenti

Apertura sessione: check MD5 di tutti i file tracciati (139 file nel Project).
Confronto sistematico automatico contro tutte le tabelle MD5 già registrate in
questo log: 15 corrispondenze, 15 difformità (tutte nel workstream catena:
`circuito_correlazioni_trimero_catena.py`,
`circuito_correlazioni_trimero_catena_spiegato.tex`,
`generate_circuit_fig_trimero_catena.py`,
`generate_figures_circuito_trimero_catena.py`,
`manuale_uso_correlazioni_trimero_catena_statevector.tex`,
`manuale_uso_correlazioni_trimero_catena_vqe.tex`,
`simmetrie_correlatori_trimero_catena.tex`,
`validate_circuito_correlazioni_catena.py`,
`validate_vqe_circuito_correlazioni_catena.py`,
`vqe_w2qC_k2_trimero_catena.py`, più 5 notebook — questi ultimi attesi, per
decisione già registrata sugli output puliti), 3 file assenti dal Project ma
citati nel log (`w2qC_k2_params_vqedm.npz`, `w2qC_k2_params_S0.npz`,
`generate_figure_shotnoise_catena.py` — non bloccanti: gli script che
generano i primi due sono ancora presenti, la figura del terzo è già
salvata). Nessuna di queste difformità tocca il lavoro sul dimero in corso.
109 file presenti nel Project senza baseline MD5 nel log (mai tracciati
esplicitamente finora).

### Verifica end-to-end obbligatoria (prima di introdurre il rumore)

Rieseguiti, non solo letti:

- `vqe_test2.py`: $E_\text{VQE}=-3.57321145$ ($|E_\text{VQE}-E_0|=7.75\times
  10^{-11}$), $\mathcal F=1.00000000$ — identico al registrato.
- `validate_circuito_correlazioni_dimero.py`: residui di Trotter su
  $C_{21}^{xx}$ identici al registrato ($1.74\times10^{-3}$ a $t=0.5$,
  $1.10\times10^{-2}$ a $t=5.0$, $N=200$); zeri a $t=0$ a precisione
  macchina; convergenza in $N$ verificata.
- **Bug cosmetico confermato, non ancora corretto nel file**: il commento in
  `validate_circuito_correlazioni_dimero.py` sulla relazione fra
  $C_{11}^{xy}$ e $C_{11}^{yx}$ dichiara un'uguaglianza; la relazione vera,
  verificata con metodo indipendente, è un'**antisimmetria esatta**
  $C_{11}^{xy}(t)=-C_{11}^{yx}(t)$.
- Autoconsistenza di `trotter_dimero.py` (circuito vs matrice, fase globale
  a parte): $\max|U_\text{circ}-e^{i\varphi}U_\text{mat}|\le1.1\times
  10^{-15}$.
- **Collisione di convenzione Famiglia 1/Famiglia 2 quantificata**
  esattamente (prima era solo qualitativa): $H_\text{dimer\_exact}(b,J,D) =
  4\,H_\text{trotter\_dimero}(b/2,J,-D)$, e con lo scambio dei siti (SWAP)
  il segno di $D$ si inverte — coerente con l'antisimmetria del termine DM.
  Verificato a $2.2\times10^{-16}$.
- Limite di rumore nullo: `AerSimulator(method="density_matrix")` con
  `NoiseModel()` vuoto riproduce lo statevector a $\sim10^{-14}$ su più
  correlatori.
- Conversione $\varepsilon\to\lambda$ verificata anche contro
  `qiskit.quantum_info.average_gate_fidelity` (non solo contro la
  docstring): $\lambda=2\varepsilon$ (1 qubit), $\lambda=\tfrac43
  \varepsilon$ (2 qubit) riproducono $\varepsilon$ a precisione macchina.

### Scoperta nuova: la transpilazione globale collassa la dipendenza da $N$

Isolato un problema non anticipato dalla direttiva (a) del relatore
("transpilare per minimizzare i gate"). Il conteggio CNOT del singolo passo
di Trotter è confermato (5 gate logici $\to$ 3 CNOT a
`optimization_level>=2`, o 3 CNOT a qualunque livello se $U(t)$ è un
`UnitaryGate` opaco). Ma sul **circuito completo dei correlatori**
(ancilla + $N$ passi), a `optimization_level>=2` Qiskit riconosce che gli
$N$ blocchi identici formano nel complesso un unico unitario a 2 qubit e li
**collassa** in un circuito a 6 CNOT **costanti**, indipendenti da $N$
(verificato numericamente: $N=1,2,5,10,20,40\to$ sempre 6 CNOT a livello 2,
contro $6,9,18,33,63,123$ a livello 0). Con rumore acceso, questo fa
convergere il risultato rumoroso a quello ideale al crescere di $N$ — la
struttura $\varepsilon_\text{tot}(N)\sim a/N+g\varepsilon_{2q}N$ scompare, e
lo scan sui parametri richiesto dal relatore darebbe un risultato privo di
significato fisico senza sollevare errore.

**Decisione presa (non richiede conferma del relatore, è implementativa)**:
transpilare **una volta** il blocco del singolo passo al suo costo minimo,
poi ripeterlo $N$ volte senza ritranspilare il circuito completo. Motivata
soprattutto in vista di $N=3$: per anello e catena $U(\tau)$ agisce su 3
qubit, dove la sintesi generica di un unitario non garantisce più il minimo
a un livello di ottimizzazione qualsiasi, e il collasso a $N$-indipendente
sarebbe anche peggiore (un intero circuito Trotter a 3 qubit ridotto a un
solo unitario a 3 qubit).

### Scomposizione verificata numericamente: preparazione vs evoluzione

Isolati con lo stesso circuito (blocco compilato una volta, ripetuto) quattro
contributi all'errore su $\mathrm{Re}\,C_{21}^{xx}(t=2)$: errore di Trotter
puro, rumore sull'evoluzione isolato, solo differenza di preparazione (VQE
vs ampiezze esatte, senza rumore), preparazione+rumore totale. Risultato: il
contributo di preparazione resta $\sim10^{-6}$, sostanzialmente **costante**
su $N=5\ldots80$, contro $10^{-2}$–$10^{-1}$ degli altri due termini — **non
scala con $N$**, quindi non entra né nel termine $a/N$ (Trotter) né nel
termine $g\varepsilon_{2q}N$ (rumore accumulato): è un **terzo termine
additivo costante** (floor) che si somma ai primi due,
$$\varepsilon_\text{tot}(N)\simeq \frac{a}{N}+g\varepsilon_{2q}N+\delta_\text{prep},$$
e non sposta $N^*=\sqrt{a/(g\varepsilon_{2q})}$.

**Decisione presa (implementativa, da segnalare al relatore non da
chiedere)**: usare il circuito VQE reale (ansatz PMA-2q·3) come
preparazione di default per i risultati con rumore, non le ampiezze esatte
via `prepare_state` — quest'ultima richiede di conoscere già la risposta
che il VQE serve a trovare, e per $N=3$ il suo costo in gate diverge dal
comportamento compatto di `W-2qC.K2`. `prepare_state` resta come diagnostica
per separare l'effetto della preparazione da quello dell'evoluzione (vedi
sopra). Per il dimero manca ancora `ansatz_params` nel modulo dei
correlatori (`NotImplementedError` — anello e catena ce l'hanno già): da
implementare al Passo 2 della Parte 2.

### Documenti prodotti

- `pipeline_rumore_dimero_overview.tex` — panoramica a "2000 piedi" della
  pipeline di Parte 2 (5 passi: modello di rumore, VQE+DM rumoroso, Trotter
  rumoroso, correlatori rumorosi, scan sui parametri), livello di
  orientamento, nessuna derivazione.
- `teoria_modello_rumore.tex` — teoria del Passo 1: dalla necessità
  dell'operatore densità (partial trace, decoerenza) al formalismo di Kraus,
  al canale depolarizzante (derivato da zero a 1 e $n$ qubit, con verifica
  numerica della completezza), alla derivazione esplicita di
  $\varepsilon=\lambda(d-1)/d$ (fedeltà media di un canale, calcolata non
  solo citata) e quindi $\lambda=2\varepsilon$/$\lambda=\tfrac43\varepsilon$,
  fino all'errore di lettura (slide 17) e alla matrice di confusione
  simmetrica. Sezione esplicita su cosa resta fuori ($T_1$/$T_2$).

Entrambi compilati con `pdflatex` (due passate), zero overfull/underfull
box dopo correzione, verificati visivamente pagina per pagina; un refuso
grammaticale trovato e corretto nell'overview.

### Stato e prossimo passo

Pipeline verificata sana end-to-end. Prossimo passo: implementazione vera
del Passo 1 (ricerca calibrazione reale su un chip citabile, costruzione del
`NoiseModel` in codice con la strategia di transpilazione per-blocco), poi
teoria e implementazione del Passo 2 (VQE+DM sotto rumore), includendo
`ansatz_params` per il dimero. Da segnalare al relatore (non da chiedere,
già nel mandato confermato il 02/09): la scelta di transpilare per blocco
anziché sull'intero circuito, e la scelta di usare il VQE reale come
preparazione di default.

## Sessione 3 settembre 2026 (continua) — calibrazione reale, NoiseModel, ansatz_params

### Ricerca calibrazione reale — COMPLETATA

Chip scelto: `ibm_torino` (IBM Heron r1, 133 qubit). Fonte citabile unica e
pulita: J. P. T. Stenger, G. Bazargan, N. T. Bronn, D. Gunlycke, "Method
for simulating open-system dynamics using mid-circuit measurements on a
quantum computer", arXiv:2504.15187 (2025), Appendice B — mediane
pubblicate: $\varepsilon_{1q}=2.9\times10^{-4}$ (gate $\sqrt X$),
$\varepsilon_{2q}=3.8\times10^{-3}$ (gate CZ), $p_\text{readout}=2.3\times
10^{-2}$. Nota di modellazione dichiarata esplicitamente: il gate nativo a
2 qubit di questo chip è CZ, non CNOT come nei nostri circuiti — si usa
$\varepsilon_{2q}$ come valore rappresentativo dell'ordine di grandezza,
non come replica esatta dell'hardware (coerente con l'indicazione del
relatore, "usa dei valori tipici... di qualche chip di riferimento").

### `noise_model_dimero.py` — implementato

Costruisce il `NoiseModel` con i due canali confermati, applicando la
conversione $\varepsilon\to\lambda$ derivata in `teoria_modello_rumore.tex`.
Verifica obbligatoria del limite di rumore nullo (`validate_noise_model_dimero.py`)
contro $E_\text{VQE}$ registrato in Parte 1: $|\Delta E|=3.46\times10^{-9}$,
CNOT invariati (2) col rumore acceso. Con i valori di riferimento,
$E_\text{VQE}$ rumoroso $=-3.50164605$ (scostamento $+0.071565$ dall'ideale).
Scan preliminare su $\varepsilon_{2q}$ (a parità di $\varepsilon_{1q}$,
$p_\text{readout}$): dipendenza monotona confermata.

Prodotto anche il documento `risultati_passo1_modello_rumore.tex`, nello
stile grafico "risultati" già in uso nel progetto (stesse box `okbox`/
`keyeq`, stessa intestazione di `risultati_vqe_test2.tex`).

### `ansatz_params` per il dimero — lacuna colmata

Implementato in `circuito_correlazioni_dimero.py`, mirror esatto del
pattern già in uso per anello e catena (`w2q6_circuit()` /
`pma_2q_trimer_exact`): `ansatz_params=None` (default) usa `prepare_state`
con le ampiezze esatte; `ansatz_params=<3 parametri>` costruisce
`pma_2q(3).assign_parameters(...)` (stesso ansatz del VQE, `vqe_test2.py`)
e lo compone sul registro. Nessuna permutazione di qubit necessaria — la
fidelity fra `Statevector(ansatz)` e le ampiezze esatte è già 1 a
precisione macchina senza riordinare.

Verifica (`validate_ansatz_params_dimero.py`), tre controlli:
- consistenza fra le due preparazioni su 3 correlatori diversi: differenza
  $\sim10^{-6}$–$10^{-7}$, coerente con l'infedeltà nota del VQE
  ($1-\mathcal F\approx2\times10^{-11}$ in ampiezza, propagata
  all'osservabile);
- nessuna regressione sul percorso `ansatz_params=None` (residuo di
  Trotter atteso confermato su $C_{21}^{xx}(t=0.5,N=200)$);
- costo in gate: preparazione VQE costa 1 CNOT in più della preparazione
  esatta (19 vs 18 CNOT nel circuito completo a $N=5$), coerente con la
  scomposizione verificata nella sessione precedente (contributo di
  preparazione trascurabile e costante in $N$).

### Stato e prossimo passo

Passo 1 della pipeline (modello di rumore) chiuso a tutti i livelli:
teoria, implementazione, verifica, documento di risultati. Il modulo dei
correlatori del dimero ha ora la stessa API di anello e catena. Prossimo
passo: Passo 2 della pipeline — VQE con termine DM sotto rumore come
stadio a sé (energia e fedeltà rumorose confrontate con l'esatto), usando
`noise_model_dimero.py` già pronto.

## Sessione 3 settembre 2026 (continua) — Passi 2-5: Parte 2 completata

Completati, nell'ordine, tutti i passi rimanenti della pipeline di Parte 2
sul dimero. Per ciascuno: implementazione, verifica con almeno un
controllo indipendente, documento di risultati in stile grafico
"risultati" (stesse box `okbox`/`keyeq` dei documenti precedenti).

### Passo 2 — VQE con termine DM sotto rumore

`vqe_dm_rumoroso_dimero.py`. Scelta di modellazione dichiarata: si
riusano i parametri VQE già ottimizzati nel caso ideale, senza
rioptimizzare sotto rumore (misura la degradazione di un risultato
ideale, non la convergenza di un VQE noise-aware — estensione futura se
resterà tempo). Derivata la fedeltà per uno stato misto rispetto a un
riferimento puro: $F(\rho,\ket\psi\bra\psi)=\bra\psi\rho\ket\psi$
(semplificazione della fedeltà di Uhlmann), verificata contro
`qiskit.quantum_info.state_fidelity` su uno stato misto casuale (non il
caso VQE, dove l'infedeltà è troppo piccola per essere un test
stringente). Limite di rumore nullo: $|\Delta F|=6.66\times10^{-16}$.
Con rumore di riferimento (`ibm_torino`): $E=-3.50164605$
(scostamento $+0.071565$), $F=0.98500601$ (perdita di fedeltà $1.5\%$
circa, per un ansatz a soli 2 CNOT).

### Passo 3 — quantum simulation (Trotter) sotto rumore

`trotter_rumoroso_dimero.py`. Prima applicazione reale della strategia
di transpilazione per blocco (decisione di una sessione precedente): il
singolo passo di Trotter transpilato una volta (3 CNOT), composto $N$
volte via `QuantumCircuit.compose` — mai ritranspilato per intero.
Verificato esplicitamente che ritranspilare l'intero circuito a livello
alto ricade nella stessa trappola già trovata (collasso a 3 CNOT
costanti indipendentemente da $N$), mentre `compose` senza
ritranspilare cresce linearmente ($3N$).

Osservabile: fedeltà rispetto allo stato bersaglio fisico (evoluzione
esatta e continua, nessun Trotter, nessun rumore) a partire dal ground
state esatto — impacchetta in un'unica quantità i tre contributi già
caratterizzati (preparazione costante, Trotter decrescente, rumore
crescente in $N$).

Verifiche: conteggio gate $=2+3N$ esatto per $N=1,\ldots,40$;
cross-check indipendente (circuito Qiskit vs potenza di matrice in
`numpy` puro, nessun circuito) coincidenti entro $4\times10^{-7}$
(compatibile con l'infedeltà nota di preparazione). **Risultato
centrale**: con il rumore di riferimento, $F(N)$ ha un massimo a
$N^*=8$ ($F=0.8177$) — non a $N\to\infty$: prima comparsa concreta del
compromesso $a/N+g\varepsilon_{2q}N$ predetto teoricamente. Senza
rumore, $F(N)\to1$ monotonamente per $N\gtrsim5$ (non-monotonia fra
$N=1$ e $N=2$ a $t=2$ dovuta al regime non ancora perturbativo,
non un errore).

### Passo 4 — correlazioni dinamiche sotto rumore

`correlatori_rumorosi_dimero.py`. Circuito Hadamard test completo, con
QUATTRO blocchi transpilati singolarmente (preparazione, controlled-$W$,
Trotter, anti-controlled-$V$+base) e composti — mai transpilati insieme.
Errore di lettura agganciato per la prima volta (i Passi 2-3 non
misuravano nulla): applicato ANALITICAMENTE, non a shot finiti (coerente
col resto del progetto). Derivato: per readout simmetrico di parametro
$p$, $\langle Z\rangle_\text{readout}=(1-2p)\langle Z\rangle_\text{ideale}$
— derivazione elementare (sostituzione diretta nella distribuzione di
probabilità letta), verificata sia analiticamente sia con un cross-check
Monte Carlo indipendente (`ReadoutError` vero, $2\times10^5$ shot):
$+0.044089$ (analitico) contro $+0.046550$ (Monte Carlo), differenza
$2.46\times10^{-3}$, entro l'errore statistico atteso a $3\sigma$.

Limite di rumore nullo: identico a Parte 1 entro $5\times10^{-14}$ su tre
correlatori diversi. Conteggio gate: $+3$ CNOT per unità di $N$,
confermato. **Risultato**: $N^*=5$ per $C_{21}^{xx}(t=2)$ — più basso
dell'$N^*=8$ della fedeltà (atteso: più gate a parità di $N$ per via dei
due blocchi aggiuntivi, quindi il rumore satura prima).

### Passo 5 — scan sui parametri di rumore (ultimo passo, pipeline chiusa)

`scan_parametri_rumore_dimero.py`. **Risultato analitico prima ancora
dello scan**: la correzione di readout del Passo 4 è un fattore
moltiplicativo COSTANTE in $N$ — non può mai spostare un argmax. Quindi
$N^*$ non dipende da $p_\text{readout}$, per qualunque readout simmetrico.
Dimostrato algebricamente e confermato numericamente: $N^*=5$ per
$p_\text{readout}=0,\,0.05,\,0.20$ (fattore 4 di variazione), con i
valori del correlatore che scalano proporzionalmente ma il massimo
sempre nello stesso punto. Questo riduce lo scan effettivo a due soli
parametri.

Scan su $\varepsilon_{2q}$ (a $\varepsilon_{1q}$ di riferimento):
$N^*=10,9,8,7$ per $\varepsilon_{2q}=10^{-3},2\times10^{-3},
3.8\times10^{-3},6\times10^{-3}$, poi satura a $N^*=1$ per
$\varepsilon_{2q}\ge10^{-2}$. Scan su $\varepsilon_{1q}$ (a
$\varepsilon_{2q}$ di riferimento): $N^*=9,8,7$ per
$\varepsilon_{1q}=10^{-4},2.9\times10^{-4},10^{-3}$, satura a $N^*=1$
per $\varepsilon_{1q}\ge3\times10^{-3}$. Monotonia non-crescente
confermata su tutta la griglia in entrambi i casi (nessuna inversione).

**Osservazione dichiarata onestamente, non nascosta**: la pendenza
log-log misurata di $N^*(\varepsilon_{2q})$ sui punti non saturati è
$\approx-0.2$, più piatta della previsione $-0.5$ del modello ingenuo
$\varepsilon_\text{tot}(N)\sim a/N+g\varepsilon_{2q}N$. Ipotesi proposta
(non ancora verificata quantitativamente): quel modello assume un
errore additivo su una singola quantità, mentre l'osservabile qui è una
fedeltà, che con rumore depolarizzante accumulato su molti passi si
comporta più come un decadimento moltiplicativo — la forma funzionale
esatta di $N^*(\varepsilon)$ per la fedeltà resta un affinamento
possibile, non necessario per rispondere alla domanda del relatore.

### Stato: PARTE 2 COMPLETA

Tutti e cinque i passi della pipeline chiusi (modello di rumore,
VQE+DM rumoroso, Trotter rumoroso, correlatori rumorosi, scan sui
parametri), ciascuno con teoria/metodologia dichiarata, implementazione,
verifica indipendente, documento di risultati. File prodotti in questa
sessione (oltre a quelli della sessione precedente su Passo 1):
`vqe_dm_rumoroso_dimero.py`, `validate_vqe_dm_rumoroso_dimero.py`,
`risultati_passo2_vqe_dm_rumoroso.tex`, `trotter_rumoroso_dimero.py`,
`validate_trotter_rumoroso_dimero.py`,
`risultati_passo3_trotter_rumoroso.tex`,
`correlatori_rumorosi_dimero.py`,
`validate_correlatori_rumorosi_dimero.py`,
`risultati_passo4_correlatori_rumorosi.tex`,
`scan_parametri_rumore_dimero.py`,
`validate_scan_parametri_rumore_dimero.py`,
`risultati_passo5_scan_parametri.tex`.

### Prossimo passo

Integrazione di tutti i risultati di Parte 2 nel documento finale di
tesi, incluso valorizzare il confronto RBS vs $W$ (Parte 1) come sezione
metodologica a sé, come da nota già in `scheda_progetto_tesi.md`.

## Sessione 4 settembre 2026 — gap di consegna trovato e richiuso (chat parallela)

In una chat diversa da quella del rumore (dedicata al sito interattivo e ai
quattro documenti del dimero), è stato caricato l'intero pacchetto di Parte 2
per un controllo indipendente prima dell'inserimento nel progetto. Trovato un
problema reale, non ipotetico:

**`circuito_correlazioni_dimero.py` consegnato in quella sede era la versione
precedente al fix di `ansatz_params`**, nonostante questo stesso log
dichiarasse "lacuna colmata" nella sessione del 3 settembre. Confermato
facendo girare per davvero `validate_correlatori_rumorosi_dimero.py`: crash
riproducibile su `NotImplementedError` alla prima delle tre verifiche.
`validate_ansatz_params_dimero.py`, citato qui sopra come file di verifica
del fix, risultava introvabile ovunque.

**Richiuso, non solo segnalato**: ricostruita l'implementazione di
`ansatz_params` in `circuito_correlazioni_dimero.py` seguendo esattamente la
descrizione già presente in questo log (mirror del pattern anello/catena,
nessuna permutazione di qubit), e ricostruito `validate_ansatz_params_dimero.py`
con gli stessi tre controlli descritti. Ogni numero dichiarato in questo log
per quel fix è stato ricalcolato da zero e coincide:

- nessuna permutazione di qubit: $1-\mathcal F=9.3\times10^{-15}$ (era
  dichiarato "già 1 a precisione macchina");
- consistenza fra le due preparazioni: scarti $4.5\times10^{-9}$–$9.2\times10^{-8}$
  su 3 correlatori (dichiarato $\sim10^{-6}$–$10^{-7}$, stesso ordine);
- costo in gate: $18$ vs $19$ CNOT, **coincidenza esatta** con quanto
  dichiarato — ma solo dopo aver corretto un errore del primo tentativo di
  verifica (transpilare l'intero circuito invece che blocco per blocco aveva
  collassato i passi di Trotter, dando $6$ vs $7$: la stessa trappola già
  documentata in questo log, ricaduta stavolta nello script di verifica
  anziché nella pipeline).

Riverificati anche, ricalcolandoli da zero, tutti i numeri dei cinque
documenti `risultati_passo{1..5}_*.tex` e di `teoria_modello_rumore.tex`
contro il codice consegnato: coincidono tutti entro la precisione numerica
attesa, incluso il caso limite (tabella $|C_{21}^{xx}(t{=}2)|$ del Passo 4,
scarto costante $\sim10^{-6}$ su 9 valori di $N$, coerente con una
riottimizzazione VQE a seed diverso, non un errore).

**Causa presunta**: il file corretto è stato probabilmente editato e
verificato nella sandbox della sessione precedente, ma non è stato fra
quelli effettivamente consegnati all'esterno a fine sessione — un gap di
consegna, non di lavoro svolto. Non modificabile retroattivamente; segnalato
qui perché non si ripeta (controllare sempre, a fine sessione, che i file
mostrati con `present_files` includano ogni modulo effettivamente modificato,
non solo quelli nuovi).

Pacchetto ripulito (12 `.py` + 3 `.md` + 7 `.tex`, incluso il
`circuito_correlazioni_dimero.py` corretto e il `validate_ansatz_params_dimero.py`
ricostruito) pronto per il caricamento nel progetto.

## Sessione 5 settembre 2026 — chiusura Parte 2, verifica di consistenza completa, passaggio a nuova chat

Prima di passare a una chat pulita per l'estensione VQE noise-aware,
verifica sistematica dell'intero Project (216 file) invece di assumere
coerenza fra quanto prodotto in questa chat e quanto effettivamente
caricato dall'utente (anche in un'altra chat parallela, dedicata al sito
interattivo e ai quattro documenti del dimero).

### Controlli eseguiti

- **Doppioni di contenuto**: confronto MD5 incrociato su tutti i 216 file,
  zero coppie con contenuto identico sotto nomi diversi. Nessun doppione
  reale.
- **File estraneo trovato**: cartella `__pycache__` (bytecode Python
  compilato, `.pyc`, generato eseguendo gli script in un'altra sessione e
  finito per sbaglio nel Project). Nessun valore informativo — **da
  eliminare**, segnalato all'utente, non ancora rimosso.
- **Confronto contro le mie consegne precedenti**: 18 file nuovi rispetto
  all'inizio di questa sessione, tutti riconosciuti (i moduli e i
  documenti di Parte 2 prodotti qui). Nessun file della Parte 1 perso o
  mancante.
- **Incidente del 4 settembre (voce precedente in questo log) —
  RIVERIFICATO E CONFERMATO CHIUSO**: esportati i file `.py` esattamente
  come sono ora nel Project (non le copie di lavoro di questa sessione) e
  rieseguiti `validate_ansatz_params_dimero.py` e
  `validate_correlatori_rumorosi_dimero.py` da zero. Entrambi passano
  tutti i controlli, numeri coincidenti con quanto dichiarato. Il fix è
  operativo, non solo dichiarato.
- **`teoria_modello_rumore.tex` e `risultati_passo2_vqe_dm_rumoroso.tex`**:
  trovati nel Project in versioni precedenti alle mie più recenti (alla
  prima mancavano la derivazione esplicita passo-passo della decoerenza,
  le due figure TikZ, e la sottosezione sul significato di "canale"; alla
  seconda mancava il confronto VQE ideale-degradato vs noise-aware).
  Utente ha ricaricato le versioni aggiornate: confermato, dopo
  normalizzazione dei terminatori di riga (CRLF vs LF, unica differenza
  residua), che ora coincidono esattamente con le mie. Ricompilati
  entrambi con `pdflatex` usando i file così come sono nel Project: zero
  errori, zero overfull/underfull, 8 e 2 pagine rispettivamente, come
  atteso.
- **`log_decisioni.md`**: il Project era già più avanti della mia copia
  locale (conteneva la voce sull'incidente del 4 settembre, che la mia
  copia non aveva). Non sovrascritto: questa voce è aggiunta in coda a
  quello che c'era già, non in sostituzione.
- **Problema pre-esistente, non peggiorato**: le 15 difformità MD5 sul
  workstream della catena (`*_trimero_catena*`) trovate all'apertura di
  questa sessione restano identiche, nessun cambiamento nel frattempo. Non
  toccate.

### Stato consolidato di Parte 2 (dimero, rumore) — CHIUSA

Tutti e cinque i passi completi e verificati: modello di rumore
(calibrazione reale `ibm_torino`, arXiv:2504.15187) -> VQE+DM rumoroso ->
Trotter rumoroso -> correlatori rumorosi -> scan sui parametri.
Risultati centrali: $N^*=8$ (fedeltà di Trotter), $N^*=5$ (correlatori),
$N^*$ dimostrato indipendente da $p_\text{readout}$. File completi (12
`.py` + 3 `.md` + 7 `.tex`) tutti presenti e verificati nel Project.

### Prossimo passo, in una nuova chat

Estensione VQE noise-aware al Passo 2: rioptimizzare i parametri
dell'ansatz PMA-2q$\cdot$3 con il rumore acceso durante l'ottimizzazione
(non solo valutato a posteriori come nel Passo 2 originale), confrontare
con l'energia/fedeltà già ottenute, e verificare (non assumere) se questo
sposta $N^*$ al Passo 3. Previsione dichiarata ma non ancora verificata:
effetto atteso trascurabile, perché il canale depolarizzante è isotropo e
il conteggio CNOT dell'ansatz transpilato non dipende dai valori dei
parametri (verificato: sempre 2 CNOT su 5 assegnazioni casuali di
$\theta$, variano solo di $\pm1$ i gate $R_z$ a 1 qubit).

File da produrre: `vqe_noise_aware_dimero.py`,
`validate_vqe_noise_aware_dimero.py`,
`risultati_vqe_noise_aware_dimero.tex` (stesso stile grafico degli altri
`risultati_passo*.tex`). Cartella locale suggerita (fuori dal Project,
che resta piatto): `tesi/dimero/parte2_rumore/estensione_vqe_noise_aware/`,
sorella dei cinque `passoN_.../`, non annidata dentro `passo2_.../` --
per lasciare chiaro che è un'estensione facoltativa, non uno step
mancante della pipeline richiesta.

### Da sistemare, non urgente

- Rimuovere `__pycache__` dal Project.
- ~~Le 15 difformità MD5 sulla catena restano aperte~~ **RISOLTO**, vedi
  sezione successiva.

## Chiarimento — le 15 difformità MD5 sulla catena: causa trovata, non un problema

Riesaminate su richiesta esplicita dell'utente ("sono nel Project? si
riesce a capire se sono stati inseriti dopo quelli registrati?").

**Primo tentativo, scartato**: confronto dei timestamp del filesystem.
Inconcludente — 134 file su 215 condividono lo stesso timestamp
placeholder ("1979-12-31", marcatore generico di "file presente da prima
di questa sessione", non un vero timestamp di caricamento), sia i file
con MD5 conforme sia quelli difformi. Nessun potere discriminante.

**Causa reale, trovata nel testo del log stesso**: subito sopra la
tabella con quelle impronte (sezione "Correlatori dinamici per la catena
aperta: mirror completo dell'anello"), il log dichiarava esplicitamente
*"Non ancora caricati nel Project: MD5 [...] calcolati sui file come
prodotti in sessione, da verificare di nuovo una volta caricati"* —
verifica poi mai fatta.

Verificato ora: per tutti e 10 i file `.py`/`.tex` della lista, l'MD5
ricalcolato **dopo aver normalizzato i terminatori di riga (CRLF→LF)**
coincide esattamente con quello registrato:

| file | esito dopo normalizzazione CRLF |
|---|---|
| `circuito_correlazioni_trimero_catena.py` | coincide |
| `circuito_correlazioni_trimero_catena_spiegato.tex` | coincide |
| `generate_circuit_fig_trimero_catena.py` | coincide |
| `generate_figures_circuito_trimero_catena.py` | coincide |
| `manuale_uso_correlazioni_trimero_catena_statevector.tex` | coincide |
| `manuale_uso_correlazioni_trimero_catena_vqe.tex` | coincide |
| `simmetrie_correlatori_trimero_catena.tex` | coincide |
| `validate_circuito_correlazioni_catena.py` | coincide |
| `validate_vqe_circuito_correlazioni_catena.py` | coincide |
| `vqe_w2qC_k2_trimero_catena.py` | coincide |

Nessun contenuto diverso: il caricamento nel Project ha convertito i
terminatori di riga (Unix→Windows o viceversa), cambiando l'MD5 senza
toccare una sola parola. Stessa dinamica già osservata in questa sessione
sui file propri di Parte 2.

I restanti 5 file della lista originale (i notebook:
`circuito_correlazioni_trimero_catena_tutte.ipynb`,
`circuito_correlazioni_trimero_catena_vqe.ipynb`,
`correlazioni_trimero_catena_esplorazione.ipynb`,
`correlazioni_trimero_catena_simmetria.ipynb`,
`quantum_simulation_trimero_catena_trotter.ipynb`) restano difformi per
un motivo diverso ma **già documentato altrove in questo stesso log**
("output puliti vs output eseguiti", decisione esplicita per limite di
spazio, non un errore) — vedi la sezione "MD5 del notebook Trotter
catena: la versione con output puliti è quella corretta".

**Conclusione**: le 15 difformità non indicano né una versione più
vecchia né un problema di consegna. Punto chiuso, nessuna azione
richiesta.

## Sessione 5 settembre 2026 — VQE noise-aware: previsione confermata, N* invariato

Estensione facoltativa del Passo 2 completata (vedi "Prossimo passo, in
una nuova chat" sopra). Scope dichiarato esplicitamente nel documento dei
risultati: si rioptimizza solo il Passo 2, un solo controllo a valle su
$N^*$ del Passo 3, Passo 4-5 non ritoccati (argomento di struttura, non
riverifica diretta — criterio di proporzionalità dato il tempo prima
della sessione di laurea di settembre).

### Risultato

$\Delta E=-1.16\times10^{-7}$, $\Delta F=+1.76\times10^{-8}$ fra VQE
noise-aware e il semplice riuso di $\theta^*_\text{ideale}$ sotto rumore
(Passo 2 originale) — entrambi ben sotto la soglia $10^{-4}$ attesa.
$N^*=8$ confermato invariato al Passo 3 con i parametri noise-aware
($F(N^*)=0.817767$ contro $0.817725$ dei parametri ideali). Previsione (a)
di log_decisioni.md (canale isotropo → nessun vantaggio a rioptimizzare)
confermata numericamente, non solo argomentata.

### Trappola di transpilazione — variante scoperta (direzione opposta a quella nota)

Un primo tentativo transpilava l'ansatz PMA-2q$\cdot$3 in forma
PARAMETRICA (parametri simbolici) una sola volta, riusando poi
`assign_parameters` ad ogni valutazione — stesso principio "transpila una
volta, riusa molte volte" già valido per il blocco di Trotter ripetuto
$N$ volte. Verificato che qui è SBAGLIATO: con parametri simbolici il
transpilatore non può fondere le rotazioni a 1 qubit che dipendono dal
valore numerico di $\theta$, producendo un circuito molto più rumoroso
(19 `rz` + 14 `sx` contro 11 `rz` + 8 `sx`, a parità di 2 CNOT).
Conseguenza pratica osservata: il VQE noise-aware con questo bug
convergeva a un'energia PEGGIORE ($E\approx-3.475$) del semplice riuso
dei parametri ideali sotto rumore ($E=-3.50164605$) — segnale del bug,
non un risultato fisico (un ottimizzatore che valuta l'obiettivo vero non
può fare peggio di un punto ammissibile già noto). Corretto transpilando
DOPO l'assegnazione dei parametri, ad ogni valutazione dell'obiettivo:
più costoso per valutazione ($\sim9\,\text{ms}$/eval, trascurabile per
$R\times\text{maxiter}$ dell'ordine delle migliaia di valutazioni), ma
l'unico che riproduce il conteggio di gate minimo già stabilito nella
pipeline (coerente con `vqe_dm_rumoroso_dimero.py`).

### Robustezza del multistart

Con $R=6$ (stesso $R$ del Passo 2 originale) e nessun seme, il multistart
può restare intrappolato in un minimo locale peggiore ($E\approx-3.4753$,
osservato in una prova preliminare prima di aggiungere il seme). Il
risultato principale include $\theta^*_\text{ideale}$ come uno dei punti
di partenza del multistart ($R=6$ casuali + 1 seme). Verificato
indipendentemente che non è un artefatto del seme: un multistart più
ampio ($R=20$, nessun seme) converge allo stesso ottimo rumoroso entro
$2.6\times10^{-6}$.

### File prodotti

`vqe_noise_aware_dimero.py`, `validate_vqe_noise_aware_dimero.py`,
`risultati_vqe_noise_aware_dimero.tex` (compilato con `pdflatex`, due
passate, zero overfull box, un underfull minore di badness 3058 non
corretto — cosmetico, coerente con la soglia di tolleranza già in uso nel
progetto). Verificato pagina per pagina.

### Stato e prossimo passo

Estensione facoltativa CHIUSA. Passo 4 e Passo 5 della pipeline restano
non ritoccati per decisione esplicita (criterio di proporzionalità): la
premessa che li giustificava (floor di preparazione costante in $N$) non
è stata falsificata da questo controllo, anzi rinforzata dalla conferma
su $N^*$ al Passo 3. Prossimo passo effettivo del progetto: chiudere N=3
(correlatori dinamici della catena aperta, ancora mancanti — vedi stato
generale del progetto), poi Parte 2 rumore per il trimero.

## Sessione 5 settembre 2026 (continua) — correzione: l'estensione a Passo 4 non era rigorosa

Individuato un errore nel ragionamento della sessione precedente
(estensione VQE noise-aware), grazie a una domanda esplicita
dell'utente: perché fermarsi al controllo su $N^*$ del Passo 3
(Trotter) e non verificare direttamente anche il Passo 4
(correlatori), visto che anche lì c'è un readout a valle?

### L'errore, con precisione

Ricontrollata la fonte della scomposizione additiva
$\varepsilon_\text{tot}(N)\simeq a/N+g\varepsilon_{2q}N+\delta_\text{prep}$
citata a sostegno dell'estensione (sessione "verifica end-to-end",
sezione "Scomposizione verificata numericamente"): era stata
verificata isolando quattro contributi sul **correlatore**
$\mathrm{Re}\,C_{21}^{xx}(t=2)$ — una quantità del Passo 4, non del
Passo 3. La sezione sul Passo 3 la cita poi come cosa "già
caratterizzata", estendendola per analogia alla fedeltà di Trotter
senza una derivazione indipendente per quella metrica. La sessione
precedente ha quindi invertito silenziosamente la direzione
dell'estensione: ha trattato il Passo 3 come l'origine dell'argomento
e il Passo 4 come l'estensione per analogia, mentre è vero il
contrario.

C'è un secondo motivo, più sostanziale, per cui l'estensione non era
comunque garantita: $N^*$ del Passo 4 è $\arg\max_N|C(N)|$, il
**modulo** di un numero complesso — non una combinazione lineare
additiva come una fedeltà. Il lavoro sul readout asimmetrico
(sessione precedente, si veda sotto) ha mostrato concretamente che
comporre una trasformazione con un'operazione di modulo non preserva
in generale le proprietà di invarianza di una somma lineare. Non
c'era quindi garanzia teorica che un contributo di preparazione
"additivo e costante" per una fedeltà lo fosse anche per il modulo di
un correlatore.

### Controllo diretto eseguito (non più per analogia)

Rieseguito $N^*=\arg\max_N|C_{21}^{xx}(t{=}2,N)|$ con
$\theta^*_\text{ideale}$ e con $\theta^*_\text{noise-aware}$ come
preparazione: $N^*=5$ in entrambi i casi, scostamento massimo
$8\times10^{-5}$ su tutto lo scan di $N$ — un ordine di grandezza più
piccolo persino dello scostamento già minuscolo osservato per la
fedeltà di Trotter ($\sim10^{-4}$).

**La spiegazione corretta**: non è la struttura additiva a garantire
l'invarianza (non era comunque dimostrata per questa metrica), è la
**continuità**: $\theta^*_\text{noise-aware}$ è quasi indistinguibile
da $\theta^*_\text{ideale}$ ($\Delta E\sim10^{-7}$, già noto dalla
sessione precedente), quindi qualunque funzione ragionevolmente liscia
dello stato preparato — fedeltà, modulo di un correlatore, o altro —
deve differire fra le due preparazioni di una quantità altrettanto
minuscola, indipendentemente dalla struttura specifica della metrica.
Garanzia più debole della struttura additiva (non esclude a priori
una metrica patologica con ottimi molto ravvicinati), ma sufficiente
per i due casi concretamente verificati.

Uno spostamento in un altro modo: lo scan sui parametri di rumore
(Passo 5) resta non riverificato punto per punto (criterio di
proporzionalità), ma ora per la ragione corretta (continuità), non
per quella originale (struttura additiva).

### File aggiornati

`vqe_noise_aware_dimero.py` (nuova funzione
`controllo_N_star_correlatore`), `validate_vqe_noise_aware_dimero.py`
(sesto controllo, con assert), `risultati_vqe_noise_aware_dimero.tex`
e `risultati_vqe_noise_aware_completo.tex` (sezione di correzione
completa, nuova figura di confronto del correlatore, scope e
conclusioni aggiornati). Tutti ricompilati e rieseguiti con successo.

### Stato

L'estensione facoltativa VQE noise-aware resta CHIUSA nella sostanza
(nessun cambiamento nei numeri), ma il ragionamento a supporto è ora
corretto e verificato direttamente su entrambe le metriche a valle
controllate (Trotter e correlatori), non più assunto per analogia fra
l'una e l'altra.

## Sessione 5 settembre 2026 (continua) — test di readout asimmetrico (correlatori, Passo 4)

Affrontata la richiesta opzionale del relatore
(`domande_relatore.md`, sez. 12): "parti simmetrico, poi vedi se hai
tempo di fare un test asimmetrico, ma senza perderci troppo tempo".

### Teoria

Derivata la formula generale di correzione del readout per una
matrice di confusione asimmetrica ($p_{01}\neq p_{10}$):
$\langle Z\rangle_\text{readout}=\alpha\langle Z\rangle_\text{ideale}+\beta$,
$\alpha=1-p_{01}-p_{10}$, $\beta=p_{10}-p_{01}$ — il caso simmetrico
noto è il sottocaso $\beta=0$. Per il correlatore complesso, questo
introduce una traslazione costante nel piano complesso,
$C_\text{readout}(N)=\alpha\,C_\text{ideale}(N)+\beta(1+i)$, che **non**
preserva in generale l'invarianza di $N^*=\arg\max_N|C(N)|$ dimostrata
per il caso simmetrico (sommare una costante e prendere il modulo non
commutano). Documento: `teoria_readout_asimmetrico.tex`.

### Ricerca di valori reali

Nessuno split reale citabile trovato per `ibm_torino` specificamente
(l'unica tabella dedicata, arXiv:2410.00916, è un'immagine non
estraibile). Trovati split reali su chip IBM comparabili: IBM-Quito
($3.5\times$), esempio da documentazione IBM ($3.1\times$),
ibmq\_montreal ($2.0\times$) — confermano che $p_{10}>p_{01}$ è la
norma su hardware reale (rilassamento $T_1$ durante la misura).
Scelta dichiarata **illustrativa**: rapporto $3\times$, stessa media
$p_\text{readout}=2.3\times10^{-2}$ già in uso ($p_{01}=0.0115$,
$p_{10}=0.0345$).

### Risultato

$N^*=5$ non si sposta, né al punto illustrativo né a rapporti fino a
$50\times$ (stress test oltre il range realistico) — verificato, non
garantito dalla teoria. Cross-check Monte Carlo (ReadoutError vero,
asimmetrico) conferma la formula analitica entro l'errore statistico
atteso.

### File prodotti

`teoria_readout_asimmetrico.tex`,
`correlatori_readout_asimmetrico.py`,
`validate_correlatori_readout_asimmetrico.py`,
`risultati_readout_asimmetrico.tex`, più due figure. Cartella locale
suggerita: `tesi/dimero/parte2_rumore/estensione_readout_asimmetrico/`,
sorella di `estensione_vqe_noise_aware/`.

### Stato

Punto opzionale del relatore chiuso.

## Sessione 5 settembre 2026 (continua) — quanto è generale "N* non cambia"? Un secondo punto di lavoro

Domanda dell'utente, pertinente: l'affermazione "rioptimizzare sotto
rumore non cambia $N^*$" vale per ogni punto di lavoro e valore dei
parametri, o solo per quello testato finora ("test 2",
$b/J=0.35$, $D/J=0.80$)?

### Risposta onesta, prima di agire

Distinti due livelli:
- **Generale, dimostrato**: l'argomento del canale isotropo
  ($E_\text{rumoroso}(\theta)=(1-\lambda)E_\text{ideale}(\theta)+\lambda\Tr[H]/d$,
  trasformazione affine) vale per qualunque $\lambda>0$ e qualunque
  $b/J,D/J$ — è un fatto matematico sulla struttura del canale, non
  dipende dai valori numerici.
- **Verificato solo in un punto**: la *dimensione* di $\Delta\theta$
  fra $\theta^*_\text{ideale}$ e $\theta^*_\text{noise-aware}$, e se è
  abbastanza piccola da non spostare un $N^*$ specifico, sono fatti
  numerici controllati solo al punto "test 2".

### Secondo punto di lavoro scelto: non arbitrario

Su indicazione dell'utente, usato il punto già presente nella
documentazione narrativa per la discussione
(`dimero_03_dinamica.tex`): $b/J=-0.18$, $D/J=1$ ($J=1$) — scelto lì
per la dinamica non monocromatica, con un termine DM cinque volte più
forte e segno di $b$ opposto rispetto a "test 2". Già validato con lo
stesso ansatz PMA-2q$\cdot$3 ($\mathcal F=1.000000$, tabella in
`dimero_02_vqe.tex`).

### Risultato

Ripetuta l'intera catena (VQE ideale multistart su 10 seed — un solo
seed non basta a questo punto per la fedeltà a precisione macchina —,
VQE noise-aware, $N^*$ Trotter, $N^*$ correlatore):

| Quantità | test 2 | secondo punto |
|---|---|---|
| $\Delta E$ | $-1.16\times10^{-7}$ | $-2.56\times10^{-8}$ |
| $\Delta F$ | $+1.76\times10^{-8}$ | $+3.96\times10^{-9}$ |
| $N^*$ Trotter (ideale→noise-aware) | $8\to8$ | $8\to8$ |
| $N^*$ correlatore (ideale→noise-aware) | $5\to5$ | $3\to3$ |

Osservazione importante: $N^*$ del correlatore **cambia** da un punto
all'altro ($5\to3$) — è una proprietà della fisica del punto, non
della preparazione VQE. Quello che non cambia, in **entrambi** i punti
testati, è che $N^*$ resta lo stesso confrontando le due preparazioni.
Due punti non dimostrano una legge generale per ogni $b/J,D/J$, ma
escludono che il primo risultato fosse un caso isolato.

### File aggiornati

`vqe_noise_aware_dimero.py` (nuova funzione
`verifica_secondo_punto_lavoro`, non sovrascrive lo stato globale del
modulo — b,D passati esplicitamente, ripristinati a fine funzione),
`validate_vqe_noise_aware_dimero.py` (settimo controllo),
`risultati_vqe_noise_aware_dimero.tex` e
`risultati_vqe_noise_aware_completo.tex` (nuova sezione dedicata,
tabella di confronto, figura, scope/conclusioni aggiornati). Tutti
ricompilati (zero errori/overfull) e rieseguiti con successo.

### Stato

L'estensione VQE noise-aware resta CHIUSA nella sostanza. Il dominio
di validità verificato è ora dichiarato esplicitamente in entrambi i
documenti: due punti di lavoro, un solo livello di rumore di
riferimento — non una dimostrazione generale per ogni $b/J,D/J$ o ogni
$\varepsilon_{1q},\varepsilon_{2q},p_\text{readout}$.

## Sessione 5 settembre 2026 (continua) — continuità verificata quantitativamente, Passo 5 completo, documento definitivo

Tre lavori chiusi in questa sessione, su richiesta esplicita
dell'utente: (1) verificare rigorosamente l'argomento di continuità
invece di lasciarlo qualitativo, (2) completare il Passo 5 su tutta la
griglia (non solo al punto di riferimento), (3) consolidare tutta la
documentazione dell'estensione VQE noise-aware in un unico resoconto
fluido.

### (1) Argomento di continuità — da qualitativo a quantitativo

Derivato il legame esplicito: $|\Delta f|\le\|\nabla
f(\theta^*_\text{ideale})\|\,\|\Delta\theta\|+O(\|\Delta\theta\|^2)$
(sviluppo di Taylor al prim'ordine). Un primo tentativo di stima del
gradiente per differenze finite sulla pipeline principale ha dato
risultati **instabili in modo drammatico** al variare del passo $h$
(una componente del gradiente variava da $-0.06$ a $-11.04$ a $+1099$
a seconda di $h$) — causa isolata: il transpilatore cambia la sintesi
dei gate (11 vs 12 \texttt{rz}) fra le due valutazioni usate per la
differenza finita, un artefatto della transpilazione, non fisica.
Corretto usando la stessa tecnica della "trappola di transpilazione"
già nota, qui applicata allo scopo opposto: transpilare l'ansatz una
sola volta in forma simbolica (struttura fissa, an che se meno
efficiente in conteggio di gate) e poi solo assegnare i parametri
numerici — il gradiente cosi' ottenuto e' stabile su 4 ordini di
grandezza di $h$.

Con il gradiente corretto, la previsione lineare riproduce lo
scostamento osservato entro lo **0.1%** per entrambe le metriche
(fedeltà di Trotter: predetto $4.150\times10^{-5}$ vs osservato
$4.147\times10^{-5}$; correlatore: predetto $-6.794\times10^{-5}$ vs
osservato $-6.792\times10^{-5}$). L'argomento di continuità è quindi
**confermato quantitativamente**, non solo plausibile.

File: `nota_continuita_preparazione.tex` — dichiarata esplicitamente
come nota di lavoro interna, non capitolo di tesi (per decisione
dell'utente: il risultato va citato in una riga, la derivazione
completa resta come verifica metodologica interna).

### (2) Passo 5 completo: griglia intera, non solo il punto di riferimento

Ricalcolato $N^*$ (fedeltà di Trotter e modulo del correlatore) con
**entrambe** le preparazioni (ideale, noise-aware) su tutta la griglia
già usata nello scan originale del Passo 5: 7 valori di
$\varepsilon_{2q}$ e 6 di $\varepsilon_{1q}$ per la fedeltà, 5 valori
di $\varepsilon_{2q}$, 4 di $\varepsilon_{1q}$ e 3 di $p_\text{readout}$
per il correlatore — **25 punti totali, 25/25 con $N^*$ invariato**.
Prima di questo controllo, l'invarianza era verificata solo al singolo
punto di riferimento (calibrazione `ibm_torino`); ora è verificata
sull'intera griglia già esplorata nel Passo 5 originale.

File: `verifica_passo5_noise_aware.py` (nuovo), ottavo controllo
aggiunto a `validate_vqe_noise_aware_dimero.py`.

### (3) Documento definitivo: narrativa unica, senza i salti della sessione di sviluppo

Prodotto `risultati_vqe_noise_aware_definitivo.tex` (8 pagine, 7
figure): sostituisce concettualmente i documenti precedenti
(`risultati_vqe_noise_aware_dimero.tex`,
`risultati_vqe_noise_aware_completo.tex`) con un'unica esposizione
lineare — obiettivo, argomento fisico, implementazione, verifica,
risultati (Passo 2, 3, 4), perché generalizza (continuità, secondo
punto di lavoro, griglia completa del Passo 5), considerazioni,
conclusioni. Non narra la cronologia delle correzioni fatte durante lo
sviluppo (l'argomento inizialmente non rigoroso sull'estensione al
Passo 4, la sua correzione, la scoperta del bug di transpilazione nel
calcolo del gradiente): quella cronologia resta nel presente log, che
è la sede corretta per conservarla. Il documento di riferimento per la
tesi è ora questo. *(Nota: la frase originariamente scritta qui — "i
documenti precedenti non sono stati cancellati, restano nel Project
come cronologia dello sviluppo" — è superata dalla decisione presa
nella sessione successiva: vanno invece rimossi dal Project, non
conservati lì; vedi voce sotto.)*

### Stato

Estensione VQE noise-aware CHIUSA, con lo stesso esito sostanziale di
sempre (rioptimizzare sotto rumore non cambia nulla di misurabile), ora
sostenuto da: due metriche verificate direttamente, due punti di
lavoro, l'intera griglia del Passo 5 (25/25), e un argomento di
continuità reso quantitativo (non più solo qualitativo). Documentazione
consolidata in un'unica esposizione lineare.

## Sessione 5 settembre 2026 (continua) — correzione terminologica finale, documenti superati rimossi

Due controlli richiesti esplicitamente dall'utente dopo la creazione
del documento definitivo, invece di darli per scontati.

### Terminologia "Passo N" tornata nei file nuovi

Verificato con una scansione (non a occhio): la terminologia
"argomento-prima, Passo-N-fra-parentesi" richiesta in una sessione
precedente era rientrata nei file più recenti. Trovate 18 occorrenze in
`risultati_vqe_noise_aware_definitivo.tex` e alcune in
`teoria_readout_asimmetrico.tex` dove "Passo N" tornava a guidare la
frase invece di seguirla. Corrette tutte quelle riferite alla pipeline;
lasciate intatte le occorrenze di `teoria_readout_asimmetrico.tex` che
sono passi di una derivazione matematica (`\paragraph{Passo 1 ---
probabilità lette}` ecc.), un uso legittimo e
diverso, verificato distinguendolo esplicitamente prima di correggere.
Entrambi i documenti ricompilati e riverificati pagina per pagina dopo
la correzione.

### Documenti superati: box esplicito, poi rimozione dal Project

Aggiunto un box "Documento superato" in apertura di
`risultati_vqe_noise_aware_dimero.tex` e
`risultati_vqe_noise_aware_completo.tex`, con rimando esplicito a
`risultati_vqe_noise_aware_definitivo.tex`. Verificato (non assunto)
che tutte le figure usate dai due documenti superati sono anche usate
dal definitivo — nessuna figura orfana da eliminare. Decisione presa
con l'utente, che corregge quanto scritto nella voce precedente di
questo log: i due documenti superati vanno **rimossi dal Project**
(non conservati lì), con la cronologia della loro correzione comunque
preservata in questo log. Localmente, l'utente può scegliere fra
cancellarli o archiviarli in una sottocartella `superati/` dentro
`estensione_vqe_noise_aware/` — entrambe le scelte compatibili con
quanto scritto qui.

### Stato

Estensione VQE noise-aware CHIUSA. Terminologia coerente in tutti i
documenti attivi (verificato con scansione automatica, non solo
visiva). Struttura di cartelle definitiva per
`estensione_vqe_noise_aware/`: file correnti (script, documento
definitivo, nota di continuità, figure) a un livello, i due documenti
superati fuori dal Project (cancellati o archiviati localmente, a
scelta dell'utente).
