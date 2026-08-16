Ho implementato la simulazione dell'evoluzione temporale del dimero con Suzuki-Trotter e ho provato diversi set di parametri con la dinamica esatta, come mi aveva chiesto. Riporto qui il circuito che ho usato e i cinque test che ho fatto.

Il circuito per un singolo passo di Trotter è quello in figura (`circuito_cnot.png`). La struttura è:

- due $R_z$ (uno per qubit) per il termine di campo $b(s_{z1}+s_{z2})$;
- $R_{XX}$, $R_{YY}$ e un blocco $R_{ZZ}$ per lo scambio isotropo $J\,\vec s_1\cdot\vec s_2$;
- due blocchi $R_{ZZ}$ coniugati con Hadamard per il termine DM $D(s_{x1}s_{z2}-s_{z1}s_{x2})$: il primo con le H sul qubit 0 (realizza $X_1Z_2$), il secondo con le H sul qubit 1 (realizza $Z_1X_2$), con angoli opposti.

Ho scritto i tre $R_{ZZ}$ esplicitamente come CNOT–$R_z$–CNOT invece di usare il gate `rzz` di Qiskit. Le due forme sono identiche (è la stessa decomposizione che Qiskit tiene nella `.definition` interna di `RZZGate`), ma scrivendola esplicitamente il conteggio dei gate diventa quello realistico per un hardware dove il CNOT è nativo. Con questa scelta il singolo passo ha 17 gate (9 a un qubit + 8 a due qubit, di cui 6 CNOT) e profondità 15; con il gate `rzz` nativo sarebbero 11 gate e profondità 9. Ho comunque lasciato la possibilità di scegliere l'una o l'altra con un parametro, e ho verificato che le due versioni danno la stessa matrice unitaria a scarto zero.

Gli angoli che si vedono nel disegno ($R_z=-0.18$, $R_{XX}=R_{YY}=0.5$, ecc.) sono quelli del set di default del notebook ($b/J=-0.18$, $D/J=1$, $\tau=1$); nei test cambiano solo i valori degli angoli, la struttura del circuito resta la stessa.

Prima di tutto ho verificato che con $D=0$ la dinamica di $\langle S_z\rangle$ è identicamente costante: lo stato iniziale $|00\rangle$ è autostato della parte di campo più scambio, quindi senza il termine DM non c'è niente da osservare. È il motivo per cui tutti i test hanno $D\neq0$.

Per giudicare i vari set ho usato due indicatori: l'escursione picco-picco di $\langle S_z\rangle$ (che deve stare sopra il rumore statistico, che con 8192 shot è circa $1/\sqrt{8192}\simeq0.011$) e il rapporto $a_2/a_1$ fra le ampiezze dei due modi spettrali dominanti, che dice quanto l'oscillazione è lontana dall'essere monocromatica. I cinque set che ho provato sono questi:

| test | $b/J$ | $D/J$ | escursione | $a_2/a_1$ | frequenze (ampiezza) |
|---|---|---|---|---|---|
| 1 | $+0.18$ | $0.55$ | $0.167$ | $0.84$ | $0.355\,(0.045)$, $1.286\,(0.038)$, $0.931\,(0.008)$ |
| 2 | $+0.35$ | $0.80$ | $0.216$ | $0.84$ | $0.670\,(0.059)$, $1.564\,(0.049)$, $0.894\,(0.017)$ |
| 3 | $-0.33$ | $1.35$ | $0.976$ | $0.52$ | $1.201\,(0.322)$, $0.670\,(0.166)$, $1.870\,(0.024)$ |
| 4 | $-0.30$ | $2.00$ | $1.281$ | $0.96$ | $1.556\,(0.386)$, $0.789\,(0.372)$, $2.345\,(0.030)$ |
| 5 | $+0.08$ | $0.30$ | $0.074$ | $0.82$ | $0.160\,(0.020)$, $1.113\,(0.017)$, $0.953\,(0.002)$ |

Una cosa che ho notato in tutti e cinque i casi è che compaiono sempre e solo tre frequenze, non sei come mi aspettavo da quattro livelli. Il motivo è che lo stato $|t_0\rangle=(|01\rangle+|10\rangle)/\sqrt2$ resta completamente fuori dalla dinamica: il termine DM lo annichila, non è popolato dallo stato iniziale e non contribuisce a $S_z$. Inoltre delle tre frequenze che restano solo due sono indipendenti, perché la terza è la somma delle altre due — l'ho verificato numericamente su tutti i test e torna sempre (per esempio nel test 4: $0.789+1.556=2.345$). Quindi il massimo che si può ottenere in termini di "non monocromaticità" sono due frequenze indipendenti.

Sui singoli test. I test 1, 2 e 5 hanno $b/J$ positivo e $D/J$ sotto l'unità: le due frequenze sono ben bilanciate ($a_2/a_1$ fra $0.82$ e $0.84$) e i battimenti si vedono, ma l'escursione resta piccola. Il caso peggiore è il test 5, con escursione $0.074$: è solo circa 7 volte il rumore statistico, quindi misurabile ma con poco margine. Nei grafici del pannello 1 questi tre casi sembrano oscillare parecchio, ma è solo un effetto della scala verticale che si adatta automaticamente — nel test 5 per esempio l'asse va da $0.93$ a $1.00$, quindi anche la curva blu del set di partenza, che oscilla di appena $0.006$, appare molto più marcata di quanto sia in realtà.

I test 3 e 4, con $b/J$ negativo e $D/J$ sopra l'unità, hanno escursione molto più grande ($0.98$ e $1.28$). Il test 3 però ha $a_2/a_1=0.52$, quindi un modo domina nettamente sull'altro. Il test 4 è quello che soddisfa meglio entrambi i criteri insieme (escursione $1.28$ e $a_2/a_1=0.96$, cioè due modi praticamente uguali), ma usa $D/J=2$, che per un'interazione DM in un magnete molecolare non è realistico — di solito $D$ è almeno un ordine di grandezza sotto $J$. Questo è il punto su cui vorrei un suo parere: se preferisce che tenga un regime fisicamente sensato accettando un segnale piccolo, o un regime dimostrativo con segnale grande.

Sulla convergenza di Trotter (pannello centrale). L'errore dipende molto dal regime, e non basta guardarlo in valore assoluto: conta quanto vale rispetto all'ampiezza del segnale che si vuole riprodurre. Nel test 1 con $N=5$ l'errore massimo è $1.50$, cioè 9 volte l'escursione del segnale — infatti nel grafico la curva arancione dopo $t\simeq15$ se ne va completamente per conto suo, arrivando a $-0.6$ mentre l'esatta resta intorno a $0.9$. Nel test 4, che ha il segnale più grande, lo stesso $N=5$ dà un errore di $1.98$, ma rapportato all'escursione è solo $1.5$ volte. In tutti i casi con $N=20$ l'errore scende sotto l'escursione del segnale (da $0.10$ a $0.80$ volte a seconda del test) e con $N=50$ va sotto il $15\%$.

Sul terzo pannello (scaling dell'errore a $t=10$): l'infedeltà $1-\mathcal F$ scala come $N^{-2}$ e la norma $\|\Delta U\|_2$ come $N^{-1}$, coerentemente con il fatto che lo schema è al prim'ordine. Le pendenze misurate stanno fra $-1.93$ e $-2.42$ per $1-\mathcal F$ e fra $-1.03$ e $-1.47$ per la norma. Nel test 3 e nel test 4 si vede bene che i primi due punti (a $N=2$ e $N=4$) sono fuori dalla retta, in alcuni casi con l'errore che addirittura sale invece di scendere: lì il passo $\tau=t/N$ è ancora troppo grande e non siamo nel regime in cui vale lo sviluppo, quindi la legge di potenza non si applica. Escludendo quei punti la pendenza torna più vicina a $-2$.

Un'ultima osservazione sui punti campionati con gli 8192 shot: nel pannello centrale i pallini seguono sempre la curva di Trotter dello stesso colore e non quella esatta, come deve essere visto che il circuito implementa Trotter e non la dinamica vera. Lo scarto dei pallini dalla loro curva è dell'ordine di $0.007$-$0.011$, mentre l'errore di Trotter a $N=20$ è molto più grande. Vuol dire che in questo regime l'errore che conta è quello algoritmico, non quello statistico: aumentare gli shot non servirebbe, bisogna aumentare $N$.

Ho controllato che tutti i numeri che si leggono nei grafici siano riproducibili ricalcolandoli, e coincidono.
