"""
Orchestratore: esegue l'intera pipeline di Parte 2 (rumore) sul trimero
ad anello in un solo comando -- dati, poi validazioni, poi figure.

Uso: python3 esegui_tutto.py   (dalla radice del pacchetto)

Struttura a onde di dipendenza reale (non ordine "logico"):
  Onda 1: 01 (nessuna dipendenza)
  Onda 2: 02-07 (dipendono tutti da 01, indipendenti fra loro)
  Onda 3: genera_figure/ (dipendono dai .npz prodotti nell'Onda 2)
"""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCRIPT_DATI_VALIDAZIONI = [
    "01_genera_parametri_vqe.py",
    "02_valida_modello_rumore.py",
    "03_valida_vqe_dm_rumoroso.py",
    "04_valida_trotter_rumoroso.py",
    "05_valida_correlatori_rumorosi.py",
    "06_genera_scan_parametri.py",
    "07_valida_scan_parametri.py",
]

SCRIPT_FIGURE = sorted(
    os.path.join("genera_figure", f)
    for f in os.listdir("genera_figure") if f.endswith(".py")
)

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
