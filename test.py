import unittest
import pandas as pd
from effects import PokemonEffects, Stat, StatusEnum, apply_effect, apply_stat_stage

import helper

expected_damage_bulbasaur = {
    0: [16,17,18,19],
    1: [0],
    2: [6, 7],
    3: [0],
    4: [0],
    5: [8, 9],
    6: [0],
    7: [0],
    8: [11, 12, 13],
    9: [34, 35, 36, 37, 38, 39, 40, 41],
    10: [0],
    11: [0],
    12: [0],
    13: [45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
    14: [16, 17, 18, 19, 20],
    15: [8, 9, 10],
    16: [0],
    17: [0],
    18: [0],
    19: [0],
    20: [0]
}

class PokemonTest(unittest.TestCase):
    def setUp(self):
        pokedex = pd.read_csv("pokedex.csv")
        pokedex = pokedex.drop(columns=['index', 'german_name', 'japanese_name', 'generation', 'is_sub_legendary', 'is_legendary', 'is_mythical', 'species', 'type_number', 'catch_rate', 'base_friendship', 'base_experience', 'growth_rate', 'egg_type_number', 'egg_type_1', 'egg_type_2', 'percentage_male', 'egg_cycles'])
        self.pokedex = pokedex.loc[:,~pokedex.columns.str.startswith('against_')]

        moves = pd.read_csv("movedex.csv")
        poke_moves = pd.read_csv("pokemon_moves.csv")
        moves = moves.join(poke_moves, lsuffix="movedex", rsuffix="poke_moves")
        self.moves = moves.drop(columns=['movemovedex'])

        self.pokemon1 = helper.create_pokemon(pokedex.iloc[0], moves)

        self.pokemon2 = helper.create_pokemon(pokedex.iloc[0], moves)

    # def test_priotiry(self):

    def test_stat_stages(self):
        helper.reset_pokemon(self.pokemon1)

        apply_stat_stage(self.pokemon1, Stat.ATK | Stat.SPATK | Stat.SPEED, 7)
        self.assertEqual(self.pokemon1.atk_stage, 6)
        self.assertEqual(self.pokemon1.spatk_stage, 6)
        self.assertEqual(self.pokemon1.speed_stage, 6)

        apply_stat_stage(self.pokemon1, Stat.DEF | Stat.SPDEF | Stat.EVASION, -7)
        self.assertEqual(self.pokemon1.def_stage, -6)
        self.assertEqual(self.pokemon1.spdef_stage, -6)
        self.assertEqual(self.pokemon1.evasion_stage, -6)

    def test_snore(self):
        helper.reset_pokemon(self.pokemon1)
        helper.reset_pokemon(self.pokemon2)

        self.pokemon1.status = StatusEnum.SLEEP
        self.pokemon1.sleep_counter = 3
        helper.calculate_damage(self.pokemon1, self.pokemon2, self.pokemon1.moves.iloc[19], False)
        damage_done = self.pokemon2.max_hp - self.pokemon2.current_hp
        self.assertTrue(damage_done != 0)
    
    def test_protect(self):
        helper.reset_pokemon(self.pokemon1)
        helper.reset_pokemon(self.pokemon2)

        self.assertTrue(self.pokemon1.protect_turns == 0)

        helper.calculate_damage(self.pokemon1, self.pokemon2, self.pokemon1.moves.iloc[20], False)
        helper.calculate_damage(self.pokemon2, self.pokemon1, self.pokemon1.moves.iloc[0], False)
        damage_done = self.pokemon1.max_hp - self.pokemon1.current_hp
        self.assertTrue(damage_done == 0)
        self.assertTrue(self.pokemon1.effects & PokemonEffects.PROTECT)
        self.assertTrue(self.pokemon1.protect_turns == 1)

        helper.apply_post_move_effects(self.pokemon1, self.pokemon2, False)
        helper.calculate_damage(self.pokemon2, self.pokemon1, self.pokemon1.moves.iloc[0], False)
        damage_done = self.pokemon1.max_hp - self.pokemon1.current_hp
        self.assertTrue(damage_done != 0)
        self.assertFalse(self.pokemon1.effects & PokemonEffects.PROTECT)

    def test_move_damage(self):
        for idx, move in self.pokemon1.moves.iterrows():
            for _ in range(100):
                helper.reset_pokemon(self.pokemon1)
                helper.reset_pokemon(self.pokemon2)

                # If bypass accuracy is true, it shouldn't miss no matter what.
                if move['bypass_accuracy'] == True:
                    move['accuracy'] = 0
                else:
                    move['accuracy'] = 100

                helper.calculate_damage(self.pokemon1, self.pokemon2, move, False)
                if self.pokemon1.effects & PokemonEffects.CHARGE_TURN:
                    if move['movepoke_moves'] in [14]:
                        helper.calculate_damage(self.pokemon1, self.pokemon2, move, False)
                    else:
                        self.assertTrue(False, "Charged on non-charging move!")

                damage_done = self.pokemon2.max_hp - self.pokemon2.current_hp
                self.assertTrue(damage_done in expected_damage_bulbasaur[idx], str(idx) + ": " + str(damage_done))

    def test_effects(self):
        helper.reset_pokemon(self.pokemon1)
        helper.reset_pokemon(self.pokemon2)

        apply_effect(1, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon2.atk_stage, -1)

        helper.reset_pokemon(self.pokemon2)

        apply_effect(2, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon1.atk_stage, 1)
        self.assertEqual(self.pokemon1.spatk_stage, 1)

        helper.reset_pokemon(self.pokemon1)

        self.pokemon2.type1 = "Normal"
        self.pokemon2.type2 = "Fire"
        apply_effect(3, self.pokemon1, self.pokemon2)
        self.assertTrue(self.pokemon2.effects & PokemonEffects.LEECH_SEED)
        helper.reset_pokemon(self.pokemon2)
        self.pokemon2.type1 = "Grass"
        apply_effect(3, self.pokemon1, self.pokemon2)
        self.assertFalse(self.pokemon2.effects & PokemonEffects.LEECH_SEED)

        apply_effect(4, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon2.status, StatusEnum.POISON)

        helper.reset_pokemon(self.pokemon2)

        apply_effect(5, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon2.status, StatusEnum.SLEEP)
        self.assertTrue(self.pokemon2.sleep_counter > 0)
        sleep_turns = self.pokemon2.sleep_counter
        for i in range(sleep_turns):
            helper.calculate_damage(self.pokemon2, self.pokemon1, self.pokemon1.moves.iloc[0], False)
            self.assertEqual(self.pokemon2.sleep_counter, sleep_turns - i - 1)
        self.assertEqual(self.pokemon2.status, StatusEnum.NONE)
        self.assertEqual(self.pokemon2.sleep_counter, 0)

        helper.reset_pokemon(self.pokemon2)

        apply_effect(6, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon2.evasion_stage, -2)

        self.pokemon1.max_hp = 100
        self.pokemon1.current_hp = 1
        apply_effect(7, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon1.current_hp, 51)

        helper.reset_pokemon(self.pokemon1)
        helper.reset_pokemon(self.pokemon2)
        apply_effect(10, self.pokemon1, self.pokemon2)
        self.assertTrue(self.pokemon1.effects & PokemonEffects.LIGHT_SCREEN)
        helper.calculate_damage(self.pokemon2, self.pokemon1, self.pokemon1.moves.iloc[15], False)
        damage_done = self.pokemon1.max_hp - self.pokemon1.current_hp
        self.assertTrue(damage_done < 8, str(damage_done))
        for i in range(5):
            self.assertTrue(self.pokemon1.effects & PokemonEffects.LIGHT_SCREEN)
            self.assertTrue(self.pokemon1.light_screen_turns == (5 - i))
            helper.apply_post_move_effects(self.pokemon1, self.pokemon2, False)
        self.assertFalse(self.pokemon1.effects & PokemonEffects.LIGHT_SCREEN)
        self.assertTrue(self.pokemon1.light_screen_turns == 0)

        helper.reset_pokemon(self.pokemon1)
        helper.reset_pokemon(self.pokemon2)
        apply_effect(11, self.pokemon1, self.pokemon2)
        self.assertTrue(self.pokemon1.effects & PokemonEffects.SAFEGUARD)
        apply_effect(5, self.pokemon2, self.pokemon1)
        self.assertTrue(self.pokemon2.status == StatusEnum.NONE)
        for i in range(5):
            self.assertTrue(self.pokemon1.effects & PokemonEffects.SAFEGUARD)
            self.assertTrue(self.pokemon1.safeguard_turns == (5 - i))
            helper.apply_post_move_effects(self.pokemon1, self.pokemon2, False)
        self.assertFalse(self.pokemon1.effects & PokemonEffects.SAFEGUARD)
        self.assertTrue(self.pokemon1.safeguard_turns == 0)
            
        helper.reset_pokemon(self.pokemon1)

        self.pokemon1.current_hp = 1
        self.pokemon1.max_hp = 100
        apply_effect(12, self.pokemon1, self.pokemon2)
        self.assertEqual(self.pokemon1.status, StatusEnum.SLEEP)
        self.assertTrue(self.pokemon1.sleep_counter == 2)
        self.assertTrue(self.pokemon1.current_hp == 51)
        for i in range(2):
            helper.calculate_damage(self.pokemon1, self.pokemon2, self.pokemon1.moves.iloc[0], False)
            self.assertEqual(self.pokemon1.sleep_counter, 2 - i - 1)
        self.assertEqual(self.pokemon1.status, StatusEnum.NONE)
        self.assertEqual(self.pokemon1.sleep_counter, 0)

        for i in range(100):
            apply_effect(13, self.pokemon1, self.pokemon2)
        self.assertTrue(self.pokemon2.effects & PokemonEffects.FLINCHED)



if __name__ == '__main__':
    unittest.main()