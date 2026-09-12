# Guida d'uso — riprodurre la pipeline di rumore sul dimero in locale

Questo pacchetto contiene tutto il codice necessario per riprodurre, da
zero, ogni simulazione, ogni numero e ogni figura usati nei documenti
sulla Parte 2 (rumore quantistico) del dimero — senza dipendere da
nessun file già calcolato: tutto si rigenera in locale.

## 1. Cosa c'è dentro

```
pacchetto_riproducibile/
├── codice/                    16 moduli Python (mattoni + pipeline + estensioni)
├── dati/                      dati intermedi (.npz) generati dagli script 01-03
├── figure/                    le 15 figure finali, in PDF e PNG
├── genera_figure/              11 script, uno o più per ciascuna figura
├── 01_genera_dati_vqe_ideale.py
├── 02_genera_dati_vqe_noise_aware.py
├── 03_genera_dati_secondo_punto.py
├── esegui_tutto.py             esegue tutto in un solo comando
└── GUIDA_USO.md                questo file
```

**`codice/`** contiene, senza alcuna modifica rispetto ai file di
progetto originali (verificato bit per bit prima di essere incluso qui):

| File | Cosa fa |
|---|---|
| `dimer_exact.py`, `vqe_test2.py` | Hamiltoniana esatta e VQE ideale (Parte 1) |
| `circuito_correlazioni_dimero.py` | circuito di Hadamard test per i correlatori (**versione corretta**, con supporto per la preparazione via VQE reale) |
| `noise_model_dimero.py` | modello di rumore (canale depolarizzante + readout, calibrazione `ibm_torino`) |
| `vqe_dm_rumoroso_dimero.py` | VQE con termine DM sotto rumore |
| `trotter_rumoroso_dimero.py` | quantum simulation (Trotter) sotto rumore |
| `correlatori_rumorosi_dimero.py` | correlatori dinamici sotto rumore |
| `scan_parametri_rumore_dimero.py` | scan sui parametri di rumore |
| `vqe_noise_aware_dimero.py` | estensione: ottimizzazione ripetuta del VQE sotto rumore |
| `correlatori_readout_asimmetrico.py` | estensione: errore di lettura asimmetrico |
| `validate_*.py` (4 file) | controlli di coerenza per ciascuno stadio, con soglie numeriche esplicite |
| `stile.py` | stile grafico condiviso da tutte le figure |

## 2. Prerequisiti

Testato con questa combinazione esatta di versioni (altre versioni
recenti di Qiskit 2.x dovrebbero funzionare, ma non sono state
verificate):

```
Python 3.12.3
qiskit           2.5.2
qiskit-aer       0.17.2
numpy            2.4.4
scipy            1.17.1
matplotlib       3.10.8
```

Installazione consigliata (ambiente virtuale):
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install qiskit qiskit-aer numpy scipy matplotlib
```

Non serve nessuna installazione LaTeX per questo pacchetto — le figure
sono generate direttamente in PDF/PNG da matplotlib, senza passare da
un motore di rendering matematico esterno (`mathtext.fontset: cm` di
matplotlib, autosufficiente).

## 3. Il modo più semplice: un solo comando

```bash
cd pacchetto_riproducibile
python3 esegui_tutto.py
```

Esegue in ordine: generazione dati (3 script), validazioni (4 script),
tutte le 15 figure (11 script). Si ferma al primo errore, indicando
esattamente quale fase e comando ha fallito. **Tempo stimato: 10–20
minuti** (le fasi più lente sono gli script di figura che ripetono
ottimizzazioni VQE a più valori di rumore).

Se tutto va a buon fine, l'ultima riga stampata è:
```
TUTTO COMPLETATO. 15 figure in figure/, dati in dati/.
```

## 4. Passo per passo (se preferisci controllare ogni fase)

### 4.1 Generazione dati

```bash
python3 01_genera_dati_vqe_ideale.py
```
Ottimizza il VQE ideale (nessun rumore) al punto di lavoro principale
(`b/J=0.35`, `D/J=0.80`). Produce `dati/ground_state_test2.npz`.
**Valore atteso**: energia $\approx-3.57321145$, fedeltà $\approx1.0000000000$.

```bash
python3 02_genera_dati_vqe_noise_aware.py
```
Ottimizza di nuovo il VQE con il rumore acceso durante l'ottimizzazione
stessa (non riusando i parametri ideali). Produce
`dati/vqe_noise_aware_result.npz`. **Valori attesi**:
$\Delta E\approx-1.16\times10^{-7}$, $\Delta F\approx+1.76\times10^{-8}$,
$N^*$ del correlatore $5\to5$.

```bash
python3 03_genera_dati_secondo_punto.py
```
Ripete gli stessi due calcoli a un secondo punto di lavoro
(`b/J=-0.18`, `D/J=1`), usato per verificare che i risultati non
dipendano dal punto scelto. Produce `dati/ground_state_punto2.npz` e
`dati/vqe_noise_aware_punto2.npz`.

### 4.2 Validazioni (facoltative ma consigliate)

Gli script `validate_*.py` dentro `codice/` si aspettano i dati nella
cartella corrente — copiali prima:
```bash
cp dati/*.npz codice/
cd codice
python3 validate_correlatori_rumorosi_dimero.py
python3 validate_scan_parametri_rumore_dimero.py
python3 validate_vqe_noise_aware_dimero.py
python3 validate_correlatori_readout_asimmetrico.py
cd ..
```
Ciascuno stampa un resoconto dettagliato con i valori attesi accanto a
quelli calcolati, e termina con un errore (`AssertionError`) se un
controllo fallisce — non un semplice messaggio ignorabile.

### 4.3 Figure

Ogni script in `genera_figure/` produce una o due figure specifiche,
elencate nel nome del file. Vanno eseguiti dalla **radice** del
pacchetto (non da dentro `genera_figure/`), perché caricano i dati da
`dati/` con percorso relativo:
```bash
python3 genera_figure/genera_fig_modello_rumore.py
python3 genera_figure/genera_fig_vqe_dm_rumoroso.py
python3 genera_figure/genera_fig_trotter_rumoroso.py
python3 genera_figure/genera_fig_correlatori_rumorosi.py
python3 genera_figure/genera_fig_scan_parametri.py
python3 genera_figure/genera_fig_trappola_transpilazione.py
python3 genera_figure/genera_fig_scan_eps2q_confronto.py
python3 genera_figure/genera_fig_correlatore_confronto.py
python3 genera_figure/genera_fig_secondo_punto.py
python3 genera_figure/genera_fig_robustezza_multistart.py
python3 genera_figure/genera_fig_griglia_completa.py
python3 genera_figure/genera_fig_readout_asimmetrico.py
```
(alcuni producono due figure ciascuno — la corrispondenza figura↔script
è comunque nel nome del file .py).

## 5. Come sapere se un numero è quello giusto

Ogni script stampa a schermo il valore appena calcolato **accanto** al
valore atteso (commento `# atteso: ...` o riga di stampa dedicata) —
non serve confrontare a memoria con i documenti. Se un numero non
coincide entro l'ultima cifra significativa mostrata, qualcosa nel tuo
ambiente locale (versione di Qiskit, seed del generatore casuale,
ordine di esecuzione) sta producendo un risultato diverso: fermati e
confronta prima di proseguire.

## 6. Due insidie già trovate e corrette — se modifichi il codice, occhio a queste

**Non transpilare mai il circuito intero per i passi di Trotter
ripetuti.** Se transpili l'intero circuito assemblato (ancilla +
preparazione + $N$ passi + misura) a un livello di ottimizzazione alto,
Qiskit può riconoscere che gli $N$ passi identici formano un unico
blocco e comprimerli in un circuito a costo costante — cancellando
silenziosamente la dipendenza da $N$ che è l'oggetto stesso dello
studio. La soluzione già in uso ovunque in questo pacchetto: transpilare
una volta il singolo passo, poi comporre il blocco già compilato $N$
volte senza più transpilare.

**Alcune funzioni hanno il punto di lavoro `(b, D, J)` fissato come
costante di modulo, non come parametro.** In particolare
`vqe_energia_fedelta_rumorosa()` (in `vqe_dm_rumoroso_dimero.py`) e
`vqe_noise_aware()` (in `vqe_noise_aware_dimero.py`) costruiscono
internamente l'Hamiltoniana usando `b`, `D`, `J` definiti in testa al
modulo (il punto "test 2"), non un argomento della funzione. Per
lavorare a un punto diverso (come nello script
`03_genera_dati_secondo_punto.py`) serve sovrascrivere esplicitamente
quegli attributi di modulo **prima** di chiamare la funzione:
```python
import vqe_noise_aware_dimero as vna_module
vna_module.b, vna_module.D, vna_module.J = -0.18, 1.0, 1.0
```
Altrimenti l'ottimizzazione avviene silenziosamente sul punto di lavoro
sbagliato, senza nessun errore — solo numeri finali non corrispondenti
a quelli attesi. Questo pacchetto lo fa già correttamente in
`03_genera_dati_secondo_punto.py`; se scrivi un nuovo script per un
terzo punto di lavoro, applica lo stesso schema.

## 7. Cosa NON è incluso in questo pacchetto

I documenti `.tex`/`.pdf` che usano queste figure (i cinque documenti
della pipeline base, l'estensione VQE noise-aware, l'estensione
readout asimmetrico) sono deliverable separati, già consegnati in
precedenza — questo pacchetto riproduce i **numeri e le figure**, non
il testo che li commenta. I nomi dei file delle figure qui prodotte
coincidono esattamente con quelli richiamati nei documenti (`\includegraphics{figure/nome.pdf}`),
quindi puoi copiare la cartella `figure/` accanto a un documento `.tex`
per ricompilarlo.
