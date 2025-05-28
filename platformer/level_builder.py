# INSTRUCTIONS: Draw or erase tiles by left clicking. To enter drawing mode, press "1" or "2". To enter eraser mode, press "e".
# To save the current tile configuration, hit "p" and copy and paste the printed console line into the levels file.



#Setup
import pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()

# Settings
SCREEN_INFO = pygame.display.Info()
WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = WIN.get_width(), WIN.get_height()
TITLE = "Tile Platformer Level Builder"
pygame.display.set_caption(TITLE)

BG_COLOR = (135, 206, 235) # Background color

TILE_COUNT_X = 30 # Number of columns
TILE_SIZE = WIDTH/TILE_COUNT_X # The size of every tile

# Allows the script to load all of the tile types
def load(type):
	return pygame.image.load(f"img/{type}.png")

# Gets each tile image and assigns them to a variable
TILE_1 = load("tile_1")
TILE_2 = load("tile_2")
BG_TILE = load("bg_tile")

# Creates the tiles array
tiles = []
for i in range(int(HEIGHT/TILE_SIZE) + 1):
	tiles.append("")
	for _ in range(TILE_COUNT_X):
		tiles[i] += "Z" # A background tile is represented with the letter "Z"

# Draws a given tile to the screen
def draw_tile(surface, type, placement, opacity = 255):
	def scale(type):
		return pygame.transform.scale(type, (round(TILE_SIZE), round(TILE_SIZE)))
	
	# Ensures the correct type of tile is drawn	
	types = {
		"a": scale(TILE_1),
		"b": scale(TILE_2),
		"Z": scale(BG_TILE)
	}
	surface.blit(types[type], placement)

# Draws the tiles and mouse position to the screen
def draw_screen(tile_screen, mouse_alpha, mouse_x, mouse_y):
	WIN.fill("black")

	WIN.blit(tile_screen, (0, 0))

	# Creates a semi-transparent block at the mouse position to indicate where the block will be placed
	mouse_block_surface = pygame.Surface((round(TILE_SIZE), round(TILE_SIZE)), pygame.SRCALPHA)
	pygame.draw.rect(mouse_block_surface, (0, 0, 0), pygame.Rect(0, 0, round(TILE_SIZE), round(TILE_SIZE)))
	mouse_block_surface.set_alpha(mouse_alpha)
	WIN.blit(mouse_block_surface, (round(mouse_x * TILE_SIZE), round(HEIGHT - TILE_SIZE * (mouse_y + 1))))

	# Update the screen so that everything drawn is actually displayed
	pygame.display.update()

# Creates a single surface with all of the tiles drawn onto it instead of drawing hundreds of tiles every frame, which would cause lag
def create_tile_screen(tiles):
	tile_screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
	for row in range(len(tiles)):
		for tile_index, tile in enumerate(tiles[row]):
			draw_tile(tile_screen, tile, (round(tile_index * TILE_SIZE), round(HEIGHT - TILE_SIZE * (row + 1))))
	return tile_screen

# The function that actually runs all the code
def main(tiles):
	pygame.display.update()
	clock = pygame.time.Clock()
	drawing_mode = "a" # Sets the type of block drawn with the mouse
	mouse_alpha = 175 # Sets the opacity of the mouse overlay
	tile_screen = create_tile_screen(tiles) # Creates the tile screen
	draw_screen(tile_screen, 0, WIDTH, HEIGHT) # Draws the screen

	while True:
		clock.tick(60) # Sets the ticks per second to 60

		# Allows the user to quit the game either by closing it manually or by pressing "q"
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		keys = pygame.key.get_pressed()
		if keys[pygame.K_q]:
			pygame.quit()
			quit()

		# Detects the users keypresses in order to use the desired block when drawing
		keys = pygame.key.get_pressed()
		if keys[pygame.K_e]:
			if keys[pygame.K_LCTRL]:
				for row_index in range(len(tiles)):
					tiles[row_index] = "Z" * TILE_COUNT_X
			else:
				drawing_mode = "Z"
				mouse_alpha = 50
		if keys[pygame.K_1]:
			if keys[pygame.K_LCTRL]:
				for row_index in range(len(tiles)):
					tiles[row_index] = "a" * TILE_COUNT_X
				tile_screen = create_tile_screen(tiles)
			else:
				drawing_mode = "a"
				mouse_alpha = 175
		if keys[pygame.K_2]:
			if keys[pygame.K_LCTRL]:
				for row_index in range(len(tiles)):
					tiles[row_index] = "b" * TILE_COUNT_X
				tile_screen = create_tile_screen(tiles)
			else:
				drawing_mode = "b"
				mouse_alpha = 175

		# Print out the current level configuration and close the program if the player presses "p"
		if keys[pygame.K_p]:
			level_tiles = ""
			for row_index, row in enumerate(tiles):
				level_tiles += row
				if row_index < len(tiles) - 1:
					level_tiles += "/"
			print(level_tiles)
			pygame.quit()
			quit()
		
		# Gets information about the mouse to help position the placed blocks
		mouse_coords = pygame.mouse.get_pos()
		mouse_coords = (mouse_coords[0], HEIGHT - mouse_coords[1])
		mouse_x = int(mouse_coords[0]/TILE_SIZE)
		mouse_y = int(mouse_coords[1]/TILE_SIZE)

		# Places a block
		if pygame.mouse.get_pressed()[0]:
			if mouse_y < len(tiles) and mouse_x < TILE_COUNT_X:
				tiles[mouse_y] = tiles[mouse_y][:mouse_x] + drawing_mode + tiles[mouse_y][mouse_x + 1:]
			tile_screen = create_tile_screen(tiles) # Updates the tile screen to show the new tile
		
		draw_screen(tile_screen, mouse_alpha, mouse_x, mouse_y) # Draws the screen

main(tiles) # Runs the main loop