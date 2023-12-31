import pandas as pd
import time
import numpy as np
import math
START=time.time()

file1="state_weights.txt"
file2="state_observation_weights.txt"
file3="state_action_state_weights.txt"
file4="observation_actions.txt"

def unique_state(file_path):
  data = {"state": [], "weight": []}

  with open(file_path, "r") as file:
      lines = file.read().splitlines()

  filename = lines[0].strip()
  filename = lines[0].strip()
  default_weight=0
  num_states=int(lines[1].split()[0])


  for line in lines[2:]:
      components = line.split()
      state = components[0].strip('"')
      weight = int(components[1])
      data["state"].append(state)
      data["weight"].append(int(weight))

  df = pd.DataFrame(data)
  unique_states=df['state'].unique()

  return unique_states

UNIQUE_STATES=unique_state(file1)

def unique_observations(file_path1,file_path2):

    #state_observation
    data = []

    with open(file_path1, "r") as file:
        lines = file.read().splitlines()

    filename = lines[0].strip()
    num_pairs, num_states, num_observations, default_weight = map(int, lines[1].split())

    for line in lines[2:]:
        components = line.split()
        components[0] = components[0].strip('"')
        components[1] = components[1].strip('"')
        components[2] = int(components[2])
        data.append(components)

    df = pd.DataFrame(data, columns=["ColumnA", "ColumnB", "ColumnC"])
    unique_obs1=list(df['ColumnB'])

    with open(file_path2, 'r') as file:
        lines = file.readlines()

        filename=lines[0].strip()
        num_observations = int(lines[1].strip())

        observation_sequence = []

        for line in lines[2:]:
            parts = line.split()
            if len(parts) == 2:
                observation_sequence.append(parts[0].strip('"'))
            else:
                observation_sequence.append(parts[0].strip('"'))

    df = pd.DataFrame(observation_sequence, columns=["ColumnA"])
    unique_obs2=list(df['ColumnA'].unique())


    unique_obs=unique_obs1+unique_obs2
    df = pd.DataFrame(unique_obs, columns=["ColumnA"])
    unique_obs3=list(df['ColumnA'].unique())

    return unique_obs3

UNIQUE_OBS=unique_observations(file2,file4)

def initial_state_probability(file_path):
    data = {"state": [], "weight": []}

    with open(file_path, "r") as file:
        lines = file.read().splitlines()

    filename = lines[0].strip()
    filename = lines[0].strip()
    default_weight=0
    num_states=int(lines[1].split()[0])


    for line in lines[2:]:
        components = line.split()
        state = components[0].strip('"')
        weight = int(components[1])
        data["state"].append(state)
        data["weight"].append(int(weight))

    df = pd.DataFrame(data)
    unique_states=df['state'].unique()
    total_weight = df['weight'].sum()

    # Probability
    df['probability'] = df['weight'] / total_weight

    df = df.drop(columns=['weight'])
    max_row = df[df["probability"] == df["probability"].max()]

    # Extract the ID with the maximum probability
    max_id = max_row["state"].values[0]

    # To dictionary
    initial_state_probabilities = df.set_index('state')['probability'].to_dict()
    sorted_dict = {key: initial_state_probabilities[key] for key in sorted(initial_state_probabilities)}
    return sorted_dict

'''
# Debugging
file_path = r"/content/state_weights.txt"
initial_state_probabilities = initial_state_probability(file_path)
print(initial_state_probabilities)
'''

def conditional_probabilities(filename,UNIQUE_STATES,UNIQUE_OBS):
    def process_data1(df, default_weight):
        # Get unique values in ColumnA and ColumnB
        unique_values_A = UNIQUE_STATES
        unique_values_B = UNIQUE_OBS

        # Create a DataFrame with all possible combinations
        combinations = pd.MultiIndex.from_product([unique_values_A, unique_values_B], names=['ColumnA', 'ColumnB'])
        all_combinations_df = pd.DataFrame({'ColumnC': default_weight}, index=combinations).reset_index()

        # Merge the existing DataFrame with the new combinations, filling missing values with default_weight
        df = all_combinations_df.merge(df, on=['ColumnA', 'ColumnB'], how='left').fillna(default_weight)

        # Rename ColumnC_y to ColumnC
        df = df.rename(columns={'ColumnC_y': 'ColumnC'})

        # Drop the original ColumnC
        df = df.drop('ColumnC_x', axis=1)

        return df

    data = []

    with open(filename, "r") as file:
        lines = file.read().splitlines()

    filename = lines[0].strip()
    num_pairs, num_states, num_observations, default_weight = map(int, lines[1].split())

    for line in lines[2:]:
        components = line.split()
        components[0] = components[0].strip('"')
        components[1] = components[1].strip('"')
        components[2] = int(components[2])
        data.append(components)

    df = pd.DataFrame(data, columns=["ColumnA", "ColumnB", "ColumnC"])

    # Call the process_data function
    df = process_data1(df, default_weight)

    # conditional probability table
    conditional_prob_table = pd.pivot_table(df, index="ColumnA", columns="ColumnB", values="ColumnC", aggfunc="sum")
    # conditional probabilities
    conditional_prob_table = conditional_prob_table.div(conditional_prob_table.sum(axis=1), axis=0)

    # To dictionary
    observation_probabilities = {}
    for index, row in conditional_prob_table.iterrows():
        observation_probabilities[index] = row.to_dict()

    sorted_dict = {key: dict(sorted(value.items())) for key, value in sorted(observation_probabilities.items())}

    return sorted_dict

'''
# Debugging
filename = r"/content/state_observation_weights.txt"
result_combined = conditional_probabilities(filename,UNIQUE_STATES,UNIQUE_OBS)
print(result_combined)
'''

def process_data(filename):
    existing_combinations = set()
    final_set = set()

    with open(filename, 'r') as file:

        lines = file.readlines()

        filename = lines[0].strip()
        num_triple, num_states, num_actions, default_weight = map(int, lines[1].split())

        for line in lines[2:]:
            components = line.strip().split()
            if len(components) == 4:
                state, action, next_state, weight = components
                state = state.strip('"')
                action = action.strip('"')
                next_state = next_state.strip('"')
                weight = int(weight)
                existing_combinations.add((state, action, next_state))
                final_set.add((state, action, next_state, weight))

    states = set(state for state in UNIQUE_STATES)
    actions = set(action for _, action, _ in existing_combinations)

    missing_tuples = [
        (state, action, next_state, default_weight)
        for state in states
        for action in actions
        for next_state in states
        if (state, action, next_state) not in existing_combinations
    ]

    data = list(final_set) + missing_tuples

    df = pd.DataFrame(data, columns=["State", "Action", "Next State", "Weight"])

    df['Total Weight'] = df.groupby(['State', 'Action'])['Weight'].transform('sum')

    # conditional probability
    df['Probability'] = df['Weight'] / df['Total Weight']

    # Pivoting the table
    pivot_table = df.pivot_table(index=['State', 'Action'], columns='Next State', values='Probability')#, fill_value=0)

    #print(pivot_table)
    pivot_table = pivot_table.div(pivot_table.sum(axis=1), axis=0)
    pivot_table.reset_index(inplace=True)

    # To dictionary
    state_transition_probabilities = {}
    for state, action in zip(pivot_table['State'], pivot_table['Action']):
        if state not in state_transition_probabilities:
            state_transition_probabilities[state] = {}
        state_transition_probabilities[state][action] = pivot_table.loc[(pivot_table['State'] == state) & (pivot_table['Action'] == action)].values.tolist()[0][2:]

    d=state_transition_probabilities
    sorted_outer_keys = sorted(d.keys())

    # sort the inner keys
    for key in d:
        d[key] = dict(sorted(d[key].items()))

    # sort the outer keys
    state_transition_probabilities = dict(sorted(d.items()))

    return state_transition_probabilities

'''
file_path = r"/content/state_action_state_weights.txt"
resulting_data = process_data(file_path)

print(resulting_data)
'''

def observation_action(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

        filename=lines[0].strip()
        num_observations = int(lines[1].strip())

        observation_sequence = []
        action_sequence = []

        for line in lines[2:]:
            parts = line.split()
            if len(parts) == 2:
                observation_sequence.append(parts[0].strip('"'))
                action_sequence.append(parts[1].strip('"'))
            else:
                observation_sequence.append(parts[0].strip('"'))

        return observation_sequence, action_sequence

'''
# Debugging
file_path = r"/content/observation_actions.txt"

# Call the function and process the file
observation_sequence, action_sequence = observation_action(file_path)

print(f"observation_sequence = {observation_sequence}")
print(f"action_sequence = {action_sequence}")
'''

initial_state_probabilities=initial_state_probability(file1)
observation_probabilities=conditional_probabilities(file2,UNIQUE_STATES,UNIQUE_OBS)
state_transition_probabilities=process_data(file3)
observation_sequence,action_sequence=observation_action(file4)


def viterbi(initial_state_probabilities, observation_probabilities, state_transition_probabilities, observation_sequence, action_sequence):
    states = list(initial_state_probabilities.keys())
    T = len(observation_sequence)
    N = len(states)
    delta = [[0 for j in range(N)] for i in range(T)]
    psi = [[0 for j in range(N)] for i in range(T)]
    q_star = [0 for i in range(T)]

    # Initialization
    for i in range(N):
        delta[0][i] = initial_state_probabilities[states[i]] * observation_probabilities[states[i]][observation_sequence[0]]
        psi[0][i] = 0

    # Recursion
    for t in range(1, T):
        for j in range(N):
            max_delta = 0
            max_psi = 0
            for i in range(N):
                temp_delta = delta[t-1][i] * state_transition_probabilities[states[i]][action_sequence[t-1]][j] * observation_probabilities[states[j]][observation_sequence[t]]
                if temp_delta > max_delta:
                    max_delta = temp_delta
                    max_psi = i
            delta[t][j] = max_delta
            psi[t][j] = max_psi

    print(delta[-1][0:5])
    # Termination
    q_star[T-1] = delta[T-1].index(max(delta[T-1]))
    print(max(delta[T-1]))

    # Path backtracking
    for t in range(T-2, -1, -1):
        q_star[t] = psi[t+1][q_star[t+1]]

    return [states[i] for i in q_star]


out =viterbi(initial_state_probabilities, observation_probabilities, state_transition_probabilities, observation_sequence, action_sequence)

def write_to_file(input_list, output_file_name):

    modified_list = ['"' + str(item) + '"' for item in input_list]

    with open(output_file_name, "w") as file:
        file.write("states\n")
        file.write(str(len(modified_list))+"\n")
        for item in modified_list:
            file.write(item + '\n')

write_to_file(out, "states.txt")
END=time.time()
print(END-START)
print(out)
