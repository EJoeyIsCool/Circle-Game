# Setup and settings

import pygame
import os
from random import randint, random
import math
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Allows referencing other files within the same folder without specifying the exact path to the file
pygame.init() # Initiates pygame
pygame.font.init() # Initiates the library that allows the code to render text

SCREEN_INFO = pygame.display.Info()
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # Creates the window the game runs in
WIDTH, HEIGHT = WIN.get_width(), WIN.get_height() # Gets the width and height of the window in pixels
TITLE = "Circle Game"
pygame.display.set_caption(TITLE)

BG_COLOR = (0, 0, 0, 230) # Background color. This has four values, but the fourth value (opacity) only applies for surfaces with the pygame.SRCALPHA tag, such as the ending screen
MOUSE_COLOR = (255, 255, 255) # Mouse color

MOUSE_RADIUS = 10 # The radius of the mouse

SPAWN_CHANCE = 0 # This many circles will spawn every second (on average). Initialized here but will be assigned a value later
SPEED_RANGE = [0, 0] # The range of speeds (in pixels per second) that a circle can travel at. Initialized here but will be assigned a value later
CIRCLE_RADIUS_LIMIT = 5 # A given circles radius is at most this much larger or smaller than the player
LIFE_LENGTH = 0 # The amount of seconds a given circle will last. Initialized here but will be assigned a value later

FONT = pygame.font.SysFont("futura", 45) # The font and font size used to render text
TEXT_COLOR = (240, 240, 240) # The text color

HEART = pygame.transform.scale(pygame.image.load("heart.png"), (45, 45)) # The image used to display heart icons in the top right of the screen
LIVES = 0 # The number of lives the player has. Initialized here but will be assigned a value later

IFRAMES_DURATION = 6 # The number of ticks after taking damage before the player can lose another heart

HIGH_SCORES = [0, 0, 0, 0] # The player's high scores across different game modes. Initialized here but will be assigned a value later
GAME_MODE = -1 # The game mode that the player is in. (0 is easy, 1 is medium, 2 is hard, and 3 is hardcore.) Initialized here but will be assigned a value later



# Definining the enemy class
class Circle:
	def __init__(self, radius, mouse, timer):
		self.color = (randint(55, 200), randint(55, 200), randint(55, 200)) # Instead of each value ranging from 0-255, these range from 55-200 in order to contrast them against both the mouse and the black background
		self.speed = random()*(SPEED_RANGE[1]-SPEED_RANGE[0]) + SPEED_RANGE[0] # Covers the SPEED_RANGE, but uses random() instead of randint() to return a float for more diverse possibilities
		self.radius = radius
		self.birth = timer

		# The following if/else statements pick a position somewhere on the edge of the screen for the circle to spawn, out of view by exactly a radius
		if randint(0, 1) == 0:
			if randint(0, 1) == 0:
				self.x = -self.radius
			else:
				self.x = WIDTH + self.radius
			self.y = randint(-self.radius, HEIGHT + self.radius)
		else:
			if randint(0, 1) == 0:
				self.y = -self.radius
			else:
				self.y = HEIGHT + self.radius
			self.x = randint(-self.radius, WIDTH + self.radius)

		distance = ((mouse.x-self.x)**2 + (mouse.y-self.y)**2)**0.5 # Calculates the distance between the circle and the mouse
		self.vector = [self.speed*(mouse.x-self.x)/distance, self.speed*(mouse.y-self.y)/distance] # Points towards the player using the unit distance vector times the circle's speed

	def draw(self):
		pygame.draw.circle(WIN, self.color, (self.x, self.y), self.radius)

	def move(self, mouse, timer):
		# This moves the circle according to its velocity vector
		self.x += self.vector[0]
		self.y += self.vector[1]
		
		# This is the same velocity vector calculation as earlier, so that the circle constantly adjusts its direction to be facing the player
		distance = ((mouse.x-self.x)**2 + (mouse.y-self.y)**2)**0.5
		self.vector = [self.speed*(mouse.x-self.x)/distance, self.speed*(mouse.y-self.y)/distance]

		# Here, returning True tells the function from which move() is being run that the circle should die of old age
		if timer >= self.birth + LIFE_LENGTH*60: # Multiply LIFE_LENGTH by 60 to convert it from seconds into ticks
			self.radius -= 0.1
			if self.radius <= 0:
				return True

		# Here, returning True tells the function from which move() is being run that the circle is offscreen and can now be deleted. This isn't really necesarry but it reduces lag in the case of a bug
		if self.x < -self.radius or self.x > WIDTH + self.radius:
			return True
		if self.y < -self.radius or self.y > HEIGHT + self.radius:
			return True
		return False

	def collide(self, mouse):
		distance = ((mouse.x-self.x)**2 + (mouse.y-self.y)**2)**0.5
		radii_sum = mouse.radius + self.radius

		# If the distance between the centers is less than the sum of the two circles' radii, we know the circles are overlapping
		if distance <= radii_sum:
			return True # This means that the circle and the mouse are colliding
		return False # This means that the circle and the mouse are not colliding

# Defining the player class
class Mouse:
	def __init__(self):
		self.x, self.y = 0, 0 # Initialize mouse position variables
		self.radius = MOUSE_RADIUS # Set the mouse radius
		self.color = MOUSE_COLOR # Set the mouse color
		self.lives = LIVES # Set the number of lives the player has

	def set_pos(self):
		# Move the mouse to the player's cursor
		mouse_coords = pygame.mouse.get_pos()
		self.x = mouse_coords[0]
		self.y = mouse_coords[1]

	def draw(self):
		self.set_pos() # Update position before drawing to the screen
		pygame.draw.circle(WIN, self.color, (self.x, self.y), self.radius)

	def collide(self, circle, since_hit):
		self.set_pos() # Update position before colliding with a circle
		if circle.collide(self):
			if since_hit > IFRAMES_DURATION: # If the player is not within their invincibility frames, they lose a life
				self.lives -= 1
			if self.lives <= 0:
				return "dead" # Tells the function from which this is being run that the player is dead
			return "pop" # Tells the function from which this is being run that the player was hit and the colliding circle can now be removed
		return "" # Return an empty string since we never do anything if no collision occured


# This function draws all of the objects present to the screen, then updates the screen to show the change
def draw_screen(mouse, circles, timer):
	WIN.fill(BG_COLOR) # Fills the background of the screen with the background color

	mouse.draw()

	for circle in circles:
		circle.draw()

	if timer: # Check if the game is running and the timer is still active
		timer_text = FONT.render(f"Time survived:  {round(timer/60, 1)} s", 1, TEXT_COLOR) # The timer is in ticks, so we must divde by 60. This value is rounded to look nicer and take up less space
		WIN.blit(timer_text, (10, 10)) # Places the timer text in the upper-left corner

	# Display the number of lives a player has remaining visually with hearts
	for i in range(mouse.lives):
		y = 10
		x = WIDTH - y - (i+1)*HEART.get_width()
		WIN.blit(HEART, (x, y))

	pygame.display.update() # Update the screen to show all of the changes made


# This function runs the main game loop
def main():
	clock = pygame.time.Clock()
	
	mouse = Mouse()
	circles = []

	timer = 0
	since_hit = 0

	while True:
		fps = round(((clock.tick(60) * 60) / 1000) * 60, 2) # Sets the ticks per second to 60. This also measures the actual frames per second (if needed)
		#print("FPS: ", fps) # If needed for debugging
		
		timer += 1 # Increment timer every tick
		since_hit += 1 # Increment the time since the player was hit every tick

		# This allows the player to close the program at any time, either by closing it manually or by pressing "q"
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]:
			pygame.quit()
			quit()

		# Spawn circles at an average rate of SPAWN_CHANCE circles per second
		if randint(0, 60)//(SPAWN_CHANCE) == 0: # If a circle should be spawned
			circle_radius = randint(mouse.radius - CIRCLE_RADIUS_LIMIT, mouse.radius + CIRCLE_RADIUS_LIMIT) # Set the new circle's radius to a random value within CIRCLE_RADIUS_LIMIT of MOUSE_RADIUS
			circles.append(Circle(circle_radius, mouse, timer)) # Add the new circle to the list of circles, passing it the randomly assigned radius and the position of the mouse (it needs the mouse position to know where to face)

		# Handle circles array, removing circles as needed
		for circle_index, circle in enumerate(circles):
			if circle.move(mouse, timer): # If a circle is offscreen, remove it
				circles.pop(circle_index)

			collision = mouse.collide(circle, since_hit) # Check if a circle has collided with the mouse and if the player is not still within their invincibility frames
			if collision == "pop": # If the player lost a life
				circles.pop(circle_index) # Remove the colliding circle from the list
				since_hit = 0 # Reset the time since the player was last hit
			elif collision == "dead": # If player runs out of hearts, end the script
				draw_screen(mouse, circles, False) # Renders the screen with no hearts left and no timer
				if timer > HIGH_SCORES[GAME_MODE]:
					HIGH_SCORES[GAME_MODE] = timer # Individual values of the global array HIGH_SCORES may be changed without writing global HIGH_SCORES
				return timer # Return the amount of time the player survived in order to display it on the end screen

		draw_screen(mouse, circles, timer)


# Defining end screen drawing function
def draw_end_screen(timer):
	transparent_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) # Creates a semi-transparent layer to display over the screen, showing the circles onscreen when the player died but making it easier to see the end screen text
	transparent_layer.fill(BG_COLOR) # Fills the semi-transparent layer with the background color
	WIN.blit(transparent_layer, (0, 0)) # Displays the semi-transparent layer, covering the entire screen by positioning the top left corner at (0, 0)

	end_text = FONT.render(f"You survived {round(timer/60, 1)} seconds!", 1, TEXT_COLOR)
	end_x = WIDTH/2 - end_text.get_width()/2
	end_y = HEIGHT/2 - end_text.get_height()/2 - 75
	WIN.blit(end_text, (end_x, end_y))

	record_text = FONT.render(f"Your best time for this gamemode is {round(HIGH_SCORES[GAME_MODE]/60, 1)} seconds!", 1, TEXT_COLOR)
	record_x = WIDTH/2 - record_text.get_width()/2
	record_y = HEIGHT/2 - record_text.get_height()/2
	WIN.blit(record_text, (record_x, record_y))

	close_text = FONT.render(f'Press "r" to restart, "d" for difficulty selector, or "q" to quit', 1, TEXT_COLOR)
	close_x = WIDTH/2 - close_text.get_width()/2
	close_y = HEIGHT/2 - close_text.get_height()/2 + 75
	WIN.blit(close_text, (close_x, close_y))

	pygame.display.update()

# Keeps end screen active until player quits
def end_screen(timer):
	clock = pygame.time.Clock()

	draw_end_screen(timer)

	while True:
		fps = round(((clock.tick(60) * 60) / 1000) * 60, 2)
		#print("FPS: ", fps)
		
		# This allows the player to close the program at any time, either by closing it manually or by pressing "q"
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]:
			pygame.quit()
			quit()

		if keys[pygame.K_r]: # Checks if player presses "r"
			end_screen(main()) # Restarts game loop without switching difficulties

		if keys[pygame.K_d]: # Checks if player presses "d"
			# Allow editing of global variables in order to switch gamemodes
			global SPAWN_CHANCE
			global LIVES
			global SPEED_RANGE
			global LIFE_LENGTH
			global GAME_MODE
			SPAWN_CHANCE, LIVES, SPEED_RANGE, LIFE_LENGTH, GAME_MODE = start_screen() # Difficulty selector
			end_screen(main()) # Restarts game loop after switching difficulties


# Defining start screen drawing function
def draw_start_screen():
	WIN.fill(BG_COLOR)

	instructions_text = FONT.render(f"Avoid the circles to survive!", 1, TEXT_COLOR)
	instructions_x = WIDTH/2 - instructions_text.get_width()/2
	instructions_y = HEIGHT/2 - instructions_text.get_height()/2 - 140
	WIN.blit(instructions_text, (instructions_x, instructions_y))

	easy_text = FONT.render(f"Easy: Press 1", 1, TEXT_COLOR)
	easy_x = WIDTH/2 - easy_text.get_width()/2
	easy_y = HEIGHT/2 - easy_text.get_height()/2 - 10
	WIN.blit(easy_text, (easy_x, easy_y))

	medium_text = FONT.render(f"Medium: Press 2", 1, TEXT_COLOR)
	medium_x = WIDTH/2 - medium_text.get_width()/2
	medium_y = HEIGHT/2 - medium_text.get_height()/2 + 40
	WIN.blit(medium_text, (medium_x, medium_y))

	hard_text = FONT.render(f"Hard: Press 3", 1, TEXT_COLOR)
	hard_x = WIDTH/2 - hard_text.get_width()/2
	hard_y = HEIGHT/2 - hard_text.get_height()/2 + 90
	WIN.blit(hard_text, (hard_x, hard_y))

	hardcore_text = FONT.render(f"Hardcore: Press 4", 1, TEXT_COLOR)
	hardcore_x = WIDTH/2 - hardcore_text.get_width()/2
	hardcore_y = HEIGHT/2 - hardcore_text.get_height()/2 + 140
	WIN.blit(hardcore_text, (hardcore_x, hardcore_y))

	pygame.display.update()

# Keeps start screen active until the player chooses a difficulty
def start_screen():
	clock = pygame.time.Clock()

	draw_start_screen()

	while True:
		fps = round(((clock.tick(60) * 60) / 1000) * 60, 2)
		#print("FPS: ", fps)

		# This allows the player to close the program at any time, either by closing it manually or by pressing "q"
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]:
			pygame.quit()
			quit()
		
		# Check which gamemode was selected and return SPAWN_CHANCE, LIVES, SPEED_RANGE, LIFE_LENGTH, and GAME_MODE
		if keys[pygame.K_1]:
			return 2, 6, [1, 3], 20, 0
		if keys[pygame.K_2]:
			return 3.5, 6, [2, 4], 30, 1
		if keys[pygame.K_3]:
			return 5, 5, [3, 5], 60, 2
		if keys[pygame.K_4]:
			return 4, 1, [3, 5.5], 100, 3

SPAWN_CHANCE, LIVES, SPEED_RANGE, LIFE_LENGTH, GAME_MODE = start_screen() # Render the difficulty selector screen and set the values returned to their corresponding variables
end_screen(main()) # Run the main game loop and pass the timer variable it returns into the end screen to display
