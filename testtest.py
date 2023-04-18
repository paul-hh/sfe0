import numpy as np

soc1, soc2 = 5, 10
tab = [soc1, soc2]
index_max = np.argmax(tab)
index_min = np.argmin(tab)
max_soc = max(soc1, soc2)
min_soc = min(soc1, soc2)

print(index_min, index_max, max_soc, min_soc)