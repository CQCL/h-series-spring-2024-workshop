"""
In this script, we will assess how long it takes to produce
diagonal ensemble expectation values using quantum circuit.
In contrast to the exact diagonalisation technique, the
circuit-based technique is feasible for > 20 qubits.
"""


from pytket import Circuit
from tenpy_lattice_adapter import get_qubit_couplings, draw_lattice
from tenpy.models.lattice import Square
import numpy as np
from matplotlib import pyplot as plt
from time import time
from pytket.extensions.qiskit import tk_to_qiskit
from qiskit import Aer
from qiskit.quantum_info import SparsePauliOp, Statevector

def get_pauli_string(N, lst):
    s = ''
    for j in range(N):
        flag = 0
        for op in lst:
            if op[1]==j:
                s = s+op[0]
                flag = 1
                break
        if flag ==0: s = s+'I'
    return s

def get_statevector(qc, noise_model=None, precision='single'):
    qc_temp = tk_to_qiskit(qc)
    qc_temp.save_statevector()
    sim_statevector = Aer.get_backend('aer_simulator_statevector', precision = precision)
    sv = sim_statevector.run(qc_temp, noise_model=noise_model, shots=1).result().data()['statevector']
    return Statevector(sv)

def Sx(N):
    # makes the qiskit SparsePauliOperator that is sum of X on N qubits, divided by N
    one_point_list_z = [[['X', j]] for j in range(N)]
    a = 0
    for z in one_point_list_z:
        a = a + SparsePauliOp(get_pauli_string(N, z))
    return a / N

def Sy(N):
    # makes the qiskit SparsePauliOperator that is sum of Y on N qubits, divided by N
    one_point_list_z = [[['Y', j]] for j in range(N)]
    a = 0
    for z in one_point_list_z:
        a = a + SparsePauliOp(get_pauli_string(N, z))
    return a / N

def XY_step(dt, couplings, n_layers=1):
    # 2nd order Trotter step in XY model
    N = max(list(map(max, couplings))) + 1
    qc = Circuit(N)

    for t in range(n_layers):
        for coupling in couplings:
            qc.YYPhase(dt/2 * 2/np.pi, coupling[0], coupling[1])
        for coupling in couplings:
            qc.XXPhase(dt * 2/np.pi, coupling[0], coupling[1])
        for coupling in couplings:
            qc.YYPhase(dt/2 * 2/np.pi, coupling[0], coupling[1])
    return qc

Ns = []
times = []
for (Lx,Ly) in [(4,4),(5,4)]:
    t0 = time()
    print('{}x{}'.format(Lx,Ly))
    N = Lx*Ly

    lattice = Square(Lx,Ly, None, bc='periodic')
    couplings = get_qubit_couplings(lattice)

    dt = 0.2
    Tmax = 20

    qc = Circuit(N)
    for j in range(N):
        qc.H(j)
    sv = get_statevector(qc)
    order_parameters = [np.real(sv.expectation_value(Sx(N) ** 2 + Sy(N) ** 2))]
    ts = [0]

    for t in range(1,Tmax):
        print('t={}/{}'.format(t,Tmax))
        qc.append(XY_step(dt, couplings))
        sv = get_statevector(qc)
        order_parameters.append( np.real( sv.expectation_value( Sx(N)**2 + Sy(N)**2) ))
        ts.append(t)

    t1 = time()
    times.append(t1-t0)
    Ns.append(N)


plt.figure()
plt.plot(Ns, times,'o',label='Time to solution [s]')
fit = np.polyfit(Ns, np.log(times),1)
x_vals = np.linspace(min(Ns),50)
plt.semilogy(x_vals, np.exp(np.polyval(fit,x_vals)),'--', label='Fit exp({:.1f}N + {:.0f})'.format(fit[0],fit[1]))
plt.hlines(3e7, min(Ns),50, label='1 year', color='C2')
plt.hlines(4e17, min(Ns),50, label='Age of the universe', color='C3')
plt.legend(loc='best')
plt.xlabel('System Size')
plt.title('Time to compute microcanonical ensembles via circuits')
plt.savefig('plots/Fig_04a_Circuits_time2solution.png')

print('done')