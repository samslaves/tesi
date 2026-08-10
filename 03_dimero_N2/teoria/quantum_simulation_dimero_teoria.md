# Quantum simulation del dimero — derivazione teorica completa

Sintesi delle derivazioni per il task di *quantum simulation* (evoluzione temporale reale $e^{-iHt}$) richiesto dal relatore sull'Hamiltoniana VQE del dimero, in vista dell'implementazione Suzuki-Trotter.

---

## 1. Hamiltoniana e struttura generale

$$H = b(s_{z1}+s_{z2}) + J\,\vec s_1\cdot\vec s_2 + D(s_{x1}s_{z2}-s_{z1}s_{x2}) = H_1+H_2$$

con

- $H_1 = b(s_{z1}+s_{z2}) + J\,\vec s_1\cdot\vec s_2$ — campo **più** scambio isotropo, **fisso**, non dipende da $D$;
- $H_2 = D(s_{x1}s_{z2}-s_{z1}s_{x2})$ — **solo** termine DM, si annulla per $D=0$.

In generale $[H_1,H_2]\neq0$ per $D\neq0$. Per $D=0$ si ha $H=H_1$ e l'evoluzione è **esatta** senza alcuna approssimazione. Per $D\neq0$ serve la decomposizione di Suzuki-Trotter.

---

## 2. Decomposizione esatta di $U_J(t) = e^{-iJt\,\vec s_1\cdot\vec s_2}$

### 2.1 Riscrittura in Pauli

Con la convenzione $s_i^\alpha=\sigma_i^\alpha/2$ (Crippa):

$$\vec s_1\cdot\vec s_2 = \frac{1}{4}\left(X_1X_2+Y_1Y_2+Z_1Z_2\right)$$

quindi

$$J\,\vec s_1\cdot\vec s_2 = \frac{J}{4}\left(XX+YY+ZZ\right), \qquad U_J(t) = \exp\!\left[-i\,\frac{Jt}{4}\left(XX+YY+ZZ\right)\right]$$

Il fattore $1/4$ emerge automaticamente dal passaggio a Pauli, coerente con la convenzione $J_{code}$ vs $J_{Crippa}$ già tracciata nel resto del progetto.

### 2.2 Commutatività di $XX$, $YY$, $ZZ$

I tre operatori a due qubit commutano a due a due. Usando $(A\otimes B)(C\otimes D)=(AC)\otimes(BD)$ e le regole di Pauli $XY=iZ$, $YX=-iZ$, $XZ=-iY$, $ZX=iY$, $YZ=iX$, $ZY=-iX$:

$$(X\otimes X)(Y\otimes Y) = (XY)\otimes(XY) = (iZ)\otimes(iZ) = -(Z\otimes Z)$$
$$(Y\otimes Y)(X\otimes X) = (YX)\otimes(YX) = (-iZ)\otimes(-iZ) = -(Z\otimes Z)$$

I due prodotti coincidono, quindi $[XX,YY]=0$. In modo analogo si verifica $[YY,ZZ]=0$ e $[ZZ,XX]=0$ (con $XX\cdot ZZ=-YY$ e $YY\cdot ZZ=-XX$).

Poiché $XX$, $YY$, $ZZ$ commutano a due a due, l'esponenziale della somma fattorizza **esattamente**, in qualunque ordine, nel prodotto degli esponenziali (nessun errore di Trotter):

$$U_J(t) = \exp\!\left(-i\tfrac{Jt}{4}XX\right)\exp\!\left(-i\tfrac{Jt}{4}YY\right)\exp\!\left(-i\tfrac{Jt}{4}ZZ\right)$$

### 2.3 Mappatura sui gate Qiskit

Verifica numerica diretta (Qiskit 2.x, `RXXGate(0.7).to_matrix()`) conferma la convenzione documentata:

$$R_{XX}(\theta)=e^{-i\frac{\theta}{2}XX},\qquad R_{YY}(\theta)=e^{-i\frac{\theta}{2}YY},\qquad R_{ZZ}(\theta)=e^{-i\frac{\theta}{2}ZZ}$$

(matrice ottenuta: elementi diagonali $\cos(\theta/2)=0.9394$, elementi fuori diagonale $-i\sin(\theta/2)=-0.3429i$ per $\theta=0.7$, in pieno accordo con la formula attesa).

Confrontando l'esponente $\theta/2 = Jt/4$ si ottiene $\theta = Jt/2$, quindi:

$$\boxed{U_J(t) = R_{XX}\!\left(\frac{Jt}{2}\right)R_{YY}\!\left(\frac{Jt}{2}\right)R_{ZZ}\!\left(\frac{Jt}{2}\right)}$$

---

## 3. Evoluzione completa di $H_1$ (campo + scambio)

### 3.1 Perché il campo commuta con lo scambio isotropo

Lo scambio isotropo si riscrive in funzione del Casimir dello spin totale $\vec S=\vec s_1+\vec s_2$:

$$\vec s_1\cdot\vec s_2 = \frac{1}{2}\left(S^2-s_1^2-s_2^2\right)$$

$S^2$ è per costruzione uno scalare invariante sotto rotazioni (il Casimir dell'algebra del momento angolare), mentre $S_z$ è il generatore delle rotazioni attorno all'asse $z$. Un operatore invariante per rotazioni commuta sempre con qualunque generatore di rotazione — è lo stesso motivo per cui, per un singolo spin, $[\vec s^{\,2},s_z]=0$. Quindi:

$$[S^2,S_z]=0 \quad\Longrightarrow\quad \left[J\,\vec s_1\cdot\vec s_2,\; b(s_{z1}+s_{z2})\right] = \left[\tfrac{J}{2}(S^2-\text{cost.}),\; bS_z\right] = \tfrac{Jb}{2}[S^2,S_z] = 0$$

(Nota: questo è distinto e più diretto rispetto all'argomento di simmetria di scambio particelle $1\leftrightarrow2$, che è una simmetria diversa — quella che garantisce che $\vec s_1\cdot\vec s_2$ sia simmetrico sotto scambio dei siti, non quella che lo lega a $S_z$.)

### 3.2 Fattorizzazione esatta di $H_1$

Poiché campo e scambio commutano, l'esponenziale fattorizza esattamente:

$$e^{-iH_1t} = e^{-i[b(s_{z1}+s_{z2})+J\vec s_1\cdot\vec s_2]t} = e^{-ibs_{z1}t}\;e^{-ibs_{z2}t}\;e^{-iJt\,\vec s_1\cdot\vec s_2}$$

Il pezzo di campo, con $s_{zi}=\sigma_{zi}/2$ e la convenzione Qiskit $R_z(\phi)=e^{-i\phi Z/2}$ (stesso fattore $1/2$ verificato per $R_{XX}$):

$$e^{-ib\,s_{zi}t} = e^{-i\frac{bt}{2}Z_i} \equiv R_z^{(i)}(bt)$$

Quindi, in qualunque ordine tra i tre fattori:

$$\boxed{|\psi(t)\rangle = R_z^{(1)}(bt)\,R_z^{(2)}(bt)\,U_J(t)\,|\psi(0)\rangle}$$

esatto, **nessun errore di approssimazione**, con $U_J(t)$ come derivato al punto 2.

---

## 4. Decomposizione esatta di $U_2(t)=e^{-iH_2t}$ (termine DM)

### 4.1 Riscrittura in Pauli

$$H_2 = D(s_{x1}s_{z2}-s_{z1}s_{x2}) = \frac{D}{4}(X_1Z_2-Z_1X_2)$$

Si definisce $P_1\equiv X_1Z_2$ e $P_2\equiv Z_1X_2$.

### 4.2 Commutatività di $P_1$ e $P_2$

$$P_1P_2 = (X_1Z_2)(Z_1X_2) = (X_1Z_1)\otimes(Z_2X_2) = (-iY_1)\otimes(iY_2) = Y_1Y_2$$
$$P_2P_1 = (Z_1X_2)(X_1Z_2) = (Z_1X_1)\otimes(X_2Z_2) = (iY_1)\otimes(-iY_2) = Y_1Y_2$$

Essendo $P_1P_2=P_2P_1$, si ha $[P_1,P_2]=0$, quindi (con $\theta=Dt/4$):

$$e^{-i\theta(P_1-P_2)} = e^{-i\theta P_1}\,e^{+i\theta P_2}$$

esatto, senza approssimazione, per lo stesso motivo generale discusso al punto 5.

### 4.3 Circuito per i singoli termini

Usando $HZH=X$ (l'Hadamard scambia $X\leftrightarrow Z$), applicata solo al qubit che porta $X$ nel termine considerato:

$$X_1Z_2 = (H_1\otimes I_2)\,Z_1Z_2\,(H_1\otimes I_2)$$

$$e^{-i\theta\,X_1Z_2} = (H_1\otimes I_2)\;R_{ZZ}(2\theta)\;(H_1\otimes I_2)$$

(fattore $2\theta$ perché $R_{ZZ}(\phi)=e^{-i\frac{\phi}{2}ZZ}$, stessa convenzione verificata al punto 2.3).

Analogamente, con l'Hadamard sul qubit 2 (che porta $X$ nel secondo termine):

$$e^{-i\theta\,Z_1X_2} = (I_1\otimes H_2)\;R_{ZZ}(2\theta)\;(I_1\otimes H_2)$$

### 4.4 Circuito completo

Con $\theta=Dt/4$ per il primo blocco e $-\theta$ per il secondo (dal segno $+i\theta P_2$ sopra):

$$\boxed{U_2(t) = \Big[(I\otimes H)\,R_{ZZ}\!\big(-\tfrac{Dt}{2}\big)\,(I\otimes H)\Big]\cdot\Big[(H\otimes I)\,R_{ZZ}\!\big(\tfrac{Dt}{2}\big)\,(H\otimes I)\Big]}$$

Anche questo blocco, isolato, è **esatto**: l'errore di Trotter entra solo nell'accoppiamento tra $H_1$ e $H_2$ (Sezione 6), non nei singoli pezzi.

### 4.5 Nota sul segno del termine DM

Se il termine DM avesse convenzione di segno opposta, cioè $H_2'=D(s_{z1}s_{x2}-s_{x1}s_{z2})=-H_2$, allora $U_2'(t)=e^{-iH_2't}=e^{+iH_2t}=U_2(-t)$. Concretamente questo significa che **entrambi** gli angoli dei due $R_{ZZ}$ cambiano segno insieme; la struttura del circuito (sequenza $H$–$R_{ZZ}$–$H$, quale Hadamard su quale qubit) resta identica — cambia solo il segno dei parametri $\theta$ passati ai gate $R_{ZZ}$.

---

## 5. Perché $[A,B]=0$ implica fattorizzazione esatta (non solo al prim'ordine)

La formula di Baker-Campbell-Hausdorff (BCH) per due operatori generici $A,B$ è:

$$e^{A}e^{B} = e^{A+B+\frac{1}{2}[A,B]+\frac{1}{12}[A,[A,B]]+\frac{1}{12}[B,[B,A]]+\cdots}$$

Tutti i termini correttivi oltre $A+B$ sono commutatori annidati di $A$ e $B$. Se $[A,B]=0$, **ogni singolo termine** della serie che coinvolge un commutatore si annulla identicamente — non solo il primo termine $\frac12[A,B]$, ma l'intera torre infinita di correzioni successive. Quindi:

$$[A,B]=0 \;\Longrightarrow\; e^{A}e^{B}=e^{A+B} \text{ esattamente}$$

Questo è il motivo per cui tutte le fattorizzazioni derivate sopra ($XX/YY/ZZ$ in $U_J$, campo/scambio in $H_1$, $P_1/P_2$ in $H_2$) sono esatte e non approssimazioni al prim'ordine: in tutti questi casi i rispettivi commutatori sono identicamente nulli.

Il caso di $H_1$ e $H_2$ è concettualmente diverso: lì $[H_1,H_2]\neq0$ per $D\neq0$, la serie BCH non si tronca, e approssimare $e^{-i(H_1+H_2)t}\approx e^{-iH_1t}e^{-iH_2t}$ significa scartare il termine $-\frac12[H_1,H_2]t^2$ e tutti i termini di ordine superiore. Da qui la necessità del prodotto di Trotter.

---

## 6. Derivazione dell'errore di Trotter

### 6.1 Espansione in serie per un singolo passo

Per un passo di durata $\tau=t/N$, si confrontano:

$$U_{\text{esatto}}(\tau) = e^{-i(H_1+H_2)\tau}, \qquad U_{\text{Trotter}}(\tau) = e^{-iH_1\tau}\,e^{-iH_2\tau}$$

Espandendo entrambe al second'ordine in $\tau$:

$$U_{\text{esatto}}(\tau) = I - i\tau(H_1+H_2) - \frac{\tau^2}{2}(H_1+H_2)^2 + O(\tau^3)$$

$$U_{\text{Trotter}}(\tau) = \left[I-i\tau H_1-\frac{\tau^2}{2}H_1^2\right]\left[I-i\tau H_2-\frac{\tau^2}{2}H_2^2\right]+O(\tau^3) = I - i\tau(H_1+H_2) - \frac{\tau^2}{2}\left(H_1^2+H_2^2+2H_1H_2\right) + O(\tau^3)$$

### 6.2 Differenza tra le due espansioni

Usando $(H_1+H_2)^2=H_1^2+H_2^2+H_1H_2+H_2H_1$:

$$U_{\text{esatto}}(\tau) - U_{\text{Trotter}}(\tau) = -\frac{\tau^2}{2}\Big[(H_1H_2+H_2H_1)-2H_1H_2\Big]+O(\tau^3) = \frac{\tau^2}{2}\underbrace{(H_1H_2-H_2H_1)}_{[H_1,H_2]}+O(\tau^3)$$

$$\boxed{U_{\text{esatto}}(\tau) - U_{\text{Trotter}}(\tau) = \frac{\tau^2}{2}[H_1,H_2] + O(\tau^3)}$$

L'errore per singolo passo è quindi $O(\tau^2)=O((t/N)^2)$, come riportato negli appunti del relatore, ed è proporzionale al commutatore $[H_1,H_2]$: coerentemente, per $D=0$ (dove $[H_1,H_2]=0$) l'errore sparisce identicamente.

### 6.3 Errore totale su $N$ passi

L'evoluzione completa è $U_{\text{Trotter}}(\tau)^N\approx U_{\text{esatto}}(t)$. Per la disuguaglianza triangolare in norma operatoriale, l'errore totale è al più $N$ volte l'errore per passo:

$$\left\|U_{\text{esatto}}(t)-U_{\text{Trotter}}(\tau)^N\right\| \lesssim N\cdot O(\tau^2) = N\cdot O\!\left(\frac{t^2}{N^2}\right) = O\!\left(\frac{t^2}{N}\right)$$

L'errore **totale** decresce quindi come $1/N$ (metodo del prim'ordine): raddoppiando $N$, l'errore totale si dimezza.

### 6.4 Scaling rispetto al tempo totale

Dallo scaling $O(t^2/N)$ dell'errore totale:

- Raddoppiando il tempo totale $t$ a $N$ fisso: l'errore scala come $(2t)^2/N = 4\cdot(t^2/N)$, quindi **quadruplica**.
- Per mantenere l'errore costante mentre $t\to 2t$, serve $t^2/N=\text{cost.}$, quindi $N$ deve scalare come $t^2$: se $t\to 2t$, allora $N\to 4N$.

Implicazione pratica: il numero di gate nel circuito (proporzionale a $N$) cresce **quadraticamente** con il tempo totale simulato a errore fissato. È uno dei limiti noti del prodotto di Trotter al prim'ordine, e motiva l'uso in letteratura di schemi di ordine superiore (Trotter simmetrico / Suzuki di ordine 2, errore $O(\tau^3)$ per passo) per simulare tempi lunghi. Per questo task si resta al prim'ordine, come richiesto dal relatore.

### 6.5 Metodi di verifica numerica

Due approcci standard, entrambi applicabili con gli strumenti già in uso nel progetto:

- **Norma operatoriale**: costruire esplicitamente $U_{\text{esatto}}(t)=\exp(-iHt)$ (es. via `scipy.linalg.expm` o `Operator.exp_i` di Qiskit) e $U_{\text{Trotter}}(\tau)^N$ come prodotto di matrici, poi calcolare $\|U_{\text{esatto}}-U_{\text{Trotter}}^N\|$ (norma spettrale o di Frobenius) al variare di $N$, verificando lo scaling $\propto1/N$.
- **Fidelity sullo stato evoluto**: applicare entrambe le evoluzioni a uno stato iniziale $|\psi_0\rangle$ e calcolare $\mathcal F(t)=|\langle\psi_{\text{esatto}}(t)|\psi_{\text{Trotter}}(t)\rangle|$, verificando che $1-\mathcal F\propto t^2/N$ (a $t$ fissato, al variare di $N$) — stessa metodologia di fidelity già usata per la validazione VQE nel resto del progetto.

---

## 7. Riepilogo dei risultati

| Blocco | Espressione | Natura |
|---|---|---|
| $U_J(t)$ (scambio) | $R_{XX}(Jt/2)R_{YY}(Jt/2)R_{ZZ}(Jt/2)$ | Esatta |
| $e^{-iH_1t}$ (campo+scambio, $D=0$) | $R_z^{(1)}(bt)R_z^{(2)}(bt)U_J(t)$ | Esatta |
| $U_2(t)$ (termine DM) | $[(I\otimes H)R_{ZZ}(-Dt/2)(I\otimes H)]\cdot[(H\otimes I)R_{ZZ}(Dt/2)(H\otimes I)]$ | Esatta |
| $e^{-i(H_1+H_2)t}$, $D\neq0$ | $\left(e^{-iH_1t/N}e^{-iH_2t/N}\right)^N$ | Approssimata, errore $O(t^2/N)$ |
