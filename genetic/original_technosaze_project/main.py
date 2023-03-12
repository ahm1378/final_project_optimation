from genetic_improved import *
import dask.distributed as dd
from genetic_improved import cost_function

client = dd.Client('127.0.0.1:8786')
n_workers = len(client.scheduler_info()['workers'])


def select_best(fitness, main_popsize,total_population ):
    total_best_index = np.argsort(fitness)
    final_best_index = total_best_index[0: main_popsize]
    new_pop = total_population[final_best_index]
    new_fitness = fitness[final_best_index]
    return new_pop, new_fitness


def main_algorithm():
    global client
    global population

    fit = []
    for it in range(generation):
        print("generation {} started ************************************".format(it))
        mating_poll, mu_pop_size, cross_pop_size = parent_selection(0.3, 0.5)
        pop_cross = crossover(pop=population, cross_size=cross_pop_size, cross_pop_index=mating_poll)
        pop_mut = mutation(population=population, mute_size=mu_pop_size, mute_pop_index=mating_poll)
        total_pop = np.concatenate((population, pop_cross, pop_mut), axis=0)


        # Distribute the total population to the worker nodes and compute the fitness values and cost function
        total_population_parts = total_pop.to_delayed()
        fitness_values = client.map(compute_fitness, total_population_parts)
        cost_values = client.map(compute_cost, total_population_parts)

        # Join the fitness values and cost function back on the master node and select the best individuals
        fitness_values = db.from_delayed(fitness_values).compute()
        cost_values = db.from_delayed(cost_values).compute()
        x_string = np.array2string(po, formatter={'float_kind': lambda x: "%.2f" % x})
        with open("fit.txt", 'a') as f:
                f.write(x_string)
                f.write('\n')
        print("generation {} finished".format(it))