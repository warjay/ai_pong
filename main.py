import pygame
import math
from random import randrange
from random import random
from tqdm import tqdm
pygame.init()

HUMAN = True
FPS = 60
WIDTH = 858
HEIGHT = 525
CENTERLINE_WIDTH = 1
BALL_RADIUS = 7
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
PADDLE_MARGIN = BALL_RADIUS*2 # margin between paddle and screen edge (looks nicer)
PADDLE_SPEED = 300
BALL_SPEED = 300



# RL Setup

import matplotlib
import matplotlib.pyplot as plt 
import numpy as np

k=0
ticksToRun = 300000000
reward = 0
action = 1
# BallX, BallY, BallVelocityX, BallVelocityY, PaddleY, Action (0: up, 1: stay, 2: down)
shape = ((HEIGHT//10)+1, (WIDTH//10)+1, (HEIGHT//10)+1, 3)
try:
    qtable = np.load('qtable.npy')
except FileNotFoundError:
    print("No qtable found, initializing a new one.")
    qtable = np.zeros(shape, dtype=int)
except ValueError:
    print("Table dimensions problably invalid.")
    qtable = np.zeros(shape)

def policy(observation, E = 1):
    global qtable
    global k
    k = randrange(3,5)
    if random() > E:
        return randrange(0,3)
    try:
        a,b,c = map(int, [x // 10 for x in observation])
        left, stay, right = qtable[a, b, c, ...]
    except IndexError:
        return randrange(0,3)
    values = [left, stay, right]
    if left == stay == right:
        return randrange(0,3)
    else:
        return values.index(max(values))

def updateQtable(preObs, postObs, action, R, y = 0.9, A = 0.2):
    global qtable
    try:
        a,b,c = map(int, [x // 10 for x in preObs])
        f,g,h = map(int, [x // 10 for x in postObs])
        postQMax = max(qtable[f, g, h, ...])
        gain = A * (R + (y * postQMax) - qtable[a,b,c,action])
        qtable[a,b,c,action] += int(gain)
        return gain
    except IndexError:
        return 0

# RL Setup END











wn = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Pong vs AI")

# HELPER FUNCTIONS

def starting_velocity(angle = randrange(0,360)):
    # 0 degree is north
    angle_radians = math.radians(angle)
    velocity_y = BALL_SPEED * math.cos(angle_radians) * -1
    velocity_x = BALL_SPEED * math.sin(angle_radians)
    return [velocity_x, velocity_y]

def bounce(velocity, direction):
    # direction = x (0) or y (1)
    velocity[direction] *= -1
    return velocity

# HELPER FUNCTIONS END
leftScore = 0
rightScore = 0
totalScore = 0
bounces = 0
font = pygame.font.Font('freesansbold.ttf', 32)



run = True
ballX = WIDTH/2 - BALL_RADIUS
ballY = HEIGHT/2 - BALL_RADIUS
leftPaddleX = PADDLE_MARGIN
leftPaddleY = HEIGHT/2 - PADDLE_HEIGHT/2
rightPaddleX = WIDTH - PADDLE_WIDTH - PADDLE_MARGIN
rightPaddleY = HEIGHT/2 - PADDLE_HEIGHT/2
ball_velocity = starting_velocity()
leftPaddle_velocity = 0
rightPaddle_velocity = 0

clock = pygame.time.Clock()

preObs = [ballX, ballY, leftPaddleY]

for tick in tqdm(range(5000000000)):
    reward = 0
    if k > 0:
        k -= 1
    else:
        action = policy(preObs)
    if action == 0:
        rightPaddle_velocity = -PADDLE_SPEED
    elif action == 1:
        rightPaddle_velocity = 0
    elif action == 2:
        rightPaddle_velocity = PADDLE_SPEED
    
    if not HUMAN:
        # basic bot to train against
        if ballY > leftPaddleY + PADDLE_HEIGHT/2:
            leftPaddle_velocity = PADDLE_SPEED
        elif ballY < leftPaddleY + PADDLE_HEIGHT/2:
            leftPaddle_velocity = -PADDLE_SPEED
        else:
            leftPaddle_velocity = 0


    wn.fill("black")
    
    clock.tick(60)
    delta_time = 0.03 # simulate 60 FPS
    
    # for i in pygame.event.get():
    #     if i.type == pygame.QUIT:
    #         run = False
    #     if HUMAN and i.type == pygame.KEYDOWN:
    #         if i.key == pygame.K_w:
    #             leftPaddle_velocity = -PADDLE_SPEED
    #         if i.key == pygame.K_s:
    #             leftPaddle_velocity = PADDLE_SPEED
            # if i.key == pygame.K_UP:
            #     rightPaddle_velocity = -PADDLE_SPEED
            # if i.key == pygame.K_DOWN:
            #     rightPaddle_velocity = PADDLE_SPEED
        # if HUMAN and i.type == pygame.KEYUP:
        #     leftPaddle_velocity = 0
        #     rightPaddle_velocity = 0

    # Check if collide with top / bottom of screen
    if ballY <= BALL_RADIUS or ballY >= HEIGHT - BALL_RADIUS:
        ball_velocity = bounce(ball_velocity, 1)
    
    # Check if exit left or right of screen and reset ball
    if ballX <= BALL_RADIUS:
        reward = 100
        rightScore += 1
        totalScore += 1
        ballX = WIDTH/2 - BALL_RADIUS
        ballY = HEIGHT/2 - BALL_RADIUS
        ball_velocity = bounce(ball_velocity, 0)
        ball_velocity = bounce(ball_velocity, 1)
    elif ballX >= WIDTH - BALL_RADIUS:
        #reward = (-int(abs(rightPaddleY - ballY))/HEIGHT)*10
        leftScore += 1
        totalScore += 1
        ballX = WIDTH/2 - BALL_RADIUS
        ballY = HEIGHT/2 - BALL_RADIUS
        ball_velocity = bounce(ball_velocity, 0)
        ball_velocity = bounce(ball_velocity, 1)
    # Check if collide with paddle
    if ball_velocity[0] < 0:
        if ballY >= leftPaddleY and ballY <= leftPaddleY + PADDLE_HEIGHT:
            if ballX - BALL_RADIUS <= leftPaddleX + PADDLE_WIDTH:
                ball_velocity = bounce(ball_velocity, 0)

                middleY = leftPaddleY + PADDLE_HEIGHT / 2
                Ydiff = middleY - ballY
                damper = (PADDLE_HEIGHT / 2) / BALL_SPEED
                ball_velocity[1] = Ydiff / damper
                ball_velocity = bounce(ball_velocity, 1)
    else:
        if ballY >= rightPaddleY and ballY <= rightPaddleY + PADDLE_HEIGHT:
            if ballX + BALL_RADIUS >= rightPaddleX:
                ball_velocity = bounce(ball_velocity, 0)

                middleY = rightPaddleY + PADDLE_HEIGHT / 2
                Ydiff = middleY - ballY
                damper = (PADDLE_HEIGHT / 2) / BALL_SPEED
                ball_velocity[1] = Ydiff / damper
                ball_velocity = bounce(ball_velocity, 1)
                reward += 20
                bounces += 1
    
    ballPaddleDist = abs(ballY - rightPaddleY)
    if ballPaddleDist < 200:
        reward += -0.05 * ballPaddleDist + 10
    elif ballPaddleDist > 250:
        reward -= 0.05 * ballPaddleDist


        

    # update ball position
    ballX += ball_velocity[0] * delta_time
    ballY += ball_velocity[1] * delta_time

    # update paddle position
    leftPaddleY += leftPaddle_velocity * delta_time 
    leftPaddleY = max(0, min(HEIGHT - PADDLE_HEIGHT, leftPaddleY)) # clamp to screen
    rightPaddleY += rightPaddle_velocity * delta_time
    rightPaddleY = max(0, min(HEIGHT - PADDLE_HEIGHT, rightPaddleY)) # clamp to screen
        
    
    postObs = [ballX, ballY, leftPaddleY]
    updateQtable(preObs, postObs, action, reward)
    preObs = postObs

#TODO
    pygame.draw.rect(wn, "grey", (WIDTH//2, 0, CENTERLINE_WIDTH, HEIGHT)) # middle line
    pygame.draw.rect(wn, "white", (leftPaddleX, leftPaddleY, PADDLE_WIDTH, PADDLE_HEIGHT), 5) # left paddle
    pygame.draw.rect(wn, "white", (rightPaddleX, rightPaddleY, PADDLE_WIDTH, PADDLE_HEIGHT), 5) # right paddle
    pygame.draw.circle(wn, "white", (ballX, ballY), BALL_RADIUS) # ball
    scoreboard = font.render(f"{leftScore} | {rightScore}", True, 'white', 'black')
    textRect = scoreboard.get_rect()
    textRect.center = (HEIGHT // 2, WIDTH // 2)
    wn.blit(scoreboard, textRect)
    pygame.display.update()
    


    if tick%100000 == 0:
        np.save('qtable.npy', qtable)
        print("Qtable saved, Total Bounces:", bounces)
        bounces = 0
    if totalScore >= 11:
        ballX = WIDTH/2 - BALL_RADIUS
        ballY = HEIGHT/2 - BALL_RADIUS
        leftPaddleX = PADDLE_MARGIN
        leftPaddleY = HEIGHT/2 - PADDLE_HEIGHT/2
        rightPaddleX = WIDTH - PADDLE_WIDTH - PADDLE_MARGIN
        rightPaddleY = HEIGHT/2 - PADDLE_HEIGHT/2
        ball_velocity = starting_velocity()
        leftPaddle_velocity = 0
        rightPaddle_velocity = 0
        preObs = [ballX, ballY, leftPaddleY]
        leftScore = 0
        rightScore = 0
        totalScore = 0
    

np.save('qtable.npy', qtable)
print("Qtable saved")






