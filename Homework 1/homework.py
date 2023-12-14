import random
import math

population_size = 51
mutation_rate = 0.3
number_of_generations = 750

'''Final Code'''

def load_dataset(filename): 
    dataset = {}
    with open(filename, 'r') as file:
        num_of_cities = int(file.readline().strip())
        for i in range(1,num_of_cities+1):
            x, y, z = file.readline().strip().split()
            dataset[i] = (float(x), float(y), float(z))
    return dataset


# To find nearest city for better initial population
def calculate_distance(city1, city2):
    return float(((city1[0] - city2[0])**2 + (city1[1] - city2[1])**2 + (city1[2] - city2[2])**2) ** 0.5)

def nearest_city(cities):
    unvisited_nodes = list(cities.keys())
    start_city = random.choice(unvisited_nodes)
    unvisited_nodes.remove(start_city)
    new_path = [start_city]

    while unvisited_nodes:
        current_city = new_path[-1]
        nearest_city = min(unvisited_nodes, key=lambda city: calculate_distance(cities[city], cities[current_city]))
        new_path.append(nearest_city)
        unvisited_nodes.remove(nearest_city)

    return new_path

# Create a population
def generate_initial_population(cities):
    initial_population = []
    for i in range(population_size):
      initial_population.append(nearest_city(cities))
    return initial_population

# Calculate length of path
def calculate_cost(path):
    total_distance = 0

    for i in range(len(path)-1):
        city_in = path[i]
        city_next = path[i + 1]
        total_distance += calculate_distance(cities[city_next], cities[city_in])
    
    last_city=path[-1]
    first_city=path[0]
    
    total_distance+= calculate_distance(cities[last_city], cities[first_city])
    if total_distance==0:
      total_distance=0.000001

    return total_distance

# Crossover
def cyclic_crossover(parent1, parent2):
    child1 = [int()] * len(parent1)
    child2 = [int()] * len(parent2)

    first_element=parent1[0]
    child1[0]=first_element
    number=0

    while True:
        get_element2=parent2[number]
        child2[number]=get_element2
        if(get_element2==first_element):
            break
        get_index1=parent1.index(get_element2)
        child1[get_index1]=parent1[get_index1]
        number=get_index1

    for num in range(0,len(child1)):
        if child1[num]==0:
            child1[num]=parent2[num]
            child2[num]=parent1[num]

    return child1, child2

# Mutation
def mutate(path):

  if random.random() > mutation_rate:
        index_to_split = random.randint(0, len(path) - 1)
        path = path[:index_to_split] + path[index_to_split:][::-1]
    
  return path

# Main
def tsp_GA():

  population = generate_initial_population(cities)

  for generation in range(number_of_generations):
      fitness_values = [1 / calculate_cost(path) for path in population]
      new_population = []
      new_population.append(population[fitness_values.index(max(fitness_values))]) # Keep path with highest fitness value to ensure elitism

      while len(new_population) < population_size:
          parent1, parent2 = random.choices(population, k=2)
          child1, child2 = cyclic_crossover(parent2, parent1)
          child1 = mutate(child1)
          child2 = mutate(child2)
          new_population.extend([child1, child2])

      population = new_population

  return min(population, key=lambda path: calculate_cost(path))

# Main
cities = load_dataset("input.txt")

best_route = tsp_GA()

best_distance = calculate_cost(best_route)
best_path_coordinates = [cities[city] for city in best_route]
best_path_coordinates.append(best_path_coordinates[0])

f = open("output.txt", "w")
f.write(format(best_distance,".3f"))
f.write("\n")
for i in best_path_coordinates:
  f.write(str(format(i[0],".0f"))+ " "+str(format(i[1],".0f"))+ " "+ str(format(i[2],".0f")))
  f.write("\n")
f.close()
