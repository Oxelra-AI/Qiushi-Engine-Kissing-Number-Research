import numpy as np, collections
def golay24():
    """Extended binary Golay [24,12,8] via the cyclic [23,12,7] QR code."""
    # g(x) = x^11 + x^10 + x^6 + x^5 + x^4 + x^2 + 1
    g = [1,0,1,0,1,1,1,0,0,0,1,1]   # coefficients of x^0..x^11
    g = np.array(g, dtype=np.uint8)
    n, k = 23, 12
    G = np.zeros((k, n), dtype=np.uint8)
    for i in range(k):
        G[i, i:i+12] = g
    words = np.zeros((4096, 24), dtype=np.uint8)
    for m in range(4096):
        bits = np.array([(m >> t) & 1 for t in range(12)], dtype=np.uint8)
        c = (bits @ G) % 2
        words[m, :23] = c
        words[m, 23] = c.sum() % 2
    return words
if __name__ == "__main__":
    W = golay24()
    print(dict(collections.Counter(W.sum(1).tolist())))
