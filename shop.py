import data_class
import pygame as pg
import logging
import tile_map

import towers.build_hologram

class Shop:
    def __init__(self, data: data_class.Data_class, tile_map_obj: tile_map.Tile_map, hologram_builder: towers.build_hologram.Build_hologram) -> None:
        self.data: data_class.Data_class = data
        self.tile_map_obj: tile_map.Tile_map = tile_map_obj
        self.hologram_builder: towers.build_hologram.Build_hologram = hologram_builder

        self.current_tile_zoom: int = 1
        self.mouse_pressed: bool = False

        self.shop_base_price: dict[str, int] = {
            "ninja": 280,
            "bomber": 680,
            "machine_gunner": 480,
            "sniper": 550,
            "magician": 800,
            "shooter": 350
        }

        self.original_shop_images: dict[str, pg.Surface] = {
            "ninja": data.original_tower_images["ninja"]["up"],
            "bomber": data.original_tower_images["bomber"]["up"],
            "machine_gunner": data.original_tower_images["machine_gunner"]["up"],
            "sniper": data.original_tower_images["sniper"]["up"],
            "magician": data.original_tower_images["magician"]["up"],
            "shooter": data.original_tower_images["shooter"]["shop_img"]
        }

        self.shop_images: dict[str, pg.Surface] = {}
        self.Scale_shop_images(True)
    

    def Scale_shop_images(self, force_scaling: bool = False) -> None:
        """
        Scales the tower images to the current tile-zoom-level
        """
        if self.data.tile_zoom != self.current_tile_zoom or force_scaling:
            for key in self.original_shop_images.keys():
                self.shop_images[key] = pg.transform.scale(self.original_shop_images[key], (self.data.tile_zoom*16, self.data.tile_zoom*16))
            self.current_tile_zoom = self.data.tile_zoom

    def Main(self) -> None:
        """
        Main function for the shop
        """
        self.Scale_shop_images()

        if self.data.tower_selected == -1:
            title_pos: tuple[int, int] = (int(26.8*self.data.tile_zoom*8) + self.tile_map_obj.Get_left_right_empty_screen(), 1*self.data.tile_zoom*8)
            self.data.Draw_text("Shop", 8*self.data.tile_zoom, (255, 255, 255), title_pos)

            current_prices: dict[str, int] = {}
            for key in self.shop_base_price.keys():
                current_prices[key] = int(round((self.shop_base_price[key] * self.data.cost_multiplier)/10,0)*10)
            
            # Draw the shop
            tower_tile_pos: dict[str, tuple[int, int]] = {
                "ninja": (25, 2),
                "bomber": (27, 2),
                "machine_gunner": (29, 2),
                "sniper": (25, 5),
                "magician": (27, 5),
                "shooter": (29, 5)
            }

            for key in tower_tile_pos.keys():
                # Shop element
                tower_pos: tuple[int, int] = tower_tile_pos[key]
                tower_img: pg.Surface = self.shop_images[key]
                tower_price: int = current_prices[key]
                px_pos: tuple[int, int] = (tower_pos[0]*self.data.tile_zoom*8 + self.tile_map_obj.Get_left_right_empty_screen(), tower_pos[1]*self.data.tile_zoom*8)
                self.data.screen.blit(tower_img, px_pos)
                # Hover effect
                mouse_pos: tuple[int, int] = pg.mouse.get_pos()
                mouse_tile_pos: tuple[int, int] = self.tile_map_obj.Calculate_tile_pos_from_px_pos(mouse_pos, only_allow_map=False)
                shop_element_tiles: list[tuple[int, int]] = [(tower_pos[0], tower_pos[1]), (tower_pos[0]+1, tower_pos[1]), (tower_pos[0], tower_pos[1]+1), (tower_pos[0]+1, tower_pos[1]+1)]
                if mouse_tile_pos in shop_element_tiles:
                    if self.data.money >= tower_price:
                        self.data.Draw_text(str(tower_price)+"$", 5*self.data.tile_zoom, (255, 255, 50), (px_pos[0], px_pos[1] + 17*self.data.tile_zoom))
                        if pg.mouse.get_pressed()[0] and self.data.currently_building == "":
                            if not self.mouse_pressed:
                                self.mouse_pressed = True
                                self.data.currently_building = key
                                self.data.money -= tower_price
                        else:
                            self.mouse_pressed = False


                    else: # Not enough money
                        self.data.Draw_text(str(tower_price)+"$", 5*self.data.tile_zoom, (255, 50, 50), (px_pos[0], px_pos[1] + 17*self.data.tile_zoom))
                else: # Not hovered
                    self.data.Draw_text(str(tower_price)+"$", 5*self.data.tile_zoom, (255, 255, 255), (px_pos[0], px_pos[1] + 17*self.data.tile_zoom))



