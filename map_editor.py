
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

    import debug
    debug_obj: debug.Debug = debug.Debug(data)

    import tile_map
    tile_map_obj: tile_map.Tile_map = tile_map.Tile_map(data)



    # Map-editor specific 
    current_placer: int = 1
    tile_map_obj.map = [[1 for _ in range(24)] for _ in range(17)]
    import easygui # type: ignore
    tile_map_obj.map_file_name = easygui.enterbox("Enter the name of the map file (without .pkl)", "Map Editor", "")
    tile_map_obj.Load_map_file()
    autosave_timer: int = 0
    enemy_path_nodes: list[tuple[int, int]] = []


    logging.info("Imported all game-classes")

    pg.display.set_caption("Points TD 2")
    # display_icon = pg.image.load("images/xyz.png").convert_alpha()
    # pg.display.set_icon(display_icon)
    
    mspf: list[float] = []
    mspf_raw: list[float] = []
    fullscreen_pressed: bool = False

    try:
        while data.run:
            # Resize the screen
            if data.resize:
                data.resize = False
            if pg.display.get_surface().get_size() != data.screen_size:
                data.screen_size = pg.display.get_surface().get_size()
                data.resize = True
                logging.info(f"Screen resized to {data.screen_size}")
            # Fullscreen
            if pg.key.get_pressed()[pg.K_F11]:
                if not fullscreen_pressed:
                    fullscreen_pressed = True
                    data.fullscreen = not data.fullscreen
                    if data.fullscreen:
                        data.screen = pg.display.set_mode((0, 0), pg.RESIZABLE|pg.SHOWN|pg.DOUBLEBUF|pg.FULLSCREEN)
                        logging.info("Fullscreen enabled")
                    else:
                        data.screen = pg.display.set_mode((800,600), pg.RESIZABLE|pg.SHOWN|pg.DOUBLEBUF)
                        logging.info("Fullscreen disabled")
                    data.resize = True
            else:
                fullscreen_pressed = False
            # Fill the background
            data.screen.fill((100,180,255))


            # Allways run these first after everything else
            data.Calculate_hud_zoom()




            # Map Editor Code
            if pg.key.get_pressed()[pg.K_1]: # Grass
                current_placer = 1
            if pg.key.get_pressed()[pg.K_2]: # Path
                current_placer = 11
            if pg.key.get_pressed()[pg.K_3]: # Sea
                current_placer = 21

            # Enemy path
            if pg.key.get_pressed()[pg.K_0]: # Enemy Path
                if pg.key.get_pressed()[pg.K_LSHIFT] and len(enemy_path_nodes) > 0:
                    tile_map_obj.Calculate_enemy_path(enemy_path_nodes)
                current_placer = 1000
                enemy_path_nodes = []
            



            if pg.mouse.get_pressed()[0]:
                mouse_pos: tuple[int, int] = pg.mouse.get_pos()
                tile_pos: tuple[int, int] = tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=True)
                if current_placer == 1: # Grass
                    tile_map_obj.map[tile_pos[1]][tile_pos[0]] = random.randint(1, 6)
                if current_placer == 11: # Path
                    tile_map_obj.map[tile_pos[1]][tile_pos[0]] = random.randint(11, 15)
                if current_placer == 1000: # Enemy
                    if pg.key.get_pressed()[pg.K_LEFT]: tile_pos = (tile_pos[0]-1, tile_pos[1])
                    if pg.key.get_pressed()[pg.K_RIGHT]: tile_pos = (tile_pos[0]+1, tile_pos[1])
                    if pg.key.get_pressed()[pg.K_UP]: tile_pos = (tile_pos[0], tile_pos[1]-1)
                    if pg.key.get_pressed()[pg.K_DOWN]: tile_pos = (tile_pos[0], tile_pos[1]+1)
                    if tile_pos not in enemy_path_nodes:
                        enemy_path_nodes.append(tile_pos)
                if current_placer == 21: # Sea
                    place_tile: int = 41
                    if pg.key.get_pressed()[pg.K_UP]: place_tile = random.choice([23, 33])
                    if pg.key.get_pressed()[pg.K_DOWN]: place_tile = random.choice([21, 31])
                    if pg.key.get_pressed()[pg.K_RIGHT]:
                        if place_tile in [23, 33]: place_tile = random.choice([26, 36])
                        elif place_tile in [21, 31]: place_tile = random.choice([25, 35])
                        else: place_tile = random.choice([22, 32])
                    if pg.key.get_pressed()[pg.K_LEFT]:
                        if place_tile in [23, 33]: place_tile = random.choice([27, 37])
                        elif place_tile in [21, 31]: place_tile = random.choice([28, 38])
                        else: place_tile = random.choice([24, 34])
                    if place_tile == 41 and random.randint(1,5)==1: place_tile = random.randint(41, 49)
                    tile_map_obj.map[tile_pos[1]][tile_pos[0]] = place_tile

                    

            tile_map_obj.Show_map()

            if pg.key.get_pressed()[pg.K_q]:
                tile_map_obj.Show_grid()
                tile_map_obj.Show_enemy_path()


            autosave_timer += 1
            if autosave_timer >= 60*60:
                tile_map_obj.Save_map_file()
                autosave_timer = 0
                logging.info("Autosaved map file")






            # Allways run these after everything else
            debug_obj.Debug_main(3, mspf, mspf_raw)


            
            # Update display
            pg.display.update()
            
            # Handle all Events
            data.mouse_wheel = ""
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    data.run = False
                    logging.info("Received Quit Event")
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        data.mouse_wheel = "up"
                    if event.button == 5:
                        data.mouse_wheel = "down"
            # Update Clock
            data.clock.tick(60)
            if len(mspf) >= 300:
                del mspf[0]
                del mspf_raw[0]
            mspf.append(data.clock.get_time())
            mspf_raw.append(data.clock.get_rawtime())

    except Exception as e:
        logging.critical(f"An Exception occured: {e}")
        easygui.exceptionbox("An Exception (Error) occured\nand the game sadly crashed...\nSorry for the inconvenience!","Points TD 2 - Crash Report")
        data.run = False

    finally:
        tile_map_obj.Save_map_file()
        logging.info("Programm closed")
        pg.quit()
