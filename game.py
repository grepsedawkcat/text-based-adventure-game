"""
Robert Oh
A01321210

Collin Chan
A01337496

The main module of our text-based adventure game.
"""
import random
import itertools
import copy
import sys

# Global constant for enumerating user choices in movement
USER_INPUT_MOVING = ("NORTH", "EAST", "SOUTH", "WEST", "MAP", "QUIT")

# Global constant used for obstacle environment detection
OBSTACLES = ("wall", "table", "door")

# Global constant for random event environments
ENVIRONMENTS = (("weak duelist", "?", "Yikes! A weak duelist approaches you"),
                ("strong duelist", "?", "Oh no! A strong duelist approaches you"),
                ("elite duelist", "?", "Oh my! An elite duelist approaches you"),
                ("nothing", "?", "There is nothing here, phew"))


"""
BOARD RELATED FUNCTIONALITY START
"""


def fill_board_coordinates_vertical(board: dict, coords: tuple, times: int, generate_function) -> None:
    (start_x, start_y) = coords
    for pair in zip(range(start_x, start_x + times), itertools.repeat(start_y, times)):
        board[pair] = generate_function


def fill_board_coordinates_horizontal(board: dict, coords: tuple, times: int, generate_function) -> None:
    (start_x, start_y) = coords
    for pair in zip(itertools.repeat(start_x, times), range(start_y, start_y + times)):
        board[pair] = generate_function


def set_coordinate_state(board: dict, coordinate: tuple, generate_function) -> None:
    board[coordinate] = generate_function


def make_board(rows: int, columns: int) -> dict:
    """
    """
    board = {}
    for row_coordinate in range(rows):
        for pair in zip(itertools.repeat(row_coordinate, rows), range(columns)):
            board[pair] = random_event
    # Create initial map layout here with items, walls, and water
    fill_board_coordinates_horizontal(board, (3, 2), 2, wall)
    fill_board_coordinates_horizontal(board, (3, 6), 2, wall)
    fill_board_coordinates_vertical(board, (0, 2), 3, wall)
    fill_board_coordinates_vertical(board, (0, 7), 3, wall)
    fill_board_coordinates_vertical(board, (5, 1), 4, table)
    fill_board_coordinates_vertical(board, (5, 3), 4, table)
    fill_board_coordinates_vertical(board, (5, 6), 4, table)
    fill_board_coordinates_vertical(board, (5, 8), 4, table)
    fill_board_coordinates_horizontal(board, (3, 4), 2, door)
    fill_board_coordinates_horizontal(board, (1, 4), 2, table)
    set_coordinate_state(board, (5, 4), final_boss)
    set_coordinate_state(board, (0, 1), item)
    set_coordinate_state(board, (3, 9), item)
    set_coordinate_state(board, (9, 9), item)
    set_coordinate_state(board, (9, 3), item)
    set_coordinate_state(board, (6, 5), item)
    return board


def map_board(board: dict, character: dict) -> None:
    print("\nMAP OF CONVENTION CENTRE:")
    for coordinate, generate_function in board.items():
        print(f"[{generate_function(character)[1]}] ", end="")
        if coordinate[1] == 9:
            print("")
    print("LEGEND: ! = you, # = table, % = wall, - = door, "
          "? = unknown, @ = piece of exodia, $ = Maximillion Pegasus\n")


"""
BOARD RELATED FUNCTIONALITY END
"""


"""
GAME PROGRESSION RELATED FUNCTIONALITY START
"""


def item_obtained(character: dict) -> None:
    character["exodia pieces"] += 1
    if character["exodia pieces"] >= 5:
        print(f"You have assembled the forbidden one\n"
              f"The power of exodia makes you feel invincible...\n")


def character_get_exp(character: dict, enemy: dict) -> None:
    character["CURRENT EXP"] += enemy["exp gained"]


def handle_level_up(board: dict, character: dict) -> None:
    character["CURRENT EXP"] = 0
    character["level"] += 1
    character["MAX HP"] = character["level"] * 100
    character["CURRENT HP"] = character["MAX HP"]
    character["cards allowed"] += 1
    if character["level"] == 3:
        fill_board_coordinates_horizontal(board, (3, 4), 2, random_event)
    print(f'Congratulations on leveling to level {character["level"]}!')
    print(f"...You feel like you are attracting more attention from stronger duelists\n")


def character_has_leveled(character: dict) -> bool:
    return character["CURRENT EXP"] >= character["EXP TO LEVEL"]


"""
GAME PROGRESSION RELATED FUNCTIONALITY END
"""


"""
COMBAT RELATED FUNCTIONALITY START
"""


def effect_the_enemy(enemy: dict, character: dict, skill: str) -> bool:
    skill_stat_list = [skills_stats for skills_stats in character["SKILLS"] if skills_stats["type"] == skill]
    skill_stat = skill_stat_list[0]
    print(skill_stat)
    if "heal range" in skill_stat.keys():
        return False
    damage = random.randint(skill_stat["damage range"][0], skill_stat["damage range"][1])
    print(enemy["HP"])
    print(max(enemy["HP"] - damage, 0))
    enemy["HP"] = max(enemy["HP"] - damage, 0)
    print(damage)
    print(f'\nYou chose to attack with {skill_stat["type"]}!')
    print(f'The opposing duelist received {damage} damage to their lifepoints! '
          f'Their lifepoints are now: {enemy["HP"]}\n')
    return enemy["HP"] <= 0


def effect_the_character(enemy: dict, character: dict, skill: str) -> None:
    skill_stat_list = [skills_stats for skills_stats in character["SKILLS"] if skills_stats["type"] == skill]
    skill_stat = skill_stat_list[0]
    print(skill_stat)
    if "heal range" in skill_stat.keys():
        health_gained = random.randint(skill_stat["heal range"][0], skill_stat["heal range"][1])
        character["CURRENT HP"] = min(character["CURRENT HP"] + health_gained, character["MAX HP"])
        print(f'You chose to heal with {skill_stat["type"]}!\n')
        print(f'You healed {health_gained} lifepoints! '
              f'Your lifepoints are now: {character["CURRENT HP"]}')
    damage = random.randint(enemy["damage range"][0], enemy["damage range"][1])
    print(damage)
    character["CURRENT HP"] = max(character["CURRENT HP"] - damage, 0)
    print(f'The opposing duelist prepares an attack!')
    print(f'you received {damage} damage to your lifepoints! '
          f'Your current lifepoints are: {character["CURRENT HP"]}\n')


def update_boss_status(enemy: dict) -> None:
    enemy["damage range"] = [50, 100]


def execute_challenge_protocol(character: dict, current_environment: tuple, enemies: tuple) -> None:
    enemy_stats_list = [enemy_stats for enemy_stats in enemies if enemy_stats["type"] == current_environment[0]]
    enemy = copy.copy(enemy_stats_list[0])
    list_of_skills = list(USER_INPUT_FIGHTING)
    if (current_environment[0] == "boss") and (character["exodia pieces"] >= 5):
        list_of_skills.append("EXODIA THE FORBIDDEN ONE")
        update_boss_status(enemy)
        print(f"Pegasus seems weary of your deck... This is your chance!\n"
              f"This is the duel of your life! Only one card can help you!")
    else:
        print(f"You are fighting a {current_environment[0]}!\n")
    while is_alive(character):
        skill_choices = random.sample(list_of_skills, character["cards allowed"])
        skill = get_user_choice(skill_choices)
        if effect_the_enemy(enemy, character, skill):
            if current_environment[0] == "boss":
                character["boss killed"] = True
            break
        effect_the_character(enemy, character, skill)
        print(character)
        print(enemy)
    character_get_exp(character, enemy)


def enemies_init() -> tuple:
    return ({"type": "weak duelist", "HP": 150, "damage range": [0, 15], "exp gained": 25},
            {"type": "strong duelist", "HP": 200, "damage range": [25, 45], "exp gained": 25},
            {"type": "elite duelist", "HP": 300, "damage range": [40, 65], "exp gained": 25},
            {"type": "boss", "HP": 100000, "damage range": [9000, 10000], "exp gained": 0})


"""
COMBAT RELATED FUNCTIONALITY END
"""


"""
BOARD ENVIRONMENT RELATED FUNCTIONALITY START
"""


def random_event(character: dict) -> tuple:
    weak_enemies_list = list(itertools.repeat(ENVIRONMENTS[0], 0 if character["level"] >= 2 else 4))
    strong_enemies_list = list(itertools.repeat(ENVIRONMENTS[1], 4 if character["level"] >= 2 else 0))
    elite_enemies_list = list(itertools.repeat(ENVIRONMENTS[2], character["level"] if character["level"] >= 3 else 0))
    none_list = list(itertools.repeat(ENVIRONMENTS[3], 5))
    scaled_environment_list = list(itertools.chain.from_iterable([weak_enemies_list, strong_enemies_list,
                                                                  elite_enemies_list, none_list]))
    # print(scaled_environment_list)
    return random.choice(scaled_environment_list)


def cool_description(_) -> tuple:
    return random.choice([("", "!", "You feel the cool air in the convention center"),
                          ("", "!", "The sound of duelists is deafening"),
                          ("", "!", "This place is jam-packed with people"),
                          ("", "!", "A bunch of tables are lined up for duels"),
                          ("", "!", "There are duels taking place eveywhere")])


def door(_) -> tuple:
    return "door", "-", "A door towers over you"


def wall(_) -> tuple:
    return "wall", "%", "A wall towers over you"


def table(_) -> tuple:
    return "table", "#", "A large table"


def item(_) -> tuple:
    return "item", "@", "You have found a piece of exodia!"


def final_boss(_) -> tuple:
    return "boss", "$", "Uh oh. Maximillion Pegasus strides towards you..."


def is_battle_environment(current_environment: dict) -> bool:
    return (current_environment in list(filter(is_not_none, list(ENVIRONMENTS)))) or (current_environment[0] == "boss")


"""
BOARD ENVIRONMENT RELATED FUNCTIONALITY END
"""


"""
MOVEMENT RELATED FUNCTIONALITY START
"""


def move_character(character: dict, direction: str) -> tuple[int, int]:
    """

    :param character:
    :param direction:
    :return:
    """
    new_coordinates = ()
    (x, y) = character["coordinates"]
    if direction == "SOUTH":
        new_coordinates = (x + 1, y)
    if direction == "NORTH":
        new_coordinates = (x - 1, y)
    if direction == "EAST":
        new_coordinates = (x, y + 1)
    if direction == "WEST":
        new_coordinates = (x, y - 1)
    return new_coordinates


def validate_move(board: dict, character: dict, direction: str) -> bool:
    """

    :param board:
    :param character:
    :param direction:
    :return:
    """
    coordinates_moved = move_character(character, direction)
    if (coordinates_moved not in board.keys()) or (board[coordinates_moved](character)[0] in OBSTACLES):
        return False
    return True


"""
MOVEMENT RELATED FUNCTIONALITY END
"""


"""
PRINTING RELATED FUNCTIONALITY START
"""


def get_character_name() -> str:
    """
    Gets character's name from standard input and returns it.

    postcondtion: prints an input prompt to the screen
    postcondition: returns a string that will become the current character's name
    :return: a string that is the current character's chosen name
    """
    return input("State your name, duelist\n>")


def print_intro(name: str) -> None:
    """
    Prints an introduction speech to the screen.

    :param name: a string
    precondition: name must be a string
    postcondition: messages are printed to the screen
    """
    print(f"\nHello, {name}.\n"
          f"It seems like you have signed up for this major dueling tournament\n"
          f"I'm the coordinator for this event and I'll give you some tips\n"
          f"Oh, you don't know anything about dueling, you say? Well, that's too bad\n"
          f"Your only way out of here is to beat the omega duelist 'Maximillion Pegasus'\n"
          f"I heard his deck is pretty awesome and you can't beat him conventionally\n"
          f"You probably have to find some cheat cards to bring him down\n"
          f"I've been hearing about these exodia cards that are busted\n"
          f"No duelist has ever been able to get all five of them, though\n"
          f"Anyway, I won't bother you any longer. You have duels to attend to\n"
          f"Good luck. And may the heart of the cards be with you\n")


def print_instructions() -> None:
    """
    Prints instruction lines to the screen.

    postcondition: messages are printed to the screen
    """
    print(f"INSTRUCTIONS\n"
          f"You will be approached by duelists while moving through the convention center\n"
          f"Select cards from your deck to defeat them. Some cards have healing effects. These are important!\n"
          f"The doors to Maximillion Pegasus's room will open when you reach level 3\n"
          f"Be warned that you will need a special card to defeat him")


def print_end_of_game(name: str) -> None:
    """
    Prints a message when the final boss is killed and game ends.

    :param name: a string
    precondition: name must be a string that is character's name
    postcondition: messages are printed to the screen that include name
    """
    print(f"you have finished the game, {name}!")


def print_obstacle_message(character: dict, direction: str) -> None:
    """
    Prints messages when user encounters an obstacle.

    :param character: a dictionary
    :param direction: a string
    precondition: character must be a dictionary that represents a character
    precondition: direction must be a string
    postcondition: messages are printed to the screen that include the coordinate that user attempted to move towards
    """
    print(f"can't move to {move_character(character, direction)}, there is an obstacle")


def print_death_message() -> None:
    """
    Prints messages after character death and then ends game.

    postcondition: messages are printed to the screen
    postcondition: program is terminated
    """
    print(f"You collapse to the floor in a daze\n"
          f"It seems you don't have what it takes to hang with these duelists\n"
          f"RIP")
    sys.exit()


def describe_current_location(board: dict, character: dict):
    """
    Describes character's current coordinate's environment on the board and returns this environment.

    :param board: a dictionary
    :param character: a dictionary
    precondition: board must be dictionary that represents the board for the game
    precondition: character must be a dictionary that represents a character
    postcondition: prints the description of the environment at the character's current coordinates
    postcondition: returns the tuple that is returned from the function at the character's boards coordinates
    :return: a tuple that represents the environment at the character's current coordinates
    """
    environment = board[character["coordinates"]](character)
    print(f"{environment[2]}. You are at {character['coordinates']}\n")
    return environment


def print_victory_message(name: str) -> None:
    """
    Prints messages after a battle victory.

    :param name: a string
    precondition: name is a string that is character's name
    postcondition: messages are printed to the screen that include name
    """
    print(f"Nice victory, {name}!\n")


"""
PRINTING RELATED FUNCTIONALITY END
"""

"""
CHARACTER RELATED FUNCTIONALITY START
"""


def boss_dead(character: dict) -> bool:
    """
    Tests whether boss is killed (i.e., game has ended).

    :param character: a dictionary
    precondition: character must be a dictionary that represents a character
    postcondition: returns the boolean value stored at character's "boss killed" key that indicates if boss is dead
    :return: the boolean value stored at character's "boss killed" key

    >>> boss_dead(make_character("Collin"))
    False
    """
    return character["boss killed"]


def is_alive(character: dict) -> bool:
    """
    Tests whether a character is alive.

    :param character: a dictionary
    precondition: character must be a dictionary that represents a character
    postcondition: returns a boolean that indicates whether character's "CURRENT HP" key is greater than 0
    :return: a boolean that indicates whether character's current hp is greater than 0

    >>> is_alive(make_character("Collin"))
    True
    """
    return character["CURRENT HP"] > 0


def make_character(name: str) -> dict:
    """
    Creates a character for the game.

    :param name: a string
    precondition: name must be a string
    postcondition: returns a dictionary with keys representing stats and information and name is stored in one of these
    :return: a dictionary that has keys representing the characters various stats and information
    """
    return {"name": name, "coordinates": (6, 4), "level": 1, "CURRENT HP": 100,
            "MAX HP": 100, "cards allowed": 3, "CURRENT EXP": 0, "EXP TO LEVEL": 150,
            "exodia pieces": 0, "boss killed": False,
            "SKILLS": [
                {"type": "DARK MAGICIAN", "damage range": [40, 80]},
                {"type": "BLUE-EYES WHITE DRAGON", "damage range": [100, 150]},
                {"type": "RED-EYES BLACK DRAGON", "damage range": [50, 100]},
                {"type": "GOBLIN'S SECRET REMEDY", "heal range": [50, 100]},
                {"type": "BLUE-EYES ULTIMATE DRAGON", "damage range": [9999, 9999]},
                {"type": "KURIBOH", "heal range": [20, 70]},
                {"type": "DARK MAGICIAN GIRL", "damage range": [50, 100]},
                {"type": "SCAPEGOAT", "heal range": [10, 70]},
                {"type": "JINZO", "damage range": [0, 150]},
                {"type": "DIAN KETO THE CURE MASTER", "heal range": [1000, 1500]},
                {"type": "CELTIC GUARDIAN", "damage range": [5, 25]},
                {"type": "MAN-EATER BUG", "damage range": [0, 20]},
                {"type": "BUSTER BLADER", "damage range": [50, 80]},
                {"type": "TOON WIZARD", "damage range": [0, 40]},
                {"type": "EXODIA THE FORBIDDEN ONE", "damage range": [999999, 999999]}
            ]
            }


# Global constant for enumerating user choices in duels, a random subset will be chosen in a battle
USER_INPUT_FIGHTING = ("DARK MAGICIAN", "BLUE-EYES WHITE DRAGON", "GOBLIN'S SECRET REMEDY",
                       "RED-EYES BLACK DRAGON", "DARK MAGICIAN GIRL", "BLUE-EYES ULTIMATE DRAGON",
                       "KURIBOH", "SCAPEGOAT", "JINZO", "DIAN KETO THE CURE MASTER", "CELTIC GUARDIAN",
                       "MAN-EATER BUG", "BUSTER BLADER", "TOON WIZARD"
                       )

"""
CHARACTER RELATED FUNCTIONALITY END
"""


def quit_game() -> None:
    """
    Stops the game.

    postcondition: message is printed to screen
    postcondition: program will terminate
    """
    print("\nThank you for playing!")
    sys.exit()


def is_not_none(environment: tuple[str, str, str]) -> bool:
    """
    Used with filter function to find board environments that have actual events.

    :param environment: a tuple containing only strings
    precondition: environment must be a tuple containing only strings that represents a board environment
    postcondition: a boolean is returned that indicates whether this board environment has an event
    :return: a boolean that represents whether this board environment is not nothing

    >>> is_not_none(("elite duelist", "?", "Oh my! An elite duelist approaches you"))
    True
    """
    return environment[0] != "nothing"


def get_user_choice(choice_list: tuple) -> str:
    """
    Gets the user's desired choice from a list of valid user input.

    :param choice_list: a tuple containing only strings
    preconditon: choice_list must be a tuple that only contains strings representing valid user input
    postcondition: returns a string that is the same as one of the strings in choice_list
    :return: a string that represents the user's choice
    """
    user_input = ""
    choices_to_print = "Make a selection:\n"
    enumerated_choices = list(enumerate(choice_list, 1))
    valid_input = [str(choice[0]) for choice in enumerated_choices]
    while user_input not in valid_input:
        for choice in enumerated_choices:
            choices_to_print += f"{choice[0]}.{choice[1]}\n"
        user_input = input(f"{choices_to_print}>")
        choices_to_print = "Invalid input, make another selection:\n"
    input_name = [choice[1] for choice in enumerated_choices if str(choice[0]) == user_input]
    print(input_name)
    return input_name[0]


def game() -> None:
    """
    The main game loop.

    postcondition: prints game messages to the screen
    """
    rows = 10
    columns = 10
    enemies = enemies_init()
    name = get_character_name()
    character = make_character(name)
    board = make_board(rows, columns)
    print_intro(name)
    print_instructions()
    while not boss_dead(character):
        set_coordinate_state(board, character["coordinates"], cool_description)
        describe_current_location(board, character)
        direction = get_user_choice(USER_INPUT_MOVING)
        if direction == "MAP":
            map_board(board, character)
            continue
        if direction == "QUIT":
            quit_game()
        valid_move = validate_move(board, character, direction)
        if valid_move:
            set_coordinate_state(board, character["coordinates"], random_event)
            character["coordinates"] = move_character(character, direction)
            current_environment = describe_current_location(board, character)
            if current_environment[0] == "item":
                item_obtained(character)
                print(character)
                continue
            if is_battle_environment(current_environment):
                execute_challenge_protocol(character, current_environment, enemies)
                print(character)
                if not is_alive(character):
                    print_death_message()
                print_victory_message(name)
                if character_has_leveled(character):
                    handle_level_up(board, character)
        else:
            print_obstacle_message(character, direction)
    print_end_of_game(name)


def main() -> None:
    """
    Drives the program.
    """
    game()


if __name__ == "__main__":
    main()
