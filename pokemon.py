import pandas as pd
import itertools
from helper import *
from time import perf_counter

def recursive_battle(mon_1, mon_2, moveset_1, moveset_2, max_turns, results_table, verbose):
    battle_iterations = 1000

    if len(moveset_1) >= max_turns:
        return False
    # If all instances in this instance are draws, then instances further up the tree are
    # unneccessary
    all_draws = True
    for i in range(mon_1.moves.shape[0]):
        for j in range(mon_2.moves.shape[0]):
            skip_iteration = False

            moveset_1_private = list(moveset_1)
            moveset_2_private = list(moveset_2)
            moveset_1_private.append(i)
            moveset_2_private.append(j)
            if verbose:
                print(moveset_1_private)
                print(moveset_2_private)
            battles = 0
            draws = 0
            mon_1_wins = 0
            mon_2_wins = 0
            recursed = False
            for k in range(battle_iterations):
                battles += 1
                winner, turns = battle(mon_1, moveset_1_private, mon_2, moveset_2_private, False)
                if winner == 0:
                    draws += 1
                    if recursed == False:
                        skip_iteration = recursive_battle(mon_1, mon_2, list(moveset_1_private), list(moveset_2_private), max_turns, results_table, verbose)
                        recursed = True
                        if skip_iteration:
                            break
                elif winner == 1:
                    mon_1_wins += 1
                elif winner == 2:
                    mon_2_wins += 1
                # If we get through 10 iterations with no winners, just skip out
                # Do NOT skip_iteration, because we want to record the results.
                if battles >= 10 and battles == draws:
                    break
            if skip_iteration == False:
                if verbose == True:
                    print("Iterations Results:")
                    print("Battles: " + str(battles))
                    print(mon_1.name + " wins: " + str(mon_1_wins) + " - " + str(moveset_1_private))
                    print(mon_2.name + " wins: " + str(mon_2_wins) + " - " + str(moveset_2_private))
                    print("Draws: " + str(draws))
                if draws != battle_iterations:
                    all_draws = False
                results_table.append(
                    {
                        "Pokemon_1": mon_1.name,
                        "Pokemon_2": mon_2.name,
                        "Moveset_1": moveset_1_private,
                        "Moveset_2": moveset_2_private,
                        "Wins_1": mon_1_wins,
                        "Wins_2": mon_2_wins,
                        "Draws": draws
                    }
                )
    return all_draws



pokedex = pd.read_csv("pokedex.csv")
pokedex = pokedex.drop(columns=['index', 'german_name', 'japanese_name', 'generation', 'is_sub_legendary', 'is_legendary', 'is_mythical', 'species', 'type_number', 'catch_rate', 'base_friendship', 'base_experience', 'growth_rate', 'egg_type_number', 'egg_type_1', 'egg_type_2', 'percentage_male', 'egg_cycles'])
pokedex = pokedex.loc[:,~pokedex.columns.str.startswith('against_')]

moves = pd.read_csv("movedex.csv")
poke_moves = pd.read_csv("pokemon_moves.csv")
moves = moves.join(poke_moves, lsuffix="movedex", rsuffix="poke_moves")
moves = moves.drop(columns=['movemovedex', 'movepoke_moves'])

#print(moves)

#print(pokedex)

pokemon1 = create_pokemon(pokedex.iloc[0], moves)

pokemon2 = create_pokemon(pokedex.iloc[0], moves)

print(pokemon1.moves)

movepools = itertools.combinations(pokemon1.moves.index, 4)
print(list(movepools))

calculate_damage_for_all_moves(pokemon1, pokemon2, True)

pokemon1_wins = 0
pokemon2_wins = 0
total_turns = 0
iterations = 2

start = perf_counter()

movepool = [1,2,3,4]
pokemon1.moves = pokemon1.moves.iloc[movepool]

results = []
#recursive_battle(pokemon1, pokemon2, [], [], 3, results, False)

result_df = pd.DataFrame(results)

print(result_df)

end = perf_counter()

print("Elapsed time: ", end-start)
#for x in range(iterations):
#    winner, turns = battle(pokemon1, [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], pokemon2, [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], True)
#    total_turns += turns
#    if winner == 1:
#        pokemon1_wins += 1
#    if winner == 2:
#        pokemon2_wins += 1

#print(pokemon1.name + " wins: " + str(pokemon1_wins))
#print(pokemon2.name + " wins: " + str(pokemon2_wins))
#print("Average turns: " + str(total_turns / iterations))