def Learner(L, PFit):
    from numpy import shape, zeros
    from numpy.random import rand, shuffle
    from random import random
    from math import floor
    size = shape(L)
    nV = size[1]
    nL = size[0]
    # create unique random numbers
    rp = [i for i in range(nL)]
    shuffle(rp)
    for i in range(nL):
        while rp[i] == 1:
            val1 = round(1 + (nL - 1) * random())
            if val1 == nL:
                rp[i] = floor(1 + (nL - 1) * random())
            else:
                rp[i] = val1
    # Calculating new Learner from Learner phase
    stepsize = zeros((nL, nV))
    for i in range(nL):
        '''
        print('PFit= ',PFit[i]);
        print('i= ', i)
        print('rp[i]= ', rp[i])
        print('PFit[rp[i]])= ', PFit[rp[i]])
        '''
        if PFit[i] < PFit[rp[i]]:
            stepsize[i, :] = L[i, :] - L[rp[i], :]
        else:
            stepsize[i, :] = L[rp[i], :] - L[i, :]
            # print('stepsizes shape=',shape(stepsize))
            # print(' rand size= ', shape(rand(nL, nV)))
    # print(rand(nL, nV));
    # print(stepsize)
    newL = L + rand(nL, nV) * stepsize

    return newL
