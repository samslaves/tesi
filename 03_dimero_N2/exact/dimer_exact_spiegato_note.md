# Note sul notebook `dimer_exact_spiegato.ipynb`

Il notebook contiene:

**Spettro analitico** (`analytic_eigenvalues`): la formula chiusa
$$E(S,M) = 2J\,S(S+1) - 3J + 2bM$$
valida solo per $D=0$. E' la soluzione algebrica vera, ottenuta a carta e penna sfruttando le simmetrie ($[H_1,H_2]=0$, buoni numeri quantici $S$ e $M$). È implementata in tre righe di Python puro, senza diagonalizzare nulla.

**Diagonalizzazione numerica esatta** (`exact_sweep` con `eigh`): costruisce la matrice $4\times4$ di $H$ e la diagonalizza numericamente. È "esatta" nel senso che non usa nessuna approssimazione variazionale (non è un VQE), ma è comunque un calcolo numerico — soggetto a errori di arrotondamento floating point (i $\sim10^{-16}$ del self-test). Funziona anche per $D\neq0$, dove la soluzione algebrica chiusa non esiste.

Il notebook contiene entrambe, e il self-test le confronta proprio per verificare che coincidano (a meno di $\sim10^{-16}$). La diagonalizzazione numerica è il *benchmark* contro cui andro' misurare il VQE — è il riferimento "vero" rispetto al quale l'errore variazionale sarà giudicato:

$$\underbrace{E(S,M) = 2JS(S+1)-3J+2bM}_{\text{algebra esatta }(D=0)} \;\approx\; \underbrace{\texttt{eigh}}_{\text{numerico esatto (}D\text{ qualunque)}} \;\geq\; \underbrace{\langle H\rangle_{\boldsymbol\theta}}_{\text{VQE (variazionale, approssimato)}}$$

Il VQE cerca il minimo di $\langle H\rangle$ su una famiglia di stati parametrizzati, e per il teorema variazionale $\langle H\rangle_{\boldsymbol\theta} \geq E_0$ sempre — può solo avvicinarsi all'esatto, mai superarlo.

---

Si può confrontare il VQE contro la formula chiusa, ma solo per $D=0$ e solo per il dimero $N=2$.

La formula chiusa $E(S,M)=2JS(S+1)-3J+2bM$ esiste perché il dimero isotropo ha due simmetrie esatte che rendono $H$ diagonale nella base $|S,M\rangle$: $[H,S^2]=0$ e $[H,S_z]=0$. E' un caso eccezionalmente fortunato.

Non appena si esce da questo caso, la formula chiusa non esiste più:

- **Con $D\neq0$**: $[H,S_z]\neq0$, i buoni numeri quantici si rompono, lo spettro non si scrive in forma chiusa. Occorre diagonalizzare numericamente.
- **Con $N=3$** (catena o triangolo): l'Hamiltoniana è $8\times8$; ci sono ancora simmetrie (es. $S_z$ totale per la catena), ma lo spettro completo non ha una forma chiusa semplice.
- **Con rumore (Parte 2)**: lo stato è $\rho$, non $|\psi\rangle$, e il confronto va fatto sull'energia dell'operatore densità — ancora numerico.

La struttura del confronto nella tesi è quindi:

| sistema | riferimento per il VQE |
|---|---|
| $N=2$, $D=0$ | formula chiusa **e** `eigh` (coincidono) |
| $N=2$, $D=0.2$ | solo `eigh` |
| $N=3$ (entrambe le topologie) | solo `eigh` |
| Parte 2 (rumore) | solo `eigh` (su $\rho$) |

Per il dimero con $D=0$ si usano entrambi — ed è utile farlo esplicitamente, perché mostra la catena di validazione completa:

$$\text{formula chiusa} \approx \texttt{eigh} \approx \text{VQE} \quad (\text{con errore variazionale misurabile})$$

Il confronto operativo del VQE è però sempre contro `eigh`, perché è quello che scala a tutti i casi che ho in roadmap.
