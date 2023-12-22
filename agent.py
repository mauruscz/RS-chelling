import mesa
from utils import *




def pick_a_cell_according_to_policy(agent,model):
    """
    This function is used to pick a cell according to the policy
    :param model: the model
    :return: the cell
    """
    pos = agent.pos
    empties = [cell[1] for cell in model.grid.coord_iter() if model.grid.is_cell_empty(cell[1])]


    if agent.policy == None:
        # pick a random empty cell
        return model.random.choice(empties)

    if agent.policy == "distance": # TODO can be pre-calculated with a global distance matrix
        empties2distances = {cell: get_distance(pos, cell) for cell in empties}
        sorted_empties2distances = sorted(empties2distances, key = lambda x: empties2distances[x], reverse = False)
        k_sorted_empties2distances = sorted_empties2distances[:model.k]

        #the probability of choosing a cell is inversely proportional to its distance from the agent
        #return model.random.choices(k_sorted_empties2distances,      weights = [1/empties2distances[cell] for cell in k_sorted_empties2distances]     )[0]

        #pick one of the k closest cells
        return model.random.choice(k_sorted_empties2distances)
    
    if agent.policy == "relevance": 
        empties2relevances = {cell: model.relevance_matrix[cell[0]][cell[1]] for cell in empties}
        sorted_empties2relevances = sorted(empties2relevances, key = lambda x: empties2relevances[x], reverse = True)
        k_sorted_empties2relevances = sorted_empties2relevances[:model.k]


        #the probability of choosing a cell is proportional to its distance from the agent
        #return model.random.choices(k_sorted_empties2relevances,      weights = [empties2relevances[cell] for cell in k_sorted_empties2relevances]     )[0]

        #pick one of the k most relevant cells
        return model.random.choice(k_sorted_empties2relevances)
    
    if agent.policy == "distance_relevance":
        empties2distances = {cell: get_distance(pos, cell) for cell in empties}
        empties2relevances = {cell: model.relevance_matrix[cell[0]][cell[1]] for cell in empties}
        empties2distances_relevances = {cell: empties2distances[cell] * empties2relevances[cell] for cell in empties}
        sorted_empties2distances_relevances = sorted(empties2distances_relevances, key = lambda x: empties2distances_relevances[x], reverse = False)
        k_sorted_empties2distances_relevances = sorted_empties2distances_relevances[:model.k]


        #pick one of the k closest cells
        return model.random.choice(k_sorted_empties2distances_relevances)
    
    if agent.policy == "rich_neighborhood":
        empties2richness = {cell: calculate_neighborhood_richness(model, cell) for cell in empties}
        sorted_empties2richness = sorted(empties2richness, key = lambda x: empties2richness[x], reverse = True)
        k_sorted_empties2richness = sorted_empties2richness[:model.k]


        return model.random.choice(k_sorted_empties2richness)
    
    if agent.policy == "poor_neighborhood":
        empties2richness = {cell: calculate_neighborhood_richness(model, cell) for cell in empties}
        sorted_empties2richness = sorted(empties2richness, key = lambda x: empties2richness[x], reverse = False)
        k_sorted_empties2richness = sorted_empties2richness[:model.k]


        return model.random.choice(k_sorted_empties2richness)
    
    if agent.policy == "minimum_improvement":
        empties2alike_neighbors = {cell: calculate_alike_destination(model, agent, cell) for cell in empties}  #now in empties2alike_neighbors we have the number of alike neighbors for each empty cell

        sorted_empties2alike_neighbors = sorted(empties2alike_neighbors, key = lambda x: empties2alike_neighbors[x], reverse = False)

        #in sorted_empties2alike_neighbors pick the cells that have at least model.homophily alike neighbors
        sorted_empties2alike_neighbors = [cell for cell in sorted_empties2alike_neighbors if empties2alike_neighbors[cell] >= model.homophily]


        k_sorted_empties2alike_neighbors = sorted_empties2alike_neighbors[:model.k]

        #if none of the k cells have more than model.homophily alike neighbors, then return (-1, -1)
        # i.e. if the agent would not be happy in any of the k cells, then return (-1, -1)
        #else, pick one at random in k_sorted_empties2alike_neighbors

        eligible_cells = [cell for cell in k_sorted_empties2alike_neighbors if empties2alike_neighbors[cell] >= model.homophily]
        if len(eligible_cells) == 0:
            return (-1, -1)
        
        else:
            return model.random.choice(eligible_cells)

    
    if agent.policy == "maximum_improvement":
        empties2alike_neighbors = {cell: calculate_alike_destination(model, agent, cell) for cell in empties}

        sorted_empties2alike_neighbors = sorted(empties2alike_neighbors, key = lambda x: empties2alike_neighbors[x], reverse = True)


        #in sorted_empties2alike_neighbors pick the cells that have at least model.homophily alike neighbors
        sorted_empties2alike_neighbors = [cell for cell in sorted_empties2alike_neighbors if empties2alike_neighbors[cell] >= model.homophily]


        k_sorted_empties2alike_neighbors = sorted_empties2alike_neighbors[:model.k]

        #if none of the k cells have more than model.homophily alike neighbors, then return (-1, -1)
        # i.e. if the agent would not be happy in any of the k cells, then return (-1, -1)
        #else, pick one at random in k_sorted_empties2alike_neighbors

        eligible_cells = [cell for cell in k_sorted_empties2alike_neighbors if empties2alike_neighbors[cell] >= model.homophily]

        if not eligible_cells:
            return (-1, -1)
        else:
            return model.random.choice(eligible_cells)
        

    if agent.policy == "recently_empty":
        empties2emptiness_time = {cell: calculate_cell_emptiness_time(model, cell) for cell in empties}
        sorted_empties2emptiness_time = sorted(empties2emptiness_time, key = lambda x: empties2emptiness_time[x], reverse = False)
        k_sorted_empties2emptiness_time = sorted_empties2emptiness_time[:model.k]

        return model.random.choice(k_sorted_empties2emptiness_time)

    if agent.policy == "recently_occupied":
        empties2emptiness_time = {cell: calculate_cell_emptiness_time(model, cell) for cell in empties}
        sorted_empties2emptiness_time = sorted(empties2emptiness_time, key = lambda x: empties2emptiness_time[x], reverse = True)
        k_sorted_empties2emptiness_time = sorted_empties2emptiness_time[:model.k]

        return model.random.choice(k_sorted_empties2emptiness_time)

    return (-1, -1)





class SchellingAgent(mesa.Agent):
    """
    Schelling segregation agent
    """

    def __init__(self, id, pos, model, agent_type, income, agent_policy):
        super().__init__(id, model)
        self.pos = pos
        self.type = agent_type
        self.policy = agent_policy
        self.income = income

    def step(self):
        similar = sum(1 for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True) if neighbor.type == self.type)

        # If unhappy, move:
        if similar < self.model.homophily:
            cell = pick_a_cell_according_to_policy(self, self.model)
            if cell != (-1, -1):
                self.model.grid.move_agent(self, cell)
        else:
            self.model.happy += 1