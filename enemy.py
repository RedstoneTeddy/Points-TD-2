import data_class
import pygame as pg
import logging
import tile_map

class Enemy:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.current_tile_zoom: int = 1

        self.__enemy_tick_clock: int = 0

        self.enemies: list[data_class.Enemy_data] = []

        self.original_enemy_images: dict[int, pg.Surface] = {
            1: pg.image.load("images/enemies/1.png").convert_alpha(),
            2: pg.image.load("images/enemies/2.png").convert_alpha(),
            3: pg.image.load("images/enemies/3.png").convert_alpha(),
            4: pg.image.load("images/enemies/4.png").convert_alpha(),
            5: pg.image.load("images/enemies/5.png").convert_alpha(),
            10: pg.image.load("images/enemies/10.png").convert_alpha(),
            20: pg.image.load("images/enemies/20.png").convert_alpha(),
            30: pg.image.load("images/enemies/30.png").convert_alpha(),
            40: pg.image.load("images/enemies/40.png").convert_alpha(),
            50: pg.image.load("images/enemies/50.png").convert_alpha(),
            100: pg.image.load("images/enemies/100.png").convert_alpha(),
            200: pg.image.load("images/enemies/200.png").convert_alpha(),
            300: pg.image.load("images/enemies/300.png").convert_alpha(),
            400: pg.image.load("images/enemies/400.png").convert_alpha(),
            500: pg.image.load("images/enemies/500.png").convert_alpha(),
            1000: pg.image.load("images/enemies/1000.png").convert_alpha()
        }

        self.enemy_images: dict[int, pg.Surface] = {}
        self.Scale_enemy_images(True)

    def Scale_enemy_images(self, force_scaling: bool = False) -> None:
        """
        Scales the enemy images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_enemy_images.keys():
                self.enemy_images[key] = pg.transform.scale(self.original_enemy_images[key], (self.data.tile_zoom*8, self.data.tile_zoom*8))
            self.current_tile_zoom = self.data.tile_zoom

    def Show_enemies(self) -> None:
        self.Scale_enemy_images()
        for enemy in self.enemies:

            # Get the enemy type => enemy img
            enemy_type: int = 0
            if enemy["health"] == 1:
                enemy_type = 1
            elif enemy["health"] == 2:
                enemy_type = 2
            elif enemy["health"] == 3:
                enemy_type = 3
            elif enemy["health"] == 4:
                enemy_type = 4
            elif enemy["health"] == 5:
                enemy_type = 5
            elif enemy["health"] > 5 and enemy["health"] <= 10:
                enemy_type = 10
            elif enemy["health"] > 10 and enemy["health"] <= 20:
                enemy_type = 20
            elif enemy["health"] > 20 and enemy["health"] <= 30:
                enemy_type = 30
            elif enemy["health"] > 30 and enemy["health"] <= 40:
                enemy_type = 40
            elif enemy["health"] > 40 and enemy["health"] <= 50:
                enemy_type = 50
            elif enemy["health"] > 50 and enemy["health"] <= 100:
                enemy_type = 100
            elif enemy["health"] > 100 and enemy["health"] <= 200:
                enemy_type = 200
            elif enemy["health"] > 200 and enemy["health"] <= 300:
                enemy_type = 300
            elif enemy["health"] > 300 and enemy["health"] <= 400:
                enemy_type = 400
            elif enemy["health"] > 400 and enemy["health"] <= 500:
                enemy_type = 500
            elif enemy["health"] > 500 and enemy["health"] <= 1000:
                enemy_type = 1000
            else:
                logging.error(f"Enemy health {enemy['health']} is not valid")
                enemy_type = 1

            # Enemy pixel position
            enemy_pos: tuple[int, int] = (int((enemy["pos"][0]-0.5)*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((enemy["pos"][1]-0.5+1)*self.data.tile_zoom*8))
            
            # Draw the enemy
            self.data.screen.blit(self.enemy_images[enemy_type], enemy_pos)


    def Tick_enemy_walk(self) -> None:
        """
        Moves the enemies one tile forward
        """
        self.__enemy_tick_clock += 1
        if self.__enemy_tick_clock >= 2:
            self.__enemy_tick_clock = 0
            for enemy in self.enemies:
                enemy["pos_i"] += 1
                if enemy["pos_i"] < len(self.tile_map_obj.enemy_path):
                    enemy["pos"] = self.tile_map_obj.enemy_path[enemy["pos_i"]]
                else:
                    logging.error(f"Enemy {enemy} reached the end of the path")
            
    def Add_enemy(self, health: int) -> None:
        """
        Adds an enemy to the list
        """
        if health <= 0:
            logging.error(f"Enemy health {health} is not valid")
            return
        

        enemy: data_class.Enemy_data = {
            "health": health,
            "pos": (0.0, 0.0),
            "pos_i": 0
        }
        self.enemies.append(enemy)
