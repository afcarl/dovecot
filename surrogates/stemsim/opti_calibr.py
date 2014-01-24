import numpy as np
import treedict
import time

import natnet
import stemcom


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

def calibration(poses, fb=None, stem_com=None):
    if fb is None:
        fb = natnet.FrameBuffer(50.0)
    if stem_com is None:
        cfg = treedict.TreeDict()
        cfg.stem.motor_range = (0, 6)
        stem_com = stemcom.StemCom(cfg)

    time.sleep(0.1)
    assert fb.fps > 100.0


    vrep_res =  [[ 0.1100481 ,  0.6823279 ,  2.45170567],
                 [ 1.51487219,  2.00143284,  2.44584283],
                 [-1.10360631,  0.93663345,  2.40484004],
                 [-0.09994282,  1.55935965,  1.30536744],
                 [-0.01479483,  1.66135542,  3.49237228],
                 [ 1.79359275,  0.19804134,  0.45459374],
                 [ 0.0395507 ,  4.13089959,  3.17526394],
                 [-1.34310143, -0.06096789,  1.13319259],
                 [-0.03732515, -0.01554558, -0.3294154 ],
                 [ 0.00578956,  1.94747721, -1.36991427]]


    stem_com.setup(poses[0])

    fb.track_only()
    timestamps = []
    for pose in poses:
        stem_com.go_to(pose, margin=1.0, timeout=10.0)
        start = time.time()
        time.sleep(1.0)
        end   = time.time()
        timestamps.append((start, end))
    fb.stop_tracking()

    stem_com.rest()
    stem_com.range_bounds = [(-110, 110)]*6



    mean_p = []
    for start, end in timestamps:
        pdata = fb.tracking_period(start, end)
        mean_p.append(np.mean([p[1] for p in pdata], axis=0))

    assert len(mean_p) == len(vrep_res)
    n = len(mean_p)
    print(np.mat(mean_p))
    print(np.mat(vrep_res))
    Mtrans = transform_3D(np.mat(mean_p), np.mat(vrep_res))

    Mtrio = np.hstack((np.matrix(mean_p), np.ones(shape=(n, 1))))
    Mvrep = np.hstack((np.matrix(vrep_res), np.ones(shape=(n, 1))))

    Mvrep2 = (Mtrans*Mtrio.T).T

    err = Mvrep2 - Mvrep
    err = np.sum(np.multiply(err, err))
    rmse = np.sqrt(err/n)
    print(rmse)

    print(Mtrans)
    #self.assertTrue(rmse < 1e-10)

poses = [[  0.0,   0.0,   0.0,   0.0,   0.0,   0.0],
         [ 57.2,  11.6, -10.7,  14.1,   6.0, -17.7],
         [ -4.1,  -9.8,   9.8, -34.9,   5.7, -19.2],
         [ -4.4,  -0.4,  -5.7,  -2.6, -69.1, -17.7],
         [ -4.1,   5.1,  -8.9,   2.4,  80.8,  13.6],
         [44.3,  -99.0,  33.6, -15.2,  72.3, -25.1],
         [-3.8,   43.5,  25.7,  -3.8,  72.3, -42.7],
         [-25.8, -99.0,  45.6,  -7.9,  76.7,  -0.1],
         [  0.0, -99.0,  20.1,  -2.0,  64.7, -64.1],
         [ -0.6, -99.0, -54.4,   0.0,  57.9,   0.1],
        ]

if __name__ == "__main__":
    calibration(poses)
