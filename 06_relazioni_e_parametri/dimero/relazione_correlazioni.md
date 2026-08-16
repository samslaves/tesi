Riprendo qui lo stesso schema della relazione sul Trotter: mostro cosa ho fatto, alcuni esempi
rappresentativi con i numeri che li descrivono, e un paio di osservazioni su cui vorrei un suo
parere.

Ho eseguito il circuito con l'ancilla (quello discusso a voce, Hadamard test con
controlled-$W$/anti-controlled-$V$ attorno al blocco $U(t)$ non controllato) per **tutte** le
$36$ combinazioni $C_{ij}^{\alpha\beta}(t)=\langle\sigma_i^\alpha(t)\sigma_j^\beta(0)\rangle$
($i,j\in\{1,2\}$, $\alpha,\beta\in\{x,y,z\}$), al punto di lavoro del test 2
($b/J=0.35$, $D/J=0.80$), partendo dal ground state VQE già trovato. Non ho scartato nessuna
combinazione a priori: le ho misurate tutte, per poi guardare quali sono davvero interessanti.

Per distinguerle uso lo stesso tipo di criterio già discusso per la scelta del punto di lavoro:
il rapporto $a_2/a_1$ fra le ampiezze spettrali dei due modi dominanti. Vicino a $1$ = segnale
"ricco" (più frequenze pesano quasi allo stesso modo, forma irregolare); vicino a $0$ = segnale
"piatto" (quasi monocromatico, un solo modo domina, forma regolare quasi periodica — non vuol
dire ampiezza piccola, solo forma semplice).

Tutte le combinazioni con una componente $x$ e una $y$ (miste, sia stesso sito che siti
diversi) risultano ricche, con $a_2/a_1\simeq0.96$ — il modo secondario ha quasi la stessa
ampiezza del primo.

*$C_{1,1}^{xy}(t)$, escursione $0.883$, $a_2/a_1=0.961$.*
![11_XY_ricco](attachment://11_XY_ricco.png)

*Spettro dietro il profilo: $|a_k b_k|$ per $k=0,1,2,3$ (normalizzato al massimo). Due canali
comparabili ($k=1$ a $\Delta E=4.15$, peso $0.961$; $k=3$ a $\Delta E=5.57$, peso $1.000$) —
il battimento fra questi due è la ragione della forma irregolare vista sopra.*
![11_XY_spettro](attachment://11_XY_spettro.png)

*$C_{1,1}^{yx}(t)$, escursione $0.883$, $a_2/a_1=0.961$ — stessa coppia di componenti della
precedente, ordine invertito: stesso valore, come atteso (i due operatori commutano a siti
uguali solo a meno di un resto, ma qui il rapporto spettrale non li distingue).*
![11_YX_ricco](attachment://11_YX_ricco.png)

*Spettro identico, cifra per cifra, a quello di $C_{1,1}^{xy}$ sopra — non è un'approssimazione,
i pesi $|a_kb_k|$ coincidono esattamente fra i due ordini.*
![11_YX_spettro](attachment://11_YX_spettro.png)

*$C_{1,2}^{yx}(t)$, escursione $0.875$, $a_2/a_1=0.961$.*
![12_YX_ricco](attachment://12_YX_ricco.png)

*Ancora lo stesso spettro esatto ($k_1=0.961$, $k_3=1.000$), stavolta a siti diversi.*
![12_YX_spettro](attachment://12_YX_spettro.png)

*$C_{2,1}^{yx}(t)$, escursione $0.875$, $a_2/a_1=0.961$ — questo è il correlatore che mi aveva
indicato lei come primo esempio concreto (salvo lo scambio $x\leftrightarrow y$ fra $V$ e $W$).*
![21_YX_ricco](attachment://21_YX_ricco.png)

![21_YX_spettro](attachment://21_YX_spettro.png)

*$C_{2,2}^{yx}(t)$, escursione $0.883$, $a_2/a_1=0.961$.*
![22_YX_ricco](attachment://22_YX_ricco.png)

![22_YX_spettro](attachment://22_YX_spettro.png)

Le autocorrelazioni e cross-correlazioni $ZZ$ sono tutte quasi monocromatiche
($a_2/a_1\simeq0.11$), mentre $C_{1,1}^{zy}$ sta in una via di mezzo ($a_2/a_1=0.71$).

*$C_{1,1}^{zz}(t)$, escursione $0.208$, $a_2/a_1=0.106$.*
![11_ZZ_piatto](attachment://11_ZZ_piatto.png)

*Spettro: un solo canale domina nettamente ($k=2$ a $\Delta E=4.57$, peso $1.000$; gli altri
due restano sotto $0.11$) — profilo quasi monocromatico, coerente con l'escursione piccola.*
![11_ZZ_spettro](attachment://11_ZZ_spettro.png)

*$C_{1,1}^{zy}(t)$, escursione $0.316$, $a_2/a_1=0.714$ — intermedio, non l'ho messo fra i
"ricchi" solo perché $a_2/a_1$ resta comunque sotto $0.75$.*
![11_ZY_piatto](attachment://11_ZY_piatto.png)

*Spettro genuinamente diverso da tutti gli altri nove: qui domina $k=1$ ($\Delta E=4.15$, peso
$1.000$), non $k=2$ come nei $ZZ$ — non è una via di mezzo casuale fra ricco e piatto, è un
terzo canale energetico diverso che entra in gioco.*
![11_ZY_spettro](attachment://11_ZY_spettro.png)

*$C_{1,2}^{zz}(t)$, escursione $0.213$, $a_2/a_1=0.106$.*
![12_ZZ_piatto](attachment://12_ZZ_piatto.png)

*Stesso spettro esatto di $C_{1,1}^{zz}$ (canale $k=2$ dominante).*
![12_ZZ_spettro](attachment://12_ZZ_spettro.png)

*$C_{2,1}^{zz}(t)$, escursione $0.213$, $a_2/a_1=0.106$.*
![21_ZZ_piatto](attachment://21_ZZ_piatto.png)

![21_ZZ_spettro](attachment://21_ZZ_spettro.png)

*$C_{2,2}^{zz}(t)$, escursione $0.208$, $a_2/a_1=0.106$.*
![22_ZZ_piatto](attachment://22_ZZ_piatto.png)

![22_ZZ_spettro](attachment://22_ZZ_spettro.png)

Tutte e 36 insieme, in griglia (verde = classico esatto, rosa = circuito, senza distinzione
Re/Im per stare nello spazio):

![all_correlations](attachment://all_correlations.png)

A colpo d'occhio si vede lo stesso pattern dei numeri: le colonne/righe con $z$ da sole
tendono a un profilo più regolare, quelle con $x,y$ misti sono visibilmente più irregolari.
Non ho trovato nessuna combinazione strutturalmente piatta (cioè con escursione vicina a
zero) — tutte e 36 hanno dinamica non banale, coerente con quanto già verificato in
precedenza con l'analisi di simmetria.

Ho verificato circuito contro classico per tutte le 36, non solo per queste 10. Un punto onesto
da segnalare: lo scarto peggiore che trovo, con $N=100$ passi di Trotter fino a $t=15$, arriva
fino a $\sim0.2$–$0.4$ a seconda della combinazione — più alto di quanto avrei voluto. Ho
controllato che non sia un errore nascosto: a $N$ fissato l'errore cresce con $t$ (atteso,
$\propto t^2/N$), e rifacendo il conto sul punto peggiore con $N$ crescente ($100\to300\to600$)
lo scarto scende in modo pulito, coerente con puro errore di Trotter, non con un problema di
circuito. Per uno sguardo d'insieme su tutte le 36 mi è sembrato un compromesso ragionevole fra
tempo di calcolo e precisione; se serve un confronto più stretto per una combinazione specifica
alzo $N$ solo per quella.

1. Il correlatore che mi aveva indicato come esempio ($\langle\sigma_{x2}(t)\sigma_{x1}(0)\rangle$)
   corrisponde, nella mia notazione, a $C_{2,1}^{xx}$ — quello **non** è fra i "ricchi": ha
   $a_2/a_1$ modesto (27° posizione su 36 per questo criterio). È comunque quello che ho tenuto
   come priorità per il circuito, per la rilevanza fisica che mi aveva segnalato lei, non per il
   segnale — le due cose non coincidono, e mi sembra giusto scriverlo esplicitamente piuttosto
   che scegliere in base a un solo criterio senza dirlo.
2. Le combinazioni "ricche" sono sempre quelle con una componente $x$ e una $y$ (mai $z$ da
   sola); quelle "piatte" sono sempre $zz$ pura. Guardando gli spettri (aggiunti sopra), il
   pattern è più netto di quanto pensassi inizialmente: **tutti** i 5 "ricchi" condividono lo
   stesso spettro esatto (canali $k=1$ e $k=3$, $\Delta E=4.15$ e $5.57$, pesi $0.961$ e
   $1.000$), e **tutti** i 4 "$zz$ piatti" condividono anch'essi lo stesso spettro esatto
   (canale $k=2$ dominante, $\Delta E=4.57$, peso $1.000$). Non è una somiglianza, sono
   identici cifra per cifra — la richezza/piattezza sembra dipendere solo dalla coppia di
   componenti $(\alpha,\beta)$, non da quali siti $(i,j)$ sono coinvolti. L'unico caso fuori
   da questo schema binario è $C_{1,1}^{zy}$, che ha un terzo spettro diverso (canale $k=1$
   dominante, non $k=2$) — non è una via di mezzo fra gli altri due, è un canale a sé. Non ho
   ancora una spiegazione fisica del perché la coppia di componenti fissi così rigidamente
   quale livello eccitato viene "raggiunto" — mi sembra collegato al fatto che il campo
   Zeeman è lungo $z$ e il DM accoppia proprio $x$ e $z$, ma non l'ho verificato con un
   argomento solido. Se ha un'intuizione diretta su questo evito di girarci intorno per conto
   mio.
