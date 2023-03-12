import numpy as np
from random import random
from matplotlib.pyplot import plot, grid, show
from Teacher import Teacher  # Teacher mechanism belong to TLBO
from Learner import Learner  # Learner mechanism belong to TLBO
from fobj import fobj  # objective function that can be changed
from genetic_improved import bound, column_var, beam_var

'''  -----------------Initial inputs-------------'''
nV = (len(column_var)*2+len(beam_var))
Lb = np.array([-2]*nV)  # upper bound limit for variable
Ub = np.array([+2]*nV)  # lower bound limit
nV = len(Lb)  # number of variables
nL = 100  # number of population
maxNFEs = 10000  # maximum number of objective functions iteration
print(bound)
'''===============Generate initial solutions==============='''
L = np.zeros((nL, nV))
# Generate initial solutions
for i in range(nL):
    rand_vec = np.random.rand(nV)
    L[i, :] = Lb + (Ub - Lb) * rand_vec
Fit = np.zeros(nL)
PFit = np.zeros(nL)
print("Design vectors all are inside the search space.")
for i in range(nL):
    res = fobj(L[i, :], Lb=Lb,Ub=Ub,bounds=bound)
    X = res[0]
    fit = res[1]
    pfit = res[2]
    L[i, :] = X
    Fit[i] = fit
    PFit[i] = pfit

# finding best student
minPFit = min(PFit)
a = list(PFit.copy())
min_num = a.index(min(a))
bestL = L[min_num, :] # best learner

'''===================Replacement function==========='''


def Replacement(L, newL, Fit, PFit, Lb, Ub):
    from numpy import shape
    size = shape(L)
    nL = size[0]
    for i in range(nL):
        res = fobj(newL[i, :], Lb=Lb,Ub=Ub,bounds=bound)
        X = res[0]
        fit = res[1]
        pfit = res[2]
        if pfit <= PFit[i]:
            L[i, :] = X
            Fit[i] = fit
            PFit[i] = pfit
    res2 = [L, Fit, PFit]
    return res2


NFEs = 0
NITs = 0
output2 = []
output1 = []
output3 = []
'''=========================Algorithm body============='''
while NFEs < maxNFEs:
    print("generation",NFEs)
    NITs = NITs + 1;
    newL = Teacher(L, PFit)
    res = Replacement(L, newL, Fit, PFit, Lb, Ub)
    L = res[0]
    Fit = res[1]
    PFit = res[2]
    NFEs = NFEs + nL
    newL = Learner(L, PFit)
    res = Replacement(L, newL, Fit, PFit, Lb, Ub)
    L = res[0]
    Fit = res[1]
    PFit = res[2]
    NFEs = NFEs + nL
    minPFit = min(PFit)

    a = list(PFit.copy())
    min_num = a.index(min(a))
    minFit = Fit[min_num]
    bestL = L[min_num, :]  # best learner
    output1.append(min(PFit))
    output2.append(max(PFit))
    output3.append(np.mean(PFit))

# printing the results
print(minFit)  # best value for cost function
print(bestL)  # The best Vairable combination
plot(range(NITs), output1, 'g')
plot(range(NITs), output2, 'r--')
plot(range(NITs), output3, 'b-.')
# grid('on')
show()