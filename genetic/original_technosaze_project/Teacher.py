def Teacher(L, PFit):
    from numpy import shape, zeros, dot
    from numpy.random import rand
    from random import randint
    size = shape(L)
    nV = size[1]
    nL = size[0]
    MeanL = zeros(nV)
    for i in range(nV):
        MeanL[i] = sum(L[:, i]) / size[0]

    # The best soluction will act as a teacher for that iteration
    min(PFit)
    a = list(PFit.copy())
    min_num = a.index(min(a))
    T = L[min_num, :]  # Teacher
    stepsize = zeros((nL, nV))
    for i in range(size[0]):
        TF = randint(1, 2)
        stepsize[i, :] = T - dot(TF, MeanL)

    newL = L + rand(size[0], size[1]) * stepsize
    return newL
