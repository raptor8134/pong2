#!/usr/bin/env python3

import pygame
import sys
import random 

class Ball():
    def __init__(self, speed: int):
        self.speed = speed 
        self.image = pygame.image.load("doge.png") # TODO replace with a ball
        self.coords = self.image.get_rect()
    def reset(self):
        # give even preference to each paddle for starting
        random.seed()
        self.velocity = [self.speed * random.choice([-1,1]), 0]
        random.shuffle(self.velocity)
        # center the ball
        c = self.coords
        self.coords.move_ip((width-c.w)//2, (width-c.h)//2)
    def move(self):
        c = self.coords
        v = self.velocity
        c.move_ip(v)
        # check for wall collisions
        if c.left < 0 or c.right > width:
            v[0] = -v[0]
        if c.top < 0 or c.bottom > height:
            v[1] = -v[1]
        self.velocity = [x * 1.0001 for x in v]
    def render(self, surface): # surface should be a surface object
        surface.blit(self.image, self.coords)

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
    def render(self, surface):
        pygame.draw.rect(surface, white, self.rect)

# initialize pygame and set options
pygame.display.init()
pygame.font.init()
pygame.key.set_repeat(2)
font = pygame.font.Font("PublicPixel-0W5Kv.ttf", 100)

# player scores
wasd_score = 0 
akey_score = 0

# initialize window and set colors
size = width, height = (1024, 1024) # these should always be the same
screen = pygame.display.set_mode(size)
black = 0, 0, 0
white = 225, 225, 225

# create the ball object
ball = Ball(5)
ball.reset()

# create the four paddle objects
pspeed = 10
pwidth, plen = 16, 128
paddle_top    = Paddle(pwidth, plen, "top",    pspeed, (pygame.K_a,    pygame.K_d))
paddle_bottom = Paddle(pwidth, plen, "bottom", pspeed, (pygame.K_LEFT, pygame.K_RIGHT))
paddle_left   = Paddle(pwidth, plen, "left",   pspeed, (pygame.K_w,    pygame.K_s))
paddle_right  = Paddle(pwidth, plen, "right",  pspeed, (pygame.K_UP,   pygame.K_DOWN))

# list helps us check if the ball has collided with any of these
paddle_rects = [x.rect for x in [paddle_top, paddle_bottom, paddle_left, paddle_right]]

while True: 
    # handle events
    for event in pygame.event.get():
        # check if the X button on the window bar or the q key
        # have been pressed, if yes, then exit
        if event.type == pygame.QUIT or \
        (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            pygame.font.quit()
            pygame.display.quit()
            sys.exit()

    # check for all other keys
    # top/left are WASD, bottom/right are arrow keys
    keys = pygame.key.get_pressed()
    paddle_top.move(keys)
    paddle_bottom.move(keys)
    paddle_left.move(keys)
    paddle_right.move(keys)

    # move the ball
    ball.move()

    # reset the canvas
    screen.fill(black)

    # scores
    s1 = font.render(str(wasd_score), False, white)
    s2 = font.render(str(akey_score), False, white)
    screen.blit(s1, (300, 300))
    screen.blit(s2, (630, 630))

    # dotted line
    step = 45 
    line_width = 16
    for x in range(0, width, 2*step):
        x -= line_width/2
        pygame.draw.line(screen, white, (x,height-x), (x+step,height-(x+step)), width=line_width)
    #pygame.draw.line(screen, white, (0,height), (width,0), width=4)

    # render ball and paddles
    ball.render(screen)
    paddle_top.render(screen)
    paddle_bottom.render(screen)
    paddle_left.render(screen)
    paddle_right.render(screen)

    # update the screen
    pygame.display.flip()
