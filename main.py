
from os import path as os_path
from os import chdir as os_chdir
directory = os_path.dirname(os_path.abspath(__file__))
os_chdir(directory) #Small Bugfix, that in some situations, the code_path isn't correct


#### Ideas ####
# Each tower is an Object. With a base class "Tower" and subclasses for each type of tower.


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

    # Import all other classes
    import transition
    transition_obj: transition.Transition = transition.Transition(data)

    import main_menu
    main_menu_obj: main_menu.Main_menu = main_menu.Main_menu(data)
    
    import debug
    debug_obj: debug.Debug = debug.Debug(data)




    pg.display.set_caption("Points TD 2")
    # display_icon = pg.image.load("images/xyz.png").convert_alpha()
    # pg.display.set_icon(display_icon)
    
    mspf: list[float] = []
    mspf_raw: list[float] = []
    fullscreen_pressed: bool = False

    import easygui # type: ignore
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



            # Show current game state / menu
            if data.is_in_main_menu:
                main_menu_obj.Render_main()

            if data.is_in_game:
                pass # TODO: Run all the main-game logic here.





            # Allways run these after everything else
            transition_obj.Render()
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
        logging.info("Programm closed")
        pg.quit()