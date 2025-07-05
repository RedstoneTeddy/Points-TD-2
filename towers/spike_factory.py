import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower
import towers.spikes
import random

class Spike_factory(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int], spikes_list: list[towers.spikes.Spikes]) -> None:
        super().__init__(data, tile_map_obj, "spike_factory", 2, pos)
        self.__shoot_waiting_timer: int = 0

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["spike_factory"]["up"],
            "left": self.data.original_tower_images["spike_factory"]["left"],
            "down": self.data.original_tower_images["spike_factory"]["down"],
            "right": self.data.original_tower_images["spike_factory"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["spike_factory"]["projectile"]

        # Tower stats
        self.range: float = 3.0
        self.shooting_speed: int = 65
        self.projectile_speed: float = 1
        self.projectile_damage: int = 0
        self.multi_hit_range = 1.0
        self.multi_hits_max = 1

        self.spike_health: int = 5
        self.spike_lifetime: int = 60 *10 # 15 seconds
        self.spike_persist_round: bool = False
        self.spike_is_hot: bool = False

        self.spikes_list: list[towers.spikes.Spikes] = spikes_list

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "sharper", "cost": 780, "requirement": "", "y_pos": 0,  "is_master": False,
             "description": ["Double Spikes", "per pile!"], "original_img": data.original_tower_images["upgrades"]["sharper"], "img": pg.Surface((24,24))},
            {"name": "long_lasting", "cost": 400, "requirement": "", "y_pos": 1,  "is_master": False,
             "description": ["Spikes last longer",  "on the ground."], "original_img": data.original_tower_images["upgrades"]["shorter_cooldown"], "img": pg.Surface((24,24))},
            {"name": "faster", "cost": 500, "requirement": "", "y_pos": 2,  "is_master": False,
             "description": ["Faster shooting"], "original_img": data.original_tower_images["upgrades"]["faster_shooting"], "img": pg.Surface((24,24))},
            {"name": "hot", "cost": 500, "requirement": "sharper", "y_pos": 0,  "is_master": True,
             "description": ["Hot Spikes!", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["lead_shots"], "img": pg.Surface((24,24))},
            {"name": "persistent", "cost": 700, "requirement": "long_lasting", "y_pos": 1,  "is_master": True,
             "description": ["Long lasting", "Master Upgrade"], "original_img": data.original_tower_images["upgrades"]["shorter_cooldown"], "img": pg.Surface((24,24))}
        ]

        self.Scale_tower_images(True)

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "sharper":
                self.spike_health += 5
            case "long_lasting":
                self.spike_lifetime += 60 * 8 # +10 seconds
            case "faster":
                self.shooting_speed -= 20
            case "hot":
                self.spike_is_hot = True
            case "persistent":
                self.spike_persist_round = True
                self.spike_lifetime += 60 * 8 # +10 seconds



    def Show_target_priority(self) -> None:
        # No target priority for this tower
        pass


    def Tick(self) -> None:
        # Custom Tick function for the spike factory
        if self.projectile_timer > 0:
            self.projectile_timer -= 1
        else:
            if self.__shoot_waiting_timer > 0:
                self.__shoot_waiting_timer -= 1
            else:
                # Check possible positions 
                possible_positions: list[int] = []
                max_range: float = self.range **2

                for i, pos in enumerate(self.tile_map_obj.enemy_path):
                    if i%2==1:
                        continue
                    distance_squared: float = (self.center_pos[0] - pos[0]) **2 + (self.center_pos[1] - pos[1]) **2
                    if distance_squared <= max_range:
                        possible_positions.append(i)

                for placed_spike in self.spikes_list:
                    if placed_spike.pos_i in possible_positions:
                        possible_positions.remove(placed_spike.pos_i)

                if len(possible_positions) == 0:
                    if self.data.performance_saving_setting == "extreme":
                        self.__shoot_waiting_timer = 4
                    elif self.data.performance_saving_setting == "default":
                        self.__shoot_waiting_timer = 1
                    else:
                        self.__shoot_waiting_timer = 0
                else:
                    # Place a spike at a random position
                    pos_i: int = random.choice(possible_positions)
                    disappear_round: int = 0 # Diappear at the end of the round
                    if self.spike_persist_round:
                        disappear_round = -1
                    spike: towers.spikes.Spikes = towers.spikes.New_spike(
                        self.data, self.tile_map_obj, pos_i, self.spike_health, self.spike_lifetime, disappear_round, self.spike_is_hot
                    )
                    self.spikes_list.append(spike)
                    self.projectile_timer = self.shooting_speed
                    self.__shoot_waiting_timer = 0


                




        