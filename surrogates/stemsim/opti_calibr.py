import numpy as np

def Rot(M33):
    R = np.eye(4)
    for i in range(3):
        for j in range(3):
            R[i, j] = M33[i, j]
    return np.matrix(R)

def Trans(T3):
    T = np.eye(4)
    for i in range(3):
        T[i, 3] = T3[i]
    return np.matrix(T)

def Scale(factor):
    S = np.eye(4)
    for i in range(3):
        S[i, i] = factor
    return np.matrix(S)

def transform_3D(A, B, scaling=True):
    assert A.shape == B.shape

    # originize A and B
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)

    A_c = A - np.tile(centroid_A, (A.shape[0], 1))
    B_c = B - np.tile(centroid_B, (B.shape[0], 1))

    # detect scaling
    norm_A = np.linalg.norm(A_c)
    norm_B = np.linalg.norm(B_c)
    if norm_B != 0:
        scaling_AB = norm_A/norm_B

    A_u = A_c/scaling_AB

    # A and B are only a rotation away now !
    H = np.transpose(A_u) * B_c
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T * U.T

    # if reflection case
    if np.linalg.det(R) < 0:
       Vt[2,:] *= -1
       R = Vt.T * U.T

    return Trans(centroid_B.T)*Rot(R)*Scale(1.0/scaling_AB)*Trans(-centroid_A.T)