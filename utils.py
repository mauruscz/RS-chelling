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
    - Return a matrix of the same size as the grid, where each cell contains the list of agents that occupy that cell
    """

    cell_occupancy_matrix = [[[] for _ in range(model.height)] for _ in range(model.width)]
    
    for agent in model.schedule.agents:
        cell_occupancy_matrix[agent.pos[0]][agent.pos[1]].append(agent.type)

    return cell_occupancy_matrix

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
        richness = 2000
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

def calculate_cell_emptiness_time(model, empty_cell):
    """
    - Calculate the time that the empty_cell has been empty. 
    Do it using the model.cell_occupancy_matrix_array that contains, per each step, the list of agents in each cell of the grid.
    """
    empty_time = 0

    #iterate reveresly over the matrices in model.cell_occupancy_matrix_array
    for i in range(len(model.cell_occupancy_matrix_array)-1, -1, -1):
        if len(model.cell_occupancy_matrix_array[i][empty_cell[0]][empty_cell[1]]) == 0:
            empty_time += 1
        else:
            break
        
    return empty_time



#pick a random row with a probability equal to the percent column
def pick_random_row(df, percent_cumul_limit_low = 0, percent_cumul_limit_high = 100):

    df1 = df[(df["percent_cumul"] >= percent_cumul_limit_low) & (df["percent_cumul"] <= percent_cumul_limit_high)]

    #df1["percent"] now not sums to 100. make it so in df1
    df1["percent"] = df1["percent"]/(df1["percent"].sum())

    #print(df1)
    return np.random.choice(df1.index, p = df1["percent"])

#pick a random amount between the lower and upper bound of a row picked with pick_random_row
def pick_random_amount(df, row):
    return np.random.uniform(df["bound_low"][row], df["bound_high"][row])

