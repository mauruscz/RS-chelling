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
    
    selected_cell = (-1, -1)

    if agent.policy not in ["random", "distance", "relevance", "distance_relevance", "rich_neighborhood", "poor_neighborhood", "minimum_improvement", "maximum_improvement", "recently_emptied", "historically_emptied", "empty_surrounded"]:
        raise Exception("Policy not recognized")

    if agent.policy == "random":
        # pick a random empty cell
        selected_cell =  model.random.choice(empties)

    if agent.policy == "distance": 
        empties2distances = {cell: 1/(get_distance(pos, cell)**2) for cell in empties}

        selected_cell = model.random.choices(list(empties2distances.keys()), weights=empties2distances.values())[0]


    
    if agent.policy == "relevance": 
        empties2relevances = {cell: (model.relevance_matrix[cell[0]][cell[1]])**2 for cell in empties}
        
        selected_cell = model.random.choices(list(empties2relevances.keys()), weights=empties2relevances.values())[0]

    
    if agent.policy == "distance_relevance":
        empties2distances = {cell: 1/(get_distance(pos, cell)**2) for cell in empties}
        empties2relevances = {cell: (model.relevance_matrix[cell[0]][cell[1]])**2 for cell in empties}
        empties2distances_relevances = {cell: empties2distances[cell] * empties2relevances[cell] for cell in empties}
        
        selected_cell = model.random.choices(list(empties2distances_relevances.keys()), weights=empties2distances_relevances.values())[0]


    if agent.policy == "rich_neighborhood":
        empties2richness = {cell: calculate_neighborhood_richness(model, cell) for cell in empties}
        
        selected_cell = model.random.choices(list(empties2richness.keys()), weights=empties2richness.values())[0]



    if agent.policy == "poor_neighborhood":
        empties2richness_inv = {cell: 1/(calculate_neighborhood_richness(model, cell)) for cell in empties}
        
        selected_cell = model.random.choices(list(empties2richness_inv.keys()), weights=empties2richness_inv.values())[0]
    
    
    if agent.policy == "minimum_improvement":
        empties2alike_neighbors = {cell: calculate_alike_destination(model, agent, cell) for cell in empties}
        #filter out the keys with value <= 0 (no neighbors of the same type) or <model.homophily (no improvement)
        empties2alike_neighbors_filtered = {cell: 1/(empties2alike_neighbors[cell]) 
                                            for cell in empties 
                                                if empties2alike_neighbors[cell] >= model.homophily} #now in empties2alike_neighbors_filtered we have the number of alike neighbors for each empty cell that have at least model.homophily alike neighbors

        selected_cell = model.random.choices(list(empties2alike_neighbors_filtered.keys()), weights=empties2alike_neighbors_filtered.values())[0]


    if agent.policy == "maximum_improvement":
        empties2alike_neighbors = {cell: calculate_alike_destination(model, agent, cell) for cell in empties}
        empties2alike_neighbors_filtered = {cell: empties2alike_neighbors[cell] 
                                            for cell in empties 
                                                if empties2alike_neighbors[cell] >= model.homophily} #now in empties2alike_neighbors_filtered we have the number of alike neighbors for each empty cell that have at least model.homophily alike neighbors

        selected_cell = model.random.choices(list(empties2alike_neighbors_filtered.keys()), weights=empties2alike_neighbors_filtered.values())[0]
        

    if agent.policy == "recently_emptied":
        empties2emptiness_time = {cell: 1/calculate_cell_emptiness_time(model, cell) for cell in empties }

        selected_cell = model.random.choices(list(empties2emptiness_time.keys()), weights=empties2emptiness_time.values())[0]

    if agent.policy == "historically_emptied":
        empties2emptiness_time = {cell: calculate_cell_emptiness_time(model, cell) for cell in empties}
      
        selected_cell = model.random.choices(list(empties2emptiness_time.keys()), weights=empties2emptiness_time.values())[0]

    if agent.policy == "empty_surrounded":
        empties2empties = {cell: calculate_empty_surrounded(model, cell) for cell in empties}

        selected_cell = model.random.choices(list(empties2empties.keys()), weights=empties2empties.values())[0]






    return selected_cell





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
            selected_cell = pick_a_cell_according_to_policy(self, self.model)
            if selected_cell != (-1, -1):
                self.model.grid.move_agent(self, selected_cell)
        else:
            self.model.happy += 1