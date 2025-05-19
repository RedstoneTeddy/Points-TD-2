import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Magician(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "magician", 2, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["magician"]["up"],
            "left": self.data.original_tower_images["magician"]["left"],
            "down": self.data.original_tower_images["magician"]["down"],
            "right": self.data.original_tower_images["magician"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["magician"]["projectile"]

        # Tower stats
        self.range: float = 4.0
        self.shooting_speed: int = 25
        self.projectile_speed: float = 0.7
        self.projectile_damage: int = 2
        self.multi_hit_range = 1.5
        self.multi_hits_max = 1

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "lead_pop", "cost": 400, "requirement": "", "y_pos": 0, "is_master": False,
             "description": ["Can damage", "lead points", "+1 Damage"], "original_img": data.original_tower_images["upgrades"]["lead_shots"], "img": pg.Surface((24,24))},
            {"name": "flash_explosion", "cost": 600, "requirement": "", "y_pos": 1, "is_master": False,
             "description": ["Flash Explosion", "+1 Damage"], "original_img": data.original_tower_images["upgrades"]["flash_explosion"], "img": pg.Surface((24,24))},
            {"name": "pushback", "cost": 800, "requirement": "slow_down", "y_pos": 2, "is_master": True,
             "description": ["Pushback"], "original_img": data.original_tower_images["upgrades"]["pushback+"], "img": pg.Surface((24,24))},
            {"name": "regeneration", "cost": 600, "requirement": "flash_explosion", "y_pos": 1, "is_master": True,
             "description": ["Regenerate 1 Health", "per Round", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["regenerate"], "img": pg.Surface((24,24))},
            {"name": "slow_down", "cost": 500, "requirement": "", "y_pos": 2, "is_master": False,
             "description": ["Slows down Points", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["pushback"], "img": pg.Surface((24,24))},

        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "lead_pop":
                self.projectile_damage += 1
                self.can_pop_lead = True
            case "flash_explosion":
                self.projectile_damage += 1
                self.multi_hit_range = 1.5
                self.multi_hits_max = 2
            case "pushback":
                pass # Pushback effect is actually handled in the parent-class
            case "regeneration":
                self.data.regeneration += 1
            case "slow_down":
                pass # Slow down effect is actually handled in the parent-class


        