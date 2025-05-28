# INSTRUCTIONS: Use the arrow keys to move around.
# Certain jumps may seem possible, but aren't. Certain jumps may seem impossible, but are completely achieveable.
# Move around the world and experience the movement and collision physics.



#Setup
import pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Allows referencing other files within the same folder without specifying the exact path to the file
pygame.init() # Initiates pygame

#Settings
SCREEN_INFO = pygame.display.Info()
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) # Creates the window the game runs in
WIDTH, HEIGHT = WIN.get_width(), WIN.get_height() # Gets the width and height of the users sceeen and saves them in variables
TITLE = "EJR Tile Platformer"
pygame.display.set_caption(TITLE)

# In case several block types are needed, this function allows that to happen easily.
def load(type):
	return pygame.image.load(f"img/{type}.png")

TILE_1 = load("tile_1") # Loads the first tile image
TILE_2 = load("tile_2") # Loads the second tile image
BG_TILE = load("bg_tile") # Loads the tile used as the blue background

PLAYER_COLOR = (255, 20, 147) # Sets the player color
PLAYER_TO_TILE_X, PLAYER_TO_TILE_Y = 1.3, 2 # Sets the player width and height ratio compared to the size of a tile
RUN_PEAK = WIDTH/200 # The maximum speed (in pixels per tick) of the player horizontally
SPRINT_PEAK = WIDTH/150 # The maximum speed (in pixels per tick) of the player vertically
DIRECTION_SWAP_SPEED = WIDTH/575 # The rate at which the player accelerates when changing directions
JUMP_HEIGHT = HEIGHT/55 # The jump strength of the player


# Creating a tile object for the background and the ground
class Tile:
	def __init__(self, x, y, type, tile_size): # This function is passed the x and y position, the tile type, and the tile size of a given tile object
		self.x = x
		self.y = y
		self.type = type
		self.width = tile_size

		self.rect = pygame.Rect( # Construct a rectangle of given dimensions to draw to the screen
			self.x,
			self.y,
			self.width,
			self.width
		)

	# This function checks if a tile is colliding with the player at any point
	def colliding(self, player, axis):
		if self.type != "Z":
			if axis == "x":
				if player.x + player.width > self.x and player.x < self.x + self.width:
					return True
			if axis == "y":
				if player.y + player.height > self.y and player.y < self.y + self.width:
					return True
			if axis == "both":
				if self.colliding(player, "x") and self.colliding(player, "y"):
					return True
		return False

	# This function draws the tile to the screen
	def draw(self, surface):
		# Scales the tile to the correct size
		def scale(type):
			return pygame.transform.scale(type, (round(self.width), round(self.width)))
		
		# Ensures the correct type of tile is drawn
		types = {
			"a": scale(TILE_1),
			"b": scale(TILE_2),
			"Z": scale(BG_TILE),
		}
		surface.blit(types[self.type], (self.x, self.y))

# Handles player collisions and level switching
def collideplayer(player, tiles, grav, vel, current_level, all_levels, tile_count_x, tile_size, tile_screen):
	y_collision = False # Initiates the y_collision variable. Collisions get checked later in the function
	grav_backup, vel_backup = grav, vel

	# Handles switching a level to the left
	if player.x + player.width/2 < 0:
		if current_level[1] > 0:
			current_level[1] -= 1
			player.x = WIDTH - player.width - 1
			vel = 0
			tile_count_x, tile_size, tiles, tile_screen = construct_tiles(current_level)
		else:
			player.x = -player.width/2
			vel = 0
	# Handles switching a level to the right
	if player.x + player.width/2 > WIDTH:
		if current_level[1] < len(all_levels[current_level[0]]) - 1:
			current_level[1] += 1
			player.x = -player.width/2 + 1
			vel = 0
			tile_count_x, tile_size, tiles, tile_screen = construct_tiles(current_level)
		else:
			player.x = WIDTH - player.width/2
			vel = 0
	# Handles switching a level down
	if player.y + player.height/2 < 0:
		if current_level[0] > 0:
			current_level[0] -= 1
			player.y = HEIGHT - player.height/2 - 1
			tile_count_x, tile_size, tiles, tile_screen = construct_tiles(current_level)
	# Handles switching a level up
	if player.y + player.height/2 > HEIGHT:
		if current_level[0] < len(all_levels) - 1:
			current_level[0] += 1
			player.y = -player.height/2 + 1
			tile_count_x, tile_size, tiles, tile_screen = construct_tiles(current_level)
		else:
			player.y = HEIGHT - player.height/2


	# Gets the players rough location relative to the tiles onscreen
	player_location_x = int(player.x/tile_size)
	player_location_y = int((HEIGHT - player.y)/tile_size)

	# Assembles a smaller array out of the tiles surrounding the player so that the function doesn't have to check collisions with every single tile, which would cause huge amounts of lag
	new_tiles = []
	for j in range(-1, int(PLAYER_TO_TILE_Y) + 2):
		col = player_location_y - j
		if col < 0 or col >= len(tiles):
			continue
		for i in range(-1, int(PLAYER_TO_TILE_X) + 2):
			row = player_location_x + i
		
			if row < 0 or row >= len(tiles[col]):
				continue
			new_tiles.append(tiles[col][row])

	# Checks if player is colliding with any of the tiles and moves the player appropriately
	for tile in new_tiles:
		if tile.colliding(player, "both"):
			player.x -= vel
			if tile.colliding(player, "both") and grav != 0:
					while tile.colliding(player, "y"):
						player.y += grav/abs(grav)
					if grav/abs(grav) == -1:
						y_collision = True
					grav = 0
			player.x += vel
			
			player.y += grav
			if tile.colliding(player, "both") and vel != 0:
					while tile.colliding(player, "x"):
						player.x -= vel/abs(vel)
					vel = 0
			player.y -= grav
			
	# Returns any information the function may have changed
	return (player, grav, vel, y_collision, current_level, tile_count_x, tile_size, tiles, tile_screen)

# This function draws the player and tiles to the screen
def draw_screen(player, tile_screen):
	WIN.fill("black")

	WIN.blit(tile_screen, (0, 0))

	pygame.draw.rect(WIN, PLAYER_COLOR, player)

	pygame.display.update()

# This function constructs the screen the tile configuration is saved on. This avoids the lag of redrawing every single tile 60 times a second
def construct_tiles(level, starting = False):
	# Reads the level layout from the levels file
	with open("levels.txt", "r") as levels_text:
		levels = levels_text.read()
	all_levels = levels.split("|")
	for row_index, row in enumerate(all_levels):
		all_levels[row_index] = row.split("-")

	# Gets the level the function is drawing
	current_level_tiles = all_levels[level[0]][level[1]]

	# Split the level file into each row
	split_tiles = current_level_tiles.split("/")

	tile_count_x = len(split_tiles[0])
	tile_size = WIDTH/tile_count_x

	# Constructs the tiles array
	tiles = []
	for j in range(int(HEIGHT/tile_size) + 1):
		tiles.append([])
		for i in range(tile_count_x):
			tiles[j].append(Tile(
				round(tile_size * i),
				round(HEIGHT - tile_size * (j+1)),
				split_tiles[j][i],
				tile_size
			))

	# Draws each tile to a tile screen, which can easily be drawn once every tick instead of drawing the hundreds of tiles every tick
	tile_screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
	for i in range(len(tiles)):
		for tile in tiles[i]:
			if tile.type == "Z":
				tile.draw(tile_screen)
	for i in range(len(tiles)):
		for tile in tiles[i]:
			if tile.type != "Z":
				tile.draw(tile_screen)

	# Checks if the function also needs to set the player size, which it does when it's first called
	if starting:
		player_width, player_height = tile_size * PLAYER_TO_TILE_X, tile_size * PLAYER_TO_TILE_Y

	# Return player information if necessary
	if starting:
		return (tile_count_x, tile_size, tiles, tile_screen, player_width, player_height, all_levels)
	return (tile_count_x, tile_size, tiles, tile_screen)


# The main game loop
def main():
	current_level = [0, 0] # Sets the level to start on (in this case, the top-left)
	clock = pygame.time.Clock()

	tile_count_x, tile_size, tiles, tile_screen, player_width, player_height, all_levels = construct_tiles(current_level, True) # Gets information about the player and tiles

	vel_peak = RUN_PEAK # Sets the players maximum horizontal speed
	y_collision = False # The player is not colliding with an object right now
	grav, vel = 0, 0 # Sets the player's horizontal and vertical speed to 0

	player = pygame.Rect( # Create the player object
		WIDTH/2 - player_width/2, HEIGHT/2 - player_height/2,
		player_width, player_height
	)

	while True:
		clock.tick(60) # Set the ticks per second of the game, which controls how often everything inside this while loop is run
		
		# Allows the user to quit the game either by closing it manually or by pressing "q"
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]:
			pygame.quit()
			quit()


		# Allows user control of the player by checking which keys have been pressed and performing the appropriate actions
		if keys[pygame.K_LCTRL]:
			vel_peak = SPRINT_PEAK
		else:
			vel_peak = RUN_PEAK
		if keys[pygame.K_LEFT] or keys[pygame.K_a]:
			if vel >= -vel_peak + DIRECTION_SWAP_SPEED:
				vel -= DIRECTION_SWAP_SPEED
			else:
				vel = -vel_peak
		if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
			if vel <= vel_peak - DIRECTION_SWAP_SPEED:
				vel += DIRECTION_SWAP_SPEED
			else:
				vel = vel_peak
		if (keys[pygame.K_UP] or keys[pygame.K_w]) and y_collision:
			grav = JUMP_HEIGHT


		# Controls the acceleration of gravity
		grav -= 0.4
		if grav < -tile_size:
			grav = -tile_size

		# Applies friction to the player, which stops the player if they're not moving
		if abs(vel) == vel:
			vel -= 0.4
		else:
			vel += 0.4

		# Change the player's actual position based on their horizontal and vertical speed
		player.x += vel
		player.y -= grav

		# Collide the player with the tiles and switch levels if necessart
		player, grav, vel, y_collision, current_level, tile_count_x, tile_size, tiles, tile_screen = collideplayer(player, tiles, grav, vel, current_level, all_levels, tile_count_x, tile_size, tile_screen)
		
		# Draws the player and the tiles to the screen
		draw_screen(player, tile_screen)


main() # Runs the main game loop