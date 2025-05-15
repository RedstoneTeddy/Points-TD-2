import data_class
import pygame as pg
import logging
import tile_map
import random

class Enemy:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.current_tile_zoom: int = 1

        self.__enemy_spawn_clock: int = 0

        self.__enemy_tick_clock: int = 0

        self.__wave_enemies: list[data_class.Wave_enemy] = []

        self.original_enemy_images: dict[int, pg.Surface] = {
            1: pg.image.load("images/enemies/1.png").convert_alpha(),
            2: pg.image.load("images/enemies/2.png").convert_alpha(),
            3: pg.image.load("images/enemies/3.png").convert_alpha(),
            4: pg.image.load("images/enemies/4.png").convert_alpha(),
            5: pg.image.load("images/enemies/5.png").convert_alpha(),
            10: pg.image.load("images/enemies/10.png").convert_alpha(),
            20: pg.image.load("images/enemies/20.png").convert_alpha(),
            30: pg.image.load("images/enemies/30.png").convert_alpha(),
            40: pg.image.load("images/enemies/40.png").convert_alpha(),
            50: pg.image.load("images/enemies/50.png").convert_alpha(),
            100: pg.image.load("images/enemies/100.png").convert_alpha(),
            200: pg.image.load("images/enemies/200.png").convert_alpha(),
            300: pg.image.load("images/enemies/300.png").convert_alpha(),
            400: pg.image.load("images/enemies/400.png").convert_alpha(),
            500: pg.image.load("images/enemies/500.png").convert_alpha(),
            1000: pg.image.load("images/enemies/1000.png").convert_alpha()
        }

        self.enemy_images: dict[int, pg.Surface] = {}
        self.Scale_enemy_images(True)

    def Scale_enemy_images(self, force_scaling: bool = False) -> None:
        """
        Scales the enemy images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_enemy_images.keys():
                self.enemy_images[key] = pg.transform.scale(self.original_enemy_images[key], (self.data.tile_zoom*8, self.data.tile_zoom*8))
            self.current_tile_zoom = self.data.tile_zoom

    def Show_enemies(self) -> None:
        self.Scale_enemy_images()
        for enemy in self.data.enemies.values():

            # Get the enemy type => enemy img
            enemy_type: int = 0
            if enemy["health"] == 1:
                enemy_type = 1
            elif enemy["health"] == 2:
                enemy_type = 2
            elif enemy["health"] == 3:
                enemy_type = 3
            elif enemy["health"] == 4:
                enemy_type = 4
            elif enemy["health"] == 5:
                enemy_type = 5
            elif enemy["health"] > 5 and enemy["health"] <= 10:
                enemy_type = 10
            elif enemy["health"] > 10 and enemy["health"] <= 20:
                enemy_type = 20
            elif enemy["health"] > 20 and enemy["health"] <= 30:
                enemy_type = 30
            elif enemy["health"] > 30 and enemy["health"] <= 40:
                enemy_type = 40
            elif enemy["health"] > 40 and enemy["health"] <= 50:
                enemy_type = 50
            elif enemy["health"] > 50 and enemy["health"] <= 100:
                enemy_type = 100
            elif enemy["health"] > 100 and enemy["health"] <= 200:
                enemy_type = 200
            elif enemy["health"] > 200 and enemy["health"] <= 300:
                enemy_type = 300
            elif enemy["health"] > 300 and enemy["health"] <= 400:
                enemy_type = 400
            elif enemy["health"] > 400 and enemy["health"] <= 500:
                enemy_type = 500
            elif enemy["health"] > 500 and enemy["health"] <= 1000:
                enemy_type = 1000
            else:
                logging.error(f"Enemy health {enemy['health']} is not valid")
                enemy_type = 1

            # Enemy pixel position
            enemy_pos: tuple[int, int] = (int((enemy["pos"][0]-0.5)*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((enemy["pos"][1]-0.5+1)*self.data.tile_zoom*8))
            
            # Draw the enemy
            self.data.screen.blit(self.enemy_images[enemy_type], enemy_pos)


    def Tick_enemy_walk(self) -> None:
        """
        Moves the enemies one tile forward
        """
        enemies_at_end: list[str] = []
        for uuid, enemy in self.data.enemies.items():
            enemy["pos_i"] += 1
            if enemy["pos_i"] < len(self.tile_map_obj.enemy_path):
                enemy["pos"] = self.tile_map_obj.enemy_path[enemy["pos_i"]]
            else:
                enemies_at_end.append(uuid)

        # Remove enemies that reached the end
        for kill_enemy in enemies_at_end:
            self.data.health -= self.data.enemies[kill_enemy]["health"]
            if self.data.health <= 0:
                logging.info("Game Over")
                raise ValueError("Game Over")
            del self.data.enemies[kill_enemy]
        
        # Check for enemies that should be dead
        dead_enemies: list[str] = []
        for uuid, enemy in self.data.enemies.items():
            if enemy["health"] <= 0:
                dead_enemies.append(uuid)
        for dead_uuid in dead_enemies:
            del self.data.enemies[dead_uuid]
            
    def Add_enemy(self, health: int, special: str) -> None:
        """
        Adds an enemy to the list
        """
        if health <= 0:
            logging.error(f"Enemy health {health} is not valid")
            return
        

        enemy: data_class.Enemy_data = {
            "health": health,
            "pos": (-10.0, -10.0),
            "pos_i": 0,
            "special": special
        }
        new_uuid: str = str(self.data.wave*1_000_000_000 + self.__enemy_spawn_clock*1_000 + random.randint(0, 999))
        self.data.enemies[new_uuid] = enemy

    

    def Main(self) -> None:
        """
        Main function for the enemy class
        """


        # Enemy tick (walk)
        if self.data.fast_forward:
            self.__enemy_tick_clock += 2
        else:
            self.__enemy_tick_clock += 1
        if self.__enemy_tick_clock >= 2:
            self.__enemy_tick_clock = 0
            self.__enemy_spawn_clock += 1
            self.Tick_enemy_walk()

            
        # Enemy spawner
        wave_enemies_to_delete: list[int] = []
        for i, new_enemy in enumerate(self.__wave_enemies):
            if self.__enemy_spawn_clock >= new_enemy["spawn_time"]:
                self.Add_enemy(new_enemy["health"], new_enemy["special"])
                wave_enemies_to_delete.append(i)
        
        for j in range(len(wave_enemies_to_delete)-1, -1, -1):
            del self.__wave_enemies[wave_enemies_to_delete[j]]

            
        # New Wave
        if self.data.new_wave:
            self.Load_new_wave()


        self.Show_enemies()

        if len(self.data.enemies) == 0 and len(self.__wave_enemies) == 0 and self.data.running_wave:
            self.data.Wave_finished()
            if self.data.new_wave:
                self.Load_new_wave()
            

    def Load_new_wave(self):
        self.__enemy_spawn_clock = 0
        self.__enemy_tick_clock = 0

        # Load the new wave out of the file            
        if self.data.wave <= 0:
            logging.error(f"Invalid wave number: {self.data.wave}")
            return
        try:
            import pickle
            with open(f"waves/normal{self.data.wave}.pkl", "rb") as file:
                file_contents = pickle.load(file)
                self.__wave_enemies = file_contents
        except Exception as load_error:
            logging.error(f"Failed to load the wave {self.data.wave}: {load_error}")



    def Save_wave_enemies(self, wave_num: int, enemies: list[data_class.Wave_enemy]) -> None:
        """
        Saves the wave enemies to a file
        """
        try:
            import pickle
            with open(f"waves/normal{wave_num}.pkl", "wb") as file:
                pickle.dump(enemies, file)
                logging.info(f"Wave {wave_num} successfully saved to 'waves/normal{wave_num}.pkl'")
        except Exception as save_error:
            logging.error(f"Failed to save the wave {wave_num}: {save_error}")