import data_class
import pygame as pg
import logging
import tile_map
import math
import random

class Base_tower:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, tower_name: str, tower_size: int, pos: tuple[int, int]) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.current_tile_zoom: int = 1
        self.tower_pos: tuple[int, int] = pos
        self.center_pos: tuple[float, float] = (self.tower_pos[0] + tower_size/2, self.tower_pos[1] + tower_size/2)

        self.projectile_pos: tuple[int, int] = (0, 0)
        self.projectile_timer: int = 0
        self.bought_upgrades: list[str] = []
        self.master_upgrade_bought: bool = False

        self.turn_state: data_class.Literal["up", "right", "down", "left"] = "up"

        self.tower_name: str = tower_name
        # Normal towers are 2x2 tiles
        self.tower_size: int = tower_size

        self.selected: bool = False

        self.__mouse_pressed: bool = False
        self.__upgrade_mouse_pressed: bool = False

        # Set by the specific tower-child-class
        self.original_tower_images: dict[str, pg.Surface] = {}
        self.original_projectile_image: pg.Surface = pg.Surface((0, 0))
        self.range: float = 0
        self.shooting_speed: int = -1 # -1 disables shooting
        self.projectile_speed: float = 0 # ideally: self.range/4
        self.projectile_damage: int = 0
        self.possible_upgrades: list[data_class.Upgrade_data] = []
        # Also this function is needed:    Give_upgrade_effect(self, upgrade_name: str) -> None
        self.multi_hits_max: int = 1 # How many enemies it can hit at once, needs to be AT LEAST 1!!!
        self.multi_hit_range: float = 0
        self.can_pop_lead: bool = False # If the tower can pop lead
        self.can_pop_anti_explosion: bool = True # If the tower can pop anti-explosion

        self.__shoot_priority: data_class.Literal["near", "first", "strong"] = "first"

        self.__projectile_pos: tuple[float, float] = (-1, -1)
        self.__projectile_angle: float = 0.0
        self.__targeted_uuid: str = ""
        self.__shoot_waiting_timer: int = 0 # When it is ready to shoot, but has no target, wait a short time before checking again
        
        self.__original_upgrade_hover_image: pg.Surface = self.data.original_tower_images["upgrades"]["hover"]
        self.__upgrade_hover_image: pg.Surface = pg.Surface((0, 0))
        self.__original_master_upgrade_image: pg.Surface = self.data.original_tower_images["upgrades"]["master_upgrade"]
        self.__master_upgrade_image: pg.Surface = pg.Surface((0, 0))
        self.__original_master_blocked_image: pg.Surface = self.data.original_tower_images["upgrades"]["master_blocked"]
        self.__master_blocked_image: pg.Surface = pg.Surface((0, 0))

        self.__original_target_prio_image: pg.Surface = self.data.original_tower_images["tower_hud"]["target_prio"]
        self.__target_prio_image: pg.Surface = pg.Surface((0, 0))
        self.__original_target_prio_hover_image: pg.Surface = self.data.original_tower_images["tower_hud"]["target_prio_hover"]
        self.__target_prio_hover_image: pg.Surface = pg.Surface((0, 0))
        self.__original_target_prio_selected_image: pg.Surface = self.data.original_tower_images["tower_hud"]["target_prio_selected"]
        self.__target_prio_selected_image: pg.Surface = pg.Surface((0, 0))
        self.__original_close_image: pg.Surface = self.data.original_tower_images["tower_hud"]["close_button"]
        self.__close_image: pg.Surface = pg.Surface((0, 0))
        self.__original_close_hover_image: pg.Surface = self.data.original_tower_images["tower_hud"]["close_button_hover"]
        self.__close_hover_image: pg.Surface = pg.Surface((0, 0))


        self.tower_images: dict[str, pg.Surface] = {}
        self.projectile_image: pg.Surface = pg.Surface((0, 0))
        

    def Scale_tower_images(self, force_scaling: bool = False) -> None:
        """
        Scales the tower images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_tower_images.keys():
                self.tower_images[key] = pg.transform.scale(self.original_tower_images[key], (self.data.tile_zoom*8*self.tower_size, self.data.tile_zoom*8*self.tower_size))
            self.current_tile_zoom = self.data.tile_zoom
            projectile_size: tuple[int, int] = self.original_projectile_image.get_size()
            self.projectile_image = pg.transform.scale(self.original_projectile_image, (self.data.tile_zoom*projectile_size[0], self.data.tile_zoom*projectile_size[1]))
            for upgrade_key in self.possible_upgrades:
                if upgrade_key["original_img"] != None:
                    upgrade_key["img"] = pg.transform.scale(upgrade_key["original_img"], (self.data.tile_zoom*8*3, self.data.tile_zoom*8*3))
            self.__upgrade_hover_image = pg.transform.scale(self.__original_upgrade_hover_image, (self.data.tile_zoom*8*3, self.data.tile_zoom*8*3))
            self.__master_upgrade_image = pg.transform.scale(self.__original_master_upgrade_image, (self.data.tile_zoom*8*3, self.data.tile_zoom*8*3))
            self.__master_blocked_image = pg.transform.scale(self.__original_master_blocked_image, (self.data.tile_zoom*8*3, self.data.tile_zoom*8*3))

            self.__target_prio_image = pg.transform.scale(self.__original_target_prio_image, (self.data.tile_zoom*8*2, self.data.tile_zoom*8*1))
            self.__target_prio_hover_image = pg.transform.scale(self.__original_target_prio_hover_image, (self.data.tile_zoom*8*2, self.data.tile_zoom*8*1))
            self.__target_prio_selected_image = pg.transform.scale(self.__original_target_prio_selected_image, (self.data.tile_zoom*8*2, self.data.tile_zoom*8*1))
            self.__close_image = pg.transform.scale(self.__original_close_image, (self.data.tile_zoom*8*1, self.data.tile_zoom*8*1))
            self.__close_hover_image = pg.transform.scale(self.__original_close_hover_image, (self.data.tile_zoom*8*1, self.data.tile_zoom*8*1))


    def Show_tower(self) -> bool: # Return if it got selected
        """
        Shows the tower on the screen
        """
        got_selected: bool = False
        self.Scale_tower_images()
        
        tower_pos: tuple[int, int] = (int((self.tower_pos[0])*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((self.tower_pos[1]+1)*self.data.tile_zoom*8))
        center_pos: tuple[int, int] = (int((self.center_pos[0])*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((self.center_pos[1]+1)*self.data.tile_zoom*8))
        size_px: int = int(self.data.tile_zoom*8*self.tower_size)
        self.data.screen.blit(self.tower_images[self.turn_state], tower_pos)

        if self.selected and self.range > 0:
            pg.draw.circle(self.data.screen, (255,255,255), center_pos, int(self.range*self.data.tile_zoom*8), self.data.tile_zoom)

        # Check if the tower gets selected
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        x_pos_shop: int = (24*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen()
        if pg.mouse.get_pressed()[0] and not self.__mouse_pressed:
            self.__mouse_pressed = True
            if tower_pos[0] < mouse_pos[0] < tower_pos[0] + size_px and tower_pos[1] < mouse_pos[1] < tower_pos[1] + size_px:
                self.selected = True
                got_selected = True
            elif mouse_pos[0] < x_pos_shop:
                if self.selected:
                    self.data.tower_selected = -1
                self.selected = False
        elif not pg.mouse.get_pressed()[0]:
            self.__mouse_pressed = False


        if self.selected:
            self.Show_upgrades()


        return got_selected
    

    def Show_upgrades(self) -> None:
        """
        Shows the upgrades for the tower
        """
        title_pos: tuple[int, int] = (int(25.6*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), 1*self.data.tile_zoom*8)
        self.data.Draw_text("Upgrades", 8*self.data.tile_zoom, (255, 255, 255), title_pos)
        tower_name: str = self.tower_name.capitalize().replace("_", " ")
        if len(tower_name) > 15:
            self.data.Draw_text(tower_name, 5*self.data.tile_zoom, (255, 255, 255), (title_pos[0] - self.data.tile_zoom*10, title_pos[1] + self.data.tile_zoom*8))
        else:
            self.data.Draw_text(tower_name, 6*self.data.tile_zoom, (255, 255, 255), (title_pos[0] - self.data.tile_zoom*8, title_pos[1] + self.data.tile_zoom*8))

        for upgrade in self.possible_upgrades:
            if upgrade["name"] not in self.bought_upgrades:
                if upgrade["requirement"] != "" and upgrade["requirement"] not in self.bought_upgrades:
                    continue
                tile_pos: tuple[int, int] = (25, 3 + upgrade["y_pos"]*3)
                px_pos: tuple[int, int] = (int(tile_pos[0]*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((tile_pos[1])*self.data.tile_zoom*8))
                self.data.screen.blit(upgrade["img"], px_pos)
                if upgrade["is_master"]:
                    if not self.master_upgrade_bought:
                        self.data.screen.blit(self.__master_upgrade_image, px_pos)
                    else:
                        self.data.screen.blit(self.__master_blocked_image, px_pos)
                upgarde_cost: int = int(round((upgrade["cost"]*self.data.cost_multiplier)/10,0)*10)

                mouse_pos: tuple[int, int] = pg.mouse.get_pos()
                mouse_tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos)
                if mouse_tile_pos[0] >= tile_pos[0] and mouse_tile_pos[0] < tile_pos[0] + 3 and mouse_tile_pos[1] >= tile_pos[1] and mouse_tile_pos[1] < tile_pos[1] + 3:
                    self.data.screen.blit(self.__upgrade_hover_image, px_pos)
                    # Show description
                    for i, line in enumerate(upgrade["description"]):
                        self.data.Draw_text(line, 5*self.data.tile_zoom, (255, 255, 255), (title_pos[0] - self.data.tile_zoom*12, 12*self.data.tile_zoom*8 + i*self.data.tile_zoom*8))

                    if self.data.money >= upgarde_cost and (not upgrade["is_master"] or not self.master_upgrade_bought):
                        self.data.Draw_text(str(upgarde_cost) + "$", 6*self.data.tile_zoom, (255, 255, 50), (px_pos[0] + self.data.tile_zoom*26, px_pos[1] + self.data.tile_zoom*18))

                        if pg.mouse.get_pressed()[0]:
                            if not self.__upgrade_mouse_pressed:
                                self.__upgrade_mouse_pressed = True
                                self.data.money -= upgarde_cost
                                self.bought_upgrades.append(upgrade["name"])
                                self.Give_upgrade_effect(upgrade["name"])   
                                if upgrade["is_master"]:
                                    self.master_upgrade_bought = True                             
                                
                        else:
                            self.__upgrade_mouse_pressed = False
                    else: # Not enough money
                        self.data.Draw_text(str(upgarde_cost) + "$", 6*self.data.tile_zoom, (255, 50, 50), (px_pos[0] + self.data.tile_zoom*26, px_pos[1] + self.data.tile_zoom*18))
                else: # Not selected
                    self.data.Draw_text(str(upgarde_cost) + "$", 6*self.data.tile_zoom, (255, 255, 255), (px_pos[0] + self.data.tile_zoom*26, px_pos[1] + self.data.tile_zoom*18))
        
        self.Show_target_priority()


    def Show_target_priority(self) -> None:
        # Target priority
        prio_first_tile_pos: tuple[int, int] = (25, 17)
        prio_near_tile_pos: tuple[int, int] = (27, 17)
        prio_strong_tile_pos: tuple[int, int] = (29, 17)
        close_tile_pos: tuple[int, int] = (31, 17)
        prio_first_pos: tuple[int, int] = (int(prio_first_tile_pos[0]*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((prio_first_tile_pos[1])*self.data.tile_zoom*8))
        prio_near_pos: tuple[int, int] = (int(prio_near_tile_pos[0]*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((prio_near_tile_pos[1])*self.data.tile_zoom*8))
        prio_strong_pos: tuple[int, int] = (int(prio_strong_tile_pos[0]*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((prio_strong_tile_pos[1])*self.data.tile_zoom*8))
        close_pos: tuple[int, int] = (int(close_tile_pos[0]*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((close_tile_pos[1])*self.data.tile_zoom*8))
        mouse_tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(pg.mouse.get_pos())

        if mouse_tile_pos[0] >= prio_first_tile_pos[0] and mouse_tile_pos[0] < prio_first_tile_pos[0] + 2 and mouse_tile_pos[1] == 17:
            self.data.screen.blit(self.__target_prio_hover_image, prio_first_pos)
            if pg.mouse.get_pressed()[0]:
                self.__shoot_priority = "first"
        else:
            if self.__shoot_priority == "first":
                self.data.screen.blit(self.__target_prio_selected_image, prio_first_pos)
            else:
                self.data.screen.blit(self.__target_prio_image, prio_first_pos)
        self.data.Draw_text("First", 4*self.data.tile_zoom, (255, 255, 255), (prio_first_pos[0] + self.data.tile_zoom*2, prio_first_pos[1] + self.data.tile_zoom*2))

        if mouse_tile_pos[0] >= prio_near_tile_pos[0] and mouse_tile_pos[0] < prio_near_tile_pos[0] + 2 and mouse_tile_pos[1] == 17:
            self.data.screen.blit(self.__target_prio_hover_image, prio_near_pos)
            if pg.mouse.get_pressed()[0]:
                self.__shoot_priority = "near"
        else:
            if self.__shoot_priority == "near":
                self.data.screen.blit(self.__target_prio_selected_image, prio_near_pos)
            else:
                self.data.screen.blit(self.__target_prio_image, prio_near_pos)
        self.data.Draw_text("Near", 4*self.data.tile_zoom, (255, 255, 255), (prio_near_pos[0] + self.data.tile_zoom*3, prio_near_pos[1] + self.data.tile_zoom*2))

        if mouse_tile_pos[0] >= prio_strong_tile_pos[0] and mouse_tile_pos[0] < prio_strong_tile_pos[0] + 2 and mouse_tile_pos[1] == 17:
            self.data.screen.blit(self.__target_prio_hover_image, prio_strong_pos)
            if pg.mouse.get_pressed()[0]:
                self.__shoot_priority = "strong"
        else:
            if self.__shoot_priority == "strong":
                self.data.screen.blit(self.__target_prio_selected_image, prio_strong_pos)
            else:
                self.data.screen.blit(self.__target_prio_image, prio_strong_pos)
        self.data.Draw_text("Strong", 4*self.data.tile_zoom, (255, 255, 255), (prio_strong_pos[0] + self.data.tile_zoom*1, prio_strong_pos[1] + self.data.tile_zoom*2))

        if mouse_tile_pos[0] >= close_tile_pos[0] and mouse_tile_pos[0] < close_tile_pos[0] + 1 and mouse_tile_pos[1] == 17:
            self.data.screen.blit(self.__close_hover_image, close_pos)
            if pg.mouse.get_pressed()[0]:
                self.selected = False
                self.data.tower_selected = -1
        else:
            self.data.screen.blit(self.__close_image, close_pos)
            

        
        



    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        """
        This function will be replaced by the specific tower-child-class
        """
        logging.error(f"Tower {self.tower_name} has no upgrade effect function for {upgrade_name} implemented. Skipping...")
        
    
    def Show_projectile(self) -> None:
        # Render shot
        if self.projectile_pos != (-1, -1):
            shot_pos: tuple[int, int] = (int((self.__projectile_pos[0])*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((self.__projectile_pos[1]+1)*self.data.tile_zoom*8))
            self.data.screen.blit(self.projectile_image, shot_pos)


    def Tick(self) -> None:
        """
        Tick function for the tower
        """
        if self.projectile_timer > 0:
            self.projectile_timer -= 1
        elif self.__projectile_pos == (-1, -1) and self.shooting_speed != -1: # Shoot
            
            if self.__shoot_waiting_timer > 0:
                self.__shoot_waiting_timer -= 1
            else:
                # nearest: tuple[str, float] = self.Nearest_enemy() # This algorithm is for the nearest enemy
                nearest: tuple[str, float]
                if self.__shoot_priority == "first":
                    nearest = self.Last_reachable_enemy() # This algorithm is for the last reachable enemy
                elif self.__shoot_priority == "strong":
                    nearest = self.Strongest_reachable_enemy()
                else:
                    nearest = self.Nearest_enemy()
                if nearest[0] != "" and nearest[1] <= self.range:  
                        self.projectile_timer = self.shooting_speed
                        self.Shoot(nearest[0])
                else:
                    if self.data.performance_saving_setting == "extreme":
                        self.__shoot_waiting_timer = 2
                    elif self.data.performance_saving_setting == "default":
                        self.__shoot_waiting_timer = 1
                    else:
                        self.__shoot_waiting_timer = 0
                    if self.tower_name == "machine_gunner":
                        self.__shoot_waiting_timer = 0

        # Projectile movement
        if self.__projectile_pos != (-1, -1):

            # Move the projectile
            self.__projectile_pos = (
                self.__projectile_pos[0] + math.cos(self.__projectile_angle) * self.projectile_speed,
                self.__projectile_pos[1] - math.sin(self.__projectile_angle) * self.projectile_speed
            )

            # Check if the projectile hit the enemy
            if self.__targeted_uuid in self.data.enemies.keys() and self.__targeted_uuid != "":
                if self.data.enemies[self.__targeted_uuid]["health"] > 0:
                    distance: float = self.Get_distance(self.__projectile_pos, (self.data.enemies[self.__targeted_uuid]["pos"][0], self.data.enemies[self.__targeted_uuid]["pos"][1]))
                    if distance <= (self.projectile_speed+0.1):
                        # Hit the enemy
                        self.__projectile_pos = self.data.enemies[self.__targeted_uuid]["pos"]
                        allready_hit: list[str] = []
                        radius_damage: int = -1 # Only useful for multishot-towers & shots
                        for i in range(self.multi_hits_max):
                            self.Damage_enemy(self.__targeted_uuid,radius_damage)
                            if i+1 >= self.multi_hits_max:
                                break
                            # Check if the projectile can hit another enemy
                            allready_hit.append(self.__targeted_uuid)
                            nearest: tuple[str, float] = self.Nearest_enemy(self.__projectile_pos, allready_hit)
                            if nearest[0] != "" and nearest[1] <= self.multi_hit_range*1.1:
                                self.__targeted_uuid = nearest[0]
                                radius_damage = int(round((self.multi_hit_range*1.1 - nearest[1])/(self.multi_hit_range*1.1)*self.projectile_damage,0))
                            else:
                                break

                        self.__projectile_pos = (-1, -1)
                        self.__targeted_uuid = ""
                if self.__projectile_pos != (-1, -1):
                    # Correct the projectile angle
                    enemy_pos: tuple[float, float] = (self.data.enemies[self.__targeted_uuid]["pos"][0], self.data.enemies[self.__targeted_uuid]["pos"][1])
                    self.__projectile_angle: float = math.atan2(-(enemy_pos[1] - self.__projectile_pos[1]), enemy_pos[0] - self.__projectile_pos[0])

            else:
                self.__targeted_uuid = ""
                nearest: tuple[str, float] = self.Nearest_enemy(self.__projectile_pos)
                if nearest[0] != "":
                    if nearest[1] <= (self.projectile_speed+0.1):
                        # Hit the enemy
                        self.__targeted_uuid = nearest[0]
                        self.__projectile_pos = self.data.enemies[self.__targeted_uuid]["pos"]
                        allready_hit: list[str] = []
                        radius_damage: int = -1 # Only useful for multishot-towers & shots
                        for i in range(self.multi_hits_max):
                            self.Damage_enemy(self.__targeted_uuid,radius_damage)
                            if i+1 >= self.multi_hits_max:
                                break
                            # Check if the projectile can hit another enemy
                            allready_hit.append(self.__targeted_uuid)
                            nearest: tuple[str, float] = self.Nearest_enemy(self.__projectile_pos, allready_hit)
                            if nearest[0] != "" and nearest[1] <= self.multi_hit_range:
                                self.__targeted_uuid = nearest[0]
                                radius_damage = int(round((self.multi_hit_range*1.1 - nearest[1])/(self.multi_hit_range*1.1)*self.projectile_damage,0))
                            else:
                                break
                        self.__projectile_pos = (-1, -1)
                        self.__targeted_uuid = ""

            # Check if the projectile is out of range
            distance: float = self.Get_distance(self.__projectile_pos, self.center_pos)
            if distance > self.range:
                self.__projectile_pos = (-1, -1)
                self.__targeted_uuid = ""



    def Shoot(self, enemy_uuid: str) -> None:
        """
        Shoots a projectile
        """
        self.__projectile_pos = (self.center_pos[0], self.center_pos[1])
        self.__targeted_uuid = enemy_uuid
        # Calculate the angle (invert Y because pygame's Y axis increases downwards)
        tower_pos: tuple[float, float] = (self.center_pos[0], self.center_pos[1])
        enemy_pos: tuple[float, float] = (self.data.enemies[enemy_uuid]["pos"][0], self.data.enemies[enemy_uuid]["pos"][1])
        self.__projectile_angle: float = math.atan2(-(enemy_pos[1] - tower_pos[1]), enemy_pos[0] - tower_pos[0])
        
        # Rotate the tower to the enemy
        if self.data.performance_saving_setting != "extreme":
            if self.__projectile_angle > 0.785 and self.__projectile_angle <= 2.356:
                self.turn_state = "up"
            elif self.__projectile_angle > -0.785 and self.__projectile_angle <= 0.785:
                self.turn_state = "right"
            elif self.__projectile_angle > -2.356 and self.__projectile_angle <= -0.785:
                self.turn_state = "down"
            else:
                self.turn_state = "left"


    def Nearest_enemy(self, start_pos: tuple[float, float] = (-1, -1), ignore_uuids: list[str] = []) -> tuple[str, float]: # [UUID of the nearest enemy, distance in tiles]
        """
        Returns the UUID of the nearest enemy and the distance to it (in tiles)
        """
        if start_pos == (-1, -1):
            start_pos = self.center_pos
        output: tuple[str, float] = ("", 9999999.0)
        for enemy_uuid, enemy in self.data.enemies.items():
            if enemy_uuid in ignore_uuids:
                continue
            if enemy["health"] > 0:
                distance: float = ((start_pos[0] - enemy["pos"][0])**2 + (start_pos[1] - enemy["pos"][1])**2)
                if distance < output[1]:
                    output = (enemy_uuid, distance)
        if output[0] != "":
            output = (output[0], output[1]**0.5)
        return output
    
    def Last_reachable_enemy(self) -> tuple[str, float]: # [UUID of the last reachable enemy, distance in tiles]
        """
        Returns the UUID of the last reachable enemy and the distance to it (in tiles)
        """
        max_distance: float = self.range**2
        output: tuple[str, float] = ("", 0.0)
        enemy_pos_i: int = 0
        for enemy_uuid, enemy in self.data.enemies.items():
            if enemy["health"] > 0:
                distance: float = ((self.center_pos[0] - enemy["pos"][0])**2 + (self.center_pos[1] - enemy["pos"][1])**2)
                if distance <= max_distance:
                    if enemy["pos_i"] > enemy_pos_i:
                        output = (enemy_uuid, distance)
                        enemy_pos_i = enemy["pos_i"]
        if output[0] != "":
            output = (output[0], output[1]**0.5)
        return output
    
    def Strongest_reachable_enemy(self) -> tuple[str, float]: # [UUID of the strongest reachable enemy, distance in tiles]
        """
        Returns the UUID of the strongest reachable enemy and the distance to it (in tiles)
        """
        max_distance: float = self.range**2
        output: tuple[str, float] = ("", 0.0)
        for enemy_uuid, enemy in self.data.enemies.items():
            if enemy["health"] > 0:
                distance: float = ((self.center_pos[0] - enemy["pos"][0])**2 + (self.center_pos[1] - enemy["pos"][1])**2)
                if distance <= max_distance:
                    if output[0] == "":
                        output = (enemy_uuid, distance)
                    else:    
                        if enemy["health"] > self.data.enemies[output[0]]["health"]:
                            output = (enemy_uuid, distance)
        if output[0] != "":
            output = (output[0], output[1]**0.5)
        return output




    
    def Get_distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        """
        Returns the distance between two points
        """
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
    
    def Damage_enemy(self, enemy_uuid: str, custom_damage: int = -1) -> None:
        """
        Damages the enemy and rewards the player with money
        """
        # Special enemies
        if self.data.enemies[enemy_uuid]["special"] == "lead" and not self.can_pop_lead:
            # If the tower can't pop lead, don't damage it
            return
        if self.data.enemies[enemy_uuid]["special"] == "anti_explosion" and not self.can_pop_anti_explosion:
            # If the tower can't pop anti-explosion, don't damage it
            return
        

        if custom_damage != -1:
            damage = custom_damage
        else:
            damage = self.projectile_damage
        health_before: int = self.data.enemies[enemy_uuid]["health"]
        self.data.enemies[enemy_uuid]["health"] -= damage
        health_after: int = self.data.enemies[enemy_uuid]["health"]
        if self.data.enemies[enemy_uuid]["health"] <= 0:
            health_after = 0
            # Special enemies
            if self.data.enemies[enemy_uuid]["special"] not in ["stack", "stack+"]:
                del self.data.enemies[enemy_uuid]
            elif self.data.enemies[enemy_uuid]["special"] == "stack":
                health_after = 10
            elif self.data.enemies[enemy_uuid]["special"] == "stack+":
                health_after = 50
        else:
            # Pushback Effect of Magician
            if self.tower_name == "magician" and "pushback" in self.bought_upgrades:
                self.data.enemies[enemy_uuid]["pos_i"] -= 10
                if self.data.enemies[enemy_uuid]["pos_i"] < 0:
                    self.data.enemies[enemy_uuid]["pos_i"] = 0
            if self.tower_name == "magician" and "slow_down" in self.bought_upgrades:
                if self.data.enemies[enemy_uuid]["slow_timer"] < 70:
                    self.data.enemies[enemy_uuid]["slow_timer"] = 70



        # Special enemies
        if health_after > 0:
            if self.data.enemies[enemy_uuid]["special"] == "lead":
                if health_after <= 10:
                    self.data.enemies[enemy_uuid]["special"] = ""
                    self.data.money -= 4
            elif self.data.enemies[enemy_uuid]["special"] == "anti_explosion":
                if health_after <= 10:
                    self.data.enemies[enemy_uuid]["special"] = ""
                    self.data.money -= 4
            elif self.data.enemies[enemy_uuid]["special"] == "stack":
                if health_after <= 10:
                    self.data.money -= 4
                    spawn_pos_i: int = self.data.enemies[enemy_uuid]["pos_i"]
                    if spawn_pos_i < 4:
                        spawn_pos_i = 4
                    # Spawn enemies from stack
                    self.Add_enemy(20, "lead", spawn_pos_i)
                    self.Add_enemy(20, "anti_explosion", spawn_pos_i-2)
                    self.Add_enemy(10, "", spawn_pos_i-4)
                    # Delete stack enemy
                    del self.data.enemies[enemy_uuid]
            elif self.data.enemies[enemy_uuid]["special"] == "stack+":
                if health_after <= 10:
                    self.data.money -= 6
                    spawn_pos_i: int = self.data.enemies[enemy_uuid]["pos_i"]
                    if spawn_pos_i < 8:
                        spawn_pos_i = 10
                    # Spawn enemies from stack+
                    self.Add_enemy(50, "", spawn_pos_i)
                    self.Add_enemy(50, "", spawn_pos_i-2)
                    self.Add_enemy(20, "lead", spawn_pos_i-4)
                    self.Add_enemy(20, "anti_explosion", spawn_pos_i-6)
                    self.Add_enemy(10, "", spawn_pos_i-8)
                    # Delete stack+ enemy
                    del self.data.enemies[enemy_uuid]
            elif self.data.enemies[enemy_uuid]["special"] == "":
                if health_before > 10 and health_after <= 10: # Too much money in early game
                    self.data.money -= 1    
                if health_before > 9 and health_after <= 9: # Too much money in early game
                    self.data.money -= 1    
                if health_before > 8 and health_after <= 8: # Too much money in early game
                    self.data.money -= 1    


            

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

    def Wave_finished(self) -> None:
        """
        Resets the tower for the next wave
        """
        self.__projectile_pos = (-1, -1)
        self.__targeted_uuid = ""
        self.projectile_timer = 0
        self.__shoot_waiting_timer = 0


    def Add_enemy(self, health: int, special: str, pos_i: int) -> None:
        """
        Adds an enemy to the list
        """
        enemy: data_class.Enemy_data = {
            "health": health,
            "pos": self.tile_map_obj.enemy_path[pos_i],
            "pos_i": pos_i,
            "special": special,
            "slow_timer": 0
        }
        self.data.special_enemy_spawn_uuid_counter += 1
        new_uuid: str = "s" + str(self.data.wave*1_000_000_000 + self.data.special_enemy_spawn_uuid_counter*1_000 + random.randint(0, 999))
        self.data.enemies[new_uuid] = enemy
    





import towers.spikes





class Tower_handler:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj

        
        self.towers: list[Base_tower] = []
        self.spikes: list[towers.spikes.Spikes] = []


    def Main(self) -> None:
        """
        Main function for the tower handler
        """

        # Main Tower Tick
        for i, tower in enumerate(self.towers):
            if tower.tower_name == "spike_factory":
                tower.spikes_list = self.spikes # Fix against the tower not having the list, when bought. # type: ignore

            if tower.Show_tower(): # If the tower got selected
                self.data.tower_selected = i
                for j, tower2 in enumerate(self.towers):
                    if i != j and tower2.selected:
                        tower2.selected = False
                        break

            if self.data.running_wave:
                tower.Tick()

        # Check for resetting the towers
        if self.data.tick_tower_wave_finished:
            for tower in self.towers:
                tower.Wave_finished()

        # Show projectiles
        if self.data.performance_saving_setting != "extreme":
            for i, tower in enumerate(self.towers):
                if tower.projectile_pos != (-1, -1):
                    tower.Show_projectile()


        #### Spikes ####
        delete_spikes: list[int] = []
        for i, spike in enumerate(self.spikes):
            spike.Show_spike()
            if self.data.running_wave:
                if spike.Tick():
                    delete_spikes.append(i)
        
        # Resetting
        if self.data.tick_tower_wave_finished:
            self.data.tick_tower_wave_finished = False
            for i, spike in enumerate(self.spikes):
                if spike.Wave_finished():
                    if i not in delete_spikes:
                        delete_spikes.append(i)

        # Delete spikes
        if len(delete_spikes) > 1:
            delete_spikes.sort(reverse=False)  # Delete from the end to avoid index errors
        for i in range(len(delete_spikes)-1, -1, -1):
            del self.spikes[delete_spikes[i]]

        




    def Tick_only(self) -> None:
        """
        Only ticks the towers, no rendering
        """
        delete_spikes: list[int] = []
        if self.data.running_wave:
            for tower in self.towers:
                tower.Tick()


            
            for i, spike in enumerate(self.spikes):
                if spike.Tick():
                    delete_spikes.append(i)

        # Delete spikes
        for i in range(len(delete_spikes)-1, -1, -1):
            del self.spikes[delete_spikes[i]]



