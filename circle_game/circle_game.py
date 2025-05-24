# Setup and settings

import pygame
import os
from random import randint
from random import random
import math
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Allows referencing other files within the same folder without specifying the exact path to the file
pygame.init() # Initiates pygame
pygame.font.init() # Initiates the library that allows the code to render text

SCREEN_INFO = pygame.display.Info()
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # Creates the window the game runs in
WIDTH, HEIGHT = WIN.get_width(), WIN.get_height() # Gets the width and height of the window in pixels
TITLE = "Mouse Game"
pygame.display.set_caption(TITLE)

BG_COLOR = (0, 0, 0, 200) # Background color. This has four values, but the fourth value (opacity) only applies for surfaces with the pygame.SRCALPHA tag, such as the ending screen
MOUSE_COLOR = (255, 255, 255) # Mouse color

STARTING_RADIUS = 10 # The initial radius of the mouse

STARTING_SPAWN_CHANCE = 5 # At the start of the game, one circle will spawn every second (on average)
CIRCLE_RADIUS_LIMIT = 5 # A given circles radius is at most this much larger than the player

FONT = pygame.font.SysFont("futura", 45) # How to render text, specifying the font and the text size
TEXT_COLOR = (240, 240, 240)

HEART = pygame.transform.scale(pygame.image.load("heart.png"), (45, 45))
LIVES = 5

IFRAMES_DURATION = 6 # The number of ticks after taking damage before the player can lose another heart


# Definining classes for all of the entities needed in the game

class Circle:
	def __init__(self, radius, mouse):
		self.color = (randint(55, 200), randint(55, 200), randint(55, 200)) # Instead of each value ranging from 0-255, these range from 55-200 in order to contrast them against both the mouse and the black background
		self.speed = random()*2 + 3 # Ranges from 3-5
		self.radius = radius

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

		distance = ((mouse.x-self.x)**2 + (mouse.y-self.y)**2)**0.5
		self.vector = [self.speed*(mouse.x-self.x)/distance, self.speed*(mouse.y-self.y)/distance] # Points towards the player using the unit distance vector times a randomly assigned speed

	def draw(self):
		pygame.draw.circle(WIN, self.color, (self.x, self.y), self.radius)

	def move(self, mouse):
		# This moves the circles according to their velocity vectors
		self.x += self.vector[0]
		self.y += self.vector[1]
		
		# This is the same velocity vector calculation as earlier, so that the circle constantly adjusts its direction to be facing the player
		distance = ((mouse.x-self.x)**2 + (mouse.y-self.y)**2)**0.5
		self.vector = [self.speed*(mouse.x-self.x)/distance, self.speed*(mouse.y-self.y)/distance]

		# Here, returning True tells the function from which move() is being run that the circle is offscreen and can now be deleted
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
			return True
		return False

class Mouse:
	def __init__(self):
		self.x, self.y = 0, 0 # Initialize mouse position variables
		self.radius = STARTING_RADIUS
		self.color = MOUSE_COLOR
		self.lives = LIVES

	def set_pos(self):
		mouse_coords = pygame.mouse.get_pos()
		self.x = mouse_coords[0]
		self.y = mouse_coords[1]

	def draw(self):
		self.set_pos()
		pygame.draw.circle(WIN, self.color, (self.x, self.y), self.radius)

	def collide(self, circle, since_hit):
		self.set_pos()
		if circle.collide(self):
			if since_hit > IFRAMES_DURATION: # If the player is not within their invincibility frames, they lose a life
				self.lives -= 1
			if self.lives <= 0:
				return "dead"
			return "pop"
		return "" # Return an empty string since we never do anything if no collision occured


# This function draws all of the objects present to the screen, then updates the screen to show the change
def draw_screen(mouse, circles, timer):
	WIN.fill(BG_COLOR) # Fills the background of the screen with the background color

	mouse.draw()

	for circle in circles:
		circle.draw()

	if timer: # Check if the game is running and the timer is still active
		timer_text = FONT.render(f"Time survived:  {round(timer/60, 1)} s", 1, TEXT_COLOR) # The reason the timer is divided by 60 and rounded to the nearest decimal place is because the timer is in ticks
		WIN.blit(timer_text, (10, 10)) # Places the timer text in the upper-left corner

	# Display the number of lives a player has remaining visually with hearts
	for i in range(mouse.lives):
		y = 10
		x = WIDTH - y - (i+1)*HEART.get_width()
		WIN.blit(HEART, (x, y))

	pygame.display.update() # Update the screen to show all of the changes made


# This function is the game loop
def main():
	clock = pygame.time.Clock()
	
	mouse = Mouse()
	circles = []

	timer = 0
	since_hit = 0

	spawn_chance = STARTING_SPAWN_CHANCE

	while True:
		fps = round(((clock.tick(60) * 60) / 1000) * 60, 2) # Sets the ticks per second to 60. It also measures the actual frames per second (if needed)
		#print("FPS: ", fps) # If needed for debugging
		
		timer += 1
		since_hit += 1

		# If the player wants to close the program, this allows them to
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return

		# Spawn circles at an average rate of spawn_chance circles per second
		if randint(0, 60)//(spawn_chance) == 0:
			circle_radius = randint(STARTING_RADIUS//2, mouse.radius + CIRCLE_RADIUS_LIMIT)
			circles.append(Circle(circle_radius, mouse))

		# Handle circles array, removing circles as needed
		for circle_index, circle in enumerate(circles):
			if circle.move(mouse):
				circles.pop(circle_index)
			collision = mouse.collide(circle, since_hit)
			if collision == "pop":
				circles.pop(circle_index)
				since_hit = 0
			elif collision == "dead": # If player runs out of hearts, end the script
				draw_screen(mouse, circles, False) # Renders the screen with no hearts left and no timer
				return timer # Passes timer to the end screen to display how long the player survived

		draw_screen(mouse, circles, timer)


# Defining end screen drawing function
def draw_end_screen(timer):
	transparent_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
	transparent_layer.fill(BG_COLOR)
	WIN.blit(transparent_layer, (0, 0))

	end_text = FONT.render(f"You survived {round(timer/60, 1)} seconds!", 1, TEXT_COLOR)
	end_x = WIDTH/2 - end_text.get_width()/2
	end_y = HEIGHT/2 - end_text.get_height()/2 - 50
	WIN.blit(end_text, (end_x, end_y))

	close_text = FONT.render(f'Press "q" to quit', 1, TEXT_COLOR)
	close_x = WIDTH/2 - close_text.get_width()/2
	close_y = HEIGHT/2 - close_text.get_height()/2 + 50
	WIN.blit(close_text, (close_x, close_y))

	pygame.display.update()

# Keeps end screen active until player quits
def end_screen(timer):
	clock = pygame.time.Clock()

	draw_end_screen(timer)

	while True:
		fps = round(((clock.tick(60) * 60) / 1000) * 60, 2)
		#print("FPS: ", fps)
		
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return

		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]: # Checks if player presses "q"
			return # Ends program

# Defining start screen drawing function
def draw_start_screen():
	WIN.fill(BG_COLOR)

	instructions_text = FONT.render(f"Avoid the circles to survive!", 1, TEXT_COLOR)
	instructions_x = WIDTH/2 - instructions_text.get_width()/2
	instructions_y = HEIGHT/2 - instructions_text.get_height()/2 - 50
	WIN.blit(instructions_text, (instructions_x, instructions_y))

	start_text = FONT.render(f"Press any key to start...", 1, TEXT_COLOR)
	start_x = WIDTH/2 - start_text.get_width()/2
	start_y = HEIGHT/2 - start_text.get_height()/2 + 50
	WIN.blit(start_text, (start_x, start_y))

	pygame.display.update()

# Keeps start screen active until player presses a key and starts game
def start_screen():
	clock = pygame.time.Clock()

	draw_start_screen()

	while True:
		fps = round(((clock.tick(60) * 60) / 1000) * 60, 2)
		#print("FPS: ", fps)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
			if event.type == pygame.KEYDOWN:
				return # Ends the start screen when any key is pressed, starting the main game loop

start_screen() # Render the start screen
end_screen(main()) # Run the main game loop, then pass the timer value returned into the end screen function to display time survived
