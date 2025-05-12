from typing import TypedDict, List, NotRequired, Literal, Mapping, Any
import pygame as pg
import logging
import pickle


class Data_class:
    def __init__(self):

        self.screen: pg.Surface = pg.display.set_mode((800,600), pg.RESIZABLE|pg.SHOWN|pg.DOUBLEBUF)
        self.clock: pg.time.Clock = pg.time.Clock()
        self.run: bool = True
        self.screen_size: tuple[int, int] = (800, 600)
        self.resize: bool = False
        self.fullscreen: bool = False
        self.mouse_wheel: Literal["up", "down", ""] = ""
        self.__font_objects: dict[str, pg.font.Font] = {}

        self.transition_to: str = ""
        self.start_black_window: bool = False
        self.ongoing_transition: bool = False

        # Current menu / game state
        self.is_in_main_menu: bool = True
        self.is_in_game: bool = False

        self.hud_zoom: int = 1

        self.difficulty: Literal["", "easy", "medium", "hard", "hacker"] = ""
        self.cost_multiplier: float = 1.0 # Gets set, when the game starts, reads the data.difficulty variable

        
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

    def Start_new_game(self):
        if self.difficulty == "":
            logging.warning("Difficulty not set")
            return

        # Difficulty settings
        match self.difficulty:
            case "easy":
                self.cost_multiplier = 0.8
            case "medium":
                self.cost_multiplier = 1.0
            case "hard":
                self.cost_multiplier = 1.2
            case "hacker":
                self.cost_multiplier = 1.5
            case _:
                logging.error("Difficulty setting invalid")
                return
            
        # Start the game
        self.Transition_black_window("game")


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