import math
import random

import pygame as pg

pg.init()
pg.font.init()

# Background
WIDTH = 800
HEIGHT = 800
screen = pg.display.set_mode((WIDTH, HEIGHT))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (60, 200, 60)
DARK_GREEN = (50, 150, 50)
BLUE = (0, 0, 255)

FOOD = (204, 90, 90)
HEAD = (19, 212, 19)
BODY = (15, 163, 37)
TAIL = (7, 138, 26)

BACKGROUND = (55, 55, 55)


def RoundUp(x):
    return int(math.ceil(x / 10.0)) * 10


class Snake:
    class SnakeHead:
        def __init__(self, head_color, start_xy, speed=10, radius=10):
            self.start_xy = start_xy  # start positions
            self.head_x = start_xy[0]  # head x pos
            self.head_y = start_xy[1]  # head y pos
            self.head_col = head_color  # head color
            self.speed = speed  # speed
            self.radius = radius  # snake head radius

        def DrawSnakeHead(self):  # draw head and tail
            pg.draw.circle(screen, self.head_col, (int(self.head_x), int(self.head_y)), self.radius)  # draw head

        def MoveSnakeHead(self, direction, score):  # move head
            utility = Utility(score, self.start_xy)
            is_game_over = False
            if direction == 1:  # UP
                self.head_y -= self.speed  # move up
                if self.head_y <= 0 + self.radius:  # is it valid
                    self.head_y += self.speed
                    is_game_over = utility.GameOver()

            elif direction == -1:  # DOWN
                self.head_y += self.speed  # move down
                if self.head_y >= HEIGHT - self.radius:  # is it valid
                    self.head_y -= self.speed
                    is_game_over = utility.GameOver()

            elif direction == 2:  # RIGHT
                self.head_x += self.speed  # move right
                if self.head_x >= WIDTH - self.radius:  # is it valid
                    self.head_x -= self.speed
                    is_game_over = utility.GameOver()

            elif direction == -2:  # LEFT
                self.head_x -= self.speed  # move left
                if self.head_x <= 0 + self.radius:  # is it valid
                    self.head_x += self.speed
                    is_game_over = utility.GameOver()

            return self.head_x, self.head_y, is_game_over

    class SnakeBody:
        def __init__(self, body_color, speed, head_x, head_y, number_of_parts=2):
            self.body_col = body_color  # body color
            self.head_x, self.head_y = head_x, head_y
            self.body_x = head_x  # body x position
            self.body_y = head_y  # body y position
            self.radius = 10  # body radius
            self.num_of_parts = number_of_parts
            self.speed = speed
            self.update_count = 0
            self.update_count_max = number_of_parts

            self.x = []
            self.y = []

        def MoveSnakeBody(self, head_x, head_y):  # move snake body
            self.update_count += 1
            self.x.append(head_x)
            self.y.append(head_y)
            if self.update_count > self.update_count_max:
                for i in range(self.num_of_parts, 0, -1):
                    self.x[i] = self.x[i - 1]
                    self.y[i] = self.y[i - 1]
                    pg.draw.circle(screen, BLACK, (int(self.x[i]), int(self.y[i])), self.radius)

        def Grow(self):
            self.num_of_parts += 1


class Food:
    def __init__(self, head_x, head_y, head_radius, color=(), radius=9):
        self.color = color  # food color
        self.radius = radius  # food radius
        self.pos_x = random.randint(0 + radius, WIDTH - radius)  # food position x
        self.pos_y = random.randint(0 + radius, HEIGHT - radius)  # food position y

        self.head_x = head_x  # snake head position x
        self.head_y = head_y  # snake head position y
        self.head_radius = head_radius  # snake head radius

    def DrawFood(self):
        pg.draw.circle(screen, self.color, (self.pos_x, self.pos_y), self.radius)  # draw food

    def CreatePosition(self):
        self.pos_x = RoundUp(random.randint(0 + self.radius, WIDTH - self.radius))  # create a new position x
        self.pos_y = RoundUp(random.randint(0 + self.radius, HEIGHT - self.radius))  # create a new position y

    def HasCollided(self, head_x, head_y):
        self.head_x = head_x  # snake head centre
        self.head_y = head_y  # snake head centre

        if (((self.pos_x - self.head_x) ** 2) + ((self.head_y - self.pos_y) ** 2)) <= (
                (self.head_radius + self.radius) ** 2):  # checks if the snake head and food collide
            return True
        else:
            return False


class Score:
    def __init__(self, text_pos_x, text_pos_y):
        self.text_pos_x = text_pos_x  # score position x
        self.text_pos_y = text_pos_y  # score position y
        self.score = 0  # score value
        self.score_text = "score = " + str(self.score)  # score text

    def DrawScore(self):
        score_font = pg.font.Font("ScoreFont.ttf", 32)  # create the score font
        score_text = score_font.render(self.score_text, False, WHITE, BACKGROUND)  # render the font

        screen.blit(score_text, (self.text_pos_x, self.text_pos_y))  # add the text to the screen

    def UpdateScore(self):
        self.score += 1  # increase the score when the player gets the food
        self.score_text = "score = " + str(self.score)  # update the score text
        return int(self.score)


class Utility:
    def __init__(self, score, start_xy):
        self.score = score  # score
        self.high_score = 0  # high score
        self.start_xy = start_xy  # start position
        self.head_x, self.head_y = start_xy[0], start_xy[1]  # split x and y coords

    def Restart(self):
        self.score = 0  # reset score
        return self.start_xy, 3, self.score,   # return starting settings

    def GameOverText(self):
        score_font = pg.font.Font("ScoreFont.ttf", 32)  # score font
        utility_score = pg.font.Font("ScoreFont.ttf", 16)  # utility font

        score = score_font.render(str(self.score), False, WHITE, BLACK)  # score value
        high_score = score_font.render(str(self.high_score), False, WHITE, BLACK)  # high score value

        score_text = score_font.render("Score:", False, WHITE, BLACK)  # score text
        high_score_text = score_font.render("High Score:", False, WHITE, BLACK)  # high score text

        restart_text = utility_score.render("Press R to Restart", False, WHITE, BLACK)  # restart score
        quit_text = utility_score.render("Press ESC to Quit", False, WHITE, BLACK)  # quit score

        screen.blit(score, (WIDTH / 2, HEIGHT / 2))  # draw score value
        screen.blit(score_text, (WIDTH / 3, HEIGHT / 2))  # draw score text

        screen.blit(high_score, (WIDTH / 1.7, HEIGHT / 4))  # draw score high score value
        screen.blit(high_score_text, (WIDTH / 3, HEIGHT / 4))  # draw high score text

        screen.blit(restart_text, (WIDTH / 3, HEIGHT / 1.5))  # draw restart text
        screen.blit(quit_text, (WIDTH / 3, HEIGHT / 1.4))  # draw quit text

    def CreateHighScore(self):
        high_score_text_file = open("HighScore.txt", "r")  # open HighScore.txt to read
        high_score = high_score_text_file.read()  # get high score from the file
        high_score_text_file.close()  # close the file
        if int(high_score) < self.score:  # if the current score is higher than high score
            high_score_text_file = open("HighScore.txt", "w")  # open HighScore.txt to write
            high_score_text_file.write(str(self.score))  # write the score the HighScore.txt
            high_score_text_file.close()  # close file
            return self.score  # return the score as high score
        else:
            return high_score  # return the high score

    def GameOver(self):
        screen.fill(BLACK)  # fill the screen in black
        self.high_score = Utility.CreateHighScore(self)  # create high score in HighScore.txt
        Utility.GameOverText(self)  # display game over text
        return True  # return that game is over
