
import pygame as pg
import logging
import data_class


class Map_select:
    def __init__(self, data: data_class.Data_class) -> None:
        self.data: data_class.Data_class = data
        self.button_pressed: bool = False

        self.original_map_images: dict[str, pg.Surface] = {
            "grass_fields": pg.image.load("images/map_selection/grass_fields.png").convert_alpha(),
            "islands": pg.image.load("images/map_selection/islands.png").convert_alpha(),
            "u_turn": pg.image.load("images/map_selection/u_turn.png").convert_alpha(),
            "sea_wall": pg.image.load("images/map_selection/sea_wall.png").convert_alpha(),
            "frame": pg.image.load("images/map_selection/frame.png").convert_alpha(),
            "hover": pg.image.load("images/map_selection/hover.png").convert_alpha()
        }

        self.current_hud_zoom: int = 1
        self.map_images: dict[str, pg.Surface] = {}
        self.Scale_map_images(True)

    def Scale_map_images(self, force: bool = False) -> None:
        if self.current_hud_zoom != self.data.hud_zoom or force:
            self.map_images = {}
            for key, image in self.original_map_images.items():
                self.map_images[key] = pg.transform.scale(image, (int(image.get_width() * self.data.hud_zoom*2), int(image.get_height() * self.data.hud_zoom*2)))
            self.current_hud_zoom = self.data.hud_zoom


    def Render_map_select(self) -> None:
        self.Scale_map_images()

        # Draw the map images
        map_pos: dict[str, tuple[int, int]] = {
            "grass_fields": (0, 0),
            "u_turn": (1, 0),
            "islands": (2, 0),
            "sea_wall": (3, 0),
        }

        map_difficulty: dict[str, str] = {
            "grass_fields": "easy",
            "u_turn": "easy",
            "islands": "medium",
            "sea_wall": "hard"
        }

        map_zoom: int = self.data.hud_zoom * 2

        self.data.Draw_text("Select a map", 10 * self.data.hud_zoom, (255, 255, 255), (self.data.screen_size[0]//2 - 35*self.data.hud_zoom, 10*self.data.hud_zoom))

        for key, pos in map_pos.items():
            px_pos: tuple[int, int] = (self.data.screen_size[0] // 2 + (pos[0]-2) * 28*map_zoom, 20*map_zoom + pos[1] * 21*map_zoom)
            frame_px_pos: tuple[int, int] = (px_pos[0] - 1*map_zoom, px_pos[1] - 1*map_zoom)

            difficulty_color: tuple[int, int, int]
            if map_difficulty[key] == "easy":
                difficulty_color = (220,220,40)
            elif map_difficulty[key] == "medium":
                difficulty_color = (203, 120, 22)
            elif map_difficulty[key] == "hard":
                difficulty_color = (220, 50, 47)

            self.data.screen.blit(self.map_images[key], px_pos)
            if pg.mouse.get_pos()[0] > px_pos[0] and pg.mouse.get_pos()[0] < px_pos[0] + self.map_images[key].get_width() and pg.mouse.get_pos()[1] > px_pos[1] and pg.mouse.get_pos()[1] < px_pos[1] + self.map_images[key].get_height():
                self.data.screen.blit(self.map_images["hover"], frame_px_pos)
                self.data.Draw_text(f"Selected: {key.capitalize().replace("_", " ")}", 8 * self.data.hud_zoom, (220,220,40), (self.data.screen_size[0]//2 - 45*self.data.hud_zoom, 20*self.data.hud_zoom))
                self.data.Draw_text(f"Difficulty: {map_difficulty[key].capitalize()}", 8 * self.data.hud_zoom, difficulty_color, (self.data.screen_size[0]//2 - 45*self.data.hud_zoom, 28*self.data.hud_zoom))
                if pg.mouse.get_pressed()[0]:
                    if not self.button_pressed and not self.data.ongoing_transition:
                        self.button_pressed = True
                        self.data.Start_new_game(key)
                else:
                    self.button_pressed = False
            else:
                self.data.screen.blit(self.map_images["frame"], frame_px_pos)
        
