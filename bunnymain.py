import os
import sys
import pygame

import tmx
from player import *
from bunny import *

class Game:
    def main(self):
	screen = pygame.display.set_mode((256,224))
	pygame.display.set_caption('bunny_quest')
	clock = pygame.time.Clock()
	fps = 60

	pygame.mixer.init()
	pygame.mixer.music.load(os.path.join('music', 'music.ogg'))
	pygame.mixer.music.play()

	self.tilemap = tmx.load('level1.tmx', screen.get_size())

	self.sprites = tmx.SpriteLayer()
	player_start = self.tilemap.layers['triggers'].find('player')[0]
	self.player = Player((player_start.px, player_start.py), self.sprites)
	self.bunny = Bunny(self.sprites)
	self.tilemap.layers.append(self.sprites)

	while 1:
	    dt = clock.tick(fps)
	    dt = dt
	    
	    for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    return
		if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
		    return

	    self.tilemap.update(dt, self)
	    screen.fill((255,255,255))
	    self.tilemap.draw(screen)
	    pygame.display.flip()


if __name__=='__main__':
    pygame.init()
    Game().main()
