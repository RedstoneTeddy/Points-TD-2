import pygame as pg
import logging
import data_class
import random

class Transition:
    def __init__(self, data: data_class.Data_class) -> None:
        self.data: data_class.Data_class = data

        self.original_img: dict[str, list[pg.Surface]] = {
            "black_window": [pg.image.load(f"images/transistion/black_window/black{i}.png").convert_alpha() for i in range(1, 10)]
        }

        self.img: dict[str, list[pg.Surface]] = {}
        self.Resize_for_screen()

        self.black_window_timer: int = 0
        self.transition_to: str = ""


    def Resize_for_screen(self):
        size = self.data.screen_size
        for key in self.original_img:
            self.img[key] = [pg.transform.scale(img, size) for img in self.original_img[key]]


    def Render(self):
        if self.data.resize:
            self.Resize_for_screen()

        if self.data.start_black_window:
            self.black_window_timer = 1
            self.data.start_black_window = False
            self.transition_to = self.data.transition_to
            self.data.ongoing_transition = True

        
        # Black Window Transition
        if self.black_window_timer > 0:
            img_to_blit: int
            match self.black_window_timer:
                case 1 | 2 | 36 | 37:
                    img_to_blit = 0
                case 3 | 4 | 34 | 35:
                    img_to_blit = 1
                case 5 | 6 | 32 | 33:
                    img_to_blit = 2
                case 7 | 8 | 30 | 31:
                    img_to_blit = 3
                case 9 | 10 | 28 | 29:
                    img_to_blit = 4
                case 11 | 12 | 26 | 27:
                    img_to_blit = 5
                case 13 | 14 | 24 | 25: 
                    img_to_blit = 6
                case 15 | 16 | 22 | 23:
                    img_to_blit = 7
                case 17 | 18 | 19 | 20 | 21:
                    img_to_blit = 8
                
            # Check that mouse is not pressed
            if self.black_window_timer == 18:
                if not pg.mouse.get_pressed()[0]:
                    self.black_window_timer += 1
            else:
                self.black_window_timer += 1

            # End transition
            if self.black_window_timer == 39:
                self.black_window_timer = 0
                self.data.transition_to = ""   
                self.data.ongoing_transition = False        

            if self.black_window_timer == 20: # Load new screen
                # Set every other game state to false
                self.data.is_in_main_menu = False
                self.data.is_in_game = False

                # Set the new game state to true
                match self.transition_to:
                    case "main_menu":
                        self.data.is_in_main_menu = True
                    case "game":
                        self.data.is_in_game = True
                    case "_":
                        logging.error(f"Unknown transition to {self.transition_to}")

                logging.info(f"Transitioned to {self.transition_to}")
            if self.black_window_timer <= 37 and self.black_window_timer >= 1:
                self.data.screen.blit(self.img["black_window"][img_to_blit], (0, 0))

            

        



    