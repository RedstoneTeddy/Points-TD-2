import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Machine_gunner(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "machine_gunner", 2, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["machine_gunner"]["up"],
            "left": self.data.original_tower_images["machine_gunner"]["left"],
            "down": self.data.original_tower_images["machine_gunner"]["down"],
            "right": self.data.original_tower_images["machine_gunner"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["machine_gunner"]["projectile"]

        # Tower stats
        self.range: float = 3.6
        self.shooting_speed: int = 13
        self.projectile_speed: float = 0.7
        self.projectile_damage: int = 1
        self.multi_hit_range = 1
        self.multi_hits_max = 1

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "fast_machine", "cost": 240, "requirement": "", "y_pos": 0, "is_master": False,
             "description": ["Faster shooting"], "original_img": data.original_tower_images["upgrades"]["fast_machine"], "img": pg.Surface((24,24))},
            {"name": "more_range", "cost": 100, "requirement": "", "y_pos": 1, "is_master": False,
             "description": ["Bigger Range"], "original_img": data.original_tower_images["upgrades"]["more_range"], "img": pg.Surface((24,24))},
            {"name": "sharper", "cost": 400, "requirement": "", "y_pos": 2, "is_master": False,
             "description": ["Sharper Shots"], "original_img": data.original_tower_images["upgrades"]["sharper"], "img": pg.Surface((24,24))},
            {"name": "ray_of_shots", "cost": 900, "requirement": "fast_machine", "y_pos": 0, "is_master": True,
             "description": ["Ray of Shots", "FAAAST", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["faster_shooting"], "img": pg.Surface((24,24))},
            {"name": "hot_shots", "cost": 800, "requirement": "sharper", "y_pos": 2, "is_master": True,
             "description": ["Hot (deadly) Shots", "Can damage lead points", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["lead_shots"], "img": pg.Surface((24,24))},

            

        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "fast_machine":
                self.shooting_speed -= 4
            case "more_range":
                self.range += 0.8
            case "sharper":
                self.projectile_damage += 1
            case "ray_of_shots":
                self.projectile_speed = 1.1
                self.shooting_speed = 6
            case "hot_shots":
                self.projectile_damage += 2
                self.shooting_speed += 1
                self.can_pop_lead = True


        