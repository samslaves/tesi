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
