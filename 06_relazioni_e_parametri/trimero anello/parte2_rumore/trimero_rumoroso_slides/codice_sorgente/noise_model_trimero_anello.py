"""
Modello di rumore per il trimero ad anello (Parte 2, Stadio 1).

RUOLO NELL'INSIEME DEL PACCHETTO: questo modulo NON ridefinisce il modello
di rumore -- lo importa e lo ri-espone tal quale da `noise_model_dimero.py`
(Parte 2 del dimero). Dipendenza dichiarata esplicitamente, non nascosta
dietro un import silenzioso: `build_noise_model()` costruisce il
`NoiseModel` con `add_all_qubit_quantum_error`/`add_all_qubit_readout_error`,
operazioni intrinsecamente indipendenti dal numero di qubit del circuito su
cui vengono applicate (verificato in `validate_noise_model_trimero_
anello.py`, tre controlli su un circuito a 3 qubit). Duplicare il codice
avrebbe introdotto due copie da tenere sincronizzate senza alcun beneficio;
questo wrapper esiste solo per dare al trimero un punto d'ingresso con lo
stesso nome/interfaccia usato per ogni altra parte del progetto (dimero,
catena), cosi' che il pacchetto riproducibile del trimero abbia un file
`noise_model_trimero_anello.py` da elencare accanto agli altri, senza
duplicare la logica.

Due soli canali, stessa calibrazione condivisa con tutta la pipeline
(errore di gate depolarizzante 1q/2q, errore di lettura simmetrico,
mediane `ibm_torino`, arXiv:2504.15187) -- vedi `noise_model_dimero.py`
per la derivazione completa e `teoria_modello_rumore.tex` per le formule.
"""

from noise_model_dimero import (
    EPS_1Q_REF,
    EPS_2Q_REF,
    P_READOUT_REF,
    BASIS_GATES,
    eps_to_lambda,
    build_noise_model,
)

__all__ = [
    "EPS_1Q_REF",
    "EPS_2Q_REF",
    "P_READOUT_REF",
    "BASIS_GATES",
    "eps_to_lambda",
    "build_noise_model",
]


if __name__ == "__main__":
    nm, params = build_noise_model()
    print("Parametri di riferimento (ibm_torino, mediane, arXiv:2504.15187):")
    print("(condivisi col dimero -- stesso NoiseModel, riapplicato a un")
    print(" circuito a 3 qubit invece che 2)")
    for k, v in params.items():
        print(f"  {k:10s} = {v:.4e}")
    print()
    print(nm)
