"""
Orchestratore: esegue l'intera pipeline di Parte 1 (sistema chiuso) sul
trimero ad anello in un solo comando.

Uso: python3 esegui_tutto.py   (dalla radice del pacchetto)

Onda 1 (nessuna dipendenza, indipendenti fra loro): 01, 02, 03, 04
Onda 2 (dipende da 02): 05
Onda 3 (dipende da 04 per classical_exact, copiata localmente):
    genera_figure/genera_figure_correlatori.py
"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCRIPT_DATI_VALIDAZIONI = [
    "01_diagonalizzazione_esatta.py",
    "02_genera_vqe_dm.py",
    "03_self_test_trotter.py",
    "04_valida_correlatori_esatti.py",
    "05_valida_correlatori_vqe.py",
]

SCRIPT_FIGURE = ["genera_figure/genera_figure_correlatori.py"]

FALLITO = False
for script in SCRIPT_DATI_VALIDAZIONI + SCRIPT_FIGURE:
    print(f"\n{'=' * 78}\n  ESECUZIONE: {script}\n{'=' * 78}")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\n*** FALLITO: {script} (exit code {result.returncode}) ***")
        FALLITO = True
        break

print(f"\n{'=' * 78}")
if FALLITO:
    print("PIPELINE FALLITA -- vedi sopra per il primo script che ha fallito.")
    sys.exit(1)
else:
    print("PIPELINE COMPLETATA CON SUCCESSO -- dati/, figure/ popolate.")
    sys.exit(0)
