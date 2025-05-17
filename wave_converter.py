
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


    class Wave_enemy_command_type(data_class.TypedDict):
        health: int
        special: str
        timer_difference: int
        amount: int


    wave_enemy_commands: list[Wave_enemy_command_type] = []


    ##################
    # Wave converter #
    ##################
    wave_num: int = 0
    wave_enemies: list[data_class.Wave_enemy] = []
    timer: int = 5
    # 1 Spawn tick => 0.05 tiles
    # 20 Spawn ticks => 1 tile

    money_per_type: dict[str, int] = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "10": 10,
        "50": 10+6,
        "100": 10+6 +10*1,
        "200": 10+6 +10*2,
        "300": 10+6 +10*3,
        "400": 10+6 +10*4,
        "500": 10+6 +10*5,
        "1000": 10+6 +10*10,
        "lead": 10+6 -4,
        "anti_explosion": 10+6 -4,
        "stack": 10 + 12 + 12,
        "stack+": 10 + 16*2 + 10 + 12 + 12
    }

    health_per_type: dict[str, int] = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 4,
        "5": 5,
        "10": 10,
        "50": 50,
        "100": 100,
        "200": 200,
        "300": 300,
        "400": 400,
        "500": 500,
        "1000": 1000,
        "lead": 20,
        "anti_explosion": 20,
        "stack": 10 + (20+10+10),
        "stack+": 60 + (50*2+20+20+10)
    }



    import easygui # type: ignore
    try:
        wave_num = int(easygui.enterbox("Enter the wave number", "Wave Converter", ""))
        # Load the wave file
        try:
            with open(f"waves/raw_normal{wave_num}.pkl", "rb") as f:
                wave_enemy_commands = pickle.load(f)
        except FileNotFoundError:
            create_answer: str = easygui.msgbox(f"Do you want to create the\nnew file for the wave {wave_num}", "Wave Converter", "Create New") # type: ignore
            logging.info(f"Wave file not found: waves/raw_normal{wave_num}.pkl")
            if create_answer != "Create New":
                raise FileNotFoundError(f"File not found: waves/raw_normal{wave_num}.pkl")
            wave_enemy_commands = []


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



            # Allways run these first before everything else
            data.Calculate_hud_zoom()

            # Show wave-information
            needed_time: int = 5
            money: int = 100
            health: int = 0
            for command in wave_enemy_commands:
                needed_time += command["timer_difference"]* command["amount"]
                if command["special"] == "":
                    enemy_type = str(command["health"])
                else:
                    enemy_type = command["special"]
                money += money_per_type[enemy_type] * command["amount"]
                health += health_per_type[enemy_type] * command["amount"]


            # Wave converter code
            data.Draw_text(f"Wave {wave_num}", 8*data.hud_zoom, (0, 0, 0), (5,5))

            # Statistics
            data.Draw_text("Statistics", 10*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 4*data.hud_zoom))
            data.Draw_text(f"Time: {needed_time}", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 14*data.hud_zoom))
            data.Draw_text(f"Money: {money}", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 22*data.hud_zoom))
            data.Draw_text(f"Health: {health}", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 30*data.hud_zoom))
            try:
                data.Draw_text(f"M/T -> {round(money/needed_time,3)}", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 38*data.hud_zoom))
                data.Draw_text(f"H/T -> {round(health/needed_time,3)}", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 46*data.hud_zoom))
                data.Draw_text(f"M/H -> {round(money/health,3)}", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 54*data.hud_zoom))
            except ZeroDivisionError:
                data.Draw_text("M/T -> 0", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 38*data.hud_zoom))
                data.Draw_text("H/T -> 0", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 46*data.hud_zoom))
                data.Draw_text("M/H -> 0", 7*data.hud_zoom, (0, 0, 0), (250*data.hud_zoom, 54*data.hud_zoom))



            # Add Button
            add_button_rect = pg.Rect(40*data.hud_zoom, 1*data.hud_zoom, 20*data.hud_zoom, 10*data.hud_zoom)
            pg.draw.rect(data.screen, (100, 100, 100), add_button_rect)
            data.Draw_text("Add", 7 * data.hud_zoom, (255, 255, 255), (44*data.hud_zoom, 2*data.hud_zoom))
            # Check for mouse click on the add button
            if pg.mouse.get_pressed()[0]:
                mouse_pos = pg.mouse.get_pos()
                if add_button_rect.collidepoint(mouse_pos):
                    # Open a dialog to add a new command
                    new_command: list[str] = easygui.multenterbox(
                        "Add command",
                        "Wave Converter",
                        ["Health", "Special", "Timer", "Amount"],
                        ["", "", "", ""]
                    ) # type: ignore
                    if new_command != None:
                        # Add the command
                        wave_enemy_commands.append({
                            "health": int(new_command[0]),
                            "special": new_command[1],
                            "timer_difference": int(new_command[2]),
                            "amount": int(new_command[3])
                        })





            # Display current commands
            # Define column headers and positions
            headers = ["Health", "Special", "Timer", "Amount", "Change"]
            col_widths = [40, 80, 40, 40, 20]
            x_start = 5
            y_start = 10
            row_height = 12

            # Draw headers
            for idx, header in enumerate(headers):
                data.Draw_text(header, 8 * data.hud_zoom, (0, 0, 0), ((x_start + sum(col_widths[:idx]))*data.hud_zoom, (y_start)*data.hud_zoom))

            # Draw each row
            for row_idx, command in enumerate(wave_enemy_commands):
                y = y_start + row_height * (row_idx + 1)
                values = [
                    str(command.get("health", "")),
                    str(command.get("special", "")),
                    str(command.get("timer_difference", "")),
                    "x"+str(command.get("amount", "")),
                ]
                for col_idx, value in enumerate(values):
                    data.Draw_text(value, 7 * data.hud_zoom, (0, 0, 0), ((x_start + sum(col_widths[:col_idx]))*data.hud_zoom, y*data.hud_zoom))
                # Draw a line below the row
                pg.draw.line(data.screen, (0, 0, 0), (x_start*data.hud_zoom, (y-1)*data.hud_zoom), ((x_start + sum(col_widths))*data.hud_zoom, (y-1)*data.hud_zoom), data.hud_zoom)

                # Draw the change button
                change_button_rect = pg.Rect((x_start + sum(col_widths) - col_widths[-1]+1)*data.hud_zoom, (y)*data.hud_zoom, col_widths[-1]*data.hud_zoom, (row_height-2)*data.hud_zoom)
                pg.draw.rect(data.screen, (100, 100, 100), change_button_rect)
                data.Draw_text("C", 7 * data.hud_zoom, (255, 255, 255), ((x_start + sum(col_widths) - col_widths[-1]+8)*data.hud_zoom, (y+1)*data.hud_zoom))
                # Check for mouse click on the change button
                if pg.mouse.get_pressed()[0]:
                    mouse_pos = pg.mouse.get_pos()
                    if change_button_rect.collidepoint(mouse_pos):
                        # Open a dialog to change the command
                        new_command: list[str] = easygui.multenterbox(
                            "Change command",
                            "Wave Converter",
                            ["Health", "Special", "Timer", "Amount"],
                            [str(command["health"]), command["special"], str(command["timer_difference"]), str(command["amount"])]
                        ) # type: ignore
                        if new_command != None:
                            # Update the command
                            wave_enemy_commands[row_idx]["health"] = int(new_command[0])
                            wave_enemy_commands[row_idx]["special"] = new_command[1]
                            wave_enemy_commands[row_idx]["timer_difference"] = int(new_command[2])
                            wave_enemy_commands[row_idx]["amount"] = int(new_command[3])
                        else:
                            del wave_enemy_commands[row_idx]
                            break






            
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


        # Convert Wave Enemy Commands to Wave Enemies
        if len(wave_enemy_commands) == 0:
            raise ValueError("No wave enemy commands found")
        for command in wave_enemy_commands:
            for _ in range(command["amount"]):
                new_enemy: data_class.Wave_enemy = {
                    "health": command["health"],
                    "special": command["special"],
                    "spawn_time": timer
                }
                timer += command["timer_difference"]
                wave_enemies.append(new_enemy)

        # Closed the window, saving...
        with open(f"waves/raw_normal{wave_num}.pkl", "wb") as f:
            pickle.dump(wave_enemy_commands, f)
        with open(f"waves/normal{wave_num}.pkl", "wb") as f:
            pickle.dump(wave_enemies, f)
    except Exception:
        easygui.exceptionbox("Error", "An error occurred while saving the wave enemies.")

    logging.info("Programm closed")
    pg.quit()

