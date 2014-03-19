import pygame
from random import choice, randint

import character

class Enemy(character.Character):
    def __init__(self, (start_x, start_y), full_image, hp, direction, (jumpy, shooty)):
	super(character.Character, self).__init__()
	self.image_full = pygame.image.load(full_image)
	self.images = {'idle': None, 'run': None, 'jump': None, 'hurt': None, 'dead': None, 'attack': None,}
	self.width, self.height = 16, 16
	self.split_multiple_images(full_image)
	self.direction = direction # -1:left, 1:right, 0:idle
	self.jumpy = jumpy
	self.shooty = shooty
	# from character.Character
	self.current_image = 'idle' # current image
	self.flip = False # whether image should be flipped horizontally or not
	self.frame = 0 # current frame in animation
	self.timer_frame = 0 # keeps track of time until next frame
	self.timer_frame_end = 0.1 # length in ~seconds for each frame
	self.timer_shoot = 0 # can only shoot when is 0
	self.timer_shoot_end = 0.2 # time ~seconds until can shoot again
	self.image = self.images[self.current_image]['image'][self.frame] # set current image
	self.speed = 25 # move speed
	self.y_velocity = 0.0
	self.y_velocity_max = 3.0
	self.jump_speed = -3.0
	# hp related
	self.hp = hp
	self.hp_invuln = False
	self.hp_invuln_time = 0.0 # seconds to be invulnerable after taking damage
	self.hp_invuln_timeleft = 0.0 # time until invulnerability ends
	# collision variables
	self.rect = pygame.Rect(start_x, start_y, self.width, self.height)
	self.touched_floor = False # true when touch ground, false after jumping
	self.base = 5 # length (in pixels) of characters foot base 
	self.base_start = self.width/3 # x (relative to character's x) where base begins
	self.base_end = self.base_start + self.base # x (relative to character's x) where base ends
    def split_multiple_images(self, full_image):
	enemy_name = full_image.rstrip('.png')
	if enemy_name == 'enemy1':
	    self.images['idle'] = self.split_images(0,1)
	    self.images['run'] = self.split_images(1,2)
	    self.images['jump'] = self.split_images(2,1)
	    self.images['hurt'] = self.split_images(3,1)
    # runs a bunch of functions
    def update(self, dt, objects, player, bullets):
	self.move(dt)
	if self.jumpy:
	    self.jump()
	self.set_image()
	self.animate(dt)
	self.gravity(dt)
	self.collision(objects, player, bullets)
	self.health(dt)
    def collision(self, objects, player, bullets):
	# player collision
	if self.rect.colliderect(player.rect) and not(self.hp_invuln):
	    self.hp_invuln = True
	    self.hp_invuln_timeleft = self.hp_invuln_time
	    self.hp -= 1
	# block collision
	for object in objects:
	    if object.properties.has_key('wall') and not object.properties.has_key('spawn'): # disregard objects that aren't walls
		object_right = object.x + object.width - 1
		object_bottom = object.y + object.height - 1
		self_right = self.rect.x + self.width - 1
		self_bottom = self.rect.y + self.height - 1
		coll_object = pygame.Rect(object.x, object.y, object.width, object.height)
		if self.rect.colliderect(coll_object):
		    # collision on character's left side
		    if 'r' in object.properties['wall'] and self.rect.x < object_right and self_bottom > object.y:
			self.rect.x = object_right
			self.direction = -self.direction
		    # collision on character's right side
		    if 'l' in object.properties['wall'] and self_right > object.x and self_bottom > object.y:
			self.rect.x = object.x - self.width
			self.direction = -self.direction
		    # collision on character's top 
		    if 'b' in object.properties['wall'] and self.rect.y < object_bottom:
			self.rect.y = object_bottom
			if self.jumpy:
			    self.jump()
		    # collision on character's bottom
		    # the '4' means the character's bottom must be within 4 pixels of the blocks top to stand on it
		    if 't' in object.properties['wall'] and (self.rect.y + self.height) < object.y + 4:
			# also check if character's base touches the block, rather than just the object's entire rect
			if (self.rect.x + self.base_start) <= object_right and (self.rect.x + self.base_end) >= object.x:
			    if self.y_velocity >= 0.0:
				self.touched_floor = True
				self.rect.y = object.y - self.height
				# set character's y velocity to zero
				self.y_velocity = 0.0


class EnemyController:
    def __init__(self, group, objects):
	self.group = group
	self.spawn_list = []
	self.locateSpawns(objects)
	self.enemy_images = ['enemy1.png']
	# behaviors = (jumpy, shooty)
	self.enemy_behaviors = [(True, False)]
	self.enemy_hp = [1]
    def locateSpawns(self, objects):
	for object in objects:
	    # add x and y of objects with 'spawn' key to list of places to spawn enemies
	    if object.properties.has_key('spawn'):
		self.spawn_list.append((object.x, object.y))
    def spawn(self):
	random_spawn = choice(self.spawn_list)
	# i will be random index to choose image, #frames, 
	i = randint(0, len(self.enemy_images)-1)
	# enemy starts moving right if on left edge of screen
	if random_spawn[0] < 16:
	    direction = 1
	# enemy starts moving left if on right edge of screen
	elif random_spawn[0] >= 128:
	    direction = -1
	# if spawn is in middle, start moving in a random direction
	else:
	    direction = choice([-1,1])
	image = self.enemy_images[i]
	hp = self.enemy_hp[i]
	behaviors = self.enemy_behaviors[i]
	return Enemy(random_spawn, image, hp, direction, behaviors) 
