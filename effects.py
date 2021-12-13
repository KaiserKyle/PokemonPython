from enum import Enum, Flag, IntEnum, auto
from math import floor
from random import randint

class StatusEnum(Enum):
    NONE = 0
    POISON = 1
    SLEEP = 2

class Stat(Flag):
    ATK = auto()
    SPATK = auto()
    DEF = auto()
    SPDEF = auto()
    SPEED = auto()
    EVASION = auto()

class PokemonEffects(Flag):
    NONE = 0
    LEECH_SEED = auto()
    CHARGE_TURN = auto()
    LIGHT_SCREEN = auto()
    SAFEGUARD = auto()
    FLINCHED = auto()

class EffectIndex(IntEnum):
    NONE = 0
    LOWER_ATK_1 = 1
    RAISE_ATK_SPATK_1 = 2
    LEECH_SEED = 3
    POISON = 4
    SLEEP = 5
    LOWER_EVASION_2 = 6
    SYNTEHSIS = 7
    WORRY_SEED = 8
    SOLAR_BEAM = 9
    LIGHT_SCREEN = 10
    SAFEGUARD = 11
    REST = 12
    SNORE = 13

def apply_stat_stage(pokemon, stats, change):
    if stats & Stat.ATK:
        pokemon.atk_stage = max(-6, min(pokemon.atk_stage + change, 6))
    if stats & Stat.SPATK:
        pokemon.spatk_stage = max(-6, min(pokemon.spatk_stage + change, 6))
    if stats & Stat.DEF:
        pokemon.def_stage = max(-6, min(pokemon.def_stage + change, 6))
    if stats & Stat.SPDEF:
        pokemon.spdef_stage = max(-6, min(pokemon.spdef_stage + change, 6))
    if stats & Stat.SPEED:
        pokemon.speed_stage = max(-6, min(pokemon.speed_stage + change, 6))
    if stats & Stat.EVASION:
        pokemon.evasion_stage = max(-6, min(pokemon.evasion_stage + change, 6))

    return pokemon

def apply_effect(effect_index, acting_pokemon, opp_pokemon):
    if effect_index == EffectIndex.NONE:
        return acting_pokemon, opp_pokemon

    if effect_index == EffectIndex.LOWER_ATK_1:
        # Lower attack of opp_pokemon
        apply_stat_stage(opp_pokemon, Stat.ATK, -1)
    elif effect_index == EffectIndex.RAISE_ATK_SPATK_1:
        # Increase SpAtk and Atk by 1
        apply_stat_stage(acting_pokemon, Stat.ATK | Stat.SPATK, 1)
    elif effect_index == EffectIndex.LEECH_SEED:
        # Leech Seed
        if opp_pokemon.type1 != "Grass" and opp_pokemon.type2 != "Grass":
            opp_pokemon.effects |= PokemonEffects.LEECH_SEED
    elif effect_index == EffectIndex.POISON:
        # Poison
        if opp_pokemon.type1 != "Poison" and opp_pokemon.type2 != "Poison" and \
           opp_pokemon.type1 != "Steel" and opp_pokemon.type2 != "Steel" and \
           opp_pokemon.status == StatusEnum.NONE and (opp_pokemon.effects & PokemonEffects.SAFEGUARD == PokemonEffects.NONE):
            opp_pokemon.status = StatusEnum.POISON
    elif effect_index == EffectIndex.SLEEP:
        # Sleep
        if opp_pokemon.status == StatusEnum.NONE and (opp_pokemon.effects & PokemonEffects.SAFEGUARD == PokemonEffects.NONE):
            opp_pokemon.status = StatusEnum.SLEEP
            opp_pokemon.sleep_counter = randint(1, 3)
    elif effect_index == EffectIndex.LOWER_EVASION_2:
        # Evasion -2
        apply_stat_stage(opp_pokemon, Stat.EVASION, -2)
    elif effect_index == EffectIndex.SYNTEHSIS:
        # Synthesis
        acting_pokemon.current_hp += floor(acting_pokemon.max_hp / 2)
        if acting_pokemon.current_hp > acting_pokemon.max_hp:
            acting_pokemon.current_hp = acting_pokemon.max_hp
    elif effect_index == EffectIndex.WORRY_SEED:
        # Worry Seed
        # Changed opp_pokemon ability to Insomnia.
        # Stub code
        opp_pokemon.current_hp
    elif effect_index == EffectIndex.SOLAR_BEAM:
        # Solar Beam
        # WEATHER CHECK NEEDED
        acting_pokemon.effects |= PokemonEffects.CHARGE_TURN
    elif effect_index == EffectIndex.LIGHT_SCREEN:
        # Light Screen
        acting_pokemon.effects |= PokemonEffects.LIGHT_SCREEN
        acting_pokemon.light_screen_turns = 5
    elif effect_index == EffectIndex.SAFEGUARD:
        # Safeguard
        acting_pokemon.effects |= PokemonEffects.SAFEGUARD
        acting_pokemon.safeguard_turns = 5
    elif effect_index == EffectIndex.REST:
        # Rest
        acting_pokemon.status = StatusEnum.SLEEP
        acting_pokemon.sleep_counter = 2
        acting_pokemon.current_hp += floor(acting_pokemon.max_hp / 2)
        if acting_pokemon.current_hp > acting_pokemon.max_hp:
            acting_pokemon.current_hp = acting_pokemon.max_hp
    elif effect_index == EffectIndex.SNORE:
        # Snore - 30% Flinch
        acc_roll = randint(0, 99)
        if acc_roll < 30:
            opp_pokemon.effects |= PokemonEffects.FLINCHED


    return acting_pokemon, opp_pokemon