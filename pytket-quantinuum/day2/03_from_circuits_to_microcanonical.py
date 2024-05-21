"""
In this script, we will compute expectation values
of diagonal ensembles at different energies
using *circuits* instead of exact diagonalisation.
For an ergodic model that fulfils the
Eigenstate Thermalisation Hypothesis, the two
ensembles are equivalent in the thermodynamic limit.

We will see that the circuit-based implementation
shows the same features of low-energy ordered
vs high-energy disordered phase as the exact
diagonalisation-based method in script #01.
"""
from pytket import Circuit
from tenpy_lattice_adapter import get_qubit_couplings, draw_lattice
from tenpy.models.lattice import Square
import numpy as np
from matplotlib import pyplot as plt
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
def XYHamiltonian(couplings):
    # makes the qiskit.opflow operator that is the Hamiltonian
    # of the XY model
    N = max(list(map(max, couplings))) + 1

    coupling = couplings[0]
    bond_X = [['X', coupling[0]], ['X', coupling[1]]]
    bond_Y = [['Y', coupling[0]], ['Y', coupling[1]]]
    H = SparsePauliOp(get_pauli_string(N, bond_X))
    H = H + SparsePauliOp(get_pauli_string(N, bond_Y))
    for coupling in couplings[1::]:
        bond_X = [['X', coupling[0]], ['X', coupling[1]]]
        bond_Y = [['Y', coupling[0]], ['Y', coupling[1]]]
        H = H + SparsePauliOp(get_pauli_string(N, bond_X))
        H = H + SparsePauliOp(get_pauli_string(N, bond_Y))
    return -H

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

Lx = 4
Ly = 4
N = Lx * Ly

lattice = Square(Lx, Ly, None, bc='periodic')
couplings = get_qubit_couplings(lattice)


###########################################################
## Note the order of the couplings. It is VERY important ##
## to manually check your circuits for parallelisation,  ##
## i.e., on a 1D chain, you could choose couplings       ##
## bad = [ [0,1], [1,2], [2,3], [3,4], [4,5], ...        ##
## This will lead to almost all gate zones being idle    ##
## all of the time, so please avoid this!                ##
## For the scenario above, you could choose even-odd,i.e.##
## good= [ [0,1], [2,3], [4,5], ..., [1,2], [3,4], ...   ##
##                                                       ##
## The tenpy_lattice_adapter does a reasonable job at    ##
## parallelisation.                                      ##
###########################################################
print(couplings)

dt = 0.2
Tmax = 20

energies = []
converged_order_parameters = []
for theta in np.linspace(0, np.pi/8,5):

    qc = Circuit(N)
    for j in range(N):
        qc.H(j)
        qc.Ry(theta * 2/np.pi,j)    #Note the non-standard Pytket convention.
    sv = get_statevector(qc)
    energies.append(np.real(sv.expectation_value(XYHamiltonian(couplings))))
    order_parameters = [np.real(sv.expectation_value(Sx(N) ** 2 + Sy(N) ** 2))]
    ts = [0]

    for t in range(1,Tmax):
        print('t={}/{}'.format(t,Tmax))
        qc.append(XY_step(dt, couplings))
        sv = get_statevector(qc)
        order_parameters.append( np.real( sv.expectation_value( Sx(N)**2 + Sy(N)**2) ))
        ts.append(t)
    converged_order_parameters.append(order_parameters[-1])

    plt.figure(0)
    plt.plot(ts, np.cumsum(order_parameters)/(np.array(ts)+1), 'o-', label='theta = {:.2f}'.format(theta))
    plt.legend(loc='best')
    plt.xlabel('Number of 2nd order Trotter steps, dt = {}'.format(dt))
    plt.ylabel('Time-averaged <Sx^2 + Sy^2>')
    plt.savefig('plots/Fig_03a_Circuits2Microcanonical_thetas.png')

plt.figure(1)
plt.plot(np.array(energies)/N,converged_order_parameters, 'o')
plt.xlabel('Energy density')
plt.ylabel('Order Parameter')
plt.savefig('plots/Fig_03b_Circuits2Microcanonical_orderParams.png',dpi=300)

print('done')