from typing import TypedDict, List, NotRequired, Literal, Mapping, Any
import pygame as pg
import logging
import pickle


class Enemy_data(TypedDict):
    health: int
    special: str
    pos_i: int
    pos: tuple[float, float] # This is the center of the tile
    slow_timer: int

class Wave_enemy(TypedDict):
    health: int
    spawn_time: int
    special: str

class Upgrade_data(TypedDict):
    name: str
    cost: int
    description: list[str]
    original_img: pg.Surface
    img: pg.Surface
    y_pos: Literal[0,1,2]
    requirement: str
    is_master: bool


Buildable_tiles: List[int] = [1,2,3,4,5,6]
Path_tiles: List[int] = [11,12,13,14,15]

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
        # default: a shoot-ready tower with no target in range will wait +1 tick  before checking again
        # extreme: a shoot-ready tower with no target in range will wait +2 ticks before checking again
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
        self.is_in_map_select: bool = False

        # For (initially) loading the game
        self.load_game: bool = False
        self.map_file_name: str = ""

        self.hud_zoom: int = 1
        self.tile_zoom: int = 2

        # Game Variables
        self.running_wave: bool = False
        self.tick_tower_wave_finished: bool = False
        self.health: int = 0
        self.enemies: dict[str, Enemy_data] = {} # UUID: Enemy_data
        self.fast_forward: bool = False
        self.auto_wave: bool = False
        self.new_wave: bool = False
        self.wave: int = 0
        self.money: int = 0
        self.regeneration: int = 0

        self.special_enemy_spawn_uuid_counter: int = 0

        self.currently_building: str = ""
        self.tower_selected: int = -1

        # Easy, Medium, Hard are normal difficulties
        # Hacker, Inflation are challenges
        self.difficulty: Literal["", "easy", "medium", "hard", "hacker", "inflation"] = ""
        self.cost_multiplier: float = 1.0 # Gets set, when the game starts, reads the data.difficulty variable

        # Tower images
        self.original_tower_images: dict[str, dict[str, pg.Surface]] = {
            "upgrades": {
                "hover": pg.image.load("images/towers/upgrades/hover.png").convert_alpha(),
                "master_upgrade": pg.image.load("images/towers/upgrades/master_upgrade.png").convert_alpha(),
                "master_blocked": pg.image.load("images/towers/upgrades/master_blocked.png").convert_alpha(),
                "big_range": pg.image.load("images/towers/upgrades/big_range.png").convert_alpha(),
                "double_kill": pg.image.load("images/towers/upgrades/double_kill.png").convert_alpha(),
                "fast_machine": pg.image.load("images/towers/upgrades/fast_machine.png").convert_alpha(),
                "faster_shooting": pg.image.load("images/towers/upgrades/faster_shooting.png").convert_alpha(),
                "more_range": pg.image.load("images/towers/upgrades/more_range.png").convert_alpha(),
                "sharper": pg.image.load("images/towers/upgrades/sharper.png").convert_alpha(),
                "sharper+": pg.image.load("images/towers/upgrades/sharper+.png").convert_alpha(),
                "sharper_shuriken": pg.image.load("images/towers/upgrades/sharper_shuriken.png").convert_alpha(),
                "shorter_cooldown": pg.image.load("images/towers/upgrades/shorter_cooldown.png").convert_alpha(),
                "bigger_bomb": pg.image.load("images/towers/upgrades/bigger_bomb.png").convert_alpha(),
                "blast_radius": pg.image.load("images/towers/upgrades/blast_radius.png").convert_alpha(),
                "lead_shots": pg.image.load("images/towers/upgrades/lead_shots.png").convert_alpha(),
                "flash_explosion": pg.image.load("images/towers/upgrades/flash_explosion.png").convert_alpha(),
                "pushback": pg.image.load("images/towers/upgrades/pushback.png").convert_alpha(),
                "pushback+": pg.image.load("images/towers/upgrades/pushback+.png").convert_alpha(),
                "regenerate": pg.image.load("images/towers/upgrades/regenerate.png").convert_alpha(),
                "atomic_bomb": pg.image.load("images/towers/upgrades/atomic_bomb.png").convert_alpha(),
                "money": pg.image.load("images/towers/upgrades/money.png").convert_alpha(),
                "money+": pg.image.load("images/towers/upgrades/money+.png").convert_alpha(),
                "percent": pg.image.load("images/towers/upgrades/percent.png").convert_alpha()
            },
            
            "ninja" : {
                "up": pg.image.load("images/towers/ninja/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/ninja/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/ninja/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/ninja/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/ninja/projectile.png").convert_alpha()
            },
            "sniper" : {
                "up": pg.image.load("images/towers/sniper/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/sniper/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/sniper/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/sniper/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/sniper/projectile.png").convert_alpha()
            },
            "machine_gunner": {
                "up": pg.image.load("images/towers/machine_gunner/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/machine_gunner/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/machine_gunner/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/machine_gunner/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/machine_gunner/projectile.png").convert_alpha()
            },
            "bomber": {
                "up": pg.image.load("images/towers/bomber/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/bomber/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/bomber/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/bomber/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/bomber/projectile.png").convert_alpha()
            },
            "magician": {
                "up": pg.image.load("images/towers/magician/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/magician/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/magician/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/magician/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/magician/projectile.png").convert_alpha()
            },
            "shooter": {
                "up": pg.image.load("images/towers/shooter/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/shooter/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/shooter/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/shooter/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/shooter/projectile.png").convert_alpha(),
                "shop_img": pg.image.load("images/towers/shooter/shop_img.png").convert_alpha()
            },

            "tower_hud": {
                "target_prio": pg.image.load("images/hud/target_prio.png").convert_alpha(),
                "target_prio_hover": pg.image.load("images/hud/target_prio_hover.png").convert_alpha(),
                "target_prio_selected": pg.image.load("images/hud/target_prio_selected.png").convert_alpha(),
                "close_button": pg.image.load("images/hud/close_button.png").convert_alpha(),
                "close_button_hover": pg.image.load("images/hud/close_button_hover.png").convert_alpha()
            },
            "bank": {
                "up": pg.image.load("images/towers/bank/normal.png").convert_alpha(),
                "left": pg.transform.rotate(pg.image.load("images/towers/bank/normal.png").convert_alpha(), 90),
                "down": pg.transform.rotate(pg.image.load("images/towers/bank/normal.png").convert_alpha(), 180),
                "right": pg.transform.rotate(pg.image.load("images/towers/bank/normal.png").convert_alpha(), 270),
                "projectile": pg.image.load("images/towers/bank/projectile.png").convert_alpha()
            },
            "spikes": {
                "normal1": pg.image.load("images/towers/spikes/normal1.png").convert_alpha(),
                "normal2": pg.image.load("images/towers/spikes/normal2.png").convert_alpha(),
                "normal3": pg.image.load("images/towers/spikes/normal3.png").convert_alpha(),
                "normal4": pg.image.load("images/towers/spikes/normal4.png").convert_alpha(),
                "normal5": pg.image.load("images/towers/spikes/normal5.png").convert_alpha(),
                "hot1": pg.image.load("images/towers/spikes/hot1.png").convert_alpha(),
                "hot2": pg.image.load("images/towers/spikes/hot2.png").convert_alpha(),
                "hot3": pg.image.load("images/towers/spikes/hot3.png").convert_alpha(),
                "hot4": pg.image.load("images/towers/spikes/hot4.png").convert_alpha(),
                "hot5": pg.image.load("images/towers/spikes/hot5.png").convert_alpha(),
                "shop_img": pg.image.load("images/towers/spikes/shop_img.png").convert_alpha()
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
                self.cost_multiplier = 0.85
                self.health = 200
                self.money = 800
            case "medium":
                self.cost_multiplier = 1.0
                self.health = 150
                self.money = 700
            case "hard":
                self.cost_multiplier = 1.15
                self.health = 100
                self.money = 600
            case "hacker":
                self.cost_multiplier = 1.3
                self.health = 1
                self.money = 600
                self.wave = 2
            case "inflation":
                self.cost_multiplier = 1.0
                self.health = 100
                self.money = 700
            case _:
                logging.error("Difficulty setting invalid")
                return
            
        self.tower_selected = -1
        self.currently_building = ""
        self.map_file_name = map_file_name
        self.load_game = True
        self.regeneration = 0

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
        self.health += self.regeneration # Regeneration from magician towers
        logging.info(f"Wave {self.wave} started")
        if self.difficulty == "inflation":
            self.cost_multiplier = round(self.cost_multiplier * 1.01, 4) # Increase cost multiplier by 1% each wave

    def Wave_finished(self) -> None:
        """
        Called when the wave is finished
        """
        self.running_wave = False
        self.money += 100
        self.tick_tower_wave_finished = True
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
