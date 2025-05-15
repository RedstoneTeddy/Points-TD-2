import data_class
import pygame as pg
import logging
import tile_map
import math

class Base_tower:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, tower_name: str, tower_size: int, pos: tuple[int, int]) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.current_tile_zoom: int = 1
        self.tower_pos: tuple[int, int] = pos
        self.center_pos: tuple[float, float] = (self.tower_pos[0] + tower_size/2, self.tower_pos[1] + tower_size/2)

        self.projectile_pos: tuple[int, int] = (0, 0)
        self.projectile_timer: int = 0

        self.turn_state: data_class.Literal["up", "right", "down", "left"] = "up"

        self.tower_name: str = tower_name
        # Normal towers are 2x2 tiles
        self.tower_size: int = tower_size

        self.selected: bool = False

        self.mouse_pressed: bool = False

        # Set by the specific tower-child-class
        self.original_tower_images: dict[str, pg.Surface] = {}
        self.original_projectile_image: pg.Surface = pg.Surface((0, 0))
        self.range: int = 0
        self.shooting_speed: int = 0
        self.projectile_speed: float = 0 # ideally: self.range/4
        self.projectile_damage: int = 0

        self.__projectile_pos: tuple[float, float] = (-1, -1)
        self.__projectile_angle: float = 0.0
        self.__targeted_uuid: str = ""
        self.__shoot_waiting_timer: int = 0 # When it is ready to shoot, but has no target, wait a short time before checking again

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

        if self.selected:
            pg.draw.circle(self.data.screen, (255,255,255), center_pos, int(self.range*self.data.tile_zoom*8), self.data.tile_zoom)

        # Check if the tower gets selected
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        if pg.mouse.get_pressed()[0] and not self.mouse_pressed:
            self.mouse_pressed = True
            if tower_pos[0] < mouse_pos[0] < tower_pos[0] + size_px and tower_pos[1] < mouse_pos[1] < tower_pos[1] + size_px:
                self.selected = True
                got_selected = True
            else:
                self.selected = False
        elif not pg.mouse.get_pressed()[0]:
            self.mouse_pressed = False

        if self.data.performance_saving_setting != "extreme":
            if self.__projectile_pos != (-1, -1):
                if self.__projectile_angle > 0.785 and self.__projectile_angle <= 2.356:
                    self.turn_state = "up"
                elif self.__projectile_angle > -0.785 and self.__projectile_angle <= 0.785:
                    self.turn_state = "right"
                elif self.__projectile_angle > -2.356 and self.__projectile_angle <= -0.785:
                    self.turn_state = "down"
                else:
                    self.turn_state = "left"


        return got_selected
    
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
        elif self.__projectile_pos == (-1, -1): # Shoot
            if self.__shoot_waiting_timer > 0:
                self.__shoot_waiting_timer -= 1
            else:
                # nearest: tuple[str, float] = self.Nearest_enemy() # This algorithm is for the nearest enemy
                nearest: tuple[str, float] = self.Last_reachable_enemy() # This algorithm is for the last reachable enemy
                if nearest[0] != "" and nearest[1] <= self.range:  
                        self.projectile_timer = self.shooting_speed
                        self.Shoot(nearest[0])
                else:
                    if self.data.performance_saving_setting == "extreme":
                        self.__shoot_waiting_timer = 5
                    elif self.data.performance_saving_setting == "default":
                        self.__shoot_waiting_timer = 3
                    else:
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
                        self.Damage_enemy(self.__targeted_uuid)
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
                        self.data.enemies[nearest[0]]["health"] -= self.projectile_damage
                        if self.data.enemies[nearest[0]]["health"] <= 0:
                            del self.data.enemies[nearest[0]]
                        self.__projectile_pos = (-1, -1)

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


    def Nearest_enemy(self, start_pos: tuple[float, float] = (-1, -1)) -> tuple[str, float]: # [UUID of the nearest enemy, distance in tiles]
        """
        Returns the UUID of the nearest enemy and the distance to it (in tiles)
        """
        if start_pos == (-1, -1):
            start_pos = self.center_pos
        output: tuple[str, float] = ("", 9999999.0)
        for enemy_uuid, enemy in self.data.enemies.items():
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
                if distance > output[1] and distance <= max_distance:
                    if enemy["pos_i"] > enemy_pos_i:
                        output = (enemy_uuid, distance)
                        enemy_pos_i = enemy["pos_i"]
        if output[0] != "":
            output = (output[0], output[1]**0.5)
        return output
    
    def Get_distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        """
        Returns the distance between two points
        """
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5
    
    def Damage_enemy(self, enemy_uuid: str) -> None:
        """
        Damages the enemy and rewards the player with money
        """
        health_before: int = self.data.enemies[enemy_uuid]["health"]
        self.data.enemies[enemy_uuid]["health"] -= self.projectile_damage
        health_after: int = self.data.enemies[enemy_uuid]["health"]
        if self.data.enemies[enemy_uuid]["health"] <= 0:
            health_after = 0
            del self.data.enemies[enemy_uuid]

        if health_before > 10: health_before = 10 # Points over 10 have a different reward-system
        
        self.data.money += int(health_before - health_after) 
    
        # Pop ceramic
        if health_before > 10 and health_after <= 10:
            self.data.money += 10
        
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
        if health_before > 1001 and health_after <= 1000:
            self.data.money += 50

    def Wave_finished(self) -> None:
        """
        Resets the tower for the next wave
        """
        self.__projectile_pos = (-1, -1)
        self.__targeted_uuid = ""
        self.projectile_timer = 0
        self.__shoot_waiting_timer = 0
    








class Tower_handler:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj

        self.__tower_clock: int = 0
        
        self.towers: list[Base_tower] = []


    def Main(self) -> None:
        """
        Main function for the tower handler
        """
        if self.data.running_wave:
            self.__tower_clock += 1
            if self.data.fast_forward:
                self.__tower_clock += 1

        # Main Tower Tick
        for i, tower in enumerate(self.towers):

            if tower.Show_tower(): # If the tower got selected
                for j, tower2 in enumerate(self.towers):
                    if i != j and tower2.selected:
                        tower2.selected = False
                        break

            if self.__tower_clock >= 2:
                tower.Tick()

        # Check for resetting the towers
        if not self.data.running_wave or self.data.new_wave:
            for tower in self.towers:
                tower.Wave_finished()

        # Show projectiles
        if self.data.performance_saving_setting != "extreme":
            for i, tower in enumerate(self.towers):
                if tower.projectile_pos != (-1, -1):
                    tower.Show_projectile()


        if self.__tower_clock >= 2:
            self.__tower_clock = 0


