"""
In this script, we load the data from the H1-1E emulator
and visualise the results of the noisy circuits for the
diagonal ensemble values in the XY model.

Can we see a trend towards order (disorder) at
lower (higher) energies?
"""


import pickle
from matplotlib import pyplot as plt

thetas = [0, 0.4, 0.6]
for theta in thetas:
    filename = 'data/XY_theta={:.2f}.pkl'.format(theta)
    with open(filename, 'rb') as file:
        data = pickle.load(file)

    plt.errorbar(data['ts'], data['order_parameters'],data['order_parameter_errorbars'], label='theta = {:.2f}'.format(theta))

plt.legend(loc='best')
plt.title('4x4 XY Model thermalisation from quantum circuits')
plt.xlabel('t')
plt.ylabel('<Sx^2 + Sy^2>')
plt.savefig('plots/Fig_07_XY_thermalisation.png',dpi=300)
print('done')
