import gamelib
import random
import math
import warnings
from sys import maxsize
import json

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, BITS, CORES
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        BITS = 1
        CORES = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  # Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    def choose_attack(self, game_state):
        primary_l = [[0, 14], [1, 14], [2, 14], [3, 14]]
        filters_in_primary_l = []
        secondary_l = [[1, 15], [2, 15], [3, 15], [2, 16], [3, 16], [3, 17]]
        filters_in_secondary_l = []
        in_attack_range_l = game_state.get_attackers([2, 13], 0)
        for x in primary_l:
            unit = game_state.contains_stationary_unit(x)
            if unit and unit.unit_type == FILTER:
                filters_in_primary_l.append(game_state.contains_stationary_unit(x))
        for y in secondary_l:
            if game_state.contains_stationary_unit(y):
                filters_in_secondary_l.append(game_state.contains_stationary_unit(x))

        primary_r = [[0, 14], [1, 14], [2, 14], [3, 14]]
        filters_in_primary_r = []
        secondary_r = [[1, 15], [2, 15], [3, 15], [2, 16], [3, 16], [3, 17]]
        filters_in_secondary_r = []
        in_attack_range_r = game_state.get_attackers([2, 13], 0)
        for x in primary_r:
            unit = game_state.contains_stationary_unit(x)
            if unit and unit.unit_type == FILTER:
                filters_in_primary_r.append(game_state.contains_stationary_unit(x))

        for y in secondary_r:
            if game_state.contains_stationary_unit(y):
                filters_in_secondary_r.append(game_state.contains_stationary_unit(y))

        left_side = []
        for x in range(14):
            for y in range(14, 28):
                if x >= y - 14:
                    left_side.append([x, y + 14])
        right_side = []
        for x in range(14, 28):
            for y in range(14, 28):
                if x < y + 14:
                    right_side.append([x, y + 14])

        filters_left_side = []
        filters_right_side = []
        destructors_left_side = []
        destructors_right_side = []
        for x in left_side:
            unit = game_state.contains_stationary_unit(x)
            if unit and unit.unit_type == FILTER:
                filters_left_side.append(game_state.contains_stationary_unit(x))
            elif unit and unit.unit_type == DESTRUCTOR:
                destructors_left_side.append(game_state.contains_stationary_unit(x))
            else:
                pass
        for x in right_side:
            unit = game_state.contains_stationary_unit(x)
            if unit and unit.unit_type == FILTER:
                filters_right_side.append(game_state.contains_stationary_unit(x))
            elif unit and unit.unit_type == DESTRUCTOR:
                destructors_right_side.append(game_state.contains_stationary_unit(x))
            else:
                pass

        right_value = len(filters_right_side) + 3 * len(destructors_right_side)
        left_value = len(filters_left_side) + 3 * len(destructors_left_side)
        left = len(filters_in_primary_l) + len(filters_in_secondary_l) + 3 * len(in_attack_range_l)
        right = len(filters_in_primary_r) + len(filters_in_secondary_r) + 3 * len(in_attack_range_r)
        if left >= 15 and right >= 15:
            if left_value <= right_value:
                return 2
            else:
                return 3
        if left <= right:
            return 0
        else:
            return 1

    def choose_corner(self, game_state, left):
        filter_locations = []
        if left:
            filter_locations = [[4, 12], [3, 13], [23, 11], [24, 11]]
        else:
            filter_locations = [[23, 12], [24, 13], [3, 11], [4, 11]]
        game_state.attempt_spawn(FILTER, filter_locations)
        game_state.attempt_remove(filter_locations)

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        bits = game_state.number_affordable(PING)
        if bits >= 16:
            attack_choice = self.choose_attack(game_state)
            ping_location = []
            emp_location = []
            if attack_choice == 0:
                ping_location = [20, 6]
                emp_location = [21, 7]
                self.choose_corner(game_state, attack_choice == 0)
            elif attack_choice == 1:
                ping_location = [7, 6]
                emp_location = [6, 7]
                self.choose_corner(game_state, attack_choice == 0)
            elif attack_choice == 2:
                ping_location = [7, 6]
                emp_location = [6, 7]
            else:
                ping_location = [20, 6]
                emp_location = [21, 7]
                
            game_state.attempt_spawn(PING, ping_location, 7)
            game_state.attempt_spawn(EMP, emp_location, 3)
        else:
            pass

        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        # self.build_reactive_defense(game_state)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place destructors that attack enemy units
        destructor_locations = [[5, 10], [22, 10]]
        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(DESTRUCTOR, destructor_locations)

        # Place filters in front of destructors to soak up damage for them
        upgraded_filter_locations = [[0, 13], [1, 13], [26, 13], [27, 13], [1, 12], [26, 12], [2, 11], [5, 11], [6, 11],
                                     [21, 11], [22, 11], [25, 11], [3, 10], [24, 10]]
        non_upgraded_filter_locations = [[6, 9], [21, 9], [7, 8], [20, 8], [8, 7], [19, 7], [9, 6], [18, 6], [10, 5],
                                         [12, 5], [13, 5], [14, 5], [15, 5], [17, 5], [11, 4], [16, 4]]
        filter_locations = upgraded_filter_locations + non_upgraded_filter_locations
        game_state.attempt_spawn(FILTER, filter_locations)
        # upgrade filters so they soak more damage
        game_state.attempt_upgrade(upgraded_filter_locations)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames 
        as shown in the on_action_frame function
        """
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            build_location = [location[0], location[1] + 1]
            game_state.attempt_spawn(DESTRUCTOR, build_location)

    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        # Remove locations that are blocked by our own firewalls 
        # since we can't deploy units there.
        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        # While we have remaining bits to spend lets send out scramblers randomly.
        while game_state.get_resource(BITS) >= game_state.type_cost(SCRAMBLER)[BITS] and len(deploy_locations) > 0:
            # Choose a random deploy location.
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(SCRAMBLER, deploy_location)
            """
            We don't have to remove the location since multiple information 
            units can occupy the same space.
            """

    def emp_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our EMP's can attack from long range.
        """
        # First let's figure out the cheapest unit
        # We could just check the game rules, but this demonstrates how to use the GameUnit class
        stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
        cheapest_unit = FILTER
        for unit in stationary_units:
            unit_class = gamelib.GameUnit(unit, game_state.config)
            if unit_class.cost[game_state.BITS] < gamelib.GameUnit(cheapest_unit, game_state.config).cost[
                game_state.BITS]:
                cheapest_unit = unit

        # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
        # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
        for x in range(27, 5, -1):
            game_state.attempt_spawn(cheapest_unit, [x, 11])

        # Now spawn EMPs next to the line
        # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
        game_state.attempt_spawn(EMP, [24, 10], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR,
                                                                                             game_state.config).damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (
                            valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
