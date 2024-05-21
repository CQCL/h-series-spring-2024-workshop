"""
In this script, we will assess how long it takes to produce
microcanonical expectation values using exact diagonalisation.
We will see that this becomes prohibitively expensive from ~<20 qubits.

For details about the dependencies, see documentation in script #01
in the same folder.
"""
from quspin.operators import hamiltonian # Hamiltonians and operators
from quspin.basis import spin_basis_general
from tenpy_lattice_adapter import get_qubit_couplings, draw_lattice
from tenpy.models.lattice import Square
import numpy as np
from matplotlib import pyplot as plt
from time import time

Ns = []
times = []
for (Lx,Ly) in [(3,3),(5,2),(4,3),(7,2)]:
    print('{}x{}'.format(Lx,Ly))
    N = Lx*Ly
    Ns.append(N)

    lattice = Square(Lx,Ly, None, bc='periodic')
    couplings = get_qubit_couplings(lattice)
    terms = [[-1.0,coupling[0], coupling[1]] for coupling in couplings]
    basis = spin_basis_general(N, Nup=N//2)
    H = hamiltonian([["xx",terms],["yy",terms]],[],basis=basis,dtype=np.float64)

    t0 = time()
    E,V=H.eigh()
    times.append(time()-t0)

plt.figure()
plt.semilogy(Ns, times,'o', label='Time to solution [s]')
fit = np.polyfit(Ns, np.log(times),1)
x_vals = np.linspace(min(Ns),50)
plt.semilogy(x_vals, np.exp(np.polyval(fit,x_vals)),'--', label='Fit exp({:.1f}N + {:.0f})'.format(fit[0],fit[1]))
plt.hlines(3e7, min(Ns),50, label='1 year', color='C2')
plt.hlines(4e17, min(Ns),50, label='Age of the universe', color='C3')
plt.legend(loc='best')
plt.xlabel('System Size')
plt.title('Time to compute microcanonical ensembles via exact diagonalisation')
plt.savefig('plots/Fig_02_ED_time2solution.png',dpi=300)
print('done')