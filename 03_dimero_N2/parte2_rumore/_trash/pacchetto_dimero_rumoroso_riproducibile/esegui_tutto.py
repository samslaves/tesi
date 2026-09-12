#!/usr/bin/env python3
"""
Esegue l'INTERA pipeline riproducibile, in ordine, con un solo comando:

    python3 esegui_tutto.py

Fasi:
  1. Generazione dati (VQE ideale, VQE noise-aware, secondo punto)
  2. Validazioni (tutti gli script validate_*.py originali, invariati)
  3. Generazione di tutte le 15 figure

Si ferma al primo errore, stampando quale fase e' fallita. Tempo
stimato totale: 10-20 minuti (le fasi piu' lente sono gli script di
figura che ripetono ottimizzazioni VQE a piu' punti).
"""
import subprocess
import sys
import shutil
import os

RADICE = os.path.dirname(os.path.abspath(__file__))


def esegui(comando, cwd, descrizione):
    print(f"\n{'='*70}\n{descrizione}\n{'='*70}")
    ris = subprocess.run(comando, cwd=cwd, shell=False)
    if ris.returncode != 0:
        print(f"\n!!! FALLITO: {descrizione}")
        print(f"    comando: {' '.join(comando)}")
        print(f"    cartella: {cwd}")
        sys.exit(1)


def main():
    # --- Fase 1: generazione dati ---
    for script in ["01_genera_dati_vqe_ideale.py",
                   "02_genera_dati_vqe_noise_aware.py",
                   "03_genera_dati_secondo_punto.py"]:
        esegui(["python3", script], RADICE, f"FASE 1 -- {script}")

    # --- Copia i dati anche in codice/, dove gli script validate_*.py
    #     originali (mai modificati) si aspettano di trovarli ---
    dati_dir = os.path.join(RADICE, "dati")
    codice_dir = os.path.join(RADICE, "codice")
    for f in os.listdir(dati_dir):
        shutil.copy(os.path.join(dati_dir, f), os.path.join(codice_dir, f))
    print(f"\n[copiati in codice/] {os.listdir(dati_dir)}")

    # --- Fase 2: validazioni (script originali, invariati) ---
    validate_scripts = [
        "validate_correlatori_rumorosi_dimero.py",
        "validate_scan_parametri_rumore_dimero.py",
        "validate_vqe_noise_aware_dimero.py",
        "validate_correlatori_readout_asimmetrico.py",
    ]
    for script in validate_scripts:
        esegui(["python3", script], codice_dir, f"FASE 2 -- {script}")

    # --- Fase 3: tutte le figure ---
    figure_scripts = sorted(os.listdir(os.path.join(RADICE, "genera_figure")))
    for script in figure_scripts:
        if script.endswith(".py"):
            esegui(["python3", os.path.join("genera_figure", script)],
                    RADICE, f"FASE 3 -- {script}")

    print(f"\n{'='*70}")
    print("TUTTO COMPLETATO. 15 figure in figure/, dati in dati/.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
