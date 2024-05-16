"""
This is the first of a series of 7 scripts in which we
show how to obtain microcanonical expectation values
with a quantum computer.
We will walk through them in real-time, but the main
purpose is *not* to get to a full understanding, but
rather that you can peruse these scripts in your
own time and copy the snippets you need for your
own experiments.

In this script, we will obtain the microcanonical ensemble
in the square lattice quantum XY model using
classical exact diagonalisation. In particular, we will see
that there is a low-energy ordered phase, in which the
order parameter is >0, and a high-energy disordered phase,
at which the order parameter -> 0.

Our classical driver of choice is the open source package quspin.
Visit
https://github.com/QuSpin/QuSpin/issues/631
if you want to install QuSpin on Mac and
https://quspin.github.io/QuSpin/
for general documentation on quspin.

We will also use a helper file, tenpy_lattice_adapter.py
that helps with setting up lattices. This requires another
open source package, tenpy, which can be installed with

pip install physics-tenpy.
"""

from quspin.operators import hamiltonian
from quspin.basis import spin_basis_general
from tenpy_lattice_adapter import get_qubit_couplings, draw_lattice
from tenpy.models.lattice import Square
import numpy as np
from matplotlib import pyplot as plt

def microcanonical(E,V, E0, variance):
    rho = V @ np.diag(np.exp(- (E-E0)**2/ variance)) @ V.conj().transpose()
    return rho/np.trace(rho)


for (Lx,Ly) in [(3,3)]:
    print('{}x{}'.format(Lx,Ly))
    N = Lx*Ly


    #############################################################
    ## Setting up a sparse instance of the XY Hamiltonian on   ##
    ## a square lattice with periodic boundary conditions.     ##
    #############################################################
    lattice = Square(Lx,Ly, None, bc='open')
    couplings = get_qubit_couplings(lattice)
    terms = [[-1.0, coupling[0], coupling[1]] for coupling in couplings]
    basis = spin_basis_general(N)
    H = hamiltonian([["xx",terms],["yy",terms]],[],basis=basis,dtype=np.complex128)
    E,V=H.eigh()


    ################################################################
    ## The order parameter of the low-temperature ordered phase   ##
    ## of the XY model is Sx^2 + Sy^2 where Sx = 1/N \sum_i^N X_i.##
    ################################################################
    Sx = hamiltonian([["x",[[1.0, j] for j in range(N)]]],[],basis=basis,dtype=np.complex128)
    Sy = hamiltonian([["y",[[1.0, j] for j in range(N)]]],[],basis=basis,dtype=np.complex128)

    order_parameter = (Sx**2 + Sy**2)/N ** 2
    # (The convention used by D,V = np.linalg.eig(H) is that V.conj().transpose() @ H @ V = np.diag(D)))

    variance = N * 4/3 #Choosing a variance = width^2 of the Gaussian filter.
    order_parameters = []
    energy_centers = []
    for energy_center in np.linspace(min(E),max(E),30): # Sweeping over energy
        rho = microcanonical(E, V, energy_center, variance)
        order_parameters.append( np.trace(order_parameter.dot(rho)))
        energy_centers.append(energy_center)

    plt.plot(np.array(energy_centers)/N, order_parameters, 'o', label='{}x{}'.format(Lx,Ly))
    plt.xlabel('Energy Density')
    plt.ylabel('<Sx^2 + Sy^2>')
    plt.title('Order Parameter of the Quantum XY Model \n in the microcanonical ensemble')
    plt.legend(loc='best')
    plt.savefig('plots/Fig_01_from_ED_to_micro.png',dpi=300)

draw_lattice(lattice)

print('done')