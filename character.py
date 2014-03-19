import pygame

class Character(pygame.sprite.Sprite):
    def __init__(self, (start_x, start_y), full_image):
	super(Character, self).__init__()
	self.image_full = pygame.image.load(full_image)
	self.width, self.height = 16, 16	
	self.images = {'idle': None, 'run': None, 'jump': None, 'hurt': None, 'dead': None, 'attack': None,}
	# split_image( row, number of images in row )
	self.images['idle'] = self.split_images(0, 1)
	self.images['run'] = self.split_images(1, 2)
	self.images['jump'] = self.split_images(2, 1)
	self.images['hurt'] = self.split_images(3, 1)
	self.current_image = 'idle' # current image
	self.flip = False # whether image should be flipped horizontally or not
	self.frame = 0 # current frame in animation
	self.timer_frame = 0 # keeps track of time until next frame
	self.timer_frame_end = 0.1 # length in ~seconds for each frame
	self.timer_shoot = 0 # can only shoot when is 0
	self.timer_shoot_end = 0.2 # time ~seconds until can shoot again
	self.image = self.images[self.current_image]['image'][self.frame] # set current image
	self.speed = 50 # move speed
	self.direction = 0 # -1:left, 1:right, 0:idle
	self.y_velocity = 0.0
	self.y_velocity_max = 3.0
	self.jump_speed = -3.0
	# hp related
	self.hp = 3
	self.hp_invuln = False
	self.hp_invuln_time = 1.0 # seconds to be invulnerable after taking damage
	self.hp_invuln_timeleft = 0.0 # time until invulnerability ends
	# collision variables
	self.rect = pygame.Rect(start_x, start_y, self.width, self.height)
	self.touched_floor = False # true when touch ground, false after jumping
	self.base = 5 # length (in pixels) of characters foot base 
	self.base_start = self.width/3 # x (relative to character's x) where base begins
	self.base_end = self.base_start + self.base # x (relative to character's x) where base ends
    # splits an image composed of many images into seperate images (ie. spritesheet => seperate images)
    def split_images(self, row, num_of_images):
	frames = []	
	for x in range(0, num_of_images):
	    new_frame = self.image_full.subsurface(pygame.Rect(x * self.width, row*self.height, self.width, self.height))
	    frames.append(new_frame)
	return {'image': frames, 'num_frames': num_of_images}
    # runs a bunch of functions
    def update(self, dt, objects, enemies, bullets):
	self.move(dt)
	self.set_image()
	self.animate(dt)
	self.gravity(dt)
	self.collision(objects, enemies, bullets)
	self.health(dt)
    # move character left/right and apply gravity
    def move(self, dt):
	self.rect.x += round(self.speed * dt) * self.direction
	self.rect.y += self.y_velocity
    # makes the character jump!
    def jump(self):
	 # self.y_velocity <= 1.0 because velocity is constantly being increased due to gravity
	 # and fluctuates between 0.0 and slightly higher values
	if self.touched_floor and self.y_velocity <= 1.0:
	    self.y_velocity = self.jump_speed
	    self.touched_floor = False
    # sets appropriate sprite image
    def set_image(self):
	old_image = self.current_image # for checking to see if image changes (to reset current frame to 0)
	# flips image horizontally if necessary
	if self.direction == -1:
	    self.flip = True
	if self.direction == 1:
	    self.flip = False
	# IDLE
	if self.direction == 0:
	    self.current_image = 'idle'
	# RUN
	if self.direction != 0:
	    self.current_image = 'run'
	# JUMP
	if self.touched_floor == False:
	    self.current_image = 'jump'
	# HURT
	if self.hp_invuln == True:
	    self.current_image = 'hurt'
	# only set new image if not already set to appropriate image
	if old_image != self.current_image:
	    self.frame = 0
	image = pygame.transform.flip(self.images[self.current_image]['image'][self.frame], self.flip, False)
	self.image = image
    # keeps track of frames, time passed between frames, and sets the appropriate frame
    def animate(self, dt):
	self.set_image()
	if self.timer_frame > self.timer_frame_end:
	    self.frame += 1
	    self.timer_frame = 0
	if self.frame >= self.images[self.current_image]['num_frames']:
	    self.frame = 0
	self.timer_frame += dt
    # calculates y velocity
    def gravity(self, dt):
	self.y_velocity += dt*5.0 # adjusted to make player fall more quickly
	self.y_velocity = min(self.y_velocity, self.y_velocity_max)
    # checks for collisisons with objects
    def collision(self, objects, enemies, bullets):
	# enemy collision
	for enemy in enemies:
	    if self.rect.colliderect(enemy.rect) and not(self.hp_invuln):
		self.hp_invuln = True
		self.hp_invuln_timeleft = self.hp_invuln_time
		self.hp -= 1
	# block collision
	for object in objects:
	    if object.properties.has_key('wall'): # disregard objects that aren't walls
		object_right = object.x + object.width - 1
		object_bottom = object.y + object.height - 1
		self_right = self.rect.x + self.width - 1
		self_bottom = self.rect.y + self.height - 1
		coll_object = pygame.Rect(object.x, object.y, object.width, object.height)
		if self.rect.colliderect(coll_object):
		    # collision on character's left side
		    if 'r' in object.properties['wall'] and self.rect.x < object_right and self_bottom > object.y: 
			self.rect.x = object_right
		    # collision on character's right side
		    if 'l' in object.properties['wall'] and self_right > object.x and self_bottom > object.y:
			self.rect.x = object.x - self.width
		    # collision on character's top 
		    if 'b' in object.properties['wall'] and self.rect.y < object_bottom:
			self.rect.y = object_bottom
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
    def health(self, dt):
	if self.hp_invuln_timeleft < 0.0:
	    self.hp_invuln = False
	    self.hp_invuln_timeleft = 0.0
	else:
	    self.hp_invuln_timeleft -= dt
	if self.hp <= 0:
	    print('DEAD')
	    # respawn animation or something
	    # preferably new lumenaut flying in from off-screen
	    self.hp = 3
