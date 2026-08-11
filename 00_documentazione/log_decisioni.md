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
- **Stato:** NON ancora iniziato. Solo presa visione e pianificazione per ora,
  su richiesta esplicita di Samuele ("per ora non fare nulla").
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
- [ ] Esteso a N=3 (catena aperta E triangolo).
- [ ] Introdotto il modello di rumore / operatore densità (Parte 2).
- [x] Caricato `Quantum_simulation_TIM_noiseless.ipynb` (esempio Trotter/TIM,
      da riusare come template metodologico, NON come Hamiltoniana da tenere).
- [x] Caricati appunti del relatore `quantum_simulation_notes.jpg` (schema
      Trotter per $H=H_1+H_2$ del dimero, casi $D=0$ esatto e $D\neq0$ Suzuki-Trotter).
- [ ] Implementata la quantum simulation ($e^{-iHt}$, Trotter) sull'Hamiltoniana
      VQE del dimero — task richiesto dal relatore, non ancora iniziato.
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
