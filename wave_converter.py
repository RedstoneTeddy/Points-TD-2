
from os import path as os_path
from os import chdir as os_chdir
directory = os_path.dirname(os_path.abspath(__file__))
os_chdir(directory) #Small Bugfix, that in some situations, the code_path isn't correct


if __name__ == "__main__":
    import logging

    # Setup logging
    # File handler for logging all messages
    logging.basicConfig(
        filename="Log.txt",
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
    )
    
    # Console handler for logging ERROR level messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Add the console handler to the root logger
    logging.getLogger().addHandler(console_handler)
    
    logging.info("Logging started")

    # Import pygame
    import pygame as pg
    pg.init()
    pg.event.set_allowed([pg.QUIT, pg.KEYDOWN, pg.KEYUP])
    logging.info("Pygame initialized")

    # Import the main game data class
    import data_class
    data: data_class.Data_class = data_class.Data_class()
    logging.info("Data initialized")

    import random
    import pickle

    import tile_map
    tile_map_obj: tile_map.Tile_map = tile_map.Tile_map(data)
    
    import enemy
    enemy_obj: enemy.Enemy = enemy.Enemy(data, tile_map_obj)
    logging.info("Imported all game-classes")



    ##################
    # Wave converter #
    ##################
    wave_num: int = 3
    wave_enemies: list[data_class.Wave_enemy] = []
    timer: int = 5
    # 1 Spawn tick => 0.05 tiles
    # 20 Spawn ticks => 1 tile



    import easygui # type: ignore
    try:
        wave_num = int(easygui.integerbox("Enter the wave number", "Wave Converter", lowerbound=1, upperbound=200)) # type: ignore
        while True:
            command: list[str] = easygui.multenterbox("Enter a new command", "Wave Converter", ["Health", "Special", "Timer Difference", "Amount"]) # type: ignore
            if command is None:
                break
            elif command[0] == "" and command[1] == "" and command[2] == "" and command[3] == "":
                break
            elif command[0] == "load":
                try:
                    import pprint
                    with open(f"waves/normal{wave_num}.pkl", "rb") as f:
                        pprint.pprint(pickle.load(f))
                except FileNotFoundError:
                    print("File not found.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                raise SystemExit

            health: int = int(command[0])
            special: str = command[1]
            timer_difference: int = int(command[2])
            amount: int = int(command[3])
            for i in range(amount):
                wave_enemy: data_class.Wave_enemy = {
                    "health": health,
                    "spawn_time": timer,
                    "special": special
                }
                wave_enemies.append(wave_enemy)
                timer += timer_difference
            print(f"Added {amount} enemies with {health} health. Time Difference: {timer_difference}")



        enemy_obj.Save_wave_enemies(wave_num, wave_enemies)
        logging.info("Wave enemies saved")
    except Exception:
        easygui.exceptionbox("Error", "An error occurred while saving the wave enemies.")

    logging.info("Programm closed")
    pg.quit()

