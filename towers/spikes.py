import data_class
import pygame as pg
import logging
import tile_map
import random

class Spikes:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos_i: int) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.pos_i: int = pos_i 
        self.tower_pos: tuple[float, float] = tile_map_obj.enemy_path[self.pos_i]

        self.original_tower_images: dict[str, pg.Surface] = {
            "normal1": self.data.original_tower_images["spikes"]["normal1"],
            "normal2": self.data.original_tower_images["spikes"]["normal2"],
            "normal3": self.data.original_tower_images["spikes"]["normal3"],
            "normal4": self.data.original_tower_images["spikes"]["normal4"],
            "normal5": self.data.original_tower_images["spikes"]["normal5"],
            "hot1": self.data.original_tower_images["spikes"]["hot1"],
            "hot2": self.data.original_tower_images["spikes"]["hot2"],
            "hot3": self.data.original_tower_images["spikes"]["hot3"],
            "hot4": self.data.original_tower_images["spikes"]["hot4"],
            "hot5": self.data.original_tower_images["spikes"]["hot5"]
        }
        self.tower_images: dict[str, pg.Surface] = {}

        self.tower_name: str = "spikes"
        self.tower_size: int = 1
        self.current_tile_zoom: int = 1

        self.disappear_round: int = -1 # -1 means never disappear
        self.__timer: int = 0
        self.lifetime: int = -1 # -1 means never disappear
        self.health: int = 20
        self.max_health: int = 20
        self.is_hot: bool = False
        self.__kill_timer: int = 0



    def Scale_tower_images(self, force_scaling: bool= False) -> None:
        if self.current_tile_zoom != self.tile_map_obj.current_tile_zoom or force_scaling:
            for key, image in self.original_tower_images.items():
                self.tower_images[key] = pg.transform.scale(image, (8 * self.tile_map_obj.current_tile_zoom,
                                                                    8 * self.tile_map_obj.current_tile_zoom))
            self.current_tile_zoom = self.tile_map_obj.current_tile_zoom



    def Show_spike(self) -> None:
        self.Scale_tower_images()
        tower_pos: tuple[int, int] = (int((self.tower_pos[0]-0.5)*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((self.tower_pos[1]+0.5)*self.data.tile_zoom*8))
        image_key: str
        if self.is_hot:
            image_key = "hot" + str(5-int(self.health / self.max_health * 4))
        else:
            image_key = "normal" + str(5-int(self.health / self.max_health * 4))
        self.data.screen.blit(self.tower_images[image_key], tower_pos)



    def Tick(self) -> bool:
        # Check for spike deletion
        deletion: bool = False
        if self.lifetime != -1:
            self.__timer += 1
            if self.__timer >= self.lifetime:
                deletion = True
        if self.health <= 0:
            deletion = True
        if self.disappear_round != -1:
            if self.data.wave >= self.disappear_round:
                deletion = True

        # Damagaging enemies
        if self.data.performance_saving_setting == "none":
            self.__kill_timer += 10
        elif self.data.performance_saving_setting == "default":
            self.__kill_timer += 4
        else: # Extreme
            self.__kill_timer += 1
        
        if self.__kill_timer >= 10 and deletion == False:
            self.__kill_timer = 0
            possible_enemies: list[str] = []
            # Search for enemies in range of the spikes
            for uuid, enemy in self.data.enemies.items():
                if enemy["pos_i"]+5 >= self.pos_i >= enemy["pos_i"]-5:
                    if enemy["health"] > 0:
                        if (enemy["special"] == "lead" and self.is_hot) or (enemy["special"] != "lead"):
                            possible_enemies.append(uuid)

            # Damage enemies
            for uuid in possible_enemies:
                if self.health <= 0:
                    deletion = True
                    break
                enemy: data_class.Enemy_data = self.data.enemies[uuid]
                dmg_to_enemy: int = self.health
                if enemy["health"] <= dmg_to_enemy:
                    dmg_to_enemy = enemy["health"]
                self.health -= dmg_to_enemy
                if self.health <= 0:
                    self.health = 0
                    

                    
                # Damage enemy
                health_before: int = enemy["health"]
                enemy["health"] -= dmg_to_enemy
                health_after: int = enemy["health"]
                if health_after <= 0:
                    health_after = 0
                    # Death of normal enemies and special enemies handling
                    if enemy["special"] not in ["stack", "stack+"]:
                        del self.data.enemies[uuid]
                    elif enemy["special"] == "stack":
                        health_after = 10
                    elif enemy["special"] == "stack+":
                        health_after = 20

                # Special enemies
                if health_after > 0:
                    if enemy["special"] == "lead":
                        if health_after <= 10:
                            enemy["special"] = ""
                            self.data.money -= 4
                    elif enemy["special"] == "anti_explosion":
                        if health_after <= 10:
                            enemy["special"] = ""
                            self.data.money -= 4
                    elif enemy["special"] == "stack":
                        if health_after <= 10:
                            self.data.money -= 4
                            spawn_pos_i: int = enemy["pos_i"]
                            if spawn_pos_i < 4:
                                spawn_pos_i = 4
                            # Spawn enemies from stack
                            Add_enemy(self.data, self.tile_map_obj, 20, "lead", spawn_pos_i)
                            Add_enemy(self.data, self.tile_map_obj, 20, "anti_explosion", spawn_pos_i-2)
                            Add_enemy(self.data, self.tile_map_obj, 10, "", spawn_pos_i-4)
                            # Delete stack enemy
                            del self.data.enemies[uuid]
                    elif enemy["special"] == "stack+":
                        if health_after <= 10:
                            self.data.money -= 6
                            spawn_pos_i: int = enemy["pos_i"]
                            if spawn_pos_i < 8:
                                spawn_pos_i = 10
                            # Spawn enemies from stack+
                            Add_enemy(self.data, self.tile_map_obj, 50, "", spawn_pos_i)
                            Add_enemy(self.data, self.tile_map_obj, 50, "", spawn_pos_i-2)
                            Add_enemy(self.data, self.tile_map_obj, 20, "lead", spawn_pos_i-4)
                            Add_enemy(self.data, self.tile_map_obj, 20, "anti_explosion", spawn_pos_i-6)
                            Add_enemy(self.data, self.tile_map_obj, 10, "", spawn_pos_i-8)
                            # Delete stack+ enemy
                            del self.data.enemies[uuid]
                    elif enemy["special"] == "":
                        if health_before > 10 and health_after <= 10: # Too much money in early game
                            self.data.money -= 1    
                        if health_before > 9 and health_after <= 9: # Too much money in early game
                            self.data.money -= 1    
                        if health_before > 8 and health_after <= 8: # Too much money in early game
                            self.data.money -= 1    

                # Rewarding Player
                if health_before <= 10: 
                    self.data.money += int(health_before - health_after) 
            
                # Pop ceramic
                if health_before > 10 and health_after <= 10:
                    self.data.money += 8
                
                # Pop 100
                if health_before > 51 and health_after <= 50:
                    self.data.money += 10
                # Pop 200
                if health_before > 101 and health_after <= 100:
                    self.data.money += 10
                # Pop 300
                if health_before > 201 and health_after <= 200:
                    self.data.money += 10
                # Pop 400
                if health_before > 301 and health_after <= 300:
                    self.data.money += 10
                # Pop 500
                if health_before > 401 and health_after <= 400:
                    self.data.money += 10
                # Pop 1000
                if health_before > 501 and health_after <= 500:
                    self.data.money += 50



        return deletion
    

    def Wave_finished(self) -> bool:
        """
        Resets the tower for the next wave
        """
        deletion: bool = False
        if self.health <= 0:
            deletion = True
        if self.disappear_round != -1:
            if self.data.wave+1 >= self.disappear_round:
                deletion = True
        return deletion
    

def New_spike(data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos_i: int, health: int, lifetime: int = -1, disappear_round: int = -1) -> Spikes:
    """
    Creates a new spike tower
    """
    new_spike: Spikes = Spikes(data, tile_map_obj, pos_i)

    new_spike.health = health
    new_spike.max_health = health
    new_spike.lifetime = lifetime
    new_spike.disappear_round = disappear_round

    return new_spike


def Convert_pos_to_path_i(tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> int:
    """
    Converts a position to the path index
    """
    path_i: int = -1
    spike_pos: tuple[float, float] = (round(pos[0]+0.5, 2), round(pos[1]+0.5, 2))
    for i in range(len(tile_map_obj.enemy_path)):
        enemy_pos: tuple[float, float] = (round(tile_map_obj.enemy_path[i][0], 2), round(tile_map_obj.enemy_path[i][1], 2))
        if enemy_pos == spike_pos:
            path_i = i
            break
    else:
        logging.error("No path index found for position: %s", pos)
    return path_i
                

def Add_enemy(data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, health: int, special: str, pos_i: int) -> None:
    """
    Adds an enemy to the list
    """
    enemy: data_class.Enemy_data = {
        "health": health,
        "pos": tile_map_obj.enemy_path[pos_i],
        "pos_i": pos_i,
        "special": special,
        "slow_timer": 0
    }
    data.special_enemy_spawn_uuid_counter += 1
    new_uuid: str = "s" + str(data.wave*1_000_000_000 + data.special_enemy_spawn_uuid_counter*1_000 + random.randint(0, 999))
    data.enemies[new_uuid] = enemy
    
