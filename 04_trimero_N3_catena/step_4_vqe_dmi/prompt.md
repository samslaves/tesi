Riprendo la tesi triennale (trimero di spin, catena aperta). Ho appena
aggiornato e ricaricato `log_decisioni.md`, `scheda_progetto_tesi.md` e
`domande_relatore.md` nel progetto: comincia leggendoli e dammi un
riepilogo dello stato confermato prima di implementare qualsiasi cosa.

**Contesto in breve**: per il trimero a catena aperta, la teoria esatta e
il VQE senza DM (Fase 4) sono completi e verificati — mirror strutturale
di quanto già fatto per l'anello (`trimer_chain_exact.py`,
`vqe_trimer_chain.py`/`_W.py`/`_nobranch.py`, due notebook "spiegato",
tutti eseguiti con successo in sessione). Per l'anello è stata completata
anche la Fase 5 (VQE con DM): due notebook
(`analisi_espressivita_PMA_anello.ipynb` +
`confronto_ansatz_entangler_trimero_anello.ipynb`) hanno stabilito che la
famiglia RBS-2q ha un tetto strutturale vero sotto DM
($\mathcal F\approx0.9999$) mentre la famiglia $W$-2q raggiunge l'esatto —
candidato canonico `W-2q.6`.

**Cosa manca, specificamente per la catena aperta**:

1. **Fase 5 (VQE con DM) per la catena — non ancora affrontata.** Il
   notebook di confronto attuale (`confronto_ansatz_entangler_trimero_catena.ipynb`)
   resta $D{=}0$-only e usa solo ansatz RBS (nessun ansatz $W$ ancora
   incluso). Serve:
   - Un'indagine mirata (mirror di `analisi_espressivita_PMA_anello.ipynb`)
     che verifichi **da zero, senza assumere lo stesso esito dell'anello**,
     se la famiglia RBS-2q ha lo stesso tipo di limite sotto DM anche sulla
     catena, o se il quadro è diverso (solo 2 bond fisici invece di 3,
     $b_c=3J$ invece di $2J+J'$).
   - Ricostruire/estendere `confronto_ansatz_entangler_trimero_catena.ipynb`
     per includere gli ansatz $W$ e lo sweep con DM, stesso mirror
     dell'anello.
   - Documentazione finale `trimero_catena_vqe_dm.pdf`, stessa struttura di
     `trimero_anello_vqe_dm.pdf` (funzioni interne, come si usa, verifiche,
     considerazioni, conclusioni — per ogni file, comprese figure e cache).

2. **Non ancora nello scope immediato, ma il fronte successivo**: Trotter e
   correlazioni dinamiche per N=3 (entrambe le topologie) — se ne parla solo
   se la Fase 5 della catena è già chiusa.

Procedi con ordine: prima il riepilogo dello stato, poi conferma con me il
piano (indagine mirata → confronto sistematico → documentazione) prima di
cominciare a scrivere codice.
