import mesa
from agent import SchellingAgent
import numpy as np
from utils import get_distance
from math import sqrt
from utils import *
import pandas as pd

def get_segregation(model):
    """
    - The average segregation of the model is the average of the segregation of the agents
    - Calculate agent's segregation is the percentage of neighbors that are like it.
    """
    segregations = []

    for agent in model.schedule.agents:
        like_neighbors = 0
        for neighbor in model.grid.iter_neighbors(agent.pos, moore=True):
            if agent.type == neighbor.type:
                like_neighbors += 1

        if like_neighbors == 0:
            segregations.append(0)
        else:
            segregations.append(like_neighbors / 8)

    return sum(segregations) / len(segregations)

class Schelling(mesa.Model):
    """
    Model class for the Schelling segregation model.
    """

    def __init__(self, width=20, height=20, density=0.8, minority_pc=0.4, k = 30, homophily=3, seed = None, policy = "classical",  follow_policy = 1.0):
        """ """

        self.width = width
        self.height = height
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(width, height, torus=False)
        self.seed = seed

        self.policy = policy
        self.follow_policy = follow_policy
        total_cell  = (self.width * self.height) * self.density
        #self.k = int(total_cell * 0.1) #10% of the cells
        self.k = k

        self.happy = 0
        self.datacollector = mesa.DataCollector(
            model_reporters = {"perc_happy": "perc_happy", "segregation": get_segregation }  
        )


        ### RELEVANCE MATRIX ###
        ### ---------------- ###
        ### ---------------- ###
        #create a relevance matrix. The relevance of a cell is inverse to the distance from the center. 
        self.relevance_matrix = np.zeros((self.width, self.height))
        #self.center = int(self.width/2,self.height/2)
        
        #if width and height are even, then the center is the cell at (width/2, height/2)
        self.center = (int(self.width/2), int(self.height/2))

        
        for i in range(self.width):
            for j in range(self.height):

                if i == self.center[0] and j == self.center[1]:
                     self.relevance_matrix[i][j] = 1

                else: 
                    d = get_distance((i,j), self.center)
                    self.relevance_matrix[i][j] = 1 / (sqrt(d)  )

        #print(self.relevance_matrix)

        ### DF reading ###
        ### ---------------- ###
        ### ---------------- ###

        self.df = pd.read_csv("income_clean.csv")
        self.majority_percentage = (1-self.minority_pc) * 100
        


        ### AGENT PLACING ###
        ### ---------------- ###
        ### ---------------- ###
        id = 0        
        for cell in self.grid.coord_iter():
            x, y = cell[1]
            if self.random.random() < self.density:

                if self.random.random() < self.minority_pc: #minority are the rich
                    agent_type = 1
                    row = pick_random_row(self.df, self.majority_percentage, 100) #pick a row between the LAST MINORITY PCT rows
                    income = pick_random_amount(self.df, row)
                else:
                    agent_type = 0
                    row = pick_random_row(self.df, 0, self.majority_percentage)
                    income = pick_random_amount(self.df, row)


    
                agent_policy = "random"
                if self.random.random() < self.follow_policy:
                    agent_policy = self.policy

                agent = SchellingAgent(id = id, pos = (x, y), model = self, agent_type= agent_type, income = income, agent_policy= agent_policy)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                id += 1

        self.running = True
        #self.datacollector.collect(self)


        self.cell_occupancy_matrix_array = []
        self.cell_occupancy_matrix = calculate_cell_occupancy_matrix(self)
        self.cell_occupancy_matrix_array.append(self.cell_occupancy_matrix)



    def step(self):
        """
        Run one step of the model. If All agents are happy, halt the model.
        """
        #print("step", self.schedule.steps)
        self.happy = 0  # Reset counter of happy agents

        self.schedule.step()


        self.perc_happy = self.happy / self.schedule.get_agent_count()

        self.cell_occupancy_matrix_array.append(calculate_cell_occupancy_matrix(self))


        self.datacollector.collect(self)

        
        if self.happy == self.schedule.get_agent_count():
            self.running = False

        #if self.happy / self.schedule.get_agent_count() >= 0.95:
            #self.running = False