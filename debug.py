import pygame as pg
import logging
import data_class
import random



class Debug:
    def __init__(self, data: data_class.Data_class) -> None:
        self.data: data_class.Data_class = data
        self.fps_debug_open: bool = False
        self.map_debug_open: bool = False
        self.debug_button_clicked: bool = False

    
    def Fps_render(self, zoom: int, mspf: list[float], mspf_raw: list[float]) -> None:
        rect_surface = pg.Surface((55 * zoom, 28 * zoom), pg.SRCALPHA)
        rect_surface.fill((0, 0, 0, 150))  # Adding alpha for transparency
        self.data.screen.blit(rect_surface, (0, 0))

        self.data.Draw_text(f"FPS:     {round(1//(round(data_class.Avg(mspf),1)/1000),1)}", 6*zoom, (255,255,255), (1*zoom, 1*zoom))
        self.data.Draw_text(f"FPS 90%: {round(1//(round(data_class.Avg_worst_10_percent(mspf),1)/1000),1)}", 6*zoom, (255,255,255), (1*zoom, 7*zoom))
        self.data.Draw_text(f"MSPF:    {round(data_class.Avg(mspf),1)}", 6*zoom, (255,255,255), (1*zoom, 13*zoom))
        self.data.Draw_text(f"MSPF_r:  {round(data_class.Avg(mspf_raw),1)}", 6*zoom, (255,255,255), (1*zoom, 19*zoom))

        pg.draw.line(self.data.screen, (0,0,0), (self.data.screen_size[0]//2,0), (self.data.screen_size[0]//2,self.data.screen_size[1]), self.data.hud_zoom)
        pg.draw.line(self.data.screen, (0,0,0), (0,self.data.screen_size[1]//2), (self.data.screen_size[0],self.data.screen_size[1]//2), self.data.hud_zoom)





    def Debug_main(self, hud_zoom: int, mspf: list[float], mspf_raw: list[float]) -> None:
        if pg.key.get_pressed()[pg.K_F1]:
            if not self.debug_button_clicked:
                self.fps_debug_open = not self.fps_debug_open
                self.debug_button_clicked = True
        else:        
            if pg.key.get_pressed()[pg.K_F2]:
                if not self.debug_button_clicked:
                    self.map_debug_open = not self.map_debug_open
                    self.debug_button_clicked = True
            else:        
                self.debug_button_clicked = False



        if self.fps_debug_open:
            self.Fps_render(hud_zoom, mspf, mspf_raw)