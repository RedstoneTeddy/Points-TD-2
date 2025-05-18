import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Sniper(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "sniper", 2, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["sniper"]["up"],
            "left": self.data.original_tower_images["sniper"]["left"],
            "down": self.data.original_tower_images["sniper"]["down"],
            "right": self.data.original_tower_images["sniper"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["sniper"]["projectile"]

        # Tower stats
        self.range: float = 7.5
        self.shooting_speed: int = 50
        self.projectile_speed: float = 3
        self.projectile_damage: int = 3
        self.multi_hit_range = 1.0
        self.multi_hits_max = 1

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "big_range", "cost": 350, "requirement": "", "y_pos": 0, "is_master": False,
             "description": ["World Wide Shots"], "original_img": data.original_tower_images["upgrades"]["big_range"], "img": pg.Surface((24,24))},
            {"name": "faster_cooldown", "cost": 450, "requirement": "", "y_pos": 1,  "is_master": False,
             "description": ["Shorter Cooldown"], "original_img": data.original_tower_images["upgrades"]["shorter_cooldown"], "img": pg.Surface((24,24))},
            {"name": "sharper", "cost": 500, "requirement": "", "y_pos": 2, "is_master": False,
             "description": ["Sharper Shots"], "original_img": data.original_tower_images["upgrades"]["sharper"], "img": pg.Surface((24,24))},
            {"name": "sharper+", "cost": 800, "requirement": "sharper", "y_pos": 2, "is_master": True,
             "description": ["Very sharp Shots", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["sharper+"], "img": pg.Surface((24,24))},
            {"name": "fast", "cost": 700, "requirement": "faster_cooldown", "y_pos": 1, "is_master": True,
             "description": ["Semi-automatic rifle", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["faster_shooting"], "img": pg.Surface((24,24))}
        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "big_range":
                self.range = 25
            case "faster_cooldown":
                self.shooting_speed -= 15
            case "sharper":
                self.projectile_damage += 2
            case "sharper+":
                self.projectile_damage += 5
            case "fast":
                self.shooting_speed -= 15


        