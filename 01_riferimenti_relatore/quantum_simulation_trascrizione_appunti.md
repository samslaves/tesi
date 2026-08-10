# Trascrizione appunti "Quantum simulation"

---

## Hamiltoniana

$$H = b(s_{z1}+s_{z2}) + J\,\vec s_1\cdot\vec s_2 + D(s_{x1}s_{z2}-s_{z1}s_{x2}) = H_1+H_2$$

- $H_1 = b(s_{z1}+s_{z2}) + J\,\vec s_1\cdot\vec s_2$ — campo **più** scambio
  isotropo. $H_1$ è **sempre** questa somma, indipendentemente dal valore di
  $D$: non cambia forma a seconda che $D$ sia zero o no.
- $H_2 = D(s_{x1}s_{z2}-s_{z1}s_{x2})$ — **solo** il termine Dzyaloshinskii–Moriya (DM). È $H_2$ a dipendere da $D$ e ad annullarsi quando $D=0$.

## Nota generale

$$[H_1,H_2]\neq 0 \quad\text{(quando } D\neq0\text{, cioè quando } H_2\neq0\text{)}$$

## Caso D = 0

$D=0 \Rightarrow H_2=0 \Rightarrow H=H_1$ (il campo+scambio, invariato).

Non essendoci $H_2$, non serve nessuna decomposizione approssimata per
separarlo da $H_1$. La nota mostra però un'ulteriore fattorizzazione, questa
volta **interna a $H_1$**: il campo $b(s_{z1}+s_{z2})$ commuta con lo scambio
isotropo $J\vec s_1\cdot\vec s_2$ (entrambi conservano lo spin totale), quindi:

$$e^{-iH_1t} = e^{-i[b(s_{z1}+s_{z2})+J\vec s_1\cdot\vec s_2]t} = e^{-ibs_{z1}t}\;e^{-ibs_{z2}t}\;e^{-iJt\,\vec s_1\cdot\vec s_2}$$

con l'identificazione:
- $e^{-ibs_{z1}t} \equiv R_z^{(1)}(bt)$ — rotazione sul qubit 1
- $e^{-ibs_{z2}t} \equiv R_z^{(2)}(bt)$ — rotazione sul qubit 2
- $e^{-iJt\,\vec s_1\cdot\vec s_2} \equiv U_J$ — blocco di scambio (a 2 qubit)

quindi, in sequenza:

$$|\psi(t)\rangle = R_z^{(1)}(bt)\,R_z^{(2)}(bt)\,U_J\,|\psi(0)\rangle$$

esatto, nessun errore di approssimazione.

## Caso D ≠ 0

Ora $H_2\neq0$ e $[H_1,H_2]\neq0$ (il termine DM non commuta con campo+scambio), quindi:

$$e^{-i(H_1+H_2)t} \neq e^{-iH_1t}\,e^{-iH_2t}$$

Qui $H_1$ resta lo stesso blocco esatto del caso precedente (campo+scambio,
scomponibile in $R_z^{(1)},R_z^{(2)},U_J$); è $H_2$ (il termine DM) a dover
essere trattato separatamente e a introdurre l'approssimazione. Serve il
prodotto di Trotter a $N$ passi (**Suzuki-Trotter**):

$$e^{-i(H_1+H_2)t} \approx \left(e^{-iH_1\frac{t}{N}}\,e^{-iH_2\frac{t}{N}}\right)^{N}$$

con errore $O\!\left((t/N)^2\right)$ per passo. È la forma standard del prodotto di Trotter al
prim'ordine.
