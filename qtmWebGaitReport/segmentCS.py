# Mathematical tools

import numpy as np


class LCS:

    # Skew-symmetric matrix
    def PPV(self, vec):
        ppv = np.zeros((3, 3))

        ppv[0, 1] = vec[2] * -1
        ppv[0, 2] = vec[1]
        ppv[1, 0] = vec[2]
        ppv[1, 2] = vec[0] * -1
        ppv[2, 0] = vec[1]
        ppv[2, 1] = vec[0]

        return ppv

    # Matrix inversion
    #    def invR(R):
    #        R1 = R[1:3,1:3]
    #        T = R[1:3,4]
    #        Rinv = [R1', -R1' * T; 0 0 0 1]
    #        return Rinv

    # Build a rotation matrix starting from the Cardan or Euler angles
    def CARtoROT(self, q, i, j, k):

        # Change sign if ciclic or anticiclic
        if np.remainder(j - i + 3, 3) == 1:
            sig = 1
        else:
            sig = -1

        # Initiate Rotation matrix
        R = np.zeros((3, 3))

        # Cardan angles
        alfa = q[:, 0]
        beta = q[:, 1]
        gamma = q[:, 2]

        sa = np.sin(alfa)
        sb = np.sin(beta)
        sc = np.sin(gamma)
        ca = np.cos(alfa)
        cb = np.cos(beta)
        cc = np.cos(gamma)

        # Rotation matrix
        R[i, i] = cb * cc
        R[i, j] = -sig * cb * sc
        R[i, k] = sig * sb

        R[j, i] = sa * sb * cc + sig * ca * sc
        R[j, j] = -sig * sa * sb * sc + cc * ca
        R[j, k] = -sig * sa * cb

        R[k, i] = -sig * ca * sb * cc + sa * sc
        R[k, j] = ca * sb * sc + sig * sa * cc
        R[k, k] = ca * cb

        return R

    # Build a Cardan angles row vector from the Rotation matrix
    def ROTtoCAR(self, R, i, j, k):

        # Change sign if ciclic or anticiclic
        if np.remainder(j - i + 3, 3) == 1:
            sig = 1
        else:
            sig = -1

        # Initiate Cardan angles vector
        q = np.zeros((3, 1))

        # Cardan angles vector
        q = np.arctan2(-sig * R[j, k], R[k, k])
        q = np.append(q, np.arcsin(sig * R[i, k]))
        q = np.append(q, np.arctan2(-sig * R[i, j], R[i, i]))
        return q

    # Local coordinate system or transformation/rotation matrix
    # Input: M (XYZ,[Origin U V])
    #        a (1 or 2) for the vector you want to keep (i.e. U or V)
    #        b ('x' 'y' or 'z') for the label of the first vector (i.e. U)
    #        c is a 3 element vectors for the offsets in degrees around X, Y and Z
    def LCS(self, M, a, b, *args):

        # Extract data
        Or = M[:, 0]
        U = M[:, 1]
        V = M[:, 2]
        #
        # Cross product between U and V
        W = np.dot(self.PPV(U), V)

        # Cross product between W and the vector you do NOT want to keep
        if a == 1:
            V = np.dot(self.PPV(W), U)
        else:
            U = np.dot(self.PPV(V), W)

        # Normalise vectors
        U = U / np.linalg.norm(U)
        V = V / np.linalg.norm(V)
        W = W / np.linalg.norm(W)

        # Organise rotation matrix according to the chosen Cardan sequence
        if b == "x":
            R = np.vstack((U, V, W, Or))
        elif b == "y":
            R = np.vstack((W, U, V, Or))
        elif b == "z":
            R = np.vstack((V, W, U, Or))

        R = np.flipud(np.rot90(R))
        R = np.vstack((R, [0, 0, 0, 1]))

        # Make a transformation matrix if necessary
        varargin = args
        nargin = 4 + len(varargin)

        if nargin == 5:
            q = np.array(varargin) * (np.pi / 180)
            Roffset = self.CARtoROT(q, 0, 1, 2)
            R[0:3, 0:3] = np.dot(R[0:3, 0:3], Roffset)
        return R


# U = np.array([0,0,10])
# V = np.array([0,-50,0])
# Or = np.array([2,2,2])
# a = 1
# b = 'y'
#
# M = np.array([Or, U, V])
# M = np.rot90(M)
# M = np.flip(M,0)
#
# aa = LCS()
# R = aa.LCS(M,a,b,[0,0,90])
# RR = aa.ROTtoCAR(R,0,1,2) * 180 / np.pi
#
