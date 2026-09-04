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
- **Catena aperta** (trimero): legami $(1,2)$ e $(2,3)$. *(Teoria non ancora iniziata.)*
- **Anello/triangolo**: aggiunge il legame $(3,1)$ → AFM **frustrato** (numero dispari).
  Parametrizzato in generale come **isoscele**: base $J$ fra $1,2$, lati $J'$ fra
  $2,3$ e $3,1$ ($J\neq J'$; l'equilatero frustrato è il caso particolare $J'=J$).
  **Teoria esatta completa** — vedi aggiornamento dedicato più sotto.
- Spazio di Hilbert $2^3=8$; spin totale $S=1/2$ (due volte, blocchi B e C) o
  $S=3/2$ (blocco A) — **mai $S=0$** (numero dispari di spin-$1/2$).
- Entrambe le topologie confermate in scope dal relatore (vedi log).

## STRUTTURA DELLA TESI (definita con il relatore)

### Parte 1 — Sistema quantistico CHIUSO (senza rumore)
- Stato = **vettore di stato** $|\psi\rangle$, evoluzione unitaria (Schrödinger).
- Si parte dal **dimero (N=2)** di 6-Applications.pdf e si **estende a N=3**.
- Metodo: VQE su simulatore statevector; confronto con la soluzione esatta
  (per il dimero, autovalori analitici qui sopra); calcolo di osservabili
  (es. magnetizzazione $M_z$) e fidelity $\mathcal{F}=|\langle\psi_0|\psi(\tilde\theta)\rangle|$.

### Blocco richiesto dal relatore — Quantum simulation (Trotter) del dimero
> **Stato: COMPLETATO.** Richiesto dal relatore il 18/07/2026, implementato
> e verificato (convergenza, costo in gate, regimi dimostrativi R0/R1) — vedi
> aggiornamento dedicato più sotto e dettaglio completo in `log_decisioni.md`.
> Collocazione nella tesi ancora da definire (probabile ponte tra Parte 1 e
> Parte 2, o sotto-sezione di Parte 1) — resta l'unico punto aperto di questo
> blocco.

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
- **Due soli canali** (confermato dal relatore, 02/09/2026): errori di **gate**
  (1 e 2 qubit, canale depolarizzante) ed errore di **lettura** (readout).
  $T_1$ (rilassamento) e $T_2$ (decoerenza) **esclusi** dalla tesi.

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

## Aggiornamento — quantum simulation (Trotter) sul dimero: COMPLETATA

Vedi `log_decisioni.md` per i dettagli completi (derivazione, verifica
numerica dello scaling dell'errore, costo in gate). In sintesi:
- **Hamiltoniana confermata** (appunti del relatore): $H=H_1+H_2$ con
  $H_1=b(s_{z1}+s_{z2})+J\vec s_1\cdot\vec s_2$ (fisso) e
  $H_2=D(s_{x1}s_{z2}-s_{z1}s_{x2})$ (solo DM, dipende da $D$).
- **Implementata direttamente con $D\neq0$** (per indicazione del relatore,
  nessun passaggio intermedio per $D=0$), Suzuki-Trotter al 1° ordine.
- **Regimi dimostrativi:** R0 (suggerimento del relatore, $J=2b,D=b/3$,
  oscillazione quasi monocromatica) e R1 (derivato, $b/J=-0.18,D/J=1$, non
  monocromatico, $a_2/a_1=0.995$) — filone esplorativo a sé, distinto dal
  punto "test 2" usato per la pipeline ground state→correlazioni.
- **Errore di Trotter verificato quantitativamente**: scaling misurato
  coerente con la teoria ($1-\mathcal F\sim O(1/N^2)$, $\|\Delta U\|\sim
  O(1/N)$).
- **File:** `trotter_dimero.py`, due notebook, note di approfondimento,
  analisi costo in gate (`costo_gate_trotter.md`).

**Prossimo passo:** decidere con il relatore la collocazione definitiva nella
tesi (unico punto ancora aperto per questo blocco).

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

**Prossimo passo (storico, superato — vedi aggiornamenti successivi nel
file):** ~~estendere ansatz PMA-2q e benchmark esatto a N=3 (catena e
triangolo); in parallelo, il task di quantum simulation Trotter sul dimero
richiesto dal relatore (vedi sezione dedicata sopra).~~ Entrambi i filoni
sono avanzati da allora: teoria esatta del triangolo isoscele completata
(vedi "Aggiornamento — N=3, triangolo isoscele") e Trotter completato (vedi
"Aggiornamento — quantum simulation Trotter del dimero: COMPLETATA").

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

## Aggiornamento — N=3, triangolo isoscele: teoria esatta completa

Vedi `log_decisioni.md` per la derivazione completa. In sintesi, per la
topologia anello/triangolo:

- **Parametrizzazione:** base $J$ (siti 1,2), lati $J'$ (siti 2,3 e 3,1),
  $J\neq J'$; l'equilatero frustrato è il caso particolare $J'=J$.
- **Risolubile in forma chiusa** (decomposizione di Kambe, Casimir
  $S_{12}^2,S^2,S_z$) grazie alla simmetria di scambio $1\leftrightarrow2$
  presente solo quando i due lati sono uguali — dimostrata esplicitamente,
  non assunta.
- **Tre multipletti** A ($S_{12}{=}1,S{=}3/2$), B ($S_{12}{=}1,S{=}1/2$),
  C ($S_{12}{=}0,S{=}1/2$), spettro in forma chiusa, limite dimero ($J'\to0$)
  verificato.
- **Campo critico** $b_c$ in forma chiusa nei due regimi ($2J+J'$ o $3J'$);
  **mappa completa dei segni** $(J,J')$ per l'esistenza del crossing, inclusi
  i quadranti con $J$ e/o $J'$ negativi.
- **Tutti gli incroci trovati sono veri** (gap nullo, non anticrossing) —
  dimostrato via regola di selezione. Il ruolo del DM nell'aprire il gap è
  discusso solo qualitativamente, non quantificato numericamente.
- **File:** `teoria_trimero_isoscele.pdf` (20 pagine),
  `animazione_trimero_isoscele.html` (esplorazione interattiva),
  `verifica.py` (batteria di test contro diagonalizzazione esatta, tutti
  superati).

**Non ancora fatto per N=3:** teoria della catena aperta; VQE per entrambe
le topologie (ansatz di partenza raccomandato: `PMA-2q·3`, già validato per
il dimero); trattazione quantitativa del DM sul triangolo.

**Prossimo passo:** da decidere fra catena aperta (teoria) o VQE sul
triangolo isoscele (ora che c'è il benchmark esatto).

## Aggiornamento — N=3: catena aperta completata, VQE con DM per l'anello

**Teoria catena aperta: completata.** Stessa decomposizione di Kambe
dell'anello, coppia di classificazione $(1,3)$ non adiacente (complicazione
tecnica in più rispetto all'anello). Per $J>0$ il fondamentale a basso
campo è sempre il blocco $B$ (mai serve il confronto $E_B$ vs $E_C$),
$b_c=3J$. File: `trimer_chain_exact.py`, `teoria_trimero_catena_aperta.pdf`,
`derivazione_stati_kambe_trimero_catena.pdf`.

**VQE senza DM: completato per entrambe le topologie**, struttura
parallela (RBS con branching, $W$ con branching, senza branching, due
guide interattive per ciascuna). Due bug reali trovati e corretti durante
la costruzione (conteggio parametri in `vqe_trimer_chain_nobranch.py`;
sensibilità al seed in `vqe_trimer_chain_spiegato.ipynb`) — vedi
`log_decisioni.md` per il dettaglio.

**VQE con DM: completato solo per l'anello (Fase 5).** Risultato centrale:
la famiglia RBS-2q ha un tetto strutturale vero sotto DM
($\mathcal F\approx0.9999$), la famiglia $W$-2q raggiunge l'esatto —
candidato canonico `W-2q.6`. **Non ancora fatto per la catena.**

**Correzione trovata nel modulo esatto dell'anello**: $\langle M_z\rangle$
a $b=0$ (fondamentale degenere) va mediato sul sottospazio, non calcolato
su un singolo autovettore arbitrario — corretto in `trimer_ring_exact.py`.

**Documentazione**: riorganizzata per fase (esatto / VQE senza DM / VQE con
DM) e per topologia (dimero, anello, catena), mirror strutturale in tutti
e sei i documenti prodotti finora — vedi `log_decisioni.md` per l'elenco
completo.

**Non ancora fatto per N=3, in ordine di priorità presunta:**
1. Fase 5 (VQE con DM) per la catena aperta.
2. Trotter e correlazioni dinamiche, entrambe le topologie — stessa
   complicazione già anticipata per l'anello (i tre bond condividono
   qubit, serve una decomposizione di Trotter annidata) più, per la
   catena, la scelta di un punto di lavoro adatto alla dinamica (non
   necessariamente lo stesso ottimale per il VQE).

**Prossimo passo:** da decidere fra completare la Fase 5 per la catena
(chiudere il parallelismo con l'anello) o aprire il fronte Trotter/correlazioni
per N=3.

## Aggiornamento — anello: Trotter, correlazioni dinamiche e tool esplorativo completati; filone anello chiuso

Risolto nei fatti quanto lasciato aperto sopra: per l'anello sono stati
completati, in sessioni successive, sia la simulazione quantistica
(Trotter, mirror del dimero con Trotter interno annidato per i tre bond
che condividono i qubit) sia le correlazioni dinamiche (circuito Hadamard
test, scan sistematico delle 81 combinazioni siti×componenti, chiusura con
VQE reale). **Il filone anello è ora chiuso a tutti i livelli**: teoria
esatta, VQE senza DM, VQE con DM (Fase 5), Trotter, correlazioni
dinamiche. Vedi `log_decisioni.md` per la cronologia completa e i file
prodotti (`trotter_trimero_anello.py`,
`circuito_correlazioni_trimero_anello.py`,
`quantum_simulation_trimero_anello_teoria.tex`/`_applicazione.tex`,
`trimero_anello_quantum_simulation.tex`, e i restanti documenti di
catalogazione/simmetria per l'anello).

Due sviluppi ulteriori, successivi alla chiusura tecnica del filone:

- **Relazione VQE anello, narrativa L-BFGS-B**: derivazione del bound
  spettrale sull'errore di fidelity, applicazione numerica al punto di
  lavoro confermato, rassegna della letteratura L-BFGS-B — dettagli
  implementativi spostati in un tex a parte (riferimento personale, non
  parte della tesi), relazione principale semplificata ai soli risultati.
- **Tool interattivo "video e foto" delle correlazioni (anello)**: celle
  ipywidgets in entrambi i notebook delle correlazioni (`_tutte`, `_vqe`)
  più un tool HTML standalone (algebra 8×8 riportata in JavaScript,
  verificata a precisione di macchina contro il calcolo classico Python;
  dati precalcolati per preparazione esatta e VQE; palette CVD-safe; tema
  chiaro/scuro) — pubblicato come pagina condivisibile e come file
  scaricabile.

**Prossimo passo:** aprire il filone catena aperta con lo stesso livello di
completezza raggiunto per l'anello — Fase 5 (VQE con DM, struttura del
termine DM già nota: $D_{12}=-D_{23}$ forzato dalla riflessione $P_{13}$,
nessuna scelta Opzione A/B come per l'anello), poi Trotter e correlazioni
dinamiche per la catena. Vedi `prompt_nuova_chat_trimero_catena.md` per il
piano operativo dettagliato.

## Aggiornamento 3 settembre 2026 — Parte 2 avviata: verifica end-to-end e primi documenti

Pipeline di Parte 1 sul dimero (VQE, $U(t)$ via Trotter, correlatori)
riverificata end-to-end e confermata sana prima di introdurre il rumore
(dettaglio numerico completo in `log_decisioni.md`). Trovato e da tenere a
mente: transpilare l'**intero** circuito dei correlatori a un livello di
ottimizzazione alto collassa gli $N$ passi di Trotter in un circuito a
costo costante, cancellando silenziosamente la dipendenza da $N$ che serve
allo scan sui parametri di rumore richiesto dal relatore — evitato
transpilando una volta il singolo passo e ripetendo il blocco compilato.

Prodotti i primi due documenti della Parte 2:
`pipeline_rumore_dimero_overview.tex` (panoramica dei 5 passi della
pipeline) e `teoria_modello_rumore.tex` (teoria del Passo 1: operatore
densità, operatori di Kraus, canale depolarizzante, conversione
$\varepsilon\leftrightarrow\lambda$, errore di lettura).

**Prossimo passo:** implementazione del Passo 1 (ricerca calibrazione reale
su un chip citabile, `NoiseModel` in codice), poi Passo 2 (VQE con termine
DM sotto rumore), che richiede prima di implementare `ansatz_params` per il
modulo dei correlatori del dimero (ancora mancante, a differenza di anello
e catena).

## Aggiornamento 3 settembre 2026 (continua) — PARTE 2 COMPLETA sul dimero

Tutti e cinque i passi della pipeline di Parte 2 (sistema aperto, dimero)
sono chiusi: modello di rumore (Passo 1), VQE con termine DM sotto rumore
(Passo 2), quantum simulation Trotter sotto rumore (Passo 3), correlazioni
dinamiche sotto rumore (Passo 4), scan sui parametri di errore (Passo 5).
Dettaglio numerico completo di ciascun passo in `log_decisioni.md`;
documenti di risultati dedicati per ciascun passo
(`risultati_passo{1..5}_*.tex`).

**Risultati centrali:**
- Punto di riferimento (`ibm_torino`, calibrazione reale citata):
  $N^*=8$ sulla fedeltà di Trotter, $N^*=5$ sui correlatori dinamici —
  prima comparsa concreta, non solo prevista, del compromesso
  Trotter/rumore richiesto dal relatore.
- Risultato analitico: $N^*$ è **indipendente da $p_\text{readout}$**
  (la correzione di readout è un fattore moltiplicativo costante in $N$,
  non può spostare un massimo) — dimostrato e verificato numericamente,
  ha ridotto lo scan effettivo a soli $\varepsilon_{1q},\varepsilon_{2q}$.
- Scan: $N^*$ monotono non-crescente in entrambi i parametri di gate,
  satura a $N^*=1$ oltre una soglia di rumore. Pendenza log-log osservata
  più piatta della previsione ingenua $N^*\propto1/\sqrt{\varepsilon_{2q}}$
  — dichiarato come osservazione aperta, non forzato un fit scorretto.

**Prossimo passo:** integrazione di tutti i risultati di Parte 2 nel
documento finale di tesi; valorizzare il confronto RBS vs $W$ (Parte 1,
`scelta_ansatz_RBS_vs_W.tex`) come sezione metodologica a sé, come da nota
precedente in questo stesso file.
