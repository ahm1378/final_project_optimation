
import numpy as np
import random
from beam_operation import ColBeam
from concerete_cost import Concerete_Cost
from cost import FrameWorkCost, Cost
from prepare_data import chrom_length, final_cost, column_id, beam_id, full_normal_data, general_data, get_variables, \
    structure_cost
from section_generator import columns_generation ,beams_generation
from create import my_etabs
from preprocces import PreProcces


pre = PreProcces(etabs_object=my_etabs)


def get_model_cost():
    pre = ColBeam(etabs_object=my_etabs, flag_design=False, flag_analysis=False)
    full_data = pre.get_full_frame_data_index_id(general_frame_data=general_data, result=full_normal_data)
    cost = structure_cost(full_data)
    return cost


beam_name, column_name = pre.create_init_section(general_data=general_data)


first_cost = 300000000
print(first_cost)
popsize = 150
generation = 100
print(first_cost)
column_var, beam_var = get_variables()


def get_limit_bound(min_beam, min_column, max_beam, max_column):
    c_dimeantions = []
    for group in column_var:
        sec = pre.etabs.FrameObj.GetSection(group[0])[0]
        c_dimeantions.append(pre.etabs.PropFrame.GetRectangle(sec)[2])
        c_dimeantions.append(pre.etabs.PropFrame.GetRectangle(sec)[3])
    for i in range(len(c_dimeantions)):
        x = c_dimeantions[i]
        if x- 15 < min_column:
            c_dimeantions[i] = min_column + 15
        if x + 15 > max_column:
            c_dimeantions[i] = max_column - 15

    b_dimeantions = []
    for group in beam_var:
        sec = pre.etabs.FrameObj.GetSection(group[0])[0]
        b_dimeantions.append(pre.etabs.PropFrame.GetRectangle(sec)[2])
    for dim in range(len(b_dimeantions)):
        x = b_dimeantions[dim]
        if x - 15 < min_beam:
            b_dimeantions[dim] = min_beam + 15
        if x + 15 > max_beam:
            c_dimeantions[i] = max_beam - 15
    final_dim = c_dimeantions + b_dimeantions
    return final_dim


def init_pop():
    n_columns = len(column_var)
    n_beams = len(beam_var)
    n_vars = n_columns*2 + n_beams
    final_pop = np.random.randint(low=-3, high=+3, size=(popsize, n_vars))
    return final_pop


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
    for i in range(cross_size, len(mute_pop_index) - 1):
        parent = population[mute_pop_index[i]]
        mute_point_1 = np.random.randint(1, len(population[0]) - 1)
        mute_point_2 = np.random.randint(1, len(population[0]) - 1)
        index_1, index_2 = min(mute_point_1,mute_point_2), max(mute_point_2, mute_point_1)
        parent[index_1:index_2] = parent[index_1:index_2][::-1]
        children_mute[j] = parent
        j = j + 1
    return children_mute


def cost_function(x, coef):

    x = np.asarray(x, dtype="int")
    pre.etabs.SapModel.SetModelIsLocked(False)
    i = 0
    for section in range(len(column_var)):
        for se in column_var[section]:
            w = int(bound[i] + 5 * x[i])
            h = int(bound[i + 1] + 5 * x[i+1])
            re = pre.set_section(frame_name=se, section_name="C{}X{}".format(w, h))
            if re!=0:
                print("cant assin section C{}X{}".format(w,h))
        i += 1
    for section in range(len(beam_var)):
        for se in beam_var[section]:
            w = int(bound[i] + 5 * x[i])
            h = 55
            pre.set_section(frame_name=se, section_name="B{}X{}".format(w, h))
        i = i + 1
    cost = final_cost(coef)[0]
    co = np.array([cost, (first_cost - cost) * 100 / first_cost])
    x_string = np.array2string(x, formatter={'float_kind': lambda x: "%.2f" % x})
    co_string = np.array2string(co, formatter={'float_kind': lambda x: "%.2f" % x})
    opt_perc = (first_cost - cost) * 100 / first_cost
    if cost < first_cost:
        with open("test.txt", 'a') as f:
            f.write(x_string)
            f.write(co_string)
            f.write('\n')


    print(x[0:5])
    print("cost is", cost)
    return cost


bound = get_limit_bound(min_beam=25, min_column=30, max_beam=60, max_column=60)


population = init_pop()


def survivor_selection(total_population, main_popsize ):
    fitness = np.zeros(len(total_population))
    j = 0
    for i in total_population:
        fitness[j] = cost_function(x=i)
        j = j+1
    total_best_index = np.argsort(fitness)
    final_best_index = total_best_index[0: main_popsize]
    new_pop = total_population[final_best_index]
    new_fitness = fitness[final_best_index]
    return new_pop, new_fitness


def parent_selection(mute_rate, cross_rate):
    mut_size = int(np.ceil(mute_rate * popsize))
    cross_size = 2 * int(np.ceil(cross_rate * popsize) / 2)
    child_pop = mut_size + cross_size
    mating_poll_index = random.sample(range(0, popsize), int(child_pop))
    return mating_poll_index, mut_size, cross_size


def main_algorithm():
    global population
    fit=[]
    for it in range(generation):
        print("generation {} started ************************************".format(it))
        mating_poll, mu_pop_size, cross_pop_size = parent_selection(0.3, 0.5)
        pop_cross = crossover(pop=population, cross_size=cross_pop_size, cross_pop_index=mating_poll)
        pop_mut = mutation(population=population, mute_size=mu_pop_size, mute_pop_index=mating_poll)
        total_pop = np.concatenate((population, pop_cross, pop_mut), axis=0)
        new_pop, new_fitness = survivor_selection(total_pop, main_popsize=popsize,coef=10**it,bound=bound)
        population = new_pop
        fit.append(np.average(new_fitness))
        po = np.array(fit)
        x_string = np.array2string(po, formatter={'float_kind': lambda x: "%.2f" % x})
        with open("fit.txt", 'a') as f:
                f.write(x_string)
                f.write('\n')
        print("generation {} finished".format(it))
