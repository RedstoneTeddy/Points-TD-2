import data_class
import pygame as pg
import logging

class Tile_map:
    def __init__(self, data: data_class.Data_class) -> None:
        self.data: data_class.Data_class = data
        self.map: list[list[int]] = []
        self.map_file_name: str = ""
        self.enemy_path: list[tuple[float, float]] = []

        self.__performance_update_timer: int = 0
        
        self.current_tile_zoom: int = 1

        self.original_tiles: dict[int, pg.Surface] = {
            -1: pg.image.load("images/tiles/hud_grid.png").convert_alpha(),
            0: pg.image.load("images/tiles/grid.png").convert_alpha(),

            1: pg.image.load("images/tiles/grass1.png").convert_alpha(),
            2: pg.image.load("images/tiles/grass2.png").convert_alpha(),
            3: pg.image.load("images/tiles/grass3.png").convert_alpha(),
            4: pg.image.load("images/tiles/grass4.png").convert_alpha(),
            5: pg.image.load("images/tiles/grass5.png").convert_alpha(),
            6: pg.image.load("images/tiles/grass6.png").convert_alpha(),

            11: pg.image.load("images/tiles/path1.png").convert_alpha(),
            12: pg.image.load("images/tiles/path2.png").convert_alpha(),
            13: pg.image.load("images/tiles/path3.png").convert_alpha(),
            14: pg.image.load("images/tiles/path4.png").convert_alpha(),
            15: pg.image.load("images/tiles/path5.png").convert_alpha(),

            101: pg.image.load("images/tiles/shop1.png").convert_alpha(),
            102: pg.image.load("images/tiles/shop2.png").convert_alpha(),
            103: pg.image.load("images/tiles/shop3.png").convert_alpha(),

            105: pg.image.load("images/tiles/shop5.png").convert_alpha(),
            106: pg.image.load("images/tiles/shop6.png").convert_alpha(),
            107: pg.image.load("images/tiles/shop7.png").convert_alpha(),
            108: pg.image.load("images/tiles/shop8.png").convert_alpha(),
            109: pg.image.load("images/tiles/shop9.png").convert_alpha()    
        }

        self.tile_images: dict[int, pg.Surface] = {}
        self.Scale_tiles(True)


    def Scale_tiles(self, force_scaling: bool = False) -> None:
        """
        Scales the tiles to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_tiles.keys():
                self.tile_images[key] = pg.transform.scale(self.original_tiles[key], (self.data.tile_zoom*8, self.data.tile_zoom*8))
            self.current_tile_zoom = self.data.tile_zoom



    def Show_grid(self) -> None:
        """
        Debug: Draws the grid on the screen
        """
        self.Scale_tiles()
        for y in range(18):
            for x in range(32):
                if y == 0 or x >= 24:
                    self.data.screen.blit(self.tile_images[-1], (x*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), y*self.data.tile_zoom*8))
                else:
                    self.data.screen.blit(self.tile_images[0], (x*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), y*self.data.tile_zoom*8))
    
    def Show_map(self) -> None:
        """
        Draws the map on the screen
        """
        if self.data.performance_saving_setting in ["none", "default"]:
            self.__performance_update_timer += 5
        self.__performance_update_timer += 5


        if self.__performance_update_timer >= 10:
            self.__performance_update_timer = 0
            self.Scale_tiles()
            for y in range(18):
                for x in range(32):
                    if y == 0 or x >= 24:
                        pass # Handled by self.Show_hud_background()
                    else:
                        try:
                            self.data.screen.blit(self.tile_images[self.map[y-1][x]], (x*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), y*self.data.tile_zoom*8))
                        except IndexError:
                            logging.error(f"IndexError in Map: {y}, {x}")
                        except KeyError:
                            logging.error(f"KeyError in Map: {y}, {x} -> Tile_ID: {self.map[y][x]}")
                        



    def Calculate_tile_pos_from_px_pos(self, px_pos: tuple[int, int], only_allow_map: bool = False) -> tuple[int, int]:
        """
        Calculates the tile position from the pixel position.
        If only_allow_map is True, it will only return the tile position if it is within the map bounds.
        It will also automatically calculate y-1, and return that (this will be directly used for the map)
        """
        output: tuple[int, int] = ((px_pos[0]-self.Get_left_right_empty_screen()) // (self.data.tile_zoom*8), px_pos[1] // (self.data.tile_zoom*8))
        if only_allow_map:
            output = (output[0], output[1] - 1)
            if output[0] < 0:
                output = (0, output[1])
            if output[1] < 0:
                output = (output[0], 0)
            if output[0] > 23:
                output = (23, output[1])
            if output[1] > 17:
                output = (output[0], 17)

        return output
    

    


    def Save_map_file(self, name: str = "") -> None:
        if name != "":
            self.map_file_name = name
        if self.map_file_name == "":
            logging.error("Map file name is empty. Cannot save map.")
            return
        try:
            import os
            import pickle

            # Check if the folder exists, otherwise create it
            if not os.path.exists("maps"):
                os.makedirs("maps")

            with open(f"maps/{self.map_file_name}.pkl", "wb") as file:
                pickle.dump((self.map, self.enemy_path), file)
                logging.info(f"Map successfully saved to 'maps/{self.map_file_name}.pkl'")
        except Exception as save_error:
            logging.error(f"Failed to save the map: {save_error}")


    def Load_map_file(self, name: str = "") -> None:
        if name != "":
            self.map_file_name = name
        if self.map_file_name == "":
            logging.error("Map file name is empty. Cannot load map.")
            return
        try:
            import pickle
            with open(f"maps/{self.map_file_name}.pkl", "rb") as file:
                file_contents = pickle.load(file)
                self.map, self.enemy_path = file_contents
                logging.info(f"Map successfully loaded from 'maps/{self.map_file_name}.pkl'")
        except Exception as load_error:
            logging.error(f"Failed to load the map: {load_error}")

    def Calculate_enemy_path(self, tile_nodes: list[tuple[int, int]]) -> None:
        """
        Calculates the enemy path ( .1) from the tile nodes
        """
        self.enemy_path = []
        for i in range(len(tile_nodes)-1):
            pos_from: tuple[float, float] = (tile_nodes[i][0] + 0.5, tile_nodes[i][1] + 0.5)
            pos_to: tuple[float, float] = (tile_nodes[i+1][0] + 0.5, tile_nodes[i+1][1] + 0.5)

            # Calculate the distance & number of steps
            step_size: float = 0.05
            distance: float = ((pos_to[0] - pos_from[0])**2 + (pos_to[1] - pos_from[1])**2)**0.5
            steps_needed: int = int(distance / step_size)

            # Calculate the step
            step: tuple[float, float] = (0.0, 0.0)
            if pos_from[0] > pos_to[0]:
                step = (-step_size, 0.0)
            elif pos_from[0] < pos_to[0]:
                step = (step_size, 0.0)
            if pos_from[1] > pos_to[1]:
                step = (0.0, -step_size)
            elif pos_from[1] < pos_to[1]:
                step = (0.0, step_size)
            
            # Walk all the steps
            for _ in range(steps_needed):
                pos_from = (pos_from[0] + step[0], pos_from[1] + step[1])
                self.enemy_path.append(pos_from)


    def Show_enemy_path(self) -> None:
        """
        Debug: Shows the enemy path on the map
        """
        if len(self.enemy_path) == 0:
            return
        
        # Calculate the gradient
        path_pos_colors: list[tuple[int, int, int]] = []
        gradient_endpoints: list[tuple[int, int, int]] = [(0, 255, 0), (255, 255, 0), (255, 0, 0)] 
        for i in range(len(self.enemy_path)):
            ratio = i / (len(self.enemy_path) - 1) if len(self.enemy_path) > 1 else 0
            start_color = gradient_endpoints[0]
            end_color = gradient_endpoints[-1]
            interpolated_color = (
            int(start_color[0] + ratio * (end_color[0] - start_color[0])),
            int(start_color[1] + ratio * (end_color[1] - start_color[1])),
            int(start_color[2] + ratio * (end_color[2] - start_color[2]))
            )
            path_pos_colors.append(interpolated_color)

        for i, path_pos in enumerate(self.enemy_path):
            pg.draw.circle(self.data.screen, path_pos_colors[i], (int(path_pos[0]*self.data.tile_zoom*8) + self.Get_left_right_empty_screen(), int((path_pos[1]+1)*self.data.tile_zoom*8)), int(self.data.tile_zoom/2+0.5))

    def Render_empty_screen_overlay(self) -> None:
        if self.__performance_update_timer == 0:
            used_screen: tuple[int, int] = (32*8*self.data.tile_zoom, 18*8*self.data.tile_zoom)
            # Left
            pg.draw.rect(self.data.screen, (100,180,255), (0, 0, self.Get_left_right_empty_screen(), self.data.screen_size[1]))
            # Right
            pg.draw.rect(self.data.screen, (100,180,255), (self.data.screen_size[0] - self.Get_left_right_empty_screen(), 0, self.Get_left_right_empty_screen()+1, self.data.screen_size[1]))
            # Bottom
            pg.draw.rect(self.data.screen, (100,180,255), (0, used_screen[1], self.data.screen_size[0], self.data.screen_size[1] - used_screen[1]))


    def Get_left_right_empty_screen(self) -> int:
        """
        Returns the left and right empty screen size
        """
        return (self.data.screen_size[0] - (32*8*self.data.tile_zoom)) // 2
    

    def Show_hud_background(self) -> None:
        """
        Shows the shop background
        """
        if self.__performance_update_timer == 0:
            self.Scale_tiles()
            for y in range(18):
                for x in range(32):
                    if y == 0:
                        self.data.screen.blit(self.tile_images[101], (x*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), y*self.data.tile_zoom*8))
                    elif x >= 24:
                        self.data.screen.blit(self.tile_images[105], (x*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), y*self.data.tile_zoom*8))

            # Background "Nails"
            self.data.screen.blit(self.tile_images[102], (0*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), 0*self.data.tile_zoom*8))
            self.data.screen.blit(self.tile_images[103], (31*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), 0*self.data.tile_zoom*8))

            self.data.screen.blit(self.tile_images[106], (24*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), 1*self.data.tile_zoom*8))
            self.data.screen.blit(self.tile_images[107], (31*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), 1*self.data.tile_zoom*8))
            self.data.screen.blit(self.tile_images[108], (31*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), 17*self.data.tile_zoom*8))
            self.data.screen.blit(self.tile_images[109], (24*self.data.tile_zoom*8 + self.Get_left_right_empty_screen(), 17*self.data.tile_zoom*8))


