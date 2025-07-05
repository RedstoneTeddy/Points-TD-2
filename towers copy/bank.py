import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Bank(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "bank", 2, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["bank"]["up"],
            "left": self.data.original_tower_images["bank"]["left"],
            "down": self.data.original_tower_images["bank"]["down"],
            "right": self.data.original_tower_images["bank"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["bank"]["projectile"]

        # Tower stats
        self.range: float = 0
        self.shooting_speed: int = -1
        self.projectile_speed: float = 1
        self.projectile_damage: int = 1
        self.multi_hit_range = 1.0
        self.multi_hits_max = 1

        self.bank_money: int = 50
        self.interest_rate: int = 0

        # Bank possible master upgrade: +0.2% interest to your total amount of money at end of round

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "money1", "cost": 500, "requirement": "", "y_pos": 0,  "is_master": False,
             "description": ["More Money!", "+30$ per Round"], "original_img": data.original_tower_images["upgrades"]["money"], "img": pg.Surface((24,24))},
            {"name": "money2", "cost": 500, "requirement": "", "y_pos": 1,  "is_master": False,
             "description": ["More Money!", "+30$ per Round"], "original_img": data.original_tower_images["upgrades"]["money"], "img": pg.Surface((24,24))},
            {"name": "money3", "cost": 500, "requirement": "", "y_pos": 2,  "is_master": False,
             "description": ["More Money!", "+30$ per Round"], "original_img": data.original_tower_images["upgrades"]["money"], "img": pg.Surface((24,24))},
            {"name": "money+", "cost": 1500, "requirement": "money1", "y_pos": 0,  "is_master": True,
             "description": ["Money Overload", "+100$ per Round", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["money+"], "img": pg.Surface((24,24))},
            {"name": "interest", "cost": 1500, "requirement": "money2", "y_pos": 1,  "is_master": True,
             "description": ["+1% Interest on", "your money", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["percent"], "img": pg.Surface((24,24))},
             
             
        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "money1" | "money2" | "money3":
                self.bank_money += 30
            case "money+":
                self.bank_money += 100
            case "interest":
                self.interest_rate += 1

    def Show_target_priority(self) -> None:
        pass # Removes the target priority indicator for the bank

    def Wave_finished(self) -> None:
        """
        Resets the tower for the next wave
        """
        super().Wave_finished()
        self.data.money += self.bank_money
        if self.interest_rate > 0:
            self.data.money += int(self.data.money * (self.interest_rate / 100))


        