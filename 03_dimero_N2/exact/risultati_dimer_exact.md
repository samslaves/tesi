# Lettura dei risultati — `dimer_exact.py`

## Cosa fa il modulo

Calcola la soluzione esatta del dimero di spin-1/2 ($N=2$) per una griglia di valori
del campo $b$, restituendo spettro, ground state, magnetizzazione e un self-test
automatico contro la formula analitica.

## Output del self-test

```
[self-test] max|E_num - E_analitico| (D=0) = 8.88e-16
```

$8.88 \times 10^{-16}$ è rumore di arrotondamento a precisione macchina
($\varepsilon_\text{float64} \approx 2.2 \times 10^{-16}$), otto ordini di grandezza
sotto la soglia di $10^{-10}$. Lo spettro numerico **coincide** con quello analitico
$E(S,M) = 2JS(S+1) - 3J + 2bM$: nessuna discrepanza fisica.

## Lettura della figura (`dimer_exact.png`)

**Pannello sinistro — Spettro $E/J$:**
- con $D=0$ (nero) il fondamentale è il singoletto ($E=-3J$, piatto) fino a
  $B/J=2$, poi lo stato $M=-1$ che scende linearmente; l'incrocio è netto;
- con $D=0.2$ (rosso tratteggiato) il fondamentale passa con continuità attraverso
  $B/J=2$: l'incrocio è diventato **evitato** (anticrossing), con gap minimo
  $\Delta \simeq 0.57$.

**Pannello destro — Magnetizzazione $\langle M_z \rangle$:**
- con $D=0$: salto netto da $0$ (singoletto) a $-1$ (tripletto $M=-1$) in $B/J=2$
  — firma della transizione del primo ordine;
- con $D=0.2$: crossover liscio attraverso $B/J=2$ — conseguenza diretta
  dell'anticrossing.

## Ruolo nel progetto

`dimer_exact.py` è il **metro di misura** dell'intera tesi. I moduli VQE importano
`dimer_hamiltonian`, `exact_sweep` e `analytic_eigenvalues` da questo file e non lo
modificano mai. La catena di validazione è:

$$\underbrace{E(S,M)}_{\text{formula chiusa}} \approx \underbrace{\texttt{eigh}}_{\text{numerico esatto}} \geq \underbrace{\langle H\rangle_{\boldsymbol\theta}}_{\text{VQE}}$$
