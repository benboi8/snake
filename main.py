import pygame as pg
from pygame import gfxdraw
import random
import datetime as dt
from datetime import timedelta
import numpy as np

pg.init()

clock = pg.time.Clock()
fps = 60

lightGray = (205, 205, 205)
darkGray = (55, 55, 55)
red = (205, 0, 0)
green = (0, 205, 0)
blue = (0, 0, 205)

sf = 2
width, height = 640 * sf, 360 * sf

screen = pg.display.set_mode((width, height))
running = True

foodSize = (10, 10)
snakeSize = (10, 10)

allFoods = []
allFoodPositions = []

boardPositions = []

debugMode = False


font = pg.font.SysFont("arial", 16 * sf)


def DrawRectOutline(surface, color, rect, width=1, outWards=False):
	x, y, w, h = rect
	width = max(width, 1)  # Draw at least one rect.
	width = min(min(width, w//2), h//2)  # Don't overdraw.

	# This draws several smaller outlines inside the first outline
	# Invert the direction if it should grow outwards.
	if outWards:
		for i in range(int(width)):
			pg.gfxdraw.rectangle(surface, (x-i, y-i, w+i*2, h+i*2), color)
	else:
		for i in range(int(width)):
			pg.gfxdraw.rectangle(surface, (x+i, y+i, w-i*2, h-i*2), color)


def CreateBoard():
	global boardPositions
	boardPositions = []
	for x in range(width // sf):
		for y in range(10 * sf, height // sf):
			if x % foodSize[0] == 0: 
				if y % foodSize[1] == 0:
					boardPositions.append((x * sf, y * sf))


def DrawLoop():
	screen.fill(darkGray)

	for food in allFoods:
		food.Draw()

	snake.Draw()

	if debugMode:
		DrawDebug()

	DrawHeader()

	pg.display.update()


def DrawHeader():
	pg.draw.line(screen, lightGray, (0, 20 * sf), (width, 20 * sf))
	score = font.render("Score: {}".format(str(snake.score)), True, lightGray)
	screen.blit(score, (width // 2 - score.get_width() // 2, 0))


def DrawDebug():
	textSurface = font.render(str(round(clock.get_fps())), True, lightGray)
	screen.blit(textSurface, (0, 0))
	for pos in boardPositions:
		DrawRectOutline(screen, lightGray, (pos[0], pos[1], foodSize[0] * sf, foodSize[1] * sf))


class Food:
	def __init__(self, rect, color):
		self.surface = screen
		self.orignalRect = pg.Rect(rect)
		self.color = color
		self.Rescale()

		allFoods.append(self)

	def Rescale(self):
		self.rect = pg.Rect(self.orignalRect.x * sf, self.orignalRect.y * sf, self.orignalRect.w * sf, self.orignalRect.h  *  sf)

	def Draw(self):
		pg.draw.rect(self.surface, self.color, (self.rect.x + 1, self.rect.y + 1, self.rect.w - 2, self.rect.h - 2))


def CreateFood(numOfFood=1):
	while len(allFoodPositions) < min(max(numOfFood, 1), len(boardPositions)):
		pos = boardPositions[random.randint(0, (len(boardPositions) - 1))]
		if pos not in allFoodPositions:
			if pos not in snake.bodyPositions:
				Food((pos[0] // sf, pos[1] // sf, foodSize[0], foodSize[1]), red)
				allFoodPositions.append(pos)


class Snake:
	def __init__(self, headPos, color, size=snakeSize, speed=5, startLength=3):
		self.surface = screen
		self.headPos = headPos
		self.headColor = color[0]
		self.bodyColor = color[1]
		self.size = size
		self.bodyPositions = []
		self.bodyDirections = []
		self.bodyLength = startLength
		self.direction = (1, 0)
		self.newDirection = (1, 0)
		self.score = 0
		self.speed = speed
		self.Rescale()
		for i in range(startLength):
			self.AddBody()

	def Rescale(self):
		self.size = (self.size[0] * sf, self.size[1] * sf)

	def Draw(self):
		for i, bodyPos in enumerate(self.bodyPositions):
			direction = abs(self.bodyDirections[i])
			pg.draw.rect(self.surface, self.bodyColor, (bodyPos[0], bodyPos[1], self.size[0], self.size[1]))

		pg.draw.rect(self.surface, self.headColor, (self.headPos[0], self.headPos[1], self.size[0], self.size[1]))

	def Move(self):
		if self.headPos in boardPositions:
			self.direction = self.newDirection
		
		self.AddBody()

		self.headPos = (self.headPos[0] + self.speed * self.direction[0], self.headPos[1] + self.speed * self.direction[1])

		self.CheckCollisions()

	def CheckCollisions(self):
		if not pg.Rect(0, 10 * sf, width, height).collidepoint(self.headPos):
			Restart()

		rect = pg.Rect(self.headPos[0], self.headPos[1], self.size[0], self.size[1])
		for foodPos in allFoodPositions:
			if rect.collidepoint(foodPos):
				self.bodyLength += 1
				allFoods.pop(allFoodPositions.index(foodPos))
				allFoodPositions.remove(foodPos)
				CreateFood()
				self.score += 1
				break

		for bodyPos in self.bodyPositions[:-1]:
			if rect.collidepoint(bodyPos):
				Restart()

		if len(self.bodyPositions) >= len(boardPositions):
			print("Win")
			Quit()

	def AddBody(self):
		bodyPositions = []
		bodyDirections = []
		for pos in self.bodyPositions:
			bodyPositions.append(pos)
		for direction in self.bodyDirections:
			bodyDirections.append(direction)

		if self.headPos in boardPositions:
			bodyPositions.append(self.headPos)
			bodyDirections.append(self.newDirection)
			print(self.newDirection, self.direction)

		if len(self.bodyPositions) > self.bodyLength:
			bodyPositions.pop(0)
			bodyDirections.pop(0)

		self.bodyPositions = np.array(bodyPositions)
		self.bodyDirections = np.array(bodyDirections)

	def HandleEvent(self, event):
		if event.type == pg.KEYDOWN:
			if self.direction == (0, 1) or self.direction == (0, -1):
				if event.key == pg.K_d:
					self.newDirection = (1, 0)
				if event.key == pg.K_a:
					self.newDirection = (-1, 0)
			if self.direction == (1, 0) or self.direction == (-1, 0):		
				if event.key == pg.K_w:
					self.newDirection = (0, -1)
				if event.key == pg.K_s:
					self.newDirection = (0, 1)


def Quit():
	global running
	running = False
			

def Restart():
	global snake
	CreateBoard()
	snake = Snake((width // 4, height // 2), (blue, green), startLength=10)
	CreateFood()


Restart()
while running:
	clock.tick_busy_loop(fps)

	for event in pg.event.get():
		if event.type == pg.QUIT:
			Quit()
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				Quit()

			if event.key == pg.K_F3:
				debugMode = not debugMode

		snake.HandleEvent(event)

	snake.Move()

	DrawLoop()
