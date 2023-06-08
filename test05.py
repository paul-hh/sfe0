import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt


delta = 0.1
x = np.arange(-3.0, 3.0, delta)
y = np.arange(-2.0, 2.0, delta)
X, Y = np.meshgrid(x, y)
Z1 = np.exp(-X**2 - Y**2)
Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
Z = (Z1 - Z2) * 2

fig, ax = plt.subplots()
CS = ax.contour(X, Y, Z)
ax.scatter(X, Y)
ax.clabel(CS, inline=True, fontsize=10)
fig.colorbar(CS, ax=ax, label='Interactive colorbar')
ax.set_title('Simplest default with labels')

plt.show()