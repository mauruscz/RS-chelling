import matplotlib.pyplot as plt
import pandas as pd
from utils import *
from mesa import batch_run
import numpy as np
from model import Schelling

plt.rcParams['figure.figsize'] = [16, 9]
np.set_printoptions(linewidth=400)
#ignore the pandas setting warning
pd.options.mode.chained_assignment = None  # default='warn'


fixed_params = {
    'width': 50,
    'height': 50,
    'density': 0.70,
    'minority_pc': 0.4,
    'homophily': 2,
    'seed': 3110,
}


policies = ["random", "distance", "relevance", "rich_neighborhood", "poor_neighborhood", "minimum_improvement", "maximum_improvement", "recently_emptied", "empty_surrounded" ]

percentages = [i / 10 for i in range(1,11)]
variable_parms = {"policy": policies, "follow_policy": percentages}
merged_params = {**fixed_params, **variable_parms}


results = batch_run(
    Schelling,
    parameters = merged_params,
    iterations=100,
    max_steps=100,
    number_processes = None
);

results_df = pd.DataFrame(results)
results_df = results_df[["RunId", "iteration", "Step", "follow_policy", "policy",  "segregation"]]


#in results_df_g_std, calculate both the standard deviation and the mean of Step and segregation, across different iteration and policy
results_df_g_std = results_df.groupby(['policy', 'follow_policy']).agg({'Step': ['std', 'mean'], 'segregation': ['std', 'mean']}).reset_index()
results_df_g_std.columns = results_df_g_std.columns.droplevel(0)
results_df_g_std.columns = ['policy', 'follow_policy', 'Step_std', 'Step_mean', 'segregation_std', 'segregation_mean']

#pivot the table, so that we have the standard deviation and the mean of Step and segregation, per each policy
results_df_g_std_step = results_df_g_std.pivot(index='follow_policy', columns='policy', values='Step_std')
results_df_g_std_segregation = results_df_g_std.pivot(index='follow_policy', columns='policy', values='segregation_std')

results_df_g_mean_step = results_df_g_std.pivot(index='follow_policy', columns='policy', values='Step_mean')
results_df_g_mean_segregation = results_df_g_std.pivot(index='follow_policy', columns='policy', values='segregation_mean')





####### PLOT #######
####################
####################

#join all the columns of the dataframe, so that we have the standard deviation and the mean of Step and segregation, per each policy, with different colors
for column in results_df_g_std_step.columns:
    plt.errorbar(results_df_g_mean_step.index, results_df_g_mean_step[column], yerr=results_df_g_std_step[column], label=column)

plt.xlabel("Follow Policy (%)", fontsize=18)
plt.ylabel("nr. steps", fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.legend(loc='upper left')
#save the plot and close it
plt.savefig("steps.pdf")
plt.close()    

for column in results_df_g_std_segregation.columns:
    plt.errorbar(results_df_g_mean_segregation.index, results_df_g_mean_segregation[column], yerr=results_df_g_std_segregation[column], label=column)

plt.xlabel("Follow Policy (%)", fontsize=18)
plt.ylabel("segregation", fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.legend(loc='upper left')
#save the plot and close it
plt.savefig("segregation.pdf")
plt.close()
