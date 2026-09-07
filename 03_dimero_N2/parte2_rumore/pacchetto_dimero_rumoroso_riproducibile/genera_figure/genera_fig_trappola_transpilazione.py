"""Genera fig_bug_conteggio_gate.pdf.
Eseguire dalla RADICE del pacchetto, dopo 01_genera_dati_vqe_ideale.py.

RUOLO NELL'INSIEME DEL PACCHETTO: produce l'unica figura dell'estensione
VQE noise-aware dedicata alla trappola di transpilazione (non un
risultato fisico, ma un confronto di conteggio gate) -- transpila lo
stesso ansatz nei due ordini possibili (prima o dopo l'assegnazione dei
parametri) per mostrare visivamente perche' l'ordine "dopo" sia quello
corretto, coerente con quanto gia' stabilito in
codice/vqe_dm_rumoroso_dimero.py.
"""
import sys
sys.path.insert(0, "codice")
import numpy as np
from qiskit import transpile
from stile import plt, C_ARANC, C_VERDE, salva
from vqe_test2 import pma_2q
from noise_model_dimero import BASIS_GATES

data = np.load("dati/ground_state_test2.npz")
vqe_params = data["vqe_params"]

# transpila PRIMA di assegnare i parametri (forma simbolica) -- sbagliato
ansatz_simbolico = transpile(pma_2q(3), basis_gates=BASIS_GATES,
                              optimization_level=3, seed_transpiler=7)
bound_sbagliato = ansatz_simbolico.assign_parameters(vqe_params)
ops_sbagliato = bound_sbagliato.count_ops()

# transpila DOPO aver assegnato i parametri -- corretto
bound = pma_2q(3).assign_parameters(vqe_params)
tqc_corretto = transpile(bound, basis_gates=BASIS_GATES,
                          optimization_level=3, seed_transpiler=7)
ops_corretto = tqc_corretto.count_ops()

print("Transpile PRIMA di assegnare (sbagliato):", dict(ops_sbagliato))
print("Transpile DOPO aver assegnato (corretto):", dict(ops_corretto))

gates = ["rz", "sx", "cx"]
sbagliato = [ops_sbagliato.get(g, 0) for g in gates]
corretto = [ops_corretto.get(g, 0) for g in gates]

x = np.arange(len(gates))
w = 0.35
fig, ax = plt.subplots(figsize=(6.2, 4.3))
b1 = ax.bar(x - w/2, sbagliato, w, label="transpile PRIMA di assign\n(sbagliato)", color=C_ARANC)
b2 = ax.bar(x + w/2, corretto, w, label="transpile DOPO assign\n(corretto)", color=C_VERDE)
for bars in (b1, b2):
    for bar in bars:
        h = bar.get_height()
        ax.annotate(str(h), xy=(bar.get_x() + bar.get_width()/2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10)
ax.set_xticks(x); ax.set_xticklabels(gates)
ax.set_ylabel("numero di gate nel circuito transpilato")
ax.set_title("Costo in gate: ordine transpilazione/assegnazione")
ax.legend(fontsize=9)
salva(fig, "fig_bug_conteggio_gate")
