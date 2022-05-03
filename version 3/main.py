import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")

from GUI import *


GAME_SIZE = (700, 700)
CELL_SIZE = (30, 30)


def Quit():
	global RUNNING
	RUNNING = False


class Cell:
	def __init__(self, rect):
		self.rect = pg.Rect(rect)

	def Draw(self, color):
		pg.draw.lines(screen, color, True, [(self.rect.x, self.rect.y), (self.rect.x + self.rect.w, self.rect.y), (self.rect.x + self.rect.w, self.rect.y + self.rect.h), (self.rect.x, self.rect.y + self.rect.h)])


class Board:
	# number of cells in the game view 
	num_of_cells = (GAME_SIZE[0] // CELL_SIZE[0], GAME_SIZE[1] // CELL_SIZE[1])

	screen_pos = ((width // 2) - (GAME_SIZE[0] // 2), (height // 2) - (GAME_SIZE[1] // 2))
	
	grid = []

	color = black
	rect = pg.Rect(screen_pos[0], screen_pos[1], GAME_SIZE[0], GAME_SIZE[1])

	def CreateBoard():
		Board.grid = [[Cell((Board.rect.x + (x * CELL_SIZE[0]), Board.rect.y + (y * CELL_SIZE[1]), CELL_SIZE[0], CELL_SIZE[1])) for y in range(Board.num_of_cells[0])] for x in range(Board.num_of_cells[1])]

	def Draw():
		DrawRectOutline(Board.color, (Board.rect.x - 1, Board.rect.y - 1, (Board.num_of_cells[0] * CELL_SIZE[0]) + 1, (Board.num_of_cells[1] * CELL_SIZE[1]) + 1))

		for row in Board.grid:
			for cell in row:
				cell.Draw(Board.color)


	def FitToGrid(x, y):
		return x, y


class Body:
	def __init__(self, rect, color=green):
		self.rect = pg.Rect(rect)
		self.color = color

		self.direction = (1, 0)

	def Draw(self):
		pg.draw.rect(screen, self.color, self.rect)

	def Move(self):
		self.rect.x += CELL_SIZE[0] * self.direction[0]
		self.rect.y += CELL_SIZE[1] * self.direction[1]


class Snake:

	NUM_OF_START_BODIES = 3
	
	# board start position
	start_index = (Board.num_of_cells[0] // 3, Board.num_of_cells[1] // 2)
	
	color = darkGreen
	rect = None

	# the keybinds for the player
	keyBinds = {
		"up": pg.K_w,
		"up-2" : pg.K_UP,
		
		"down": pg.K_s,
		"down-2" : pg.K_DOWN,
		
		"left": pg.K_a,
		"left-2" : pg.K_LEFT,
		
		"right": pg.K_d,
		"right-2" : pg.K_RIGHT,
	}
	# the start direction for the snake head
	direction = (1, 0)
	# the previous direction of the snake head
	prev_direction = (1, 0)
	# how many frames is required to pass for the snake to update its position, smaller values mean the head is moved more often
	update_time = 6
	# has the snake died
	dead = False
	# food pieces eaten
	score = 0

	body_positions = []
	
	def CreateBody(num_of_pieces):
		start_rect = Board.grid[Snake.start_index[0]][Snake.start_index[1]].rect
		Snake.rect = pg.Rect(start_rect)
		Snake.body = [Body((start_rect.x - (i * CELL_SIZE[0]), start_rect.y, CELL_SIZE[0], CELL_SIZE[1])) for i in range(1, num_of_pieces + 1)]
		for body in Snake.body:
			Snake.body_positions.append(body.rect)

	def Restart():
		Snake.body_positions = []
		Snake.CreateBody(Snake.NUM_OF_START_BODIES)
		Snake.direction = (1, 0)
		Snake.prev_direction = Snake.direction
		Snake.dead = False
		Snake.score = 0
		GameUI.Restart()
		Food.Restart()

	def Draw():
		pg.draw.rect(screen, Snake.color, Snake.rect)

		for piece in Snake.body:
			piece.Draw()

	def Update():
		Snake.CheckBounds()
		Snake.CheckForBody()

		if not Snake.dead:
			Snake.Move()

			for index in range(len(Snake.body) - 1, 0, -1):
				Snake.body[index].direction = Snake.body[index - 1].direction
			Snake.body[0].direction = Snake.prev_direction

			for i, piece in enumerate(Snake.body):
				piece.Move()
				Snake.body_positions[i] = piece.rect

			Snake.prev_direction = Snake.direction
	
	def Move():
		Snake.rect.x += CELL_SIZE[0] * Snake.direction[0]
		Snake.rect.y += CELL_SIZE[1] * Snake.direction[1]

		Snake.CheckForFood()

	def CheckBounds():
		rect = pg.Rect(Snake.rect.x + CELL_SIZE[0] * Snake.direction[0], Snake.rect.y + CELL_SIZE[1] * Snake.direction[1], Snake.rect.w, Snake.rect.h)
		if not Board.rect.contains(rect):
			Snake.Kill()

	def CheckDirection():
		if Snake.direction == (Snake.prev_direction[0] * -1, Snake.prev_direction[1] * -1):
			Snake.Kill()

	def CheckForBody():
		rect = pg.Rect(Snake.rect.x + CELL_SIZE[0] * Snake.direction[0], Snake.rect.y + CELL_SIZE[1] * Snake.direction[1], Snake.rect.w, Snake.rect.h)
		if rect in Snake.body_positions:
			Snake.Kill()

	def CheckForFood():
		for f in Food.food:
			if f.rect == Snake.rect:
				f.Kill()
				Snake.Eat()
				break

	def Eat():
		Snake.score += 1
		Snake.AddBody()
		GameUI.UpdateScore(Snake.score)

	def AddBody(num_of_pieces=1):
		body = Snake.body[-1]
		Snake.body.append(Body((body.rect.x - body.direction[0] * CELL_SIZE[0], body.rect.y - body.direction[1] * CELL_SIZE[1], body.rect.w, body.rect.h)))
		Snake.body_positions.append(Snake.body[-1].rect)

	def Kill():
		Snake.dead = True
		GameUI.GameOver()
			
	def HandleEvent(event):
		if event.type == pg.KEYDOWN:
			if event.key == Snake.keyBinds["up"] or event.key == Snake.keyBinds["up-2"]:
				Snake.direction = (0, -1)

			elif event.key == Snake.keyBinds["down"] or event.key == Snake.keyBinds["down-2"]:
				Snake.direction = (0, 1)

			elif event.key == Snake.keyBinds["left"] or event.key == Snake.keyBinds["left-2"]:
				Snake.direction = (-1, 0)

			elif event.key == Snake.keyBinds["right"] or event.key == Snake.keyBinds["right-2"]:
				Snake.direction = (1, 0)

		Snake.CheckDirection()


class GameUI:

	score = Label((10, 10, 200, 50), (lightBlack, darkWhite), text="Score: 0", lists=[])

	def UpdateScore(score):
		GameUI.score.UpdateText(f"Score: {score}")

	show_death_message = False
	death_message = MessageBox((width // 2 - 200, height // 2 - 100, 400, 200), (lightBlack, darkWhite), messageBoxData={"text": "You have died"}, confirmButtonData={"text": "Restart", "onClick": Snake.Restart, "colors": (lightBlack, darkWhite, darkBlue)}, cancelButtonData={"text": "Quit", "onClick": Quit, "colors": (lightBlack, darkWhite, darkBlue)}, lists=[])

	def GameOver():
		GameUI.show_death_message = True

	def Draw():
		GameUI.score.Draw()
		if GameUI.show_death_message:
			GameUI.death_message.Draw()

	def HandleEvent(event):
		if GameUI.show_death_message:
			GameUI.death_message.HandleEvent(event)

	def Restart():
		GameUI.UpdateScore(0)
		GameUI.show_death_message = False


class Food:

	NUM_OF_START_FOOD = 1

	color = red

	# indexs of all exisiting foods
	indexs = []
	food = []

	def DrawFood():
		for f in Food.food:
			f.Draw()

	def CreateFood(num_of_pieces):

		possible_positions = []

		for j, row in enumerate(Board.grid):
			for i, cell in enumerate(row):
				if cell.rect not in Snake.body_positions:
					possible_positions.append((i, j))
				
		for i in range(num_of_pieces):
			shuffle(possible_positions)
			index = possible_positions.pop()
			f = Food(index)

	def Restart():
		Food.indexs = []
		Food.food = []
		Food.CreateFood(Food.NUM_OF_START_FOOD)

	def __init__(self, index):
		self.index = index

		self.rect = Board.grid[self.index[0]][self.index[1]].rect

		Food.indexs.append(self.index)
		Food.food.append(self)

	def Draw(self):
		pg.draw.rect(screen, Food.color, self.rect)

	def Kill(self):
		Food.indexs.remove(self.index)
		Food.food.remove(self)
		Food.CreateFood(Food.NUM_OF_START_FOOD)


Board.CreateBoard()
Snake.CreateBody(Snake.NUM_OF_START_BODIES)
Food.CreateFood(Food.NUM_OF_START_FOOD)



def DrawLoop():
	global FRAME
	screen.fill(darkGray)

	DrawAllGUIObjects()

	Board.Draw()
	Snake.Draw()
	Food.DrawFood()
	GameUI.Draw()

	if FRAME >= Snake.update_time:
		Snake.Update()
		FRAME = 0
		# print(clock.get_fps())

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)

	Snake.HandleEvent(event)
	GameUI.HandleEvent(event)


FRAME = 0


while RUNNING:
	clock.tick_busy_loop(FPS)
	deltaTime = clock.get_time()

	FRAME += 1

	for event in pg.event.get():
		if event.type == pg.QUIT:
			Quit()
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				Quit()

		HandleEvents(event)

	DrawLoop()
