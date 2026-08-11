# Scheda progetto — Tesi triennale

## Dati
- **Titolo (provvisorio):** Quantum simulation of molecular systems on quantum hardware
- **Corso:** Laurea triennale in Fisica, Università degli Studi di Parma
- **Relatore:** Prof. Alessandro Chiesa
- **Sessione di laurea obiettivo:** *(da definire: luglio / settembre)*
- **Formato deliverable:** documento breve (~2 pagine) / slide

## Riferimenti nella conoscenza del progetto
- **Punto di partenza operativo:** documento **6-Applications.pdf** (slide del corso
  Quantum Computing del Prof. Chiesa), esempio **"VQE on a spin dimer"** (slide 19–21).
- **Paper di riferimento concettuale:** Crippa et al., *Simulating Static and Dynamic
  Properties of Magnetic Molecules with Prototype Quantum Computers*,
  **Magnetochemistry 7, 117 (2021)**.

## Inquadramento
"Sistemi molecolari" = sistemi di spin-1/2 (modello di spin), non struttura
elettronica. Ogni spin-1/2 si mappa direttamente su un qubit: niente mapping
fermionico (no Jordan-Wigner, no UCCSD).

## Modello — spin dimer (caso di partenza, N=2)
Dall'esempio di 6-Applications.pdf (slide 19):
$$H = J_x X_1X_2 + J_y Y_1Y_2 + J_z Z_1Z_2 + b(Z_1+Z_2)$$
Caso isotropo $J_x=J_y=J_z=J$ (slide 21), risolubile analiticamente:
$$H = H_1 + H_2,\quad H_1 = J(X_1X_2+Y_1Y_2+Z_1Z_2)=2J(S^2-s_1^2-s_2^2),\quad H_2=b(Z_1+Z_2)=2bS_z$$
Autovalori (con $s_1=s_2=1/2$):
$$(H_1+H_2)|S,M\rangle = [\,2bM + 2JS(S+1)-3J\,]\,|S,M\rangle$$
- $S=0,\,M=0$: $E=-3J$ (singoletto)
- $S=1,\,M=+1,0,-1$: $E = J+2b,\ J,\ J-2b$ (tripletto)

Stato fondamentale: singoletto $(|\!\uparrow\downarrow\rangle-|\!\downarrow\uparrow\rangle)/\sqrt2$ a campo
basso; incrocio con $|\!\downarrow\downarrow\rangle$ (= $|S{=}1,M{=}-1\rangle$) a $b/J=2$
(nel grafico l'asse è $B/J$, con $B\equiv b$). Parametro di controllo: $b/J$.

> NOTA convenzione: 6-Applications.pdf usa $b$ per il campo e $J$ davanti a
> $(XX+YY+ZZ)$. Il paper di Crippa usa $H=2J\sum \mathbf{s}_i\cdot\mathbf{s}_{i+1}+B\sum s_i^z$.
> È lo stesso modello a meno di fattori 2 nelle costanti; usare la convenzione di
> 6-Applications.pdf come operativa.

## Estensione — N=3 (3 spin-1/2)
$$H = J\!\!\sum_{\langle i,j\rangle}\!\!(X_iX_j+Y_iY_j+Z_iZ_j) + b\sum_{i=1}^{3} Z_i$$
- **Catena aperta** (trimero): legami $(1,2)$ e $(2,3)$.
- **Anello/triangolo**: aggiunge il legame $(3,1)$ → AFM **frustrato** (numero dispari).
- Spazio di Hilbert $2^3=8$; spin totale $S=1/2$ (due volte) o $S=3/2$.
- *(Topologia da decidere con il relatore — vedi log.)*

## STRUTTURA DELLA TESI (definita con il relatore)

### Parte 1 — Sistema quantistico CHIUSO (senza rumore)
- Stato = **vettore di stato** $|\psi\rangle$, evoluzione unitaria (Schrödinger).
- Si parte dal **dimero (N=2)** di 6-Applications.pdf e si **estende a N=3**.
- Metodo: VQE su simulatore statevector; confronto con la soluzione esatta
  (per il dimero, autovalori analitici qui sopra); calcolo di osservabili
  (es. magnetizzazione $M_z$) e fidelity $\mathcal{F}=|\langle\psi_0|\psi(\tilde\theta)\rangle|$.

### Nuovo blocco richiesto dal relatore — Quantum simulation (Trotter) del dimero
> **Stato: richiesto dal relatore il 18/07/2026, NON ancora implementato.**
> Collocazione nella tesi ancora da definire (probabile ponte tra Parte 1 e
> Parte 2, o sotto-sezione di Parte 1) — vedi `log_decisioni.md`.

Distinto dal VQE: non si cerca variazionalmente lo stato fondamentale, ma si
simula l'**evoluzione temporale reale** $e^{-iHt}|\psi_0\rangle$ dell'Hamiltoniana
**del dimero** (Heisenberg isotropo + campo + DM), con la stessa metodologia
(Suzuki-Trotter, decomposizione in gate) del notebook di esempio
`Quantum_simulation_TIM_noiseless.ipynb` — ma **sostituendo l'Hamiltoniana TIM
con l'Hamiltoniana VQE del dimero**, secondo gli appunti del relatore
(`quantum_simulation_notes.jpg`):
$$H = b(s_{z1}+s_{z2}) + J\,\vec s_1\!\cdot\!\vec s_2 + D(s_{x1}s_{z2}-s_{z1}s_{x2}) = H_1+H_2,\quad [H_1,H_2]\neq0$$
- **Caso $D=0$:** $H_1$ (campo) e $J\vec s_1\!\cdot\!\vec s_2$ commutano →
  decomposizione **esatta** $e^{-iHt}=R_z^{(1)}(bt)R_z^{(2)}(bt)U_J$, senza
  errore di Trotter.
- **Caso $D\neq0$:** serve **Suzuki-Trotter** a N step:
  $e^{-i(H_1+H_2)t}\approx(e^{-iH_1t/N}e^{-iH_2t/N})^N+O((t/N)^2)$.

### Parte 2 — Sistema quantistico APERTO (con rumore)
- Modelli di **rumore approssimati in Qiskit**.
- Si passa al **operatore densità** $\rho$ (stati misti): non si conosce esattamente
  lo stato, ma una distribuzione di probabilità su stati diversi; perdita di
  informazione per interazione con l'ambiente (decoerenza).
- Effetti $T_1$ (rilassamento), $T_2$ (decoerenza), errori di gate e di lettura.

## Obiettivo
- **Parte 1:** riprodurre il dimero (N=2), estenderlo a N=3, trovare lo stato
  fondamentale via VQE su sistema chiuso, validare contro l'esatto.
- **Parte 2:** rifare lo studio introducendo il rumore (operatore densità) e
  osservarne l'effetto.

## Fuori scope (allo stato attuale)
- Reti neurali / Neural Quantum States: NON nella tesi (impostazione del relatore).
- Funzioni di correlazione dinamiche, hardware reale, error mitigation avanzata,
  QAOA, HHL, image processing (altri argomenti delle slide, non pertinenti).

## Bibliografia minima
- Crippa et al., Magnetochemistry 7, 117 (2021) — riferimento concettuale.
- Peruzzo et al., Nat. Commun. 5, 4213 (2014) — origine del VQE.
- Kandala et al., Nature 549, 242 (2017) — ansatz hardware-efficient.

## Aggiornamento 18/07/2026 — quantum simulation (Trotter) sul dimero: stato avanzato

Vedi `log_decisioni.md` per i dettagli completi. In sintesi:
- **Hamiltoniana confermata** (appunti del relatore): $H=H_1+H_2$ con
  $H_1=b(s_{z1}+s_{z2})+J\vec s_1\cdot\vec s_2$ (fisso) e
  $H_2=D(s_{x1}s_{z2}-s_{z1}s_{x2})$ (solo DM, dipende da $D$).
- **$D=0$:** decomposizione esatta $R_z^{(1)}(bt)R_z^{(2)}(bt)U_J$.
- **$D\neq0$:** Suzuki-Trotter, errore $O((t/N)^2)$ per passo.
- **Notebook template** `Quantum_simulation_TIM_noiseless.ipynb` (Trotter su
  Ising) **eseguito con successo** con Qiskit 2.x, nessuna incompatibilità
  (solo l'import inutilizzato di `qiskit_ibm_runtime` va commentato).
- **Prossimo passo:** riscrivere lo stesso schema Trotter sostituendo
  l'Hamiltoniana Ising con quella del dimero, prima per $D=0$ (verifica
  esatta) poi per $D\neq0$.

## Aggiornamento 18/07/2026 — N=2 (dimero) sostanzialmente completo

Vedi `log_decisioni.md` per il dettaglio numerico completo. In sintesi, per
Parte 1 / N=2 sono stati prodotti e validati:
- `dimer_exact.py` — benchmark esatto (formula chiusa + `eigh`), self-test
  a precisione macchina.
- `vqe_dimer.py` — VQE con ansatz HA (6 par., generico) e PMA base (1 par.,
  $M$-conservante); il PMA batte l'HA a $D=0$ ma degrada a $D\neq0$ vicino
  a $B/J=2$ (rottura di $M$).
- `confronto_ansatz_entangler.ipynb` — 4 ansatz reali generici (sempre
  $\mathcal F=1$) + due famiglie PMA estese che recuperano $\mathcal F=1$
  anche a $D\neq0$: **PMA-1q** (da 4 par.) e **PMA-2q** (da 3 par., minimo
  teorico). **`PMA-2q·3` è l'ansatz raccomandato per N=3.**
- `analisi_rotazioni_PMA.ipynb` — derivazione di perché servano rotazioni
  $R_y$ indipendenti sui due qubit (parametro condiviso non basta).

**Metodologia VQE confermata per il seguito (N=3):** multistart $R=6$,
reinizializzazione nel ciclo esterno.

**Prossimo passo:** estendere ansatz PMA-2q e benchmark esatto a N=3 (catena
e triangolo); in parallelo, il task di quantum simulation Trotter sul dimero
richiesto dal relatore (vedi sezione dedicata sopra).

## Aggiornamento — fase VQE → ground state → correlazioni dinamiche

Estensione confermata dal relatore (rimandata al 19/07, riavviata dopo
l'apprezzamento della relazione sui test): sostituire $|00\rangle$ con il
ground state trovato via VQE come stato iniziale della dinamica, e
calcolare correlazioni dinamiche (richiede l'ancilla, finora non usata).

- **Punto di lavoro:** parametri del "test 2" (`relazione_test_parametri.md`),
  $b/J=0.35$, $D/J=0.80$.
- **VQE completato:** ground state trovato con PMA-2q·3 (riuso totale
  dell'ansatz/metodologia N=2), $\mathcal F=1$ a precisione macchina.
  File: `vqe_test2.py`, `vqe_ground_state_test2.ipynb`,
  `risultati_vqe_test2.md`, stato salvato in `ground_state_test2.npz`.
- **Osservabile di correlazione — risposta del relatore ricevuta:**
  sia auto-correlazione (stesso sito) sia correlazione fra spin diversi
  sono di interesse; più componenti da provare ($S_z,S_x,S_y$); alcune
  combinazioni si annulleranno per simmetria dell'Hamiltoniana (atteso,
  da verificare classicamente prima di implementare il circuito).
- **Prossimo passo (completato — vedi aggiornamento sotto):** ~~controllo
  classico di quali combinazioni sono nulle per simmetria, poi circuito
  con l'ancilla (Hadamard test) parametrico in (sito, componente), con
  stato iniziale preparato da `ground_state_test2.npz` al posto di
  $|00\rangle$.~~
- **Primo caso concreto suggerito dal relatore** (appunti manoscritti):
  $\langle\sigma_{x2}(t)\,\sigma_{x1}(0)\rangle$. Il circuito abbinato nello
  schizzo è indicativo, non verificato (il relatore stesso non ne era
  sicuro) — ri-derivato da zero, non usato come riferimento diretto.
  Dettagli in `log_decisioni.md`.

## Aggiornamento — circuito con l'ancilla: derivato, validato, tutte le 36 misurate

Circuito con l'ancilla derivato da zero (non lo schizzo del relatore),
verificato contro due fonti di letteratura indipendenti (Crippa et al.
eq. 12; Tacchino-Chiesa-Carretta-Gerace, *Adv. Quantum Technol.* 2020,
Fig. 3), validato su statevector e con shot finiti. Tutte le 36
combinazioni $C_{ij}^{\alpha\beta}(t)$ misurate direttamente via
circuito — nessuna strutturalmente nulla per ogni $t$. Due bug
metodologici trovati e corretti nel percorso (dettagli in
`log_decisioni.md`). Relazione con i risultati inviata al relatore
(`relazione_correlazioni.docx`), due osservazioni in attesa di risposta
(vedi `domande_relatore.md`, punto 6).

Filone collaterale chiuso: analisi del circuito compatto a 3 CNOT
(risposta alla domanda del relatore su come ridurre il conteggio di
gate), con raccomandazione su dove si applica legittimamente — non
ancora integrato nel circuito delle correlazioni, resta un'opzione
futura.

**Prossimo passo vero e proprio:** in attesa della risposta del relatore
sulle due osservazioni; in parallelo, la Parte 2 (sistemi aperti) resta
il blocco più grande non ancora iniziato — il rumore di gate reale sul
circuito delle correlazioni si collega naturalmente a quella fase.

## Nota — materiale preparatorio per la Parte 2 (non ancora iniziata)

Appunti del relatore su formalismo Kraus/Lindblad (equazione
$\dot\rho=-\frac{i}{\hbar}[H,\rho]+\mathcal D[\rho]$, rappresentazione di
Kraus, esempio canale bit-flip) caricati nel progetto. Materiale di
riferimento per quando si apre il blocco Parte 2 — nessuna azione
immediata. Dettagli in `log_decisioni.md`.
