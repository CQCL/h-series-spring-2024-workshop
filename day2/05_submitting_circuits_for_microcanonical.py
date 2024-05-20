"""
In this script, we will submit the circuits to
compute the order parameter in the XY model
diagonal ensemble at different energies
to the H1-Emulator hosted in Nexus.

In particular, we will note
1) how to make sure 2nd order Trotterisation
is done properly and
2) How to deal with different measurement bases.

Unlike the other scripts, we will not execute this
in real time, but this code can be used as a basis
that you can copy into your own experiments.
"""


from pytket import Circuit
import os
import pickle
from tenpy_lattice_adapter import get_qubit_couplings
from tenpy.models.lattice import Square
import numpy as np
from pytket.extensions.nexus import NexusBackend, QuantinuumConfig, Nexus
from pytket.extensions.nexus.exceptions import ResourceFetchFailed

def XY_step(dt, couplings, n_layers=1):
    # 2nd order Trotter step in XY model
    N = max(list(map(max, couplings))) + 1
    qc = Circuit(N)
    for coupling in couplings:
        qc.YYPhase(dt / 2 * 2 / np.pi, coupling[0], coupling[1])


    for t in range(n_layers-1):
        for coupling in couplings:
            qc.XXPhase(dt * 2/np.pi, coupling[0], coupling[1])
        for coupling in couplings:
            qc.YYPhase(dt * 2/np.pi, coupling[0], coupling[1])

    for coupling in couplings:
        qc.XXPhase(dt * 2 / np.pi, coupling[0], coupling[1])
    for coupling in couplings:
        qc.YYPhase(dt / 2 * 2 / np.pi, coupling[0], coupling[1])

    return qc

Lx = 4
Ly = 4
N=Lx*Ly
lattice = Square(Lx, Ly, None, bc='periodic')
couplings = get_qubit_couplings(lattice)
dt = 0.2
Tmax = 20

machine = 'H1-Emulator'
emulator_config = QuantinuumConfig(device_name=machine)
project_name="Microcanonical ExpVal Project"
try:
    project = Nexus().get_project_by_name(project_name=project_name)
except ResourceFetchFailed:
    project = Nexus().new_project(name=project_name)
backend = NexusBackend(
    backend_config=emulator_config,
    project=project,
)
n_shots = 100

thetas = [0, 0.4, 0.6]

for theta in thetas:
    for n_steps in range(1, Tmax):

        qc = Circuit(N)
        for j in range(N):
            qc.H(j)
            qc.Ry(theta * 2 / np.pi, j)
        qc.append(XY_step(dt, couplings, n_layers=n_steps))

        for basis in ['X','Y']:
            if basis == 'X':
                for j in range(N):
                    qc.H(j)
            elif basis == 'Y':
                for j in range(N):
                    qc.Sdg(j)
                    qc.H(j)

            qc.measure_all()
            id = 'XY_theta={:.2f}_n={}_basis={}'.format(theta, n_steps, basis)
            qc.name = id
            print(id)

            compiled_circuit = backend.get_compiled_circuit(qc, optimisation_level=1)
            handle = backend.process_circuit(compiled_circuit,n_shots=n_shots)
            data = {
                'Lx': Lx,
                'Ly': Ly,
                'n_steps': n_steps,
                'dt': dt,
                'handle': handle,
                'basis': basis,
            }

            filename = 'handles/{}.pkl'.format(id)
            os.makedirs('handles', mode=0o777, exist_ok=True)
            with open(filename, 'wb') as file:
                pickle.dump(data, file)

print('done')