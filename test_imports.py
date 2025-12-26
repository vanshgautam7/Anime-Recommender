
try:
    print("Importing loading...")
    import pandas as pd
    print("Pandas imported")
    import numpy as np
    print("Numpy imported")
    import sklearn
    from sklearn.neighbors import NearestNeighbors
    print("Sklearn imported")
    import scipy
    from scipy.sparse import csr_matrix
    print("Scipy imported")
    print("All good!")
except Exception as e:
    print(f"Error: {e}")
except ImportError as e:
    print(f"ImportError: {e}")
