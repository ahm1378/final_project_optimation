import json
from threading import Thread, Lock
import requests
import numpy as np
import random


from genetic_improved import *
from prepare_data import get_variables

popsize= 4


def init_pop(popsize):

    column_var, beam_var = get_variables()
    n_columns = len(column_var)
    n_beams = len(beam_var)
    n_vars = n_columns*2 + n_beams
    final_pop = np.random.randint(low=-3, high=+3, size=(popsize, n_vars))
    return final_pop


def parent_selection(mute_rate, cross_rate):
    mut_size = int(np.ceil(mute_rate * popsize))
    cross_size = 2 * int(np.ceil(cross_rate * popsize) / 2)
    child_pop = mut_size + cross_size
    mating_poll_index = random.sample(range(0, popsize), int(child_pop))
    return mating_poll_index, mut_size, cross_size


def survivor_selection(total_population, main_popsize, coef ):
    fitness = np.zeros(len(total_population))
    print(len(servers))
    SizeOfVMs = len(total_population) // len(servers)
    arrays = []
    threads = []
    for j in range(len(servers)):
        if j != len(servers) - 1:
            arrays.append(total_pop[j*SizeOfVMs:(j+1)*SizeOfVMs])
        else:
            arrays.append(total_pop[j*SizeOfVMs:])

    for k in range(len(arrays)):
        coef = it
        url = f"{servers[k]}/api/calculate/"
        t = Thread(target=request_calc, args=(url, arrays[k].tolist(),coef))
        threads.append(t)
    for y in threads:
        y.start()
    for y in threads:
        y.join()

    #     threads.append(t)
    # for u in threads:
    #     u.join()

    flatten_cost = lambda y:[x for a in y for x in flatten_cost(a)] if type(y) is list else [y]
    fitness_f = flatten_cost(fitness)

    total_best_index = np.argsort(fitness_f)
    final_best_index = total_best_index[0: main_popsize]
    new_pop = total_population[final_best_index]
    new_fitness = fitness[final_best_index]
    return new_pop, new_fitness


iterations = 1

# servers = ["192.168.0.1", "192.168.0.2", "192.168.0.3", "192.168.0.4"]
servers = ["http://localhost:8000", "http://localhost:8000", "http://localhost:8000", "http://localhost:8000", ]
n_pop = 4
population = init_pop(4)


lock = Lock()

fitness = []


def request_calc(url, data, coef):
    global fitness
    global lock
    result = requests.post(url, data=json.dumps({"data": data,"coef":coef}), headers={'Content-Type': 'application/json'})
    with lock:
        fitness.append(result.json())


for it in range(1):
    print("generation {} started ************************************".format(it))
    mating_poll, mu_pop_size, cross_pop_size = parent_selection(0.3, 0.5)
    #pop_cross = crossover(pop=population, cross_size=cross_pop_size, cross_pop_index=mating_poll)
    #pop_mut = mutation(population=population, mute_size=mu_pop_size, mute_pop_index=mating_poll)
    #total_pop = np.concatenate((population, pop_cross, pop_mut), axis=0)
    total_pop = population

    new_pop, new_fitness = survivor_selection(total_population=total_pop , main_popsize=popsize , coef=it+1)

    population = new_pop



print(new_pop)





