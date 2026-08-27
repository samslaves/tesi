"""Diagramma SCHEMATICO del circuito per C_ij^{alpha,beta}(t) sulla catena --
mirror di generate_circuit_fig_trimero_anello.py. U(t) disegnato come box
opaco (struttura interna Trotter discussa a parte nel testo).
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from qiskit.circuit.library import YGate
from PIL import Image

ANCILLA = 3


def build(part):
    qc = QuantumCircuit(4, 1)
    qc.append(Gate(name="State\nPrep.", num_qubits=3, params=[]), [0, 1, 2])
    qc.barrier()
    qc.h(ANCILLA)
    W = YGate().control(1, ctrl_state=1)
    qc.append(W, [ANCILLA, 1])   # Q[2] = 1
    qc.append(Gate(name="U", num_qubits=3, params=[]), [0, 1, 2])
    V = YGate().control(1, ctrl_state=0)
    qc.append(V, [ANCILLA, 2])   # Q[1] = 2
    if part == 're':
        qc.h(ANCILLA)
    else:
        qc.rx(np.pi / 2, ANCILLA)
    qc.measure(ANCILLA, 0)
    return qc


qc_re = build('re')
qc_im = build('im')

fig_re = qc_re.draw('mpl', style='iqp', fold=-1, scale=1.15)
fig_re.suptitle('Parte reale: rotazione $H$, misura $\\langle\\sigma_x^{(a)}\\rangle=\\mathrm{Re}\\,C(t)$',
                 fontsize=13, y=1.03)
fig_re.savefig('fig_circuito_trimero_catena_re.png', dpi=200, bbox_inches='tight')

fig_im = qc_im.draw('mpl', style='iqp', fold=-1, scale=1.15)
fig_im.suptitle('Parte immaginaria: rotazione $R_x(\\pi/2)$, misura $\\langle\\sigma_y^{(a)}\\rangle=\\mathrm{Im}\\,C(t)$',
                 fontsize=13, y=1.03)
fig_im.savefig('fig_circuito_trimero_catena_im.png', dpi=200, bbox_inches='tight')

im_re = Image.open('fig_circuito_trimero_catena_re.png')
im_im = Image.open('fig_circuito_trimero_catena_im.png')
w = max(im_re.width, im_im.width)
gap = 40
h = im_re.height + im_im.height + gap
combined = Image.new('RGB', (w, h), 'white')
combined.paste(im_re, ((w - im_re.width) // 2, 0))
combined.paste(im_im, ((w - im_im.width) // 2, im_re.height + gap))
combined.save('fig_circuito_trimero_catena.png')

print("fig_circuito_trimero_catena.png salvata (due varianti, Re sopra / Im sotto)")
