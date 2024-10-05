import numpy as np
np.random.seed(0)
values = np.random.randint(1, 100, size=1000000)
%timeit result = 1.0/values