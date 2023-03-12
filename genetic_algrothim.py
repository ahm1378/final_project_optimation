import time

import numpy as np
import random
from beam_operation import ColBeam
from concerete_cost import Concerete_Cost
from cost import FrameWorkCost, Cost
from prepare_data import chrom_length, final_cost, column_id, beam_id, full_normal_data, general_data, get_variables
from section_generator import columns_generation,beams_generation
from create import my_etabs
from preprocces import PreProcces
from setting import default

pre = PreProcces(etabs_object=my_etabs)


def get_model_cost():
    global full_normal_data
    pre = ColBeam(etabs_object=my_etabs, flag_design=False, flag_analysis=False)
    full_data = pre.get_full_frame_data_index_id(general_frame_data=general_data, result=full_normal_data)
    conc = Concerete_Cost(etabs_object=my_etabs)
    volume_conc = conc.concrete_volume(full_data=full_data)
    conc_price = conc.concrete_total_price(volume_conc)
    frame = FrameWorkCost(etabs_object=my_etabs, full_frame_data=full_data)
    frame_price = frame.total_value_frame()
    pre.run_model()
    pre.start_design()
    ho = Cost(etabs_object=my_etabs)
    rebar = ho.total_value_rebar(full_data=full_data, beams=beam_id, columns=column_id)
    cost = conc_price + frame_price + rebar
    return cost


beam_name, column_name = pre.create_init_section(general_data=general_data)
first_cost = 440919429
print(first_cost)
popsize = 200
generation = 100
print(first_cost)
column_var, beam_var = get_variables()


def init_pop():
    n_columns = len(column_var)
    n_beams = len(beam_var)
    print("len",len(beams_generation))
    final_pop = np.zeros((popsize, n_beams+n_columns))
    for pop in final_pop:
        pop[0:n_columns] = np.random.choice(len(columns_generation)-1, n_columns)
        pop[n_columns:(n_columns+n_beams)] = np.random.choice(len(beams_generation)-1, n_beams)
    return final_pop


def parent_selection(mute_rate, cross_rate):
    mut_size = int(np.ceil(mute_rate * popsize))
    cross_size = 2 * int(np.ceil(cross_rate * popsize) / 2)
    child_pop = mut_size + cross_size
    mating_poll_index = random.sample(range(0, popsize), int(child_pop))
    return mating_poll_index, mut_size, cross_size


def crossover(pop, cross_size, cross_pop_index):
    children = np.zeros((cross_size, len(pop[0])))
    chrom_size = len(pop[0])
    for i in range(0, cross_size, 2):
        parent_1 = pop[cross_pop_index[i]]
        parent_2 = pop[cross_pop_index[i + 1]]
        cross_pont = np.random.randint(1, len(pop[0]) - 1)
        children[i] = np.concatenate((parent_1[0:cross_pont], parent_2[cross_pont:chrom_size]), axis=0)
        children[i + 1] = np.concatenate((parent_2[0:cross_pont], parent_1[cross_pont:chrom_size]), axis=0)
    return children


def mutation(population, mute_size, mute_pop_index):
    children_mute = np.zeros((mute_size, len(population[0])))
    cross_size = len(mute_pop_index) - mute_size - 1
    j = 0
    for i in range(cross_size, len(mute_pop_index)-1):
        parent = population[mute_pop_index[i]]
        mute_pont = np.random.randint(1, len(population[0]) - 1)
        if mute_pont < len(column_var):
            parent[mute_pont] = np.random.randint(0, len(columns_generation)-1)
        else:
            parent[mute_pont] = np.random.randint(len(columns_generation)-1, len(columns_generation)+len(beams_generation))
        children_mute[j] = parent
        j = j+1
    return children_mute


def cost_function(x, coef):
    x = np.asarray(x, dtype="int")
    pre.etabs.SapModel.SetModelIsLocked(False)
    i = 0
    try:
        for section in range(len(column_var)):
            for se in column_var[section]:
                 pre.set_section(frame_name=se, section_name=columns_generation[x[i]])
            i += 1
        for section in range(len(beam_var)):
            for se in beam_var[section]:
                 pre.set_section(frame_name=se, section_name=beams_generation[x[i]])
            i = i+1
    except:
        print("error in setting")
        print("x[i]",x[i])
        print("i", i)
        print(x[0:len(column_var)])
        print(x[len(column_var):len(beam_var)+len(column_var)])
        print(beams_generation)
    cost = final_cost(coef)
    co = np.array([cost, (first_cost-cost)*100/first_cost])
    x_string = np.array2string(x, formatter={'float_kind':lambda x: "%.2f" % x})
    co_string = np.array2string(co, formatter={'float_kind':lambda x: "%.2f" % x})
    if cost < first_cost:
        with open("test.txt",'a') as f:
            f.write(x_string)
            f.write(co_string)
            f.write('\n')

    print(x[0:5])
    print("cost is", cost)
    return cost


def survivor_selection(total_population, main_popsize,coef):
    fitness = np.zeros(len(total_population))
    j = 0
    for i in total_population:
        fitness[j] = cost_function(i, coef)
        j = j+1
    total_best_index = np.argsort(fitness)
    final_best_index = total_best_index[0: main_popsize]
    new_pop = total_population[final_best_index]
    new_fitness = fitness[final_best_index]
    return new_pop, new_fitness


def main_algorithm():


    fit=[]
    for it in range(generation):
        print("generation {}".format(it))
        mating_poll, mu_pop_size, cross_pop_size = parent_selection(0.3, 0.7)
        pop_cross = crossover(pop=population, cross_size=cross_pop_size, cross_pop_index=mating_poll)
        pop_mut = mutation(population=population, mute_size=mu_pop_size, mute_pop_index=mating_poll)
        total_pop = np.concatenate((population, pop_cross, pop_mut), axis=0)
        new_pop, new_fitness = survivor_selection(total_pop, main_popsize=popsize,coef=10**it)
        population = new_pop
        fit.append(np.average(new_fitness))
        po = np.array(fit)
        x_string = np.array2string(po, formatter={'float_kind': lambda x: "%.2f" % x})
        with open("fit.txt", 'a') as f:
                f.write(x_string)
                f.write('\n')
        print("generation {} finished".format(it))


main_algorithm()

# init pop
# ----------------------------------------------