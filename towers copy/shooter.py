import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Shooter(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "shooter", 1, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["shooter"]["up"],
            "left": self.data.original_tower_images["shooter"]["left"],
            "down": self.data.original_tower_images["shooter"]["down"],
            "right": self.data.original_tower_images["shooter"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["shooter"]["projectile"]

        # Tower stats
        self.range: float = 2.6
        self.shooting_speed: int = 30
        self.projectile_speed: float = 0.4
        self.projectile_damage: int = 1
        self.multi_hit_range = 1
        self.multi_hits_max = 1
        self.can_pop_lead: bool = False

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "shorter_cooldown", "cost": 200, "requirement": "", "y_pos": 0, "is_master": False,
             "description": ["Shorter Cooldown"], "original_img": data.original_tower_images["upgrades"]["shorter_cooldown"], "img": pg.Surface((24,24))},
            {"name": "more_range", "cost": 150, "requirement": "", "y_pos": 1,  "is_master": False,
             "description": ["Bigger Range"], "original_img": data.original_tower_images["upgrades"]["more_range"], "img": pg.Surface((24,24))}
        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "shorter_cooldown":
                self.shooting_speed -= 8
            case "more_range":
                self.range += 0.6


        