from classes import *  # import all classes

# vars
direction = 3  # head direction
speed = 1  # snake speed
radius = 10  # snake draw size
score_value = 0
is_game_over = False

start_xy = (WIDTH / 4, HEIGHT / 2)

snake_head = Snake.SnakeHead(HEAD, start_xy, speed)  # create snake obj
snake_body = Snake.SnakeBody(BODY, speed, WIDTH / 4 - radius * 2, HEIGHT / 2)  # snake body obj

food = Food(WIDTH / 4, HEIGHT / 2, radius, FOOD)  # food obj

score = Score(WIDTH / 2 - 80, 0)  # score text position

utility = Utility(score_value, start_xy)

running = True
while running:
    # RGB values for background
    screen.fill(BACKGROUND)

    score.DrawScore()  # render score text

    food.DrawFood()  # draw food

    utility = Utility(score_value, start_xy)

    # Checks every event
    for event in pg.event.get():
        # Check if event is quiting
        if event.type == pg.QUIT:
            # Ends loop
            running = False

        if not is_game_over:
            if event.type == pg.KEYDOWN:  # check for a key press
                if event.key == pg.K_UP or event.key == pg.K_w:  # is it up key
                    direction = 1  # up
                if event.key == pg.K_DOWN or event.key == pg.K_s:  # is it down key
                    direction = -1  # down
                if event.key == pg.K_LEFT or event.key == pg.K_a:  # is it left
                    direction = -2  # left
                if event.key == pg.K_RIGHT or event.key == pg.K_d:  # is it right
                    direction = 2  # right

        elif is_game_over:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    start_xy, direction, score_value = utility.Restart()
                    snake_head = Snake.SnakeHead(HEAD, start_xy, speed)  # create snake obj
                    snake_body = Snake.SnakeBody(BODY, speed, WIDTH / 4 - radius * 2, HEIGHT / 2)  # snake body obj
                if event.key == pg.K_ESCAPE:
                    running = False

    head_x, head_y, is_game_over = snake_head.MoveSnakeHead(direction, score_value)  # move snake head
    snake_body.MoveSnakeBody(int(head_x), int(head_y))

    has_collided = food.HasCollided(int(head_x), int(head_y))  # check for head and food collision

    if has_collided:  # has head and food collided
        food.CreatePosition()  # if true create a new position
        score_value = score.UpdateScore()  # update the score
        snake_body.Grow()

    snake_head.DrawSnakeHead()  # draw snake

    pg.display.update()  # update screen
