import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Ninja(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "ninja", 2, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["ninja"]["up"],
            "left": self.data.original_tower_images["ninja"]["left"],
            "down": self.data.original_tower_images["ninja"]["down"],
            "right": self.data.original_tower_images["ninja"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["ninja"]["projectile"]

        # Tower stats
        self.range: int = 5
        self.shooting_speed: int = 30
        self.projectile_speed: float = 0.5
        self.projectile_damage: int = 1


        self.Scale_tower_images(True)

    



        