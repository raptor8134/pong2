#!/usr/bin/env python3
#disable pygame import message
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "True"

import pygame
import sys
import random 
import math
import pyfiglet

 #############
### Classes ###
 #############

class Ball():
    def __init__(self, speed: float, radius: int):
        self.speed = speed 
        img = pygame.Surface((2*radius,2*radius), pygame.SRCALPHA)
        pygame.draw.circle(img, white, (radius,radius), radius)
        self.image = img
        self.rect = self.image.get_rect()
    def reset(self):
        # give even preference to each paddle for starting
        random.seed()
        self.velocity = [self.speed * random.choice([-1,1]), 0]
        random.shuffle(self.velocity)
        # center the ball
        c = self.rect
        c.center = (width//2, height//2)
    def move(self):
        c = self.rect
        v = self.velocity
        c.move_ip(v)
        # check for wall collisions
        if c.left < 0 or c.right > width:
            v[0] = -v[0]
        if c.top < 0 or c.bottom > height:
            v[1] = -v[1]
        self.velocity = [x * 1.0005 for x in v]
    def render(self, surface): # surface should be a surface object
        surface.blit(self.image, self.rect)

class Paddle():
    def __init__(self, pwidth: int, plength: int, side: str, speed: int, keys: tuple):
        self.pw = pw = pwidth
        self.pl = pl = plength
        self.side = side
        self.speed = speed
        self.keys = keys
        match side:
            case "top":
                x = (width-pl)//2
                y = pw
            case "bottom":
                x = (width-pl)//2
                y = height - 2*pw
            case "left":
                x = pw
                y = (width-pl)//2
                pw, pl = pl, pw
            case "right":
                x = width - 2*pw
                y = (width-pl)//2
                pw, pl = pl, pw
            case _:
                raise Exception # you know what you did
        self.rect = pygame.Rect(x, y, pl, pw)
    def move(self, keymap: pygame.key.ScancodeWrapper):
        r = self.rect
        match self.side:
            case "top" | "bottom":
                ltest = r.left
                utest = r.right
                flip = 1
            case "left" | "right":
                ltest = r.top
                utest = r.bottom
                flip = -1
        if keymap[self.keys[0]] and ltest > 2*self.pw:
            r.move_ip([-pspeed, 0][::flip])
        if keymap[self.keys[1]] and utest < width - 2*self.pw:
            r.move_ip([pspeed, 0][::flip])
    def reflect(self, ball: Ball):
        v = ball.velocity
        vabs = math.sqrt(v[0]**2 + v[1]**2)
        # radius is doubled to keep acos within bounds and going to reasonalbe
        # angles (no 90° reflections)
        radius = self.pl/2 * 2 
        match self.side:
            case "top":
                if ball.velocity[1] < 0:
                    angle = math.acos(
                        (ball.rect.center[0]-self.rect.center[0]) / radius)
                    ball.velocity = [vabs*math.cos(angle), vabs*math.sin(angle)]
            case "bottom":
                if ball.velocity[1] > 0:
                    angle = math.acos(
                            (ball.rect.center[0]-self.rect.center[0]) / radius)
                    ball.velocity = [vabs*math.cos(angle), -vabs*math.sin(angle)]
            case "left":
                if ball.velocity[0] < 0:
                    angle = math.acos(
                            (ball.rect.center[1]-self.rect.center[1]) / radius)
                    ball.velocity = [vabs*math.sin(angle), vabs*math.cos(angle)]
            case "right":
                if ball.velocity[0] > 0:
                    angle = math.acos(
                            (ball.rect.center[1]-self.rect.center[1]) / radius)
                    ball.velocity = [-vabs*math.sin(angle), vabs*math.cos(angle)]
            case _: 
                raise Exception
    def render(self, surface: pygame.Surface):
        pygame.draw.rect(surface, white, self.rect)

 ####################
### Initialization ###
 ####################

# starting message
print("\n                     Now playing:\n")
print(pyfiglet.Figlet(font="banner3").renderText(" PONG 2 ").replace("#", "█"))

# initialize pygame and set options
pygame.display.init()
pygame.font.init()
pygame.key.set_repeat(2)
font = pygame.font.Font("PublicPixel-0W5Kv.ttf", 100)

# player scores
wasd_score = 0 
akey_score = 0

# initialize window and set colors
sidelen = 1024
size = width, height = (sidelen,sidelen)
screen = pygame.display.set_mode(size)
black = 0, 0, 0
white = 225, 225, 225

# create the ball object
ball = Ball(5, 16)
ball.reset()

# create the four paddle objects
pspeed = 9
pwidth, plen = 16, 128
paddle_top    = Paddle(pwidth, plen, "top",    pspeed, (pygame.K_a,    pygame.K_d))
paddle_bottom = Paddle(pwidth, plen, "bottom", pspeed, (pygame.K_LEFT, pygame.K_RIGHT))
paddle_left   = Paddle(pwidth, plen, "left",   pspeed, (pygame.K_w,    pygame.K_s))
paddle_right  = Paddle(pwidth, plen, "right",  pspeed, (pygame.K_UP,   pygame.K_DOWN))

# list helps us check if the ball has collided with any of these
paddles = [paddle_top, paddle_bottom, paddle_left, paddle_right]

# now run the game forever
while True: 

 ################
### Game Logic ###
 ################

    # check for quit and score reset events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
        (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            pygame.font.quit()
            pygame.display.quit()
            sys.exit() # cleans up any remaining windows better than regular exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                wasd_score = 0 
                akey_score = 0

    # paddle and ball movement
    # top/left are WASD, bottom/right are arrow keys
    keys = pygame.key.get_pressed()
    paddle_top.move(keys)
    paddle_bottom.move(keys)
    paddle_left.move(keys)
    paddle_right.move(keys)
    ball.move()

    # check if the ball hit the paddles and reflect it
    index = ball.rect.collidelist([x.rect for x in paddles])
    if index != -1: paddles[index].reflect(ball)

    # check if the ball went out
    if ball.rect.midleft[0] < 0 or ball.rect.midtop[1] < 0:
        akey_score += 1
        ball.reset()
    if ball.rect.midright[0] > width or ball.rect.midbottom[1] > height:
        wasd_score += 1 
        ball.reset()

 ###############
### Rendering ###
 ###############

    # reset the canvas
    screen.fill(black)

    # scores
    s1 = font.render(f"{wasd_score:02}", False, white)
    s2 = font.render(f"{akey_score:02}", False, white)
    screen.blit(s1, (200, 300))
    screen.blit(s2, (630, 630))

    # dotted line
    step = 45 
    line_width = 16
    for x in range(0, width, 2*step):
        x -= line_width/2
        pygame.draw.line(screen, white, (x,height-x), (x+step,height-(x+step)), width=line_width)

    # ball and paddles
    ball.render(screen)
    paddle_top.render(screen)
    paddle_bottom.render(screen)
    paddle_left.render(screen)
    paddle_right.render(screen)

    # update the screen
    pygame.display.flip()
