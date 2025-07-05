import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Bomber(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "bomber", 2, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["bomber"]["up"],
            "left": self.data.original_tower_images["bomber"]["left"],
            "down": self.data.original_tower_images["bomber"]["down"],
            "right": self.data.original_tower_images["bomber"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["bomber"]["projectile"]

        # Tower stats
        self.range: float = 3.3
        self.shooting_speed: int = 46
        self.projectile_speed: float = 0.4
        self.projectile_damage: int = 2
        self.multi_hit_range = 1.3
        self.multi_hits_max = 3
        self.can_pop_lead: bool = True
        self.can_pop_anti_explosion: bool = False

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "bigger_bomb", "cost": 680, "requirement": "", "y_pos": 0, "is_master": False,
             "description": ["Bigger Bomb"], "original_img": data.original_tower_images["upgrades"]["bigger_bomb"], "img": pg.Surface((24,24))},
            {"name": "blast_radius", "cost": 520, "requirement": "", "y_pos": 1, "is_master": False,
             "description": ["Bigger Blast Radius"], "original_img": data.original_tower_images["upgrades"]["blast_radius"], "img": pg.Surface((24,24))},
            {"name": "shorter_cooldown", "cost": 270, "requirement": "", "y_pos": 2, "is_master": False,
             "description": ["Shorter Cooldown"], "original_img": data.original_tower_images["upgrades"]["shorter_cooldown"], "img": pg.Surface((24,24))},
            {"name": "bigger_range", "cost": 690, "requirement": "blast_radius", "y_pos": 1, "is_master": True,
             "description": ["Fast Rockets", "+ bigger range", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["big_range"], "img": pg.Surface((24,24))},
            {"name": "atomic_bomb", "cost": 1600, "requirement": "bigger_bomb", "y_pos": 0, "is_master": True,
             "description": ["Nuclear Bomb", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["atomic_bomb"], "img": pg.Surface((24,24))},
        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "bigger_bomb":
                self.projectile_damage += 2
            case "blast_radius":
                self.multi_hit_range = 1.6
                self.multi_hits_max = 5
            case "shorter_cooldown":
                self.shooting_speed -= 8
            case "bigger_range":
                self.range += 1.6
                self.shooting_speed -= 8
            case "atomic_bomb":
                self.multi_hits_max += 2
                self.multi_hit_range += 0.2
                self.projectile_damage += 4


        