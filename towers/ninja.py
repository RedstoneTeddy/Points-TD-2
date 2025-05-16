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
        self.range: float = 4
        self.shooting_speed: int = 20
        self.projectile_speed: float = 0.5
        self.projectile_damage: int = 1
        self.multi_hit_range = 1.0
        self.multi_hits_max = 1

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "sharper_shuriken", "cost": 200, "requirement": "", "y_pos": 0,  "is_master": False,
             "description": ["Sharper Shurikens"], "original_img": data.original_tower_images["upgrades"]["sharper_shuriken"], "img": pg.Surface((24,24))},
            {"name": "double_kill", "cost": 350, "requirement": "sharper_shuriken", "y_pos": 0,  "is_master": True,
             "description": ["Double Kill Possibility", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["double_kill"], "img": pg.Surface((24,24))},
            {"name": "more_range", "cost": 100, "requirement": "", "y_pos": 1,  "is_master": False,
             "description": ["Bigger Range"], "original_img": data.original_tower_images["upgrades"]["more_range"], "img": pg.Surface((24,24))},
            {"name": "lead_pop", "cost": 150, "requirement": "more_range", "y_pos": 1, "is_master": True,
             "description": ["Can damage", "lead points"], "original_img": data.original_tower_images["upgrades"]["lead_shots"], "img": pg.Surface((24,24))},
            {"name": "shorter_cooldown", "cost": 150, "requirement": "", "y_pos": 2,  "is_master": False,
             "description": ["Shorter Cooldown"], "original_img": data.original_tower_images["upgrades"]["shorter_cooldown"], "img": pg.Surface((24,24))}
        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "sharper_shuriken":
                self.projectile_damage += 1
            case "double_kill":
                self.multi_hit_range = 1.0
                self.multi_hits_max = 2
            case "more_range":
                self.range += 1
            case "shorter_cooldown":
                self.shooting_speed -= 8
            case "lead_pop":
                self.can_pop_lead = True


        