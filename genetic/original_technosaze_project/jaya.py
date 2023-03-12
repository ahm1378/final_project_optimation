import matplotlib.pyplot as plt
import numpy as np
from fobj import final_cost
from genetic_improved import bound, cost_function, beam_var, column_var

nV = (len(column_var) + len(beam_var)) * 2


class JayaAlgorithm(object):

    def __init__(self, dimention, ub, lb, function, variable_type="unf", max_iter=100, pop_size=40):
        self.pop_size = pop_size
        self.dimention = dimention
        self.ub = ub
        self.lb = lb
        self.max_iter = max_iter
        self.objective_function = function

        if variable_type == "unf":
            self.pop = np.random.uniform(lb, ub, (pop_size, dimention))
        elif variable_type == "int":
            self.pop = np.random.randint(lb, ub, (pop_size, dimention))

    def selection(self, pop, value=False):
        obj = np.array([])
        for i in range(self.pop_size):
            obj = np.append(obj, self.objective_function(pop[i], 10 ** 9, bound))

        if value == False:
            return obj.argmin(), obj.argmax()
        else:
            return obj.min(), obj.max()

    def new_pop(self, r):
        Xnew = np.zeros_like(self.pop)
        Xold = self.pop.copy()
        best, worst = self.selection(self.pop)
        Xbest = self.pop[best]
        Xworst = self.pop[worst]

        for i in range(self.pop_size):
            Xnew[i] = Xold[i] + r[0] * (Xbest - abs(Xold[i])) - r[1] * (Xworst - abs(Xold[i]))

        for i in range(self.pop_size):
            for j in range(self.dimention):
                if Xnew[i][j] > self.ub:
                    Xnew[i][j] = self.ub
                elif Xnew[i][j] < self.lb:
                    Xnew[i][j] = self.lb

        return Xnew

    def result(self):
        value = self.selection(self.pop, value=True)[0]
        variables = self.pop[self.selection(self.pop)[0]]

        plt.figure(figsize=(10, 5))
        plt.plot(self.obj_list)
        plt.title("Jaya Algorithm Solution by Each Iterations")
        plt.xlabel("Iteration")
        plt.ylabel("Objective Value")
        plt.show()

        return {"Objective Value:": value, "Variables": variables}

    def main(self):
        self.obj_list = []
        best, worst = self.selection(self.pop, value=True)

        for it in range(self.max_iter):
            r = np.random.uniform(0, 1, (2, self.dimention))
            new_population = self.new_pop(r)
            new_best, new_worst = self.selection(new_population, value=True)

            if new_best < best:
                self.pop = new_population
                best = new_best
                worst = new_worst
            else:
                if new_best == best and new_worst < worst:
                    self.pop = new_population
                    best = new_best
                    worst = new_worst


solver = JayaAlgorithm(dimention=nV, ub=+3, lb=-3, function=cost_function, variable_type='int', pop_size=50 ,max_iter=100)
print("algorithm started")
solver.main()
print(solver.result())
