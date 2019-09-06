import numpy as np
import math

lista = np.arange(0,2000,1)
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

oi = list(chunks(lista, 128))

print(math.ceil(1.))