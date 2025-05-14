from typing import TypedDict, List, NotRequired, Literal, Mapping, Any
import pygame as pg
import logging
import pickle


class Enemy_data(TypedDict):
    health: int
    special: str
    pos_i: int
    pos: tuple[float, float] # This is the center of the tile

class Wave_enemy(TypedDict):
    health: int
    spawn_time: int
    special: str


class Data_class:
    def __init__(self):

        self.screen: pg.Surface = pg.display.set_mode((1050, 600), pg.RESIZABLE|pg.SHOWN|pg.DOUBLEBUF)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.run: bool = True
        self.screen_size: tuple[int, int] = (1050, 600)
        self.resize: bool = False
        self.fullscreen: bool = False
        self.mouse_wheel: Literal["up", "down", ""] = ""
        self.__font_objects: dict[str, pg.font.Font] = {}

        self.performance_saving_setting: Literal["none", "default", "extreme"] = "default"
        #### Affected by this:
        # default: a shoot-ready tower with no target in range will wait 3 ticks before checking again
        # extreme: a shoot-ready tower with no target in range will wait 5 ticks before checking again
        # extreme: projectiles will never render
        # extreme: towers will never turn towards the target
        # extreme: wave_button is not responsive
        # default: during the game, the whole screen will only be filled with the background color each 60 frames (1 second)
        # extreme: tile_map will only be (re-)drawn every 2 frames


        self.transition_to: str = ""
        self.start_black_window: bool = False
        self.ongoing_transition: bool = False

        # Current menu / game state
        self.is_in_main_menu: bool = True
        self.is_in_game: bool = False

        # For (initially) loading the game
        self.load_game: bool = False
        self.map_file_name: str = ""

        self.hud_zoom: int = 1
        self.tile_zoom: int = 2

        # Game Variables
        self.running_wave: bool = False
        self.health: int = 0
        self.enemies: dict[str, Enemy_data] = {} # UUID: Enemy_data
        self.fast_forward: bool = False
        self.auto_wave: bool = False
        self.new_wave: bool = False
        self.wave: int = 0
        self.money: int = 0


        self.difficulty: Literal["", "easy", "medium", "hard", "hacker"] = ""
        self.cost_multiplier: float = 1.0 # Gets set, when the game starts, reads the data.difficulty variable

        # Tower images
        self.original_tower_images: dict[str, dict[str, pg.Surface]] = {
            "ninja" : {
                "up": pg.image.load("images/towers/ninja/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/ninja/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/ninja/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/ninja/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/ninja/projectile.png").convert_alpha()
            }
        }

        
    def Get_font(self, size: int) -> pg.font.Font:
        """
        Get a font object with the given size.
        (If the font at this size was never generated, the programm will automatically generate it and store it for future use.)
        """
        # Font: VCR OSD MONO
        needed_size: str = str(int(size))
        if self.__font_objects.get(needed_size) is None:
            self.__font_objects[needed_size] = pg.font.Font("images/VCR_OSD_MONO_1.001.ttf", size)
        return self.__font_objects[needed_size]
    
    def Draw_text(self, text: str, text_size: int, text_color: tuple[int, int, int], pos: tuple[int, int]) -> None:
        """
        Draws the given text (text) with the given size (text_size) with the color (text_color) at the specific location (pos)
        """
        font: pg.font.Font = self.Get_font(text_size)
        img: pg.Surface = font.render(text, True, text_color)
        self.screen.blit(img, pos)


    def Transition_black_window(self, transition_to: str):
        self.transition_to = transition_to
        self.start_black_window = True
        # The actual transition will be handled in the transition-class in transition.py

    def Calculate_hud_zoom(self):
        # Check if HUD needs to be rescaled
        new_zoom: int
        if self.screen_size[0] < 700:
            new_zoom = 2
        elif self.screen_size[0] < 1600:
            new_zoom = 3
        elif self.screen_size[0] < 2400:
            new_zoom = 4
        else:
            new_zoom = 5

        if self.hud_zoom != new_zoom:
            self.hud_zoom = new_zoom
            logging.info(f"HUD zoom changed to {self.hud_zoom}")

        # Check for the tile-map to change
        # 18x32 ratio for everything.
        # on right side -> 8 for the shop
        # 1 on the top -> header / HUD
        # tile_map: 17x24
        new_tile_zoom: int
        tile_screen: tuple[int, int] = (self.screen_size[0]//8, self.screen_size[1]//8)
        for i in range(10, 0, -1):
            if tile_screen[0] >= 32*i and tile_screen[1] >= 18*i:
                new_tile_zoom = i
                break

        
        if self.tile_zoom != new_tile_zoom:
            self.tile_zoom = new_tile_zoom
            logging.info(f"Tile zoom changed to {self.tile_zoom}")
            

    def Start_new_game(self, map_file_name: str = "") -> None:
        if self.difficulty == "":
            logging.error("Difficulty not set")
            return

        # Difficulty settings
        match self.difficulty:
            case "easy":
                self.cost_multiplier = 0.8
                self.health = 200
            case "medium":
                self.cost_multiplier = 1.0
                self.health = 150
            case "hard":
                self.cost_multiplier = 1.2
                self.health = 100
            case "hacker":
                self.cost_multiplier = 1.5
                self.health = 1
            case _:
                logging.error("Difficulty setting invalid")
                return
            
        self.map_file_name = map_file_name
        self.load_game = True

            
        # Start the game
        self.Transition_black_window("game")

    def Next_wave(self) -> None:
        """
        Starts the next wave
        """
        self.wave += 1
        self.running_wave = True
        self.new_wave = True
        self.enemies = {}
        logging.info(f"Wave {self.wave} started")

    def Wave_finished(self) -> None:
        """
        Called when the wave is finished
        """
        self.running_wave = False
        logging.info(f"Wave {self.wave} finished")

        if self.auto_wave:
            self.Next_wave()


def Avg(elements: list[float]) -> float:
    """
    Returns the average of the given elements.
    """
    if len(elements) == 0:
        return 0.0
    return sum(elements) / len(elements)

def Avg_worst_10_percent(elements: list[float]) -> float:
    """
    Returns the average of the given elements, but only the 10% worst element
    """
    elements = elements.copy()
    if len(elements) == 0:
        return 0.0
    elements.sort()
    elements = elements[int(len(elements)*0.9):]
    return sum(elements) / len(elements)
