import pygame, random, os
from pygame.locals import *
import pygame.mixer as mixer

pygame.init()
mixer.init()
clock = pygame.time.Clock()
PATH = os.path.dirname(__file__)
FPS = 60

SCREEN_W = 1500
SCREEN_H = 700
BG_COLOR = (30,30,30)
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("PONG")
flag = 0
paused = False

player_dim = (10, 110)
ball_rad = 12
ball_rad_l = ball_rad
ball_rad_r = ball_rad
boundary = pygame.Rect(0,0,SCREEN_W,SCREEN_H)
player_l = pygame.Rect(0,0,*player_dim)
player_l.center = (10,SCREEN_H/2)
player_r = pygame.Rect(0,0,*player_dim)
player_r.center = (SCREEN_W-10,SCREEN_H/2)
ball = pygame.Rect(0,0,ball_rad*2, ball_rad*2)
ball.center = (SCREEN_W/2, SCREEN_H/2)

speed = 11
p_speed_l = 0
p_speed_r = 0
b_speed_x = 0
b_speed_y = 0
score = [0,0]
TARGET = 11
target = TARGET

verdana = pygame.font.SysFont("verdana", 40)
comicsans = pygame.font.SysFont("comicsans", 30)
comics = pygame.font.SysFont("comicsans", 20)
play = pygame.image.load(PATH+"/pause.png")
play = pygame.transform.scale(play, (50,50))


def draw_screen():
    global ball
    pygame.draw.rect(screen, (200,200,0), boundary, 1)
    pygame.draw.aaline(screen, (255,255,255), (SCREEN_W/2, 0), (SCREEN_W/2, SCREEN_H))
    pygame.draw.rect(screen, (0,200,100), ball, 0, ball_rad)
    pygame.draw.rect(screen, (100,100,100), player_l)
    pygame.draw.rect(screen, (100,100,100), player_r)
    left = comics.render("LEFT", 1, (50,200,150), BG_COLOR)
    right = comics.render("RIGHT", 1, (50,200,150), BG_COLOR)
    match = comics.render(f"Target: {target}", 1, (50,200,150), BG_COLOR)
    screen.blit(left, (10,10))
    screen.blit(match, ((SCREEN_W-match.get_width())/2, SCREEN_H-match.get_height()-20))
    screen.blit(right, (SCREEN_W-right.get_width()-10,10))
    if paused:
        screen.blit(play, ((SCREEN_W-play.get_width())/2, (SCREEN_H-play.get_height())/2))

def reset_ball():
    global b_speed_x,b_speed_y
    b_speed_x = speed*random.choice((-1,1))
    b_speed_y = speed*random.choice((-1,1))

def bounce():
    global b_speed_x, b_speed_y
    ball.centerx+=b_speed_x
    ball.centery+=b_speed_y
    if ball.centerx>=SCREEN_W or ball.centerx<=0:
        mixer.music.load(PATH+"/miss.mp3")
        mixer.music.play()
        if ball.centerx<=0:
            score[1]+=1
        else:
            score[0]+=1
        ball.center = (SCREEN_W/2, SCREEN_H/2)
        reset_ball()
        screen.fill((255,0,0))
    if ball.centery>=SCREEN_H or ball.centery<=0:
        b_speed_y*=-1
        mixer.music.load(PATH+"/bounce.mp3")
        mixer.music.play()
    if ball.colliderect(player_l) or ball.colliderect(player_r):
        b_speed_x*=-1
        mixer.music.load(PATH+"/hit.mp3")
        mixer.music.play()

def move():
    global p_speed_l, p_speed_r
    player_l.y+=p_speed_l
    player_r.y+=p_speed_r
    if player_l.y>=(SCREEN_H-player_l.height):
        p_speed_l=0
        player_l.y=SCREEN_H-player_l.height-1
    if player_l.y<=0:
        p_speed_l=0
        player_l.y=0
    if player_r.y>=(SCREEN_H-player_r.height):
        p_speed_l=0
        player_r.y=SCREEN_H-player_r.height-1
    if player_r.y<=0:
        p_speed_r=0
        player_r.y=0

def show_score():
    l = str(score[0])
    r = str(score[1])
    while len(l)<len(r):
        l='0'+l
    while len(l)>len(r):
        r='0'+r
    text = verdana.render(f"{l}  :  {r}", 1, (200,100,100), BG_COLOR)
    screen.blit(text, ((SCREEN_W-text.get_width())/2,10))

def winner():
    global b_speed_x, b_speed_y, p_speed_l, p_speed_r, flag
    if score[0]==target or score[1]==target:
        b_speed_x, b_speed_y, p_speed_l, p_speed_r = 0,0,0,0
        flag = 2
        screen.fill(BG_COLOR)
        if score[0]==target:
            side = "LEFT"
        elif score[1]==target:
            side = "RIGHT"
        text = comicsans.render(f"Player on {side} is the winner !", 1, (255,255,255), BG_COLOR)
        text2 = verdana.render(f"{score[0]}  :  {score[1]}", 1, (200,100,100), BG_COLOR)
        text3 = comics.render(f"(Press SPACEBAR to Replay)", 1, (200,200,100), BG_COLOR)
        screen.blit(text, ((SCREEN_W-text.get_width())/2, (SCREEN_H-text.get_height())/2))
        screen.blit(text2, ((SCREEN_W-text2.get_width())/2, 20))
        screen.blit(text3, ((SCREEN_W-text3.get_width())/2, (SCREEN_H-text.get_height())/2+text3.get_height()*5))

def lift_target():
    global target
    if score[0] == score[1] and score[0] == target-1:
        target+=1

def instruct():
    text = comics.render("(Press SPACEBAR to start Game)", 1, (200,200,100), BG_COLOR)
    if flag == 0:
        screen.blit(text, ((SCREEN_W-text.get_width())/2, SCREEN_H-text.get_height()-20))

def pause():
    global saved_ball, b_speed_x, b_speed_y, paused
    if paused:
        b_speed_x, b_speed_y = saved_ball[0], saved_ball[1]
        paused = False
    else:
        saved_ball = [b_speed_x,b_speed_y]
        b_speed_x, b_speed_y = 0,0
        paused = True

while True:
    screen.fill(BG_COLOR)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif ev.type == KEYDOWN:
            if not paused:
                if ev.key == K_UP:
                    p_speed_r=-speed-1
                if ev.key == K_DOWN:
                    p_speed_r=speed+1
                if ev.key == K_w:
                    p_speed_l=-speed-1
                if ev.key == K_s:
                    p_speed_l=speed+1
        elif ev.type == KEYUP:
            if (ev.key == K_UP or ev.key == K_DOWN) and not paused:
                p_speed_r=0
            elif (ev.key == K_w or ev.key == K_s) and not paused:
                p_speed_l=0
            elif ev.key == K_SPACE:
                if flag == 2:
                    flag = 0
                    score = [0,0]
                    target = TARGET
                elif flag == 0:
                    flag = 1
                    reset_ball()
                    pygame.time.delay(1000)
                else:
                    pause()
    
    show_score()
    draw_screen()
    bounce()
    move()
    lift_target()
    instruct()
    winner()
    pygame.display.update()
    clock.tick(FPS)