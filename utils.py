import math
import numpy as np

def get_distance (cell1, cell2):

    """
    - Calculate the euclideandistance between two cells
    - cell1 and cell2 are tuples (x,y)
    """
    return math.sqrt(   (cell1[0] - cell2[0])**2 + (cell1[1] - cell2[1])**2   )



def calculate_cell_occupancy_matrix(model):
    """
    - Calculate the occupancy of each cell in the grid
    - Return a matrix of the same size as the grid, where each cell contains -1 if it is empty, or the type of the agent occupying it
    """

    occupancy_matrix = np.zeros((model.width, model.height)) -1

    for agent in model.schedule.agents:
        occupancy_matrix[agent.pos[0]][agent.pos[1]] = agent.type

    return occupancy_matrix


def calculate_neighborhood_richness(model, cell):
    """
    - Calculate the  average richness of the neighborhood of a cell
    - cell is a tuple (x,y)
    """
    richness = 0
    neighbors = model.grid.get_neighbors(cell, moore=True, include_center = False)
    for neighbor in neighbors:
        richness += neighbor.income
    
    if len(neighbors) == 0:
        richness = 100000000
    else:
        richness = richness / len(neighbors)

    return richness


def calculate_alike_destination(model, agent, empty_cell):
    """
    - Take the origin_cell of an agent, that moves, which mean that is unhappy. Calculate the nr of alike neighbors the agent would have if moved to the empty_cell.
    - Return the number of alike neighbors.
    """

    alike_neighbors = 0
    for neighbor in model.grid.iter_neighbors(empty_cell, moore=True):
        if neighbor.type == agent.type:
            alike_neighbors += 1
        
    return alike_neighbors



#return a measure of similarity between the neighborhood richness of the agent and the neighborhood richness of the empty_cell
#must be inversely proportional to the difference between the two

def calculate_alike_neighborhood_composition(model, agent, empty_cell):
    neighborhood_richness_mean = calculate_neighborhood_richness(model, agent.pos)

    neighborhood_richness_mean_empty = calculate_neighborhood_richness(model, empty_cell)

    return 1 /  ( (abs(neighborhood_richness_mean - neighborhood_richness_mean_empty)+100)   ) **2

def calculate_different_destination(model, agent, empty_cell):

    neighborhood_richness_mean = calculate_neighborhood_richness(model, agent.pos)

    neighborhood_richness_mean_empty = calculate_neighborhood_richness(model, empty_cell)

    return abs(neighborhood_richness_mean - neighborhood_richness_mean_empty)**2


def calculate_cell_emptiness_time(model, empty_cell):
    """
    - Calculate the time that the empty_cell has been empty. 
    Do it using the model.cell_occupancy_matrix_array that contains, per each step, the agent in each cell.
    """
    empty_time = 1 #so that the minimum is 1+


    #iterate reveresly over the matrices in model.cell_occupancy_matrix_array
    for i in range(len(model.cell_occupancy_matrix_array)-1, -1, -1):
        if model.cell_occupancy_matrix_array[i][empty_cell[0]][empty_cell[1]] == -1:
            empty_time += 1
        else:
            break
    
        
    return empty_time

def calculate_empty_surrounded(model, empty_cell):
    """
    - Calculate the number of empty cells that surround the empty_cell
    """
    empty_surrounded = 0

    for neighbor in model.grid.iter_neighborhood(empty_cell, moore=True):
        if model.grid.is_cell_empty(neighbor):
            empty_surrounded += 1

    return empty_surrounded


#pick a random row with a probability equal to the percent column
def pick_random_row(df, percent_cumul_limit_low = 0, percent_cumul_limit_high = 100):

    df1 = df[(df["percent_cumul"] >= percent_cumul_limit_low) & (df["percent_cumul"] <= percent_cumul_limit_high)]

    #df1["percent"] now not sums to 100. make it so in df1
    total_percent = df1["percent"].sum()
    df1.loc[:, "percent"] = df1["percent"] / total_percent

    #print(df1)
    return np.random.choice(df1.index, p = df1["percent"])

#pick a random amount between the lower and upper bound of a row picked with pick_random_row
def pick_random_amount(df, row):
    return np.random.uniform(df["bound_low"][row], df["bound_high"][row])



