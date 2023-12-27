import matplotlib.pyplot as plt
import pandas as pd
from utils import *
from mesa import batch_run
from model import Schelling



fixed_params = {
    'width': 50,
    'height': 50,
    'density': 0.75,
    'minority_pc': 0.4,
    'homophily': 3,
}

#policies = ["random", "distance", "relevance", "distance_relevance", "rich_neighborhood", "poor_neighborhood", "minimum_improvement", "maximum_improvement", "recently_emptied", "historically_emptied" ]

policies = ["random", "distance_relevance", "rich_neighborhood", 
            "minimum_improvement", "maximum_improvement", "recently_emptied", 
            "similar_neighborhood", "different_neighborhood" ]

percentages = [i / 10 for i in range(0,11)]

variable_parms = {"policy": policies, "follow_policy": percentages}

merged_params = {**fixed_params, **variable_parms}
merged_params 
pd.options.mode.chained_assignment = None

results = batch_run(
    Schelling,
    parameters = merged_params,
    iterations=100,
    max_steps=100,
    number_processes = None
);

results_df = pd.DataFrame(results)

results_df.to_csv("results.csv", index=False)
