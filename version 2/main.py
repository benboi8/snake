import pygame as pg
from pygame import gfxdraw
import random
import datetime as dt
from datetime import timedelta
import numpy as np
import json

pg.init()

clock = pg.time.Clock()
fps = 120

lightGray = (205, 205, 205)
darkGray = (55, 55, 55)
white = (25, 255, 255)
lightBlack = (30, 30, 30)
black = (0, 0, 0)
red = (205, 0, 0)
green = (0, 205, 0)
blue = (0, 0, 205)

sf = 2
width, height = 300 * sf, 300 * sf

screen = pg.display.set_mode((width, height))
font = pg.font.SysFont("arial", 16 * sf)
running = True

boardSize = (width // sf, 20, height // sf)
foodSize = (10, 10)
snakeSize = (10, 10)

allFoods = []
allFoodPositions = []

boardPositions = []

highscoreFilePath = "highscore.json"
replyAllBodyPositions = []
replyAllFoodPositions = []
isReplaying = False


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
	for x in range(boardSize[0]):
		for y in range(boardSize[1], boardSize[2]):
			if x % foodSize[0] == 0: 
				if y % foodSize[1] == 0:
					boardPositions.append((x * sf, y * sf))


def DrawLoop():
	screen.fill(black)
	
	snake.Draw()

	for food in allFoods:
		food.Draw()

	DrawHeader()

	pg.display.update()


def DrawHeader():
	pg.draw.line(screen, lightGray, (0, 20 * sf), (width, 20 * sf))
	textObjs = []
	score = font.render("Score: {}".format(str(snake.score)), True, lightGray)
	textObjs.append((score, (0, 0)))
	highscore = font.render("Highscore: {}".format(str(GetHighScore())), True, lightGray)
	textObjs.append((highscore, (width - highscore.get_width() - (10 * sf), 0)))
	for i in range(len(textObjs)):
		screen.blit(textObjs[i][0], textObjs[i][1])


class Food:
	def __init__(self, rect, color):
		self.surface = screen
		self.orignalRect = pg.Rect(rect)
		self.color = color
		self.Rescale()

		allFoods.append(self)
		replyAllFoodPositions.append((self.rect.x, self.rect.y))

	def Rescale(self):
		self.rect = pg.Rect(self.orignalRect.x * sf, self.orignalRect.y * sf, self.orignalRect.w * sf, self.orignalRect.h  *  sf)

	def Draw(self):
		pg.draw.rect(self.surface, self.color, (self.rect.x + 1, self.rect.y + 1, self.rect.w - 2, self.rect.h - 2))


def CreateFood(numOfFood=1):
	pos = boardPositions[random.randint(0, (len(boardPositions) - 1))]
	snakeBody = []
	for bodyPos in snake.bodyPositions:
		snakeBody.append((bodyPos[0], bodyPos[1]))
	foodCheck = False
	while not foodCheck:
		pos = boardPositions[random.randint(0, (len(boardPositions) - 1))]
		if pos not in snakeBody:
			foodCheck = True
	if foodCheck:
		Food((pos[0] // sf, pos[1] // sf, foodSize[0], foodSize[1]), red)
		allFoodPositions.append(pos)


class Snake:
	def __init__(self, headPos, color, size=snakeSize, speed=2.5, startLength=3, replayPos=[]):
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
		self.speed = speed * sf
		self.replayPos = replayPos 
		self.Rescale()
		for i in range(startLength):
			self.AddBody()

	def Rescale(self):
		self.size = (self.size[0] * sf, self.size[1] * sf)

	def Draw(self):
		for i, bodyPos in enumerate(self.bodyPositions):
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
				break

		if len(self.bodyPositions) >= len(boardPositions):
			print("Win")
			Quit()

	def AddBody(self):
		bodyPositions = []
		for pos in self.bodyPositions:
			bodyPositions.append(pos)

		if self.headPos in boardPositions:
			bodyPositions.append(self.headPos)
			replyAllBodyPositions.append(self.headPos)

		if len(self.bodyPositions) > self.bodyLength:
			bodyPositions.pop(0)

		self.bodyPositions = np.array(bodyPositions)

	def HandleEvent(self, event):
		if event.type == pg.KEYDOWN:
			if self.direction == (0, 1) or self.direction == (0, -1):
				if event.key == pg.K_d or event.key == pg.K_RIGHT:
					self.newDirection = (1, 0)
				if event.key == pg.K_a or event.key == pg.K_LEFT:
					self.newDirection = (-1, 0)
			if self.direction == (1, 0) or self.direction == (-1, 0):
				if event.key == pg.K_w or event.key == pg.K_UP:
					self.newDirection = (0, -1)
				if event.key == pg.K_s or event.key == pg.K_DOWN:
					self.newDirection = (0, 1)


def GetHighScore():
	try:
		with open(highscoreFilePath, "r") as highscoreFile:
			data = json.load(highscoreFile)
			highscoreFile.close()
		return data["highscore"]
	except:
		return 0


def CheckHighscore():
	data = {"highscore": 0, "replay": {"bodyPos": [], "foodPos": []}}
	try:
		with open(highscoreFilePath, "r") as highscoreFile:
			data = json.load(highscoreFile)
			highscoreFile.close()
	except:
		try:
			with open(highscoreFilePath, "x") as highscoreFile:
				json.dump(data, fp=highscoreFile, indent=2)
				highscoreFile.close()
		except:
			with open(highscoreFilePath, "w") as highscoreFile:
				json.dump(data, fp=highscoreFile, indent=2)
				highscoreFile.close()
	UpdateHighscore(data)


def UpdateHighscore(data):
	try:
		previousHighscore = data["highscore"]
		if snake.score > previousHighscore:
			data["highscore"] = snake.score
			data["replay"]["bodyPos"] = replyAllBodyPositions
			data["replay"]["foodPos"] = replyAllFoodPositions

		with open(highscoreFilePath, "w") as highscoreFile:
			json.dump(data, fp=highscoreFile, indent=2)
			highscoreFile.close()
	except NameError: 
		print("Error: snake doesn't exist.")
	except:
		print("Other Error")


def Quit():
	global running
	running = False


def Restart():
	global allFoodPositions, allFoods, snake
	CheckHighscore()
	allFoods = []
	allFoodPositions = []
	CreateBoard()
	snake = Snake((width // 4, height // 2), (green, green), startLength=2, speed=1)
	CreateFood()


Restart()
while running:
	clock.tick_busy_loop(fps)

	if len(allFoodPositions) < 1:
		CreateFood()

	for event in pg.event.get():
		if event.type == pg.QUIT:
			Quit()
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				Quit()

		snake.HandleEvent(event)

	snake.Move()

	DrawLoop()
