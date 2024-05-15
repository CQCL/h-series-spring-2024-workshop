#Tenpy can be installed with pip install physics-tenpy
from tenpy.models import lattice
import numpy as np
import matplotlib.pyplot as plt


def coordinate2qubit_mapping(lattice):
    mapping = []
    for e, site in enumerate(lattice.order):
        mapping.append([site, e])
        #print('Site [X,Y,U] = {} is mapped to qubit {}'.format(site, e))
    return mapping

def qubit2coordinate(lattice):
    mapping = []
    for e, site in enumerate(lattice.order):
        mapping.append([e, site])
        #print('Site [X,Y,U] = {} is mapped to qubit {}'.format(site, e))
    return mapping


def get_qubit_couplings(lattice, which='nearest_neighbors'):
    couplings = lattice.pairs[which]
    unit_cell_size = max(lattice.order[:, 2]) + 1

    qubit_couplings = []
    for u1, u2, dx in couplings:
        dx = np.r_[np.array(dx), u2 - u1]
        lat_idx_1 = lattice.order[lattice._mps_fix_u[u1], :]
        lat_idx_2 = lat_idx_1 + dx[np.newaxis, :]
        lat_idx_2_mod = np.mod(lat_idx_2[:, :-1], lattice.Ls)
        keep = lattice._keep_possible_couplings(lat_idx_2_mod, lat_idx_2[:, :-1], u2)

        lat_idx_2_mod = np.mod(lat_idx_2, (lattice.Ls[0], lattice.Ls[1], unit_cell_size))

        sites1 = lat_idx_1[keep, :]
        sites2 = lat_idx_2[keep, :]
        sites2_mod = lat_idx_2_mod[keep, :]

        for s1, s2 in zip(sites1, sites2_mod):
            qubit1 = np.where((lattice.order == s1).all(axis=1))[0][0]
            qubit2 = np.where((lattice.order == s2).all(axis=1))[0][0]
            qubit_couplings.append([qubit1, qubit2])
        #print('Couplings: {}'.format(qubit_couplings))
    return qubit_couplings


def draw_lattice(lat):
    fig = plt.figure()
    ax = plt.gca()
    lat.plot_coupling(ax, linestyle='-', linewidth=2)
    lat.plot_order(ax, linestyle=':', linewidth=0.5)
    lat.plot_sites(ax)
    ax.set_aspect('equal')
    plt.show()

if __name__ == '__main__':
    lat = lattice.Honeycomb(5, 5, None, bc='periodic', order='default')
    print('Coordinate to qubit mapping is {}'.format(coordinate2qubit_mapping(lat)))
    print('Paralellized Qubit Couplings are {}'.format(get_qubit_couplings(lat)))
    draw_lattice(lat)