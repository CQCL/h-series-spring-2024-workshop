"""
In this script, we will retrieve shots for the circuits
that encode the diagonal ensemble in the XY-model
at different energies, turn the counts into
expectation values and error bars and then save
those values to disk.

We will not execute this script in real time.
"""

import os
import pickle
import numpy as np
from pytket.extensions.nexus import NexusBackend, QuantinuumConfig

def moments_from_counts(counts, moment=2):
    #1 is mean <X>
    #2 is structure factor <X^2>
    mean = 0

    total_shots = 0
    for bitstring, frequency in counts.items():
        s = sum([1-2*i for i in bitstring])/len(bitstring)
        mean = mean + s**moment * frequency
        total_shots = total_shots + frequency
    mean = mean/total_shots

    if total_shots > 1:
        stdev = 0
        for bitstring, frequency in counts.items():
            s = sum([1-2*i for i in bitstring])/len(bitstring)
            stdev = stdev + (s**moment - mean)**2 * frequency
        stdev = np.sqrt(stdev/(total_shots-1))
        standard_error = stdev / np.sqrt(total_shots)

        return mean, standard_error
    return mean

Lx = 4
Ly = 4
N=Lx*Ly
dt = 0.2
Tmax = 20

machine = 'H1-1E'
emulator_config = QuantinuumConfig(device_name=machine)
project_name="Microcanonical ExpVal Project"
backend = NexusBackend(
    backend_config=emulator_config,
    project_name=project_name,
)
n_shots = 100

thetas = [0, 0.4, 0.6]
for theta in thetas:
    ts = []
    observables = {'SX^2':[], 'SY^2':[]}
    errorbars   = {'SX^2':[], 'SY^2':[]}
    for n_steps in range(1, Tmax):

        for basis in ['X','Y']:
            id = 'XY_theta={:.2f}_n={}_basis={}'.format(theta, n_steps, basis)
            filename = 'handles/{}.pkl'.format(id)

            with open(filename, 'rb') as file:
                data = pickle.load(file)
            result = backend.get_result(data['handle'])
            counts = result.get_counts()

            S2 = moments_from_counts(counts)
            observables['S{}^2'.format(basis)].append(S2[0])
            errorbars['S{}^2'.format(basis)].append(S2[1])
        ts.append(n_steps*dt)

    order_parameters = np.array(observables['SX^2']) + np.array(observables['SY^2'] )
    order_parameter_errorbars =  np.array(errorbars['SX^2']) + np.array(errorbars['SY^2'] )
    data = {
        'order_parameters': order_parameters,
        'order_parameter_errorbars': order_parameter_errorbars,
        'theta':theta,
        'Lx':Lx,
        'Ly':Ly,
        'dt':dt,
        'ts':ts
    }

    filename = 'data/XY_theta={:.2f}.pkl'.format(theta)
    os.makedirs('data', mode=0o777, exist_ok=True)
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
print('done')