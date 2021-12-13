import math
import numpy as np
import functools
from effects import *
from random import choice
from random import getrandbits
from random import randint
from numpy import floor

# Ordering:
# NOR, FIR, WAT, ELE, GRA, ICE, FIG, POI, GRO, FLY, PSY, BUG, ROC, GHO, DRA, DAR, STE, FAI
elemental_dict = {
    "normal" : [1,1,1,1,1,1,2,1,1,1,1,1,1,0,1,1,1,1],
    "fire" : [1,0.5,2,1,0.5,0.5,1,1,2,1,1,0.5,2,1,1,1,0.5,0.5],
    "water" : [1,0.5,0.5,2,2,0.5,1,1,1,1,1,1,1,1,1,1,0.5,1],
    "electric" : [1,1,1,0.5,1,1,1,1,2,0.5,1,1,1,1,1,1,0.5,1],
    "grass" : [1,2,0.5,0.5,0.5,2,1,2,0.5,2,1,2,1,1,1,1,1,1],
    "ice" : [1,2,1,1,1,0.5,2,1,1,1,1,1,2,1,1,1,2,1],
    "fighting" : [1,1,1,1,1,1,1,1,1,2,2,0.5,0.5,1,1,0.5,1,2],
    "poison" : [1,1,1,1,0.5,1,0.5,0.5,2,1,2,0.5,1,1,1,1,1,0.5],
    "ground" : [1,1,2,0,2,2,1,0.5,1,1,1,1,0.5,1,1,1,1,1],
    "flying" : [1,1,1,2,0.5,2,0.5,1,0,1,1,0.5,2,1,1,1,1,1],
    "psychic" : [1,1,1,1,1,1,0.5,1,1,1,0.5,2,1,2,1,2,1,1],
    "bug" : [1,2,1,1,0.5,1,0.5,1,0.5,2,1,1,2,1,1,1,1,1],
    "rock" : [0.5,0.5,2,1,2,1,2,0.5,2,0.5,1,1,1,1,1,1,2,1],
    "ghost" : [0,1,1,1,1,1,0,0.5,1,1,1,0.5,1,2,1,2,1,1],
    "dragon" : [1,0.5,0.5,0.5,0.5,2,1,1,1,1,1,1,1,1,2,1,1,2],
    "dark" : [1,1,1,1,1,1,2,1,1,1,0,2,1,0.5,1,0.5,1,2],
    "steel" : [0.5,2,1,1,0.5,0.5,2,0,2,0.5,0.5,0.5,0.5,1,0.5,1,0.5,0.5],
    "fairy" : [1,1,1,1,1,1,0.5,2,1,1,1,0.5,1,1,0,0.5,2,1]
}

def calcHP(base, iv, ev):
    stat = 2 * base + iv + math.floor(ev / 4.0)
    stat = stat * 50
    stat = math.floor(0.01 * stat)
    return stat + 60

@functools.lru_cache
def calcStat(base, iv, ev, stage):
    stat = 2 * base + iv + math.floor(ev / 4.0)
    stat = stat * 50
    stat = math.floor(0.01 * stat)
    stat = stat + 5
    if stage == 0:
        return stat
    if stage > 0:
        return math.floor((2.0 + stage) * stat / 2.0)
    if stage < 0:
        return math.floor(2.0 * stat / (2 - stage))

@functools.lru_cache
def calcBaseDamage(power, atk, defense):
    damage = 22 * power * (atk / defense)
    damage = math.floor(damage / 50)
    return damage + 2

@functools.lru_cache
def getAllDamageRolls(totalDamage):
    a = []
    for x in range(85, 101):
        damage = math.floor(totalDamage * x / 100)
        a.append(damage)
    return np.array(a)

def getTypeEffectiveness(atkType, defType1, defType2):
    defArray = elemental_dict[defType1.lower()]
    effectiveness1 = defArray[getIndexOfType(atkType)]
    effectiveness2 = 1.0
    if defType2 != "":
        defArray = elemental_dict[defType2.lower()]
        effectiveness2 = defArray[getIndexOfType(atkType)]
    return effectiveness1 * effectiveness2

def getIndexOfType(type):
    return list(elemental_dict).index(type.lower())

class Pokemon:
    def __init__(self, name, pokedex_num, hp, atk, defense, spatk, spdef, speed, type1, type2):
        self.name = name
        self.pokedex_num = pokedex_num
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.spatk = spatk
        self.spdef = spdef
        self.speed = speed
        self.type1 = type1
        self.type2 = type2

    def __str__(self):
        return self.name + " - [" + self.type1 + "," + self.type2 + "]\r\n" \
               "    BST - HP:" + str(self.hp) +  " ATK:" + str(self.atk) + " DEF:" + str(self.defense) + " SPATK:" + str(self.spatk) + " SPDEF:" + str(self.spdef) + " SPD:" + str(self.speed)

def create_pokemon(pokedex_row, movedex):
    pokemon = Pokemon(pokedex_row['name'], pokedex_row['pokedex_number'], pokedex_row['hp'], pokedex_row['attack'], pokedex_row['defense'], pokedex_row['sp_attack'], pokedex_row['sp_defense'], pokedex_row['speed'], pokedex_row['type_1'], pokedex_row['type_2'])
    pokemon.moves = movedex[movedex['pokemon'] == pokemon.pokedex_num]
    return pokemon

def calculate_damage_for_all_moves(poke1, poke2, verbose):
    for _, move in poke1.moves.iterrows():
        reset_pokemon(poke1)
        reset_pokemon(poke2)
        calculate_damage(poke1, poke2, move, verbose)
        print(poke1.name, ": ", str(poke1.current_hp) + "/" + str(poke1.max_hp))
        print("    " + poke1.status.name) 
        print(poke2.name, ": ", str(poke2.current_hp) + "/" + str(poke2.max_hp))
        print("    " + poke2.status.name) 

def reset_pokemon(poke):
    poke.current_hp = calcHP(poke.hp, 31, 0)
    poke.max_hp = poke.current_hp
    poke.atk_stage = 0
    poke.def_stage = 0
    poke.spatk_stage = 0
    poke.spdef_stage = 0
    poke.speed_stage = 0
    poke.evasion_stage = 0
    poke.status = StatusEnum.NONE
    poke.effects = PokemonEffects.NONE
    poke.charge_move = None
    poke.sleep_counter = 0
    poke.light_screen_turns = 0
    poke.safeguard_turns = 0

    return poke

def battle(poke1, poke1_script, poke2, poke2_script, verbose):
    poke1 = reset_pokemon(poke1)
    poke2 = reset_pokemon(poke2)

    moves_1 = 0
    moves_2 = 0
    while poke1.current_hp > 0 and poke2.current_hp > 0 and moves_1 < len(poke1_script) and moves_2 < len(poke2_script):
        current_speed_1 = calcStat(poke1.speed, 31, 0, poke1.speed_stage)
        current_speed_2 = calcStat(poke2.speed, 31, 0, poke2.speed_stage)

        # Break Speed Tie
        if current_speed_1 == current_speed_2:
            speed_roll = getrandbits(1)
            if speed_roll:
                current_speed_1 = current_speed_1 + 1
            else:
                current_speed_2 = current_speed_2 + 1

        if current_speed_1 > current_speed_2:
            poke1, poke2 = calculate_damage(poke1, poke2, poke1.moves.iloc[poke1_script[moves_1]], verbose)
            if poke1.current_hp <= 0 or poke2.current_hp <= 0:
                break
            poke2, poke1 = calculate_damage(poke2, poke1, poke2.moves.iloc[poke2_script[moves_2]], verbose)
            poke1, poke2 = apply_post_move_effects(poke1, poke2, verbose)
            poke2, poke1 = apply_post_move_effects(poke2, poke1, verbose)
        else:
            poke2, poke1 = calculate_damage(poke2, poke1, poke2.moves.iloc[poke2_script[moves_2]], verbose)
            if poke1.current_hp <= 0 or poke2.current_hp <= 0:
                break
            poke1, poke2 = calculate_damage(poke1, poke2, poke1.moves.iloc[poke1_script[moves_1]], verbose)
            poke2, poke1 = apply_post_move_effects(poke2, poke1, verbose)
            poke1, poke2 = apply_post_move_effects(poke1, poke2, verbose)
        
        if verbose:
            print(poke1.name, ": ", str(poke1.current_hp) + " HP")
            print(poke2.name, ": ", str(poke2.current_hp) + " HP")

        if poke1.effects & PokemonEffects.CHARGE_TURN == False:
            moves_1 += 1
        if poke2.effects & PokemonEffects.CHARGE_TURN == False:
            moves_2 += 1

    winner = 0
    if poke1.current_hp <= 0:
        winner = 2
    elif poke2.current_hp <= 0:
        winner = 1

    return winner, max(moves_1, moves_2)
    
def apply_post_move_effects(poke1, poke2, verbose):
    if poke1.effects & PokemonEffects.LEECH_SEED:
        damage = max(1, floor(poke1.max_hp / 8))
        if damage > poke1.current_hp:
            damage = poke1.curren_hp
        poke1.current_hp -= damage
        poke2.current_hp += damage

        if verbose:
            print(poke1.name + " takes Leech Seed damage! (" + str(damage) + ")")

    if poke1.status == StatusEnum.POISON:
        damage = max(1, floor(poke1.max_hp / 8))
        if damage > poke1.current_hp:
            damage = poke1.curren_hp
        poke1.current_hp -= damage

        if verbose:
            print(poke1.name + " takes Poison damage! (" + str(damage) + ")")

    poke1.light_screen_turns = max(0, poke1.light_screen_turns - 1)
    if poke1.light_screen_turns == 0:
        poke1.effects &= ~PokemonEffects.LIGHT_SCREEN

    poke1.safeguard_turns = max(0, poke1.safeguard_turns - 1)
    if poke1.safeguard_turns == 0:
        poke1.effects &= ~PokemonEffects.SAFEGUARD

    poke1.effects &= ~PokemonEffects.FLINCHED

    return poke1, poke2

def calculate_damage(poke1, poke2, move, verbose):
    stab = 1.5
    category = move['category']
    move_type = move['type']
    already_charged = False

    # Flinch check
    if poke1.effects & PokemonEffects.FLINCHED:
        if verbose:
            print(poke1.name + " flinched!")
        return

    # Sleep check
    if poke1.sleep_counter != 0:
        if verbose:
            print(poke1.name + " is asleep!")
        poke1.sleep_counter -= 1
        if poke1.sleep_counter == 0:
            poke1.status = StatusEnum.NONE
        if move.effect != EffectIndex.SNORE:
            return
    else:
        if move.effect == EffectIndex.SNORE:
            if verbose:
                print(poke1.name + " is not asleep!")
            return

    # Check if previously charged
    if poke1.effects & PokemonEffects.CHARGE_TURN:
        poke1.effects &= ~PokemonEffects.CHARGE_TURN
        move = poke1.charge_move
        poke1.charge_move = None
        already_charged = True

    # Accuracy Roll
    if move['bypass_accuracy'] == False:
        effective_accuracy = move['accuracy']
        if move['category'] != "Status":
            evasion_multiplier = 3
            evasion_divisor = 3
            if poke2.evasion_stage < 0:
                evasion_multiplier = 3 - poke2.evasion_stage
            if poke2.evasion_stage > 0:
                evasion_divisor = 3 + poke2.evasion_stage
            effective_accuracy = effective_accuracy * evasion_multiplier / evasion_divisor
        acc_roll = randint(0, 99)
        if acc_roll > effective_accuracy:
            if verbose:
                print(poke1.name + " missed! (" + str(effective_accuracy) + "%)")
            return

    # Calculate Base Damage
    if category == "Physical":
        totalDamage = calcBaseDamage(move["power"], calcStat(poke1.atk, 31, 0, poke1.atk_stage), calcStat(poke2.defense, 31, 0, poke2.def_stage))
    elif category == "Special":
        totalDamage = calcBaseDamage(move["power"], calcStat(poke1.spatk, 31, 0, poke1.spatk_stage), calcStat(poke2.spdef, 31, 0, poke2.spdef_stage))
    elif category == "Status":
        totalDamage = 0
    else:
        print("ERROR: Bad move category: " + category)

    # Weather

    # Critical

    # Random
    damageRolls = getAllDamageRolls(totalDamage)

    # STAB
    if move_type == poke1.type1 or move_type == poke1.type2:
        damageRolls = floor(damageRolls * stab)

    # Type effectiveness
    damageRolls = floor(damageRolls * getTypeEffectiveness(move_type, poke2.type1, poke2.type2))

    # Burn penalty

    # Apply effects
    effect = move['effect']
    if effect != 0:
        poke1, poke2 = apply_effect(effect, poke1, poke2)

    # Check for charge
    if poke1.effects & PokemonEffects.CHARGE_TURN and already_charged == False:
        poke1.charge_move = move
        if verbose:
            print("Charging!")
    # Calculate final damage
    else:
        poke1.effects &= ~PokemonEffects.CHARGE_TURN
        actual_damage = choice(damageRolls)

        if move['category'] == "Special" and poke2.effects & PokemonEffects.LIGHT_SCREEN:
            actual_damage = floor(actual_damage * 0.5)

        if verbose:
            print(move['name'])
            print(damageRolls)
            print(move['name'] + " does " + str(actual_damage) + " damage!")
        
        poke2.current_hp = poke2.current_hp - actual_damage

        if move['recoil_damage'] != 0:
            poke1.current_hp = poke1.current_hp - floor(actual_damage * move['recoil_damage'])

    return poke1, poke2