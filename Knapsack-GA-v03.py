import random


# ITEMS INPUT Example
weights = [382745,799601,909247,729069,467902, 44328,34610,698150,823460,903959,853665,551830,610856,670702,488960,951111,323046,446298,931161,31385,496951,264724,224916,169684]
values = [825594,1677009,1676628,1523970,943972,97426,69666,1296457,1679693,1902996,1844992,1049289,1252836,1319836,953277,2067538,675367,853655,1826027,65731,901489,577243,466257,369261]
capacity = 6404180

# CONFIGS
POPULATION_SIZE = 400
GEN_MAX = 200
XOVER_CHANCE = 0.9
MUTATION_CHANCE = 0.25
XOVER_TYPE = 'Two_Point'    # All-types: 'One_Point', 'Two_Point'
SELECT_PARENTS_TYPE = 'Ranking'    # All-types: 'Roulette_Wheel', 'Ranking', 'SUS'
SELECT_SORVIVORS_TYPE = 'Ranking'    # All-types: 'Roulette_Wheel', 'Ranking', 'SUS'
ONLY_CHILDREN_SURVIVE = False   # if True: children_selection_percentage must be bigger than 1

parents_selection_percentage = 0.6
children_selection_percentage = 1.2

# best genotype of several run algorithm
best_genotype = []
best_genotype_fitness = 0
best_genotype_weight = 0
best_genotype_config = ''

class Item(object):
	# set the details of this problem
    def properties(self, capacity, weights, values):
        self.weights = weights
        self.values = values
        self.capacity = capacity
    
    def get_weight(self, genotype):
        sum_w = 0
        for index, gene in enumerate(genotype):
            if gene == 1:
                sum_w += self.weights[index]
        return sum_w
        
    # fitness of each genotype    
    def fitness(self, genotype):
        sum_w = 0
        sum_v = 0
		# get weights and profits
        for index, gene in enumerate(genotype):
            if gene == 1:
                sum_w += self.weights[index]
                sum_v += self.values[index]
		# if sum_w greater than the total weight return 1
        if sum_w > self.capacity:
            # 1 instead of 0 because of preventing zero deviation in fitness_prob
            return 1
        else: 
            return sum_v 

    # sort population based on fitness proportionate
    # first item have most fitness
    def sort_pop(self, population):
        return sorted(population, key=lambda x: self.fitness(x), reverse = True)

    # population probability based on fitness proportionate
    def fitness_prob_list(self, pop, sum_fit):
        sum_probability = 0
        pop_probability = []
        for p in pop:
            sum_probability += self.fitness(p) / sum_fit
            pop_probability.append(sum_probability)
        return pop_probability
    
    def fitness_cumulative_list(self, pop, sum_fit):
        sum_probability = 0
        pop_probability = []
        for p in pop:
            sum_probability += self.fitness(p)
            pop_probability.append(sum_probability)
        return pop_probability

          
def first_population():
    return [[random.randint(0, 1) for x in range(len(values))] for x in range(POPULATION_SIZE)]

# Bit Flip Mutation
def mutate(genotype):
    gene_index = random.randint(0,len(genotype)-1)
    if genotype[gene_index] == 1:
        genotype[gene_index] = 0
    else:
        genotype[gene_index] = 1
    return genotype

def xover_one_point(male, female):
    point = random.randint(1,len(male)-1)
    child1 = male[:point] + female[point:]
    child2 = female[:point] + male[point:]
    return child1, child2

def xover_two_point(male, female):
    # two single-point xover
    male, female = xover_one_point(male, female)
    child1, child2 = xover_one_point(male, female)
    return child1, child2

def xover(male, female):
    if XOVER_TYPE == 'One_Point' :
        return xover_one_point(male, female)
    elif XOVER_TYPE == 'Two_Point':
        return xover_two_point(male, female)
    else:
        print("xover_type is incorrect!")
    
def mating_pool(parents, children_quantity):
    children = []
    while len(children) < children_quantity:
        # select mates
        male = parents[random.randint(0,len(parents)-1)]
        female = parents[random.randint(0,len(parents)-1)]
        # xover parents
        if XOVER_CHANCE > random.random():
            child1, child2 = xover(male, female)
        else:
            child1 = female
            child2 = male
        # mutate child
        if MUTATION_CHANCE > random.random():
            if random.randint(0,1) :
                child1 = mutate(child1)
            else:
                child2 = mutate(child2)
            
        children.append(child1)
        children.append(child2)

    return children

def select_Ranking(pop, size):
    return pop[:size]

def select_Roulette_Wheel(pop, pop_prob, size):
    selected_population = []
    for i in range(size):
        random_prob = random.random()
        for index, pb in enumerate(pop_prob):
            if random_prob < pb :
                selected_population.append(pop[index-1])
                break
    return selected_population

# SUS (Stochastic Universal Sampling)
def select_SUS(pop, pop_fit_cum, size, sum_fit):
    selected_population = []
    point_distance = int(sum_fit// size)
    start_point = random.uniform(0, point_distance)
    points = [start_point + i * point_distance for i in range(0 , size)]
    for point in points:
        for index, pb in enumerate(pop_fit_cum):
            if point < pb :
                selected_population.append(pop[index-1])
                break
    return selected_population

def main():
    # creating object
    i = Item()
    i.properties(capacity, weights, values)
    # creating first population randomly
    population = first_population()
    population = i.sort_pop(population)
    for generation in range(1,GEN_MAX+1):
        generation_sum_fitness = 0

        # select parents
        if SELECT_PARENTS_TYPE == 'Ranking':
            parents = select_Ranking(population, int(parents_selection_percentage * POPULATION_SIZE))
        elif SELECT_PARENTS_TYPE == 'Roulette_Wheel':
            # calculate sum_fitness
            for p in population:
                generation_sum_fitness += i.fitness(p)
            pop_prob_list = i.fitness_prob_list(population, generation_sum_fitness)
            parents = select_Roulette_Wheel(population, pop_prob_list, int(parents_selection_percentage * POPULATION_SIZE))
        elif SELECT_PARENTS_TYPE =='SUS':
            for p in population:
                generation_sum_fitness += i.fitness(p)
            pop_fitness_list = i.fitness_cumulative_list(population, generation_sum_fitness)
            parents = select_SUS(population,pop_fitness_list,int(parents_selection_percentage * POPULATION_SIZE),generation_sum_fitness)
        # children_quantity must be integer and even, even because of parents in crossover
        children_quantity  = int (children_selection_percentage * POPULATION_SIZE)
        # making children
        children = mating_pool(parents, children_quantity)
        
        if ONLY_CHILDREN_SURVIVE :
            # (μ,λ)
            if children_selection_percentage < 1:
                print('children_selection_percentage must be bigger than 1 in ONLY_CHILDREN_SURVIVE type!')
                return
            pop = children
        else:
            # (μ+λ)
            children.extend(parents)
            pop = children
    
        #select sorvivors
        if SELECT_SORVIVORS_TYPE == 'Ranking':
            pop = i.sort_pop(pop)
            population = select_Ranking(pop, POPULATION_SIZE)
        elif SELECT_SORVIVORS_TYPE == 'Roulette_Wheel':
            # need calculate sum_fitness if it wasn't calculate before
            if generation_sum_fitness == 0:
                for p in pop:
                    generation_sum_fitness += i.fitness(p)
            pop_prob_list = i.fitness_prob_list(pop,generation_sum_fitness)
            population = select_Roulette_Wheel(pop, pop_prob_list, POPULATION_SIZE)
            population = i.sort_pop(population)
        elif SELECT_SORVIVORS_TYPE == 'SUS':
            if generation_sum_fitness == 0:
                for p in pop:
                    generation_sum_fitness += i.fitness(p)
            pop_fitness_list = i.fitness_cumulative_list(population, generation_sum_fitness)
            population = select_SUS(pop, pop_fitness_list, POPULATION_SIZE, generation_sum_fitness)
            population = i.sort_pop(population)
        # logging every generation results
        print("Generation %s :\n generation_sum_fitness: %s \n Best_Answer: %s  with fitness: %s" % (generation, generation_sum_fitness, population[0], i.fitness(population[0]) ) )
        generation += 1
    # compare best answer of each run and save the best
    global best_genotype_fitness
    global best_genotype
    global best_genotype_weight
    global best_genotype_config
    if i.fitness(population[0]) > best_genotype_fitness :
        best_genotype = population[0]
        best_genotype_fitness = i.fitness(population[0])
        best_genotype_weight = i.get_weight(population[0])
        best_genotype_config = 'CONFIGS: ' + ' ---POPULATION_SIZE:' + str(POPULATION_SIZE) + ' ---GEN_MAX:' + str(GEN_MAX) + ' ---XOVER_CHANCE:' + str(XOVER_CHANCE) + ' ---MUTATION_CHANCE:' + str(MUTATION_CHANCE) + ' ---XOVER_TYPE:' + str(XOVER_TYPE) + ' ---SELECT_PARENTS_TYPE:' + str(SELECT_PARENTS_TYPE) + ' ---SELECT_SORVIVORS_TYPE:' + str(SELECT_SORVIVORS_TYPE) + ' ---ONLY_CHILDREN_SURVIVE:' + str(ONLY_CHILDREN_SURVIVE) + '\n' 

if __name__ == "__main__":
    # run algorithm several times
    for i in range(30):
        main()
    # adding best answer details and configs to file
    # print best answer genotype and fitness
    print('===================================\nBest Answer: ' + str(best_genotype) + '\n--fitnees:' + str(best_genotype_fitness) + '\n--weight:' + str(best_genotype_weight) + ' <=' + ' --capacity:' + str(capacity) )