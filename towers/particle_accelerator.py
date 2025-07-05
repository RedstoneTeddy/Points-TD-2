import data_class
import pygame as pg
import logging
import tile_map
import towers.base_tower

class Particle_accelerator(towers.base_tower.Base_tower):
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, pos: tuple[int, int]) -> None:
        super().__init__(data, tile_map_obj, "particle_accelerator", 3, pos)

        self.original_tower_images: dict[str, pg.Surface] = {
            "up": self.data.original_tower_images["particle_accelerator"]["up"],
            "left": self.data.original_tower_images["particle_accelerator"]["left"],
            "down": self.data.original_tower_images["particle_accelerator"]["down"],
            "right": self.data.original_tower_images["particle_accelerator"]["right"]
        }
        self.original_projectile_image: pg.Surface = self.data.original_tower_images["particle_accelerator"]["projectile"]

        self.original_animation_images: dict[str, pg.Surface] = {
            "1": self.data.original_tower_images["accelerator_animation"]["1"],
            "2": self.data.original_tower_images["accelerator_animation"]["2"],
            "3": self.data.original_tower_images["accelerator_animation"]["3"],
            "4": self.data.original_tower_images["accelerator_animation"]["4"],
            "5": self.data.original_tower_images["accelerator_animation"]["5"],
            "6": self.data.original_tower_images["accelerator_animation"]["6"],
            "7": self.data.original_tower_images["accelerator_animation"]["7"],
            "8": self.data.original_tower_images["accelerator_animation"]["8"]
        }
        self.animation_images: dict[str, pg.Surface] = {}

        # Tower stats
        self.range: float = 5.0
        self.shooting_speed: int = 60
        self.projectile_speed: float = 1.0
        self.projectile_damage: int = 10
        self.multi_hit_range = 1.0
        self.multi_hits_max = 1

        self.animation_timer: int = 0

        self.possible_upgrades: list[data_class.Upgrade_data] = [
            {"name": "sharper", "cost": 800, "requirement": "", "y_pos": 0,  "is_master": False,
             "description": ["Sharper Shots"], "original_img": data.original_tower_images["upgrades"]["sharper"], "img": pg.Surface((24,24))},
            {"name": "lightspeed", "cost": 450, "requirement": "", "y_pos": 1,  "is_master": False,
             "description": ["Lightspeed", "Increase Range &", "small damage buff"], "original_img": data.original_tower_images["upgrades"]["flash_explosion"], "img": pg.Surface((24,24))},
            {"name": "double_kill", "cost": 900, "requirement": "", "y_pos": 2,  "is_master": False,
             "description": ["Double Kill", "Possibility"], "original_img": data.original_tower_images["upgrades"]["double_kill"], "img": pg.Surface((24,24))},
        ]

        self.Scale_tower_images(True)

    def Scale_tower_images(self, force_scaling: bool = False) -> None:
        """
        Scales the tower images to the current tile zoom
        """
        super().Scale_tower_images(force_scaling)

        # Scale the animation images
        for key, image in self.original_animation_images.items():
            self.animation_images[key] = pg.transform.scale(image, (int(24 * self.data.tile_zoom), int(24 * self.data.tile_zoom)))

    
    def Give_upgrade_effect(self, upgrade_name: str) -> None:
        match upgrade_name:
            case "sharper":
                self.projectile_damage += 7
            case "lightspeed":
                self.range += 1.0
                self.projectile_speed += 0.3
                self.projectile_damage += 3
            case "double_kill":
                self.multi_hit_range = 1.0
                self.multi_hits_max = 2



    def Tick(self) -> None:
        """
        Tick function for the tower
        """
        super().Tick()
        self.animation_timer += 1
        if self.animation_timer >= 8*8*2 + 4*8*4 + 2*8*8 + 8*8*4: # Phase 1, Phase 2, Phase 3, Break
            self.animation_timer = 0



    def Show_tower(self) -> bool: # Return if it got selected
        """
        Shows the tower on the screen
        """
        output: bool = super().Show_tower()

        if self.animation_timer > 0:
            animation_frame: int = 0
            if self.animation_timer < 8*8*2:
                animation_frame = (self.animation_timer // 8)%8 + 1

            elif self.animation_timer < 8*8*2 + 4*8*4:
                animation_frame = ((self.animation_timer - 8*8*2) // 4)%8 +1

            elif self.animation_timer < 8*8*2 + 4*8*4 + 2*8*8:
                animation_frame = ((self.animation_timer - 8*8*2 - 4*8*4) // 2)%8 +1

            else:
                animation_frame = 0
            if animation_frame != 0:
                animation_image: pg.Surface = self.animation_images[str(animation_frame)]
                tower_pos: tuple[int, int] = (int((self.tower_pos[0])*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), int((self.tower_pos[1]+1)*self.data.tile_zoom*8))
                self.data.screen.blit(animation_image, tower_pos)

        return output
    


    def Wave_finished(self) -> None:
        """
        Resets the tower for the next wave
        """
        super().Wave_finished()
        self.animation_timer = 0


        