import data_class
import pygame as pg
import logging
import tile_map

import towers.base_tower
import towers.ninja
import towers.bomber
import towers.machine_gunner
import towers.sniper
import towers.magician
import towers.shooter
import towers.bank
import towers.spikes

class Build_hologram:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, tower_handler: towers.base_tower.Tower_handler) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.tower_handler: towers.base_tower.Tower_handler = tower_handler
        self.current_tile_zoom: int = 1

        self.original_tower_images: dict[str, pg.Surface] = {
            "ninja" : data.original_tower_images["ninja"]["up"],
            "bomber" : data.original_tower_images["bomber"]["up"],
            "machine_gunner" : data.original_tower_images["machine_gunner"]["up"],
            "sniper" : data.original_tower_images["sniper"]["up"],
            "magician" : data.original_tower_images["magician"]["up"],
            "shooter" : data.original_tower_images["shooter"]["up"],
            "bank" : data.original_tower_images["bank"]["up"],
            "spikes" : data.original_tower_images["spikes"]["normal1"]
        }

        self.tower_size: dict[str, int] = {
            "ninja" : 2,
            "bomber" : 2,
            "machine_gunner" : 2,
            "sniper" : 2,
            "magician" : 2,
            "shooter" : 1,
            "bank" : 2,
            "spikes" : 1
        }

        self.tower_range: dict[str, float] = {
            "ninja" : 4.0,
            "bomber" : 3.3,
            "machine_gunner" : 3.6,
            "sniper" : 7.5,
            "magician" : 4.0,
            "shooter" : 2.6,
            "bank" : 0.0,
            "spikes" : 0.0
        }


        self.tower_images: dict[str, pg.Surface] = {}
        self.Scale_hologram_images(True)
        
    def Scale_hologram_images(self, force_scaling: bool = False) -> None:
        """
        Scales the tower images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_tower_images.keys():
                img_size: tuple[int, int] = self.original_tower_images[key].get_size()
                self.tower_images[key] = pg.transform.scale(self.original_tower_images[key], (self.data.tile_zoom*img_size[0], self.data.tile_zoom*img_size[1]))
            self.current_tile_zoom = self.data.tile_zoom
        



    def Main(self) -> None:
        """
        Main function for the build hologram
        """
        self.Scale_hologram_images()
        
        if self.data.currently_building != "":
            self.__Build()



    def __Build(self) -> None:
        """
        Show the hologram and ultimately build the tower
        """
        mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=True)
        spike_pos_i: int = -1
        if (tile_pos[0], tile_pos[1]+1) == self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False):
            # Selected tile is on the map
            tower_can_build: bool = True
            if self.data.currently_building == "spikes":
                if tile_pos[0] < 0 or tile_pos[1] < 0 or tile_pos[0] >=  24 or tile_pos[1] >= 17:
                    tower_can_build = False
                else:
                    if self.tile_map_obj.map[tile_pos[1]][tile_pos[0]] not in data_class.Path_tiles:
                        tower_can_build = False
                if tower_can_build:
                    spike_pos_i = towers.spikes.Convert_pos_to_path_i(self.tile_map_obj, tile_pos)
                    if spike_pos_i == -1:
                        tower_can_build = False
                    else:
                        for spike in self.tower_handler.spikes:
                            if spike_pos_i == spike.pos_i:
                                tower_can_build = False
                                break
            else:
                tower_sub_tiles: list[tuple[int, int]] = []

                for i in range(self.tower_size[self.data.currently_building]):
                    for j in range(self.tower_size[self.data.currently_building]):
                        tower_sub_tiles.append((tile_pos[0]+i, tile_pos[1]+j))

                for sub_tile in tower_sub_tiles:
                    # Check if map-tile is buildable
                    if sub_tile[0] < 0 or sub_tile[1] < 0 or sub_tile[0] >=  24 or sub_tile[1] >= 17:
                        tower_can_build = False
                        break
                    else:
                        if self.tile_map_obj.map[sub_tile[1]][sub_tile[0]] not in data_class.Buildable_tiles:
                            tower_can_build = False
                            break
                    

                    # Check if the tile is already occupied by a tower
                    for tower in self.tower_handler.towers:
                        other_sub_tiles: list[tuple[int, int]] = []
                        for i in range(self.tower_size[tower.tower_name]):
                            for j in range(self.tower_size[tower.tower_name]):
                                other_sub_tiles.append((tower.tower_pos[0]+i, tower.tower_pos[1]+j))
                        if sub_tile in other_sub_tiles:
                            tower_can_build = False
                            break

            # Draw the hologram
            hologram_pos: tuple[int, int] = (tile_pos[0]*self.data.tile_zoom*8 + self.tile_map_obj.Get_left_right_empty_screen(), (tile_pos[1]+1)*self.data.tile_zoom*8)
            center_pos: tuple[int, int] = (tile_pos[0]*self.data.tile_zoom*8 + self.tile_map_obj.Get_left_right_empty_screen() + self.tower_size[self.data.currently_building]*4*self.data.tile_zoom, (tile_pos[1]+1)*self.data.tile_zoom*8 + self.tower_size[self.data.currently_building]*4*self.data.tile_zoom)
            self.data.screen.blit(self.tower_images[self.data.currently_building], hologram_pos)
            if tower_can_build:
                # Draw a green-overlay with alpha 50%
                overlay: pg.Surface = pg.Surface((self.data.tile_zoom*8*self.tower_size[self.data.currently_building], self.data.tile_zoom*8*self.tower_size[self.data.currently_building]), pg.SRCALPHA)
                overlay.fill((0, 0, 255, 50))
                self.data.screen.blit(overlay, hologram_pos)
            else:
                # Draw a red-overlay with alpha 50%
                overlay: pg.Surface = pg.Surface((self.data.tile_zoom*8*self.tower_size[self.data.currently_building], self.data.tile_zoom*8*self.tower_size[self.data.currently_building]), pg.SRCALPHA)
                overlay.fill((255, 0, 0, 50))
                self.data.screen.blit(overlay, hologram_pos)
            if self.tower_range[self.data.currently_building] > 0:
                pg.draw.circle(self.data.screen, (150,150,150), center_pos, int(self.tower_range[self.data.currently_building]*self.data.tile_zoom*8), self.data.tile_zoom)

            if tower_can_build:
                # Check if the mouse is pressed
                if pg.mouse.get_pressed()[0]:
                    # Build the tower
                    match self.data.currently_building:
                        case "ninja":
                            self.tower_handler.towers.append(
                                towers.ninja.Ninja(self.data, self.tile_map_obj, tile_pos))
                        case "bomber":
                            self.tower_handler.towers.append(
                                towers.bomber.Bomber(self.data, self.tile_map_obj, tile_pos))
                        case "machine_gunner":
                            self.tower_handler.towers.append(
                                towers.machine_gunner.Machine_gunner(self.data, self.tile_map_obj, tile_pos))
                        case "sniper":
                            self.tower_handler.towers.append(
                                towers.sniper.Sniper(self.data, self.tile_map_obj, tile_pos))
                        case "magician":
                            self.tower_handler.towers.append(
                                towers.magician.Magician(self.data, self.tile_map_obj, tile_pos))
                        case "shooter":
                            self.tower_handler.towers.append(
                                towers.shooter.Shooter(self.data, self.tile_map_obj, tile_pos))
                        case "bank":
                            self.tower_handler.towers.append(
                                towers.bank.Bank(self.data, self.tile_map_obj, tile_pos))
                        case "spikes":
                            self.tower_handler.spikes.append(
                                towers.spikes.New_spike(self.data, self.tile_map_obj, spike_pos_i, 20))
                            
                        case _:
                            logging.error(f"Unknown tower type: {self.data.currently_building}")
                            return
                            
                    self.data.currently_building = ""

                