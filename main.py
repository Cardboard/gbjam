import pygame
import os
import sys
import tiledtmxloader as tmx

# game classes
from character import *
from enemy import *

pygame.init()
pygame.mixer.init()

def main():
    # game set up variables 
    WINDOW_WIDTH, WINDOW_HEIGHT = 640, 576
    PRE_WIDTH, PRE_HEIGHT = 160, 144
    PRE_SCALED = pygame.surface.Surface((PRE_WIDTH, PRE_HEIGHT))
    WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
   # WINDOW = pygame.display.set_mode((PRE_WIDTH, PRE_HEIGHT))
    pygame.display.set_caption('gbjam - cardboard')
    CLOCK = pygame.time.Clock()
    FPS = 30
    # load map, set up camera
    tilemap = tmx.tmxreader.TileMapParser().parse_decode('level1.tmx')
    resources = tmx.helperspygame.ResourceLoaderPygame()
    resources.load(tilemap)
    renderer = tmx.helperspygame.RendererPygame()
    cam_pos_x = PRE_WIDTH/2
    cam_pos_y = PRE_HEIGHT/2
    renderer.set_camera_position_and_size(cam_pos_x, cam_pos_y, \
	    PRE_WIDTH, PRE_HEIGHT, 'center')
    # retrieve layers
    layers = tmx.helperspygame.get_layers_from_map(resources)
    sprite_layers = []
    for layer in layers:
	if not layer.is_object_group:
	    sprite_layers.append(layer)
	else:
	    object_layer = layer

    # set up sprites
    player = Character((64, 112), 'player.png')
    sprites = pygame.sprite.Group()
    sprites.add(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    # enemy controller spawns enemies
    enemyCont = EnemyController(enemies, object_layer.objects)
    
    running = True
    # main loop
    while running:
	dt = CLOCK.tick(FPS) / 1000.0
	keys = pygame.key.get_pressed() # store keypresses
	# events that should only happen once per keypress
	for event in pygame.event.get():
	    if event.type == pygame.KEYDOWN:
		if event.key == pygame.K_ESCAPE:
		    print('quitting..')
		    sys.exit()
		    pygame.quit()
		if event.key == pygame.K_UP:
		    player.jump()
		if event.key == pygame.K_SPACE:
		    new_enemy = enemyCont.spawn()
		    enemies.add(new_enemy)
	#PRE_SCALED.fill((255,255,255))
	if keys[pygame.K_RIGHT]:
	    player.direction = 1
	if keys[pygame.K_LEFT]:
	    player.direction = -1
	if not(keys[pygame.K_RIGHT] or keys[pygame.K_LEFT]):
	    player.direction = 0
	# update all sprites
	sprites.update(dt, object_layer.objects, enemies, bullets)
	enemies.update(dt, object_layer.objects, player, bullets)
	# draw stuff then update display
	for sprite_layer in sprite_layers:
	    if sprite_layer.is_object_group:
		continue
	    else:
		renderer.render_layer(PRE_SCALED, sprite_layer)
	#for object in object_layer.objects:
	#    pygame.draw.rect(PRE_SCALED, (255,255,255), (object.x, object.y, object.width, object.height))
	enemies.draw(PRE_SCALED)
	sprites.draw(PRE_SCALED)
	#pygame.draw.line(PRE_SCALED, (255, 10, 56), (player.rect.x+player.base_start, player.rect.bottom), (player.rect.x+player.base_end, player.rect.bottom))
#	pygame.transform.scale(PRE_SCALED, (PRE_WIDTH, PRE_HEIGHT), WINDOW)
	pygame.transform.scale(PRE_SCALED, (WINDOW_WIDTH, WINDOW_HEIGHT), WINDOW)
	pygame.display.update()


if __name__ == '__main__':
    main()
