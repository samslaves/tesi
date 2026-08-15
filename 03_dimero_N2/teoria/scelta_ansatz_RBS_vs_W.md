# RBS vs $W_{ij}(\theta)$: perché il blocco $M$-conservante del PMA-2q resta RBS anche per il trimero

**Contesto.** In `confronto_ansatz_entangler.ipynb` (N=2) il blocco $M$-conservante del PMA
è realizzato come rotazione di Givens reale (RBS). Crippa et al. (*Magnetochemistry* 7,
117, 2021), nel costruire il PMA per anelli di spin a $N=4,6$, usano invece un gate diverso,
$W_{ij}(\theta)=e^{-i\theta\,\mathbf s_i\cdot\mathbf s_j}$. Questo documento deriva
esplicitamente la differenza fra i due gate, quantifica il costo in gate e l'espressività,
e motiva la scelta di **restare su RBS** anche per l'estensione a N=3 (triangolo isoscele).

---

## 1. Il gate RBS

Nel sottospazio a due qubit, ristretto al settore $M=0$ (cioè allo spazio
$\{|01\rangle,|10\rangle\}$), RBS è la rotazione di Givens reale:

$$
\mathrm{RBS}(\varphi) =
\begin{pmatrix}
1 & 0 & 0 & 0\\
0 & \cos\varphi & -\sin\varphi & 0\\
0 & \sin\varphi & \cos\varphi & 0\\
0 & 0 & 0 & 1
\end{pmatrix}
\quad\text{(base }|00\rangle,|01\rangle,|10\rangle,|11\rangle\text{)}.
$$

Identità su $|00\rangle,|11\rangle$; sul sottospazio $\{|01\rangle,|10\rangle\}$ agisce come
$R_y(2\varphi)$ reale (a meno di parametrizzazione dell'angolo). Applicato a $|01\rangle$:

$$
\mathrm{RBS}(\varphi)\,|01\rangle = \cos\varphi\,|01\rangle + \sin\varphi\,|10\rangle .
$$

**Punto chiave:** i coefficienti sono **reali** per ogni $\varphi$.

Implementazione già validata nel progetto (self-test $\sim10^{-16}$ contro il target):
$$
\mathrm{RBS}(\varphi) = (H\otimes H)\;\mathrm{CZ}\;\big(R_y(\varphi)_{q_0}\otimes R_y(-\varphi)_{q_1}\big)\;\mathrm{CZ}\;(H\otimes H).
$$

Costo: **2 gate a due qubit** ($CZ$, equivalenti a CNOT tramite $CZ = (I\otimes H)\,\mathrm{CNOT}\,(I\otimes H)$).

---

## 2. Il gate $W_{ij}(\theta)$ (Crippa et al.)

$$
W_{ij}(\theta) = e^{-i\theta\,\mathbf s_i\cdot\mathbf s_j}, \qquad \mathbf s = \boldsymbol\sigma/2.
$$

### 2.1 Spettro di $\mathbf s_i\cdot\mathbf s_j$

Per due spin-1/2, usando $\mathbf s_i\cdot\mathbf s_j = \tfrac12\big(\mathbf S^2 - s_i^2 - s_j^2\big)$
con $s_i^2=s_j^2=\tfrac34$ (autovalore di $s(s+1)$ con $s=1/2$):

- **Tripletto** ($S=1$, $S(S+1)=2$): $\mathbf s_i\cdot\mathbf s_j = \tfrac12(2-\tfrac34-\tfrac34)=\tfrac14$.
- **Singoletto** ($S=0$): $\mathbf s_i\cdot\mathbf s_j = \tfrac12(0-\tfrac34-\tfrac34)=-\tfrac34$.

Quindi $W_{ij}(\theta)$ è **diagonale nella base singoletto/tripletto**, con autovalori
$e^{-i\theta/4}$ (tripletto) ed $e^{i3\theta/4}$ (singoletto) — una fase relativa fra i due
settori, non una rotazione reale.

### 2.2 Azione esplicita su $|01\rangle$

Scriviamo $|01\rangle$ nella base singoletto/tripletto:
$$
|01\rangle = \frac{|t_0\rangle+|s\rangle}{\sqrt2},\qquad
|t_0\rangle=\frac{|01\rangle+|10\rangle}{\sqrt2},\quad
|s\rangle=\frac{|01\rangle-|10\rangle}{\sqrt2}.
$$

Applicando $W_{ij}(\theta)$ (autovalore $e^{-i\theta/4}$ su $|t_0\rangle$, $e^{i3\theta/4}$ su $|s\rangle$):

$$
W_{ij}(\theta)\,|01\rangle = \frac{1}{\sqrt2}\Big(e^{-i\theta/4}|t_0\rangle + e^{i3\theta/4}|s\rangle\Big).
$$

Tornando alla base computazionale ($|t_0\rangle,|s\rangle$ in funzione di $|01\rangle,|10\rangle$):

$$
W_{ij}(\theta)\,|01\rangle = \frac{1}{2}\Big[(e^{-i\theta/4}+e^{i3\theta/4})\,|01\rangle
+(e^{-i\theta/4}-e^{i3\theta/4})\,|10\rangle\Big].
$$

Raccogliendo la fase globale $e^{-i\theta/4}$:

$$
W_{ij}(\theta)\,|01\rangle = \frac{e^{-i\theta/4}}{2}\Big[(1+e^{i\theta})\,|01\rangle+(1-e^{i\theta})\,|10\rangle\Big].
$$

### 2.3 Confronto diretto con RBS: stesse probabilità, fase diversa

Usando $1+e^{i\theta}=2\cos(\theta/2)\,e^{i\theta/2}$ e $1-e^{i\theta}=-2i\sin(\theta/2)\,e^{i\theta/2}$:

$$
W_{ij}(\theta)\,|01\rangle = e^{i\theta/4}\Big[\cos(\theta/2)\,|01\rangle - i\sin(\theta/2)\,|10\rangle\Big].
$$

A meno della fase globale $e^{i\theta/4}$ (irrilevante fisicamente), ponendo $\varphi=\theta/2$:

$$
\boxed{\;W_{ij}(2\varphi)\,|01\rangle \;\dot=\; \cos\varphi\,|01\rangle - i\sin\varphi\,|10\rangle\;}
\qquad\text{contro}\qquad
\mathrm{RBS}(\varphi)\,|01\rangle = \cos\varphi\,|01\rangle + \sin\varphi\,|10\rangle .
$$

Le **probabilità** di misurare $|01\rangle$ o $|10\rangle$ sono identiche in entrambi i casi
($\cos^2\varphi$, $\sin^2\varphi$): i due gate sono equivalenti *a livello di popolazioni*.
Quello che li distingue è la **fase relativa** fra le due ampiezze: reale ($+1$, riassorbibile
nel segno) per RBS, **immaginaria** ($-i$) per $W$. Non è un dettaglio di convenzione: è una
proprietà strutturale del generatore. $\mathbf s_i\cdot\mathbf s_j$, ristretto al sottospazio
$\{|01\rangle,|10\rangle\}$, è proporzionale a una matrice di Pauli $X$ effettiva (scambio puro),
il cui esponenziale genera rotazioni con off-diagonal immaginario — la stessa famiglia del gate
iSWAP, non quella del gate SWAP/Givens reale. RBS, per costruzione (Ry reali coniugati da
Hadamard/CZ), resta nella famiglia delle rotazioni **reali**.

---

## 3. Costo in gate

| gate | decomposizione | gate a 2 qubit |
|---|---|---|
| $\mathrm{RBS}(\varphi)$ | $H\text{-}CZ\text{-}R_y\text{-}R_y\text{-}CZ\text{-}H$ | **2** ($CZ$) |
| $W_{ij}(\theta)$ (Crippa, eq. 6) | sequenza a gate singolo qubit + CNOT | **3** (CNOT) |

Sostituire RBS con $W$ **non** rende l'ansatz più compatto: lo appesantisce di un gate a due
qubit per blocco (50% in più).

**Nota per evitare un'ambiguità di lettura.** Questo costo aggiuntivo è un argomento *a favore*
di RBS, non a favore di $W$ — vale ancora di più, non di meno, quando in Parte 2 si introduce
il rumore: ogni gate a due qubit (CNOT o CZ) è un canale di errore in più (depolarizzazione,
errori di gate, ecc. — coerente con l'analisi già fatta in `costo_gate_trotter.md` per il
blocco Trotter del dimero, dove il conteggio di CNOT è stato esplicitamente il criterio per
confrontare le decomposizioni). Meno CNOT per blocco significa un ansatz più robusto quando si
passa al simulatore rumoroso. **RBS resta quindi la scelta giusta anche in Parte 2, a maggior
ragione**, non solo in Parte 1.

Va sottolineato che il passaggio a Parte 2 cambia la *dinamica* (stato puro → operatore
densità, evoluzione unitaria → canali di Kraus/Lindblad), non l'*Hamiltoniana*: $H$ resta la
stessa matrice reale simmetrica. L'argomento di realtà della Sezione 4 (teorema spettrale
$\Rightarrow$ ground state reale $\Rightarrow$ RBS espressivamente sufficiente) dipende solo
da $H$, non da come si esegue la ricerca variazionale né da quanto rumore è presente nel
circuito. Il rumore (bit-flip, $T_1$, $T_2$, ecc.) non richiede fasi complesse nell'*ansatz*
per essere modellato: agisce come canale separato sull'output del circuito, non sui parametri
variazionali. Le due motivazioni — realtà di $H$ e minor costo in gate — si sommano, non si
sostituiscono a vicenda.

---

## 4. Espressività: perché la fase immaginaria è superflua qui

**Argomento di realtà (teorema spettrale).** L'Hamiltoniana del trimero isoscele,

$$
H = J\,\boldsymbol\sigma_1\cdot\boldsymbol\sigma_2 + J'(\boldsymbol\sigma_2\cdot\boldsymbol\sigma_3+\boldsymbol\sigma_3\cdot\boldsymbol\sigma_1) + b\sum_i Z_i,
$$

è **reale simmetrica** in ogni base computazionale: $\boldsymbol\sigma_i\cdot\boldsymbol\sigma_j = X_iX_j+Y_iY_j+Z_iZ_j$
ha matrice reale (anche $Y_iY_j$: il prodotto di due entrate immaginarie di $Y$ dà un'entrata
reale — stesso argomento già verificato per il dimero), e $\sum_i Z_i$ è diagonale reale. Per il
teorema spettrale, una matrice reale simmetrica ammette una base ortonormale di **autovettori
reali**: lo stato fondamentale può sempre essere scelto reale, qualunque sia la degenerazione.

**Conseguenza per l'ansatz.** Un ansatz che deve raggiungere solo stati reali non ha bisogno di
esplorare fasi complesse. $W_{ij}(\theta)$ esplora l'intero $U(2)$ ristretto al settore $M=0$
della coppia (include la fase $-i$ di iSWAP); RBS esplora solo il sottogruppo reale $SO(2)$.
La differenza è esattamente lo stesso tipo di ridondanza già isolata e quantificata per gli
ansatz A–D nel dimero (dove $n_\text{par}-3$ parametri risultavano gauge, non fisici): qui il
"parametro extra" non è un angolo in più ma un **grado di libertà di fase per blocco**, sempre
sprecato.

**Quando smetterebbe di essere superfluo.** Il vincolo di realtà cade se si introduce un
termine che rende $H$ genuinamente complessa. Il DM già usato nel dimero, nella forma
$D(X_iZ_j-Z_iX_j)$, resta **reale** (stessa argomentazione) — quindi anche estendendolo al
triangolo con la stessa forma, RBS continuerebbe a bastare. Servirebbe passare a $W$ (o
equivalentemente aggiungere $R_z$ nel blocco) solo con un termine genuinamente immaginario,
come il DM "canonico" $D(X_iY_j-Y_iX_j)$ — esplicitamente fuori dallo scope attuale (vedi
punto 9 di `domande_relatore.md`).

---

## 5. Verifica numerica di quanto derivato sopra

Controllo diretto (non solo simbolico) che $W_{ij}(2\varphi)$ e $\mathrm{RBS}(\varphi)$ diano
le stesse probabilità ma fasi diverse, per alcuni valori di $\varphi$:

```python
import numpy as np

def sdot(theta):
    """W_ij(theta) = exp(-i*theta*s_i.s_j), spin s=sigma/2, base |00>,|01>,|10>,|11>."""
    X = np.array([[0,1],[1,0]], dtype=complex)
    Y = np.array([[0,-1j],[1j,0]], dtype=complex)
    Z = np.array([[1,0],[0,-1]], dtype=complex)
    s = [0.5*X, 0.5*Y, 0.5*Z]
    sdotop = sum(np.kron(a,a) for a in s)
    w, v = np.linalg.eigh(sdotop)
    return v @ np.diag(np.exp(-1j*theta*w)) @ v.conj().T

def rbs(phi):
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]], dtype=complex)

ket01 = np.array([0,1,0,0], dtype=complex)
for phi in [0.3, 0.9, 1.4]:
    out_W   = sdot(2*phi) @ ket01
    out_RBS = rbs(phi) @ ket01
    print(f"phi={phi:.2f}  W: {out_W.round(4)}   RBS: {out_RBS.round(4)}  "
          f"|prob uguali|: {np.allclose(np.abs(out_W)**2, np.abs(out_RBS)**2)}")
```

Atteso (coerente con la derivazione della Sezione 2.3): componente su $|01\rangle$ reale e
uguale in entrambi i casi ($\cos\varphi$); componente su $|10\rangle$ reale positiva per RBS
($\sin\varphi$), immaginaria negativa per $W$ ($-i\sin\varphi$, a meno della fase globale
$e^{i\theta/4}$) — probabilità identiche, fase strutturalmente diversa.

---

## 6. Conclusione operativa

1. **RBS resta il blocco $M$-conservante di riferimento**, anche per il trimero: stesso
   potere espressivo di $W$ sulle popolazioni, costo inferiore (2 vs 3 gate a due qubit per
   blocco), nessuna capacità aggiuntiva sprecata dato che $H$ è reale.
2. Quello che vale la pena **riusare concettualmente** dal paper di Crippa et al. non è il
   gate, ma la **struttura**: layer su più legami (qui i tre bond $12,23,31$), stato iniziale
   scelto nel settore di simmetria del multipletto target (qui, guidato dalla decomposizione
   di Kambe: $S_{12}=0$ per il blocco C, $S_{12}=1$ per A/B), e l'euristica sull'ordine dei
   legami (applicare prima il bond che porta lo stato locale singoletto/tripletto).
3. Il blocco RBS applicato su una coppia qualunque, con il terzo qubit spettatore, **conserva
   comunque $M$ totale** a 3 qubit (conserva $m_i+m_j$ della coppia, lascia $m_k$ invariato):
   la proprietà chiave del PMA si eredita intatta nel passaggio a N=3.
4. Il vincolo va **ridiscusso** solo se in futuro si introduce un termine DM immaginario sul
   triangolo (non in scope ora).

---

## 7. Perché RBS trova il ground state anche sopra soglia ($b/J>2$)

### Il problema: RBS da solo conserva $M$

Un singolo blocco RBS agisce solo sul settore $\{|01\rangle,|10\rangle\}$ e lascia
invariati $|00\rangle$ e $|11\rangle$. Partendo da $|01\rangle$:

$$\mathrm{RBS}(\varphi)|01\rangle = \cos\varphi\,|01\rangle + \sin\varphi\,|10\rangle,$$

cioè lo stato rimane sempre a $M=0$. Il ground state sopra soglia ($b/J>2$) è
$|t_-\rangle=|11\rangle$ con $M=-1$: irraggiungibile applicando solo RBS.

Questa è la stessa ragione per cui il PMA di base (1 parametro, solo un blocco RBS
dopo lo stato iniziale $X|00\rangle=|10\rangle$) fallisce a $b/J>2$ anche con $D=0$:
non è un effetto del termine DM, è semplicemente l'assenza di un meccanismo per uscire
dal settore $M=0$.

### La soluzione: gli strati $R_y$ rompono la conservazione di $M$

L'ansatz PMA-2q non è solo RBS. Ogni strato ha la struttura

$$\bigl(R_y(\alpha_k)\otimes R_y(\beta_k)\bigr)\cdot\mathrm{RBS}(\varphi_k),$$

con $\alpha_k \neq \beta_k$ in generale (parametri indipendenti sui due qubit). Un gate
$R_y(\alpha)$ su un singolo qubit $q_i$ agisce localmente come

$$R_y(\alpha)|0\rangle = \cos\tfrac{\alpha}{2}|0\rangle - \sin\tfrac{\alpha}{2}|1\rangle,\quad
R_y(\alpha)|1\rangle = \sin\tfrac{\alpha}{2}|0\rangle + \cos\tfrac{\alpha}{2}|1\rangle,$$

e quindi **mescola $|0\rangle$ e $|1\rangle$ su quel qubit**. Applicato dopo RBS (che ha
prodotto uno stato in $M=0$), un $R_y$ locale redistribuisce ampiezza verso settori
$M=\pm1$, incluso $|11\rangle$. La sequenza completa esplora tutto lo spazio reale dei
2 qubit, non solo il settore $M=0$.

**Meccanismo esplicito.** Dopo il blocco RBS lo stato è
$|\psi\rangle = a|01\rangle+b|10\rangle$ (con $a,b$ reali, $a^2+b^2=1$).
Applicando $R_y(\alpha)\otimes R_y(\beta)$:

$$\bigl(R_y(\alpha)\otimes R_y(\beta)\bigr)(a|01\rangle+b|10\rangle)$$
$$= a\bigl(\cos\tfrac\alpha2|0\rangle-\sin\tfrac\alpha2|1\rangle\bigr)\otimes
\bigl(\sin\tfrac\beta2|0\rangle+\cos\tfrac\beta2|1\rangle\bigr)$$
$$+\ b\bigl(\sin\tfrac\alpha2|0\rangle+\cos\tfrac\alpha2|1\rangle\bigr)\otimes
\bigl(\cos\tfrac\beta2|0\rangle-\sin\tfrac\beta2|1\rangle\bigr).$$

Espandendo, il coefficiente di $|11\rangle$ è
$-a\sin\tfrac\alpha2\cos\tfrac\beta2 + b\cos\tfrac\alpha2\sin\tfrac\beta2$,
che è zero solo se $\alpha=\beta$ oppure $a=b=0$. Per $\alpha\neq\beta$ generici
lo stato ha componente non nulla su $|11\rangle$ (settore $M=-1$): l'ottimizzatore
può quindi portare $E(\boldsymbol\theta)$ verso l'energia di $|11\rangle$ sopra soglia.

### Perché $W$ non aveva questo problema (ma per una ragione diversa da quella apparente)

$W_{ij}(\theta)=e^{-i\theta\,\mathbf{s}_i\cdot\mathbf{s}_j}$ **conserva anch'esso $M$**
(è diagonale nella base $\{$singoletto, tripletto$\}$, che è una base con $M$ definito).
La ragione per cui il PMA originale di Crippa et al. funzionava sopra soglia non è che $W$
esce dal settore $M=0$, ma che nell'implementazione di Crippa il gate $W$ era sempre
accompagnato da rotazioni locali, esattamente come nel PMA-2q qui — quelle rotazioni
locali sono il meccanismo che popola $|11\rangle$, non $W$ in sé.

### Tabella riassuntiva

| componente | conserva $M$? | raggiunge $|11\rangle$? | ruolo |
|---|---|---|---|
| $\mathrm{RBS}(\varphi)$ da solo | sì ($M=0$) | no | entangler nel settore $M=0$ |
| $R_y(\alpha)\otimes R_y(\alpha)$ (parametro condiviso) | no | sì | ma non abbastanza per $\mathcal{F}=1$ (vedi `analisi_rotazioni_PMA.ipynb`) |
| $R_y(\alpha)\otimes R_y(\beta)$ (parametri indipendenti) | no | sì | popola tutti i settori, necessario per $\mathcal{F}=1$ |
| PMA-2q·3 (K=1, 3 parametri totali) | no | sì | $\mathcal{F}=1$ su tutto il range con il numero minimo teorico di parametri |

**Nota sulla ridondanza del parametro condiviso.** Se $\alpha=\beta$ (stessa rotazione su
entrambi i qubit), il coefficiente di $|11\rangle$ diventa
$\sin\tfrac\alpha2\cos\tfrac\alpha2(b-a) = \tfrac12\sin\alpha\,(b-a)$,
che si annulla per $a=b$ (mescolamento massimo, cioè proprio $b/J=2$, il punto critico).
Questo spiega quantitativamente perché un parametro condiviso non basta: fallisce
esattamente nel punto più difficile, dove il mescolamento singoletto/$|t_-\rangle$ è
massimo e il ground state richiede componenti uguali di entrambi.

**Riferimento.** Dimostrazione completa con tutti i casi che falliscono:
`analisi_rotazioni_PMA.ipynb`.
