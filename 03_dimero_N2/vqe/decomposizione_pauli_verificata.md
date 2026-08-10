# La Decomposizione di Pauli per Hamiltoniane Quantistiche

> **Nota di verifica** (A. Chiesa / UniPR): documento rivisto per coerenza con la convenzione di
> 6-Applications e Crippa et al., *Magnetochemistry* **7**, 117 (2021).
> Le correzioni rispetto alla versione originale sono segnalate in corsivo tra parentesi quadre.

---

## 1. La Base di Pauli

In meccanica quantistica, l'Hamiltoniana $H$ di un sistema a $N$ qubit è una matrice hermitiana di
dimensioni $2^N \times 2^N$.

Le matrici di Pauli a singolo qubit, insieme alla matrice identità, formano un insieme di 4 operatori:

$$\{\sigma_0 = I,\quad \sigma_1 = X,\quad \sigma_2 = Y,\quad \sigma_3 = Z\}$$

Per un sistema di $N$ qubit, le **stringhe di Pauli** sono tutti i prodotti tensoriali di $N$ operatori:

$$P_{\boldsymbol{\mu}} = \sigma_{\mu_1} \otimes \sigma_{\mu_2} \otimes \cdots \otimes \sigma_{\mu_N},
\qquad \mu_i \in \{0,1,2,3\}.$$

Il numero totale di stringhe è $4^N$. Esse formano una **base ortonormale completa** dello spazio
vettoriale delle matrici $2^N \times 2^N$ rispetto al prodotto scalare di Hilbert–Schmidt:

$$\frac{1}{2^N}\operatorname{Tr}(P_{\boldsymbol{\mu}}^\dagger\, P_{\boldsymbol{\nu}}) = \delta_{\boldsymbol{\mu}\boldsymbol{\nu}}.$$

Di conseguenza, qualsiasi hamiltoniana hermitiana $H$ ammette la decomposizione **esatta e unica**:

$$\boxed{H = \sum_{\boldsymbol{\mu}} h_{\boldsymbol{\mu}}\, P_{\boldsymbol{\mu}}}$$

con coefficienti **reali** (la hermitianità di $H$ garantisce $h_{\boldsymbol{\mu}} \in \mathbb{R}$).

---

## 2. Come si trovano i coefficienti

Per isolare il peso di una specifica stringa di Pauli $P_k$ si sfrutta l'ortogonalità:

$$\boxed{h_k = \frac{1}{2^N}\operatorname{Tr}(P_k\, H)}$$

Il calcolo è esplicito: poiché $P_k$ è hermitiana e unitaria, $P_k^2 = I$, quindi
$\operatorname{Tr}(P_k \cdot P_j) = 2^N \delta_{kj}$.

---

## 3. Convenzione di notazione Qiskit (little-endian)

> *Punto critico per evitare errori di implementazione.*

In Qiskit, le stringhe di Pauli sono scritte in ordine **little-endian**: il carattere più a
**destra** della stringa corrisponde al qubit con indice **0**, quello più a sinistra al qubit con
indice più alto. Quindi:

| Stringa Qiskit | Operatore matematico |
|:---:|:---:|
| `"ZI"` | $Z_1 \otimes I_0$ |
| `"IZ"` | $I_1 \otimes Z_0$ |
| `"XX"` | $X_1 \otimes X_0$ |
| `"XY"` | $X_1 \otimes Y_0$ |

Questa convenzione si applica a `SparsePauliOp` in Qiskit 2.x ed è **invertita** rispetto alla
notazione matematica standard (dove il primo indice è il qubit più a sinistra nel prodotto
tensoriale). Tenerne conto è essenziale nella costruzione di `SparsePauliOp.from_list(...)`.

---

## 4. Sistemi non a qubit: fermioni e bosoni

Se l'Hamiltoniana descrive elettroni (fermioni) o campi (bosoni), non nasce direttamente in termini
di Pauli, ma in termini di operatori di creazione e annichilazione $\hat{a}_i^\dagger, \hat{a}_j$.

Per i **sistemi fermionici** (es. elettroni in una molecola) si usano mappature come:
- **Jordan–Wigner**: mappa locale, ma genera stringhe di Pauli di lunghezza $O(N)$.
- **Bravyi–Kitaev**: stringhe mediamente più corte, overhead minore.

Queste trasformazioni preservano le relazioni di anticommutazione e quindi lo spettro energetico.

Per i **sistemi bosonici** (spazio di Hilbert infinito-dimensionale) occorre prima troncare lo spazio
a un numero massimo di occupazione, poi mappare i livelli risultanti su qubit.

> **Vantaggio dei sistemi spin-1/2** (rilevante per la tesi): ogni spin-1/2 si mappa
> *direttamente* su un qubit senza alcun mapping aggiuntivo — questo è il punto chiave
> sottolineato da Crippa et al. e dal Prof. Chiesa in 6-Applications.

---

## 5. Un esempio esplicito: due qubit interagenti

Consideriamo la seguente matrice hermitiana $4\times 4$:

$$H = \begin{pmatrix} 1.0 & 0.0 & 0.0 & 0.5 \\ 0.0 & -1.0 & 0.5 & 0.0 \\ 0.0 & 0.5 & -1.0 & 0.0 \\ 0.5 & 0.0 & 0.0 & 1.0 \end{pmatrix}$$

Applicando la formula dei coefficienti si ottiene:

$$H = 0.5\,(Z \otimes I) + 0.5\,(I \otimes Z) + 0.5\,(X \otimes X)$$

ovvero, in notazione con pedici fisici:

$$H = 0.5\, Z_1 + 0.5\, Z_0 + 0.5\, X_1 X_0$$

Il valore atteso su uno stato $|\psi\rangle$ si calcola per linearità:

$$\langle H \rangle = 0.5\,\langle Z_1 \rangle + 0.5\,\langle Z_0 \rangle + 0.5\,\langle X_1 X_0 \rangle$$

---

## 6. Il modello di Heisenberg isotropo per il dimero (convenzione 6-Applications)

> *Sezione aggiunta per chiarire la convenzione della tesi.*

In 6-Applications e in Crippa et al., il dimero di Heisenberg è scritto come:

$$H = J_x X_1 X_2 + J_y Y_1 Y_2 + J_z Z_1 Z_2 + b(Z_1 + Z_2)$$

dove $X_i, Y_i, Z_i$ **sono già operatori di Pauli** (non operatori di spin $s_i = \sigma_i/2$).
Nel caso isotropo $J_x = J_y = J_z = J$:

$$H = J(X_1 X_2 + Y_1 Y_2 + Z_1 Z_2) + b(Z_1 + Z_2)$$

> **Attenzione alla convenzione**: questo va distinto dall'Hamiltoniana scritta in termini di
> operatori di spin $\vec{s}_i = \vec{\sigma}_i/2$, che darebbe
> $H = 2J\,\vec{s}_1\cdot\vec{s}_2 + \ldots$ con un fattore di scala 4 sulle energie.
> In 6-Applications la scrittura in Pauli è quella diretta (nessun fattore 1/4).

L'energia del **ground state** (singoletto, $b=0$) per questa convenzione è $E_0 = -3J$.

---

## 7. Come si misura una stringa di Pauli su hardware quantistico

I computer quantistici commerciali (IBM, Rigetti, ecc.) misurano nativamente solo lungo l'asse $Z$
(base computazionale $|0\rangle, |1\rangle$). Per misurare un termine diverso si applica una
**rotazione di base** prima della misura:

| Operatore da misurare | Porta(e) da applicare prima della misura |
|:---:|:---:|
| $Z$ | Nessuna (base nativa) |
| $X$ | $H$ (Hadamard) |
| $Y$ | $S^\dagger$ poi $H$ |

La corrispondenza bit → autovalore è: $0 \mapsto +1$, $1 \mapsto -1$.

### Esempio: misura della stringa $X_0 Y_1 Z_2$

```
|ψ_0⟩ ──[ H ]──────[ M ]   ← asse X
|ψ_1⟩ ──[ S†]─[ H ]─[ M ]  ← asse Y
|ψ_2⟩ ───────────────[ M ]  ← asse Z (nativo)
```

Per ogni *shot* (es. risultato `010`):

$$0 \to +1, \quad 1 \to -1, \quad 0 \to +1 \implies (+1)\times(-1)\times(+1) = -1$$

Il valore atteso $\langle X_0 Y_1 Z_2 \rangle$ è la media su tutti gli *shot*.

---

## 8. Misura dell'Hamiltoniana del dimero isotropo

Per $H = J(X_1 X_2 + Y_1 Y_2 + Z_1 Z_2)$ sono necessari **tre circuiti di misura distinti**,
poiché le stringhe $XX$, $YY$, $ZZ$ non sono simultaneamente diagonalizzabili nella stessa base
(non commutano tutte a coppie: ad esempio $[X_1 X_2,\, Y_1 Y_2] \neq 0$).

> *Nota: il documento originale usava la formula "non commutano tutte simultaneamente" senza
> precisare perché questo implica circuiti separati. Il motivo è che ciascuna stringa è
> diagonalizzabile nella propria base di autostati, ma le tre basi sono diverse, quindi non
> esiste un'unica rotazione che diagonalizzi tutte e tre contemporaneamente.*

**Circuito 1** — misura di $Z_1 Z_2$ (base nativa, nessuna rotazione):

$$ZZ: \quad 00 \to +1,\quad 01 \to -1,\quad 10 \to -1,\quad 11 \to +1$$

**Circuito 2** — misura di $X_1 X_2$ (applicare $H$ su entrambi i qubit, poi misurare):

$$\text{Post-processing identico a } ZZ$$

**Circuito 3** — misura di $Y_1 Y_2$ (applicare $S^\dagger H$ su entrambi i qubit, poi misurare):

$$\text{Post-processing identico a } ZZ$$

L'energia totale:

$$\langle H \rangle = J\bigl(\langle X_1 X_2\rangle + \langle Y_1 Y_2\rangle + \langle Z_1 Z_2\rangle\bigr)$$

---

## 9. Verifica analitica: lo stato di singoletto

Lo stato di singoletto è:

$$|\psi\rangle = \frac{1}{\sqrt{2}}\bigl(|01\rangle - |10\rangle\bigr)$$

> *Convenzione ket Qiskit*: in $|q_1 q_0\rangle$, lo stato $|01\rangle$ significa
> $q_1 = 0$, $q_0 = 1$.

### Termine $Z_1 Z_2$

$$(Z \otimes Z)|\psi\rangle = \frac{1}{\sqrt{2}}\bigl[(Z|0\rangle)\otimes(Z|1\rangle) - (Z|1\rangle)\otimes(Z|0\rangle)\bigr]
= \frac{1}{\sqrt{2}}\bigl[-|01\rangle + |10\rangle\bigr] = -|\psi\rangle$$

$$\Rightarrow \langle Z_1 Z_2\rangle = -1$$

### Termine $X_1 X_2$

$$(X \otimes X)|\psi\rangle = \frac{1}{\sqrt{2}}\bigl[|10\rangle - |01\rangle\bigr] = -|\psi\rangle$$

$$\Rightarrow \langle X_1 X_2\rangle = -1$$

### Termine $Y_1 Y_2$

$$(Y \otimes Y)|\psi\rangle = \frac{1}{\sqrt{2}}\bigl[(i|1\rangle)\otimes(-i|0\rangle) - (-i|0\rangle)\otimes(i|1\rangle)\bigr]$$

$$= \frac{1}{\sqrt{2}}\bigl[|10\rangle - |01\rangle\bigr] = -|\psi\rangle$$

$$\Rightarrow \langle Y_1 Y_2\rangle = -1$$

### Energia totale

$$\langle H \rangle = J(-1-1-1) = -3J$$

Per $J > 0$ (accoppiamento antiferromagnetico), $-3J$ è il minimo dello spettro, confermando
che il singoletto è lo **stato fondamentale**.

> **Raccordo con la convenzione di Crippa**: se si parte da
> $H = 2J\sum_i \vec{s}_i \cdot \vec{s}_{i+1}$ con $\vec{s}_i = \vec{\sigma}_i/2$,
> il termine di scambio diventa $\frac{J}{2}(XX+YY+ZZ)$ e l'energia del singoletto è
> $-3J/4$. Il fattore 4 di differenza proviene da $s_i = \sigma_i/2$.
> In questo documento si usa la convenzione di 6-Applications dove i coefficienti
> $J_x, J_y, J_z$ moltiplicano direttamente gli operatori di Pauli, senza il fattore $1/4$.

---

## 10. Il vantaggio pratico: perché la decomposizione di Pauli è il pilastro del VQE

La decomposizione in stringhe di Pauli è essenziale perché:

1. **I computer quantistici non possono misurare una matrice generica**, ma sanno misurare
   $X$, $Y$, $Z$ su ogni qubit con alta efficienza.
2. **La linearità** del valor medio permette di calcolare $\langle H \rangle$ come somma pesata
   dei valori medi dei singoli termini.
3. **La sparsità** delle hamiltoniane fisiche garantisce che il numero di termini non nulli cresca
   polinomialmente in $N$ (come $O(N^k)$ per interazioni a $k$ corpi), rendendo il calcolo scalabile.
4. **Nel caso spin-1/2 → qubit**, l'Hamiltoniana è *già* in forma di Pauli senza mapping
   aggiuntivo — il vantaggio chiave sottolineato da Crippa et al.
