import pygame, random, os, math
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
flag = 3
paused = False

player_dim = (10, 110)
player_dim_max = (10, 200)
player_dim_min = (10, 50)
ball_rad = 12
ball_rad_min = 5
ball_rad_max = 40
ball_rad_l = ball_rad
ball_rad_r = ball_rad
boundary = pygame.Rect(0,0,SCREEN_W,SCREEN_H)
player_l = pygame.Rect(0,0,*player_dim)
player_l.center = (10,SCREEN_H/2)
player_r = pygame.Rect(0,0,*player_dim)
player_r.center = (SCREEN_W-10,SCREEN_H/2)
ball = pygame.Rect(0,0,ball_rad*2, ball_rad*2)
ball.center = (SCREEN_W/2, SCREEN_H/2)

speed = 10
speed_min = speed//2
speed_max = speed*2
p_speed_l = 0
p_speed_r = 0
b_speed_x = 0
b_speed_y = 0
b_speed_l = speed
b_speed_r = speed
score = [0,0]
TARGET = 11
target = TARGET

pow_duration = 10
recoil_duration = 10

OPPOSERS = [(1,4), (2,5), (3,6)]

verdana = pygame.font.SysFont("verdana", 40)
comicsans = pygame.font.SysFont("comicsans", 30)
comics = pygame.font.SysFont("comicsans", 20)

play = pygame.image.load(PATH+"/pause.png")
play = pygame.transform.scale(play, (50,50))
pow1 = pygame.image.load(PATH+"/big_ball.png")
pow2 = pygame.image.load(PATH+"/big_striker.png")
pow3 = pygame.image.load(PATH+"/small_speed.png")
pow4 = pygame.image.load(PATH+"/small_ball.png")
pow5 = pygame.image.load(PATH+"/small_striker.png")
pow6 = pygame.image.load(PATH+"/big_speed.png")
POWER_IMG = [None]+[eval(f"pow{i}") for i in range(1,7)]
for i in range(1,7):
    POWER_IMG[i] = pygame.transform.scale(POWER_IMG[i], (40,40))

s_rect=None
m_rect=None
ai=None
collided=None
strike=1
muted=0

def initialize_power():
    global show_l,show_count_l,active_l,r_l,pow_l,pos_l,active_count_l,show_r,show_count_r,active_r,r_r,pow_r,pos_r,active_count_r,power
    show_l=False
    show_r=False
    show_count_l=0
    show_count_r=0
    active_l=False
    active_r=False
    active_count_l=0
    active_count_r=0
    pos_l=()
    pos_r=()
    r_l=0
    r_r=0
    pow_l=0
    pow_r=0
    power = [0,0]

def draw_screen():
    global ball
    pygame.draw.rect(screen, (200,200,0), boundary, 2)
    pygame.draw.aaline(screen, (255,255,255), (SCREEN_W/2, 0), (SCREEN_W/2, SCREEN_H))
    if ball.centerx<SCREEN_W/2:
        ball = pygame.Rect(ball.x,ball.y,ball_rad_l*2, ball_rad_l*2)
        pygame.draw.rect(screen, (0,200,100), ball, 0, ball_rad_l)
    elif ball.centerx>SCREEN_W/2:
        ball = pygame.Rect(ball.x,ball.y,ball_rad_r*2, ball_rad_r*2)
        pygame.draw.rect(screen, (0,200,100), ball, 0, ball_rad_r)
    else:
        ball = pygame.Rect(ball.x,ball.y,ball_rad*2, ball_rad*2)
        pygame.draw.rect(screen, (0,200,100), ball, 0, ball_rad)
    pygame.draw.rect(screen, (100,100,100), player_l)
    pygame.draw.rect(screen, (100,100,100), player_r)
    if ai:
        opp = "COMPUTER"
        plr = "YOU"
    else:
        opp = "LEFT"
        plr = "RIGHT"
    left = comics.render(opp, 1, (50,200,150), BG_COLOR)
    right = comics.render(plr, 1, (50,200,150), BG_COLOR)
    match = comics.render(f"Target: {target}", 1, (50,200,150), BG_COLOR)
    screen.blit(left, (10,10))
    screen.blit(match, ((SCREEN_W-match.get_width())/2, SCREEN_H-match.get_height()-20))
    screen.blit(right, (SCREEN_W-right.get_width()-10,10))
    if paused:
        screen.blit(play, ((SCREEN_W-play.get_width())/2, (SCREEN_H-play.get_height())/2))

def reset_ball():
    global b_speed_x,b_speed_y, factor
    b_speed_x = random.choice((-1,1))
    b_speed_y = random.choice((-1,1))
    if b_speed_x<0:
        if b_speed_y<0:
            factor = SCREEN_W/2-SCREEN_H/2
        else:
            factor = (3/2)*SCREEN_H-SCREEN_W/2


def bounce():
    global b_speed_x, b_speed_y, collided, strike
    if ball.centerx<=SCREEN_W/2:
        ball.centerx+=b_speed_l*b_speed_x
        ball.centery+=b_speed_l*b_speed_y
    elif ball.centerx>SCREEN_W/2:
        ball.centerx+=b_speed_r*b_speed_x
        ball.centery+=b_speed_r*b_speed_y

    if ball.colliderect(player_l) or ball.colliderect(player_r):
        b_speed_x*=-1
        collided = ball.center
        mixer.music.load(PATH+"/hit.mp3")
        if not muted:
            mixer.music.play()
        strike=1
    elif ball.right>=boundary.right or ball.left<=boundary.left:
        mixer.music.load(PATH+"/miss.mp3")
        if not muted:
            mixer.music.play()
        if ball.left<=boundary.left:
            score[1]+=1
        else:
            score[0]+=1
        ball.center = (SCREEN_W/2, SCREEN_H/2)
        reset_ball()
        strike=1
        screen.fill((255,0,0))
    elif ball.bottom>=boundary.bottom or ball.top<=boundary.top:
        b_speed_y*=-1
        mixer.music.load(PATH+"/bounce.mp3")
        if not muted:
            mixer.music.play()
    else:
        strike=0


def move():
    global p_speed_l, p_speed_r
    player_l.y+=p_speed_l
    player_r.y+=p_speed_r
    if player_l.bottom>=SCREEN_H-2:
        p_speed_l=0
        player_l.bottom=SCREEN_H-2
    if player_l.top<=2:
        p_speed_l=0
        player_l.top=2
    if player_r.bottom>=SCREEN_H-2:
        p_speed_r=0
        player_r.bottom=SCREEN_H-2
    if player_r.top<=2:
        p_speed_r=0
        player_r.top=2

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
        if ai:
            if score[0]>score[1]:
                disp = "You LOST the game ! Better luck next time !"
            else:
                disp = "Hooray ! You WON the game ! Congrats !"
        else:
            disp = f"Player on {['LEFT','RIGHT'][score.index(max(*score))]} is the winner !"
        text = comicsans.render(disp, 1, (255,255,255), BG_COLOR)
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
    global saved_ball, b_speed_x, b_speed_y, paused, p_speed_l, p_speed_r
    if paused:
        b_speed_x, b_speed_y = saved_ball[0], saved_ball[1]
        paused = False
    else:
        saved_ball = [b_speed_x,b_speed_y]
        b_speed_x, b_speed_y, p_speed_l, p_speed_r = 0,0,0,0
        paused = True

def no_power(i):
    big_ball(i,True)
    big_striker(i,True)
    small_ball(i,True)
    small_striker(i,True)
    small_speed(i,True)
    big_speed(i,True)

def big_ball(i, flip=False):
    global ball_rad_l, ball_rad_r
    if not flip:
        if not i:
            ball_rad_l = ball_rad_max
        else:
            ball_rad_r = ball_rad_max
    else:
        if not i and ball_rad_l>ball_rad:
            ball_rad_l=ball_rad
        elif i and ball_rad_r>ball_rad:
                ball_rad_r=ball_rad
    
def big_striker(i, flip=False):
    global player_l, player_r
    if not flip:
        if not i:
            player_l = pygame.Rect(player_l.x, player_l.y,*player_dim_max)
        else:
            player_r = pygame.Rect(player_r.x, player_r.y,*player_dim_max)
    else:
        if not i and player_l.size>player_dim:
            player_l=pygame.Rect(player_l.x, player_l.y,*player_dim)
        elif i and player_r.size>player_dim:
            player_r=pygame.Rect(player_r.x, player_r.y,*player_dim)

def small_speed(i, flip=False):
    global b_speed_l, b_speed_r
    if not flip:
        if not i and ball.centerx<SCREEN_W/2:
            b_speed_l = speed_min
        elif i and ball.centerx>SCREEN_W/2:
            b_speed_r = speed_min
    else:
        if not i and b_speed_l<speed:
            b_speed_l=speed
        elif i and b_speed_r<speed:
            b_speed_r=speed

def small_ball(i, flip=False):
    global ball_rad_l, ball_rad_r
    if not flip:
        if i:
            ball_rad_l = ball_rad_min
        else:
            ball_rad_r = ball_rad_min
    else:
        if not i and ball_rad_r<ball_rad:
            ball_rad_r=ball_rad
        elif i and ball_rad_l<ball_rad:
            ball_rad_l=ball_rad

def small_striker(i, flip=False):
    global player_l, player_r
    if not flip:
        if i:
            player_l = pygame.Rect(player_l.x, player_l.y,*player_dim_min)
        else:
            player_r = pygame.Rect(player_r.x, player_r.y,*player_dim_min)
    else:
        if not i and player_r.size<player_dim:
            player_r=pygame.Rect(player_r.x, player_r.y,*player_dim)
        elif i and player_l.size<player_dim:
            player_l=pygame.Rect(player_l.x, player_l.y,*player_dim)
    
def big_speed(i, flip=False):
    global b_speed_l, b_speed_r
    if not flip:
        if i and ball.centerx<SCREEN_W/2:
            b_speed_l = speed_max
        elif not i and ball.centerx>SCREEN_W/2:
            b_speed_r = speed_max
    else:
        if not i and b_speed_r>speed:
            b_speed_r=speed
        elif i and b_speed_l>speed:
            b_speed_l=speed

POWERS = [None, big_ball, big_striker, small_speed, small_ball, small_striker, big_speed]
initialize_power()
    
def apply_powers():
    global b_speed_l, b_speed_r
    for i,x in enumerate(power):
        if not x:
            no_power(i)
        else:
            for j,f in enumerate(POWERS[1:]):
                if j!=x:
                    f(i,True)
            if x==1:
                big_ball(i)
            elif x==2:
                big_striker(i)
            elif x==3:
                small_speed(i)
            elif x==4:
                small_ball(i)
            elif x==5:
                small_striker(i)
            elif x==6:
                big_speed(i)

def show_powers():
    global show_l,show_count_l,active_l,r_l,pow_l,pos_l,active_count_l,show_r,show_count_r,active_r,r_r,pow_r,pos_r,active_count_r

    if show_l:
        img = POWER_IMG[pow_l]
        if r_l:
            pos = pos_l
        else:
            pos = [5, random.randrange(0, SCREEN_H-img.get_height())]
            pos_l = pos
            r_l+=1
        screen.blit(img, pos)
        if math.dist(player_l.center, pos)<=(img.get_height()+player_l.height)/2:
            show_l = False
            active_l = True
            if ((pow_l,pow_r) in OPPOSERS or (pow_r,pow_l) in OPPOSERS) and active_r:
                    pow_r = 0
                    active_r = False
                    active_count_r = 0
                    show_r = False
                    power[1] = 0
    else:
        if active_l:
            power[0] = pow_l
            active_count_l+=1
            timer = comics.render(str(pow_duration-active_count_l//FPS), 1, (255,255,255), BG_COLOR)
            screen.blit(POWER_IMG[pow_l], ((SCREEN_W/2-timer.get_width())/2, 20))
            screen.blit(timer, ((SCREEN_W/2-timer.get_width())/2+POWER_IMG[pow_l].get_width()*1.3, 20))
            if active_count_l>=pow_duration*FPS:
                active_l = False
                power[0] = 0
                active_count_l=0
        else:
            show_count_l+=1
            if show_count_l>=recoil_duration*FPS:
                pow_l = random.randint(1,6)
                show_l=True
                show_count_l=0

    if show_r:
        img = POWER_IMG[pow_r]
        if r_r:
            pos = pos_r
        else:
            pos = [SCREEN_W-img.get_width()-5, random.randrange(0, SCREEN_H-img.get_height())]
            pos_r = pos
            r_r+=1
        screen.blit(img, pos)
        if math.dist(player_r.center, pos)<=(img.get_height()+player_r.height)/2:
            show_r = False
            active_r = True
            if ((pow_l,pow_r) in OPPOSERS or (pow_r,pow_l) in OPPOSERS) and active_l:
                    pow_l = 0
                    active_l = False
                    active_count_l = 0
                    show_l = False
                    power[0] = 0
    else:
        if active_r:
            power[1] = pow_r
            active_count_r+=1
            timer = comics.render(str(pow_duration-active_count_r//FPS), 1, (255,255,255), BG_COLOR)
            screen.blit(POWER_IMG[pow_r], (SCREEN_W*(3/4)-timer.get_width(), 20))
            screen.blit(timer, (SCREEN_W*(3/4)-timer.get_width()+POWER_IMG[pow_r].get_width()*1.3, 20))
            if active_count_r>=pow_duration*FPS:
                active_r = False
                power[1] = 0
                active_count_r=0
        else:
            show_count_r+=1
            if show_count_r>=recoil_duration*FPS:
                pow_r = random.randint(1,6)
                show_r=True
                show_count_r=0

def opening_screen():
    global s_rect,m_rect
    screen.fill(BG_COLOR)
    head = verdana.render("PONG",1,(255,255,255),BG_COLOR)
    single = verdana.render("Single Player",1,(0,100,100),(0,0,0))
    s_pos = ((SCREEN_W/2-single.get_width())/2,SCREEN_H/2-20)
    s_rect = single.get_rect(x=s_pos[0]-15, y=s_pos[1]-10)
    s_rect.w+=30
    s_rect.h+=20
    multi = verdana.render("Multi Player",1,(0,100,100),(0,0,0))
    m_pos = ((3*SCREEN_W/2-multi.get_width())/2,SCREEN_H/2-20)
    m_rect = multi.get_rect(x=m_pos[0]-15, y=m_pos[1]-10)
    m_rect.w+=30
    m_rect.h+=20
    screen.blit(head, ((SCREEN_W-head.get_width())/2,20))
    pygame.draw.rect(screen, (0,0,0), s_rect)
    screen.blit(single, s_pos)
    pygame.draw.rect(screen, (0,0,0), m_rect)
    screen.blit(multi, m_pos)

def AI_player1():
    global player_l, p_speed_l
    if b_speed_x<0:
        if player_l.top>ball.top:
            p_speed_l=-speed-1
        elif player_l.bottom<ball.bottom:
            p_speed_l=speed+1
        else:
            p_speed_l=0
    elif show_l and pos_l:
        if pos_l[1]>player_l.bottom:
            p_speed_l=speed+1
        elif pos_l[1]>player_l.top:
            p_speed_l=-speed-1
        else:
            p_speed_l=0

def AI_player2():
    global player_l, p_speed_l
    if b_speed_x<0:
        if player_l.centery>ball.centery:
            p_speed_l=-speed-1
        elif player_l.centery<ball.centery:
            p_speed_l=speed+1
        else:
            p_speed_l=0

c_pos = (0,0)
factor=0
def AI_player3():
    global player_l, p_speed_l, c_pos, factor
    if b_speed_x<0:
        if ball.centerx>=SCREEN_W/2:
            c_pos = ball.center
            if b_speed_y<1:
                factor = c_pos[0]-c_pos[1]
            else:
                factor = SCREEN_H*2-c_pos[0]-c_pos[1]
        if factor>SCREEN_H:
            factor = factor-SCREEN_H
        if player_l.centery<factor-speed:
            p_speed_l=speed+1
        elif player_l.centery>factor+speed:
            p_speed_l=-speed-1
        else:
            p_speed_l=0

def AI_player4():
    global player_l, p_speed_l
    global player_l, p_speed_l
    if b_speed_x<0:
        if player_l.centery<ball.centery:
            p_speed_l=-speed-1
        elif player_l.centery>ball.centery:
            p_speed_l=speed+1
        else:
            p_speed_l=0

aimind=AI_player1
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
                    if ai:
                        p_speed_r=-speed-1
                    else:
                        p_speed_l=-speed-1
                if ev.key == K_s:
                    if ai:
                        p_speed_r=speed+1
                    else:
                        p_speed_l=speed+1

        elif ev.type == KEYUP:
            if (ev.key == K_UP or ev.key == K_DOWN) and not paused:
                p_speed_r=0
            elif (ev.key == K_w or ev.key == K_s) and not paused:
                if ai:
                    p_speed_r=0
                else:
                    p_speed_l=0
            elif ev.key == K_SPACE:
                if flag == 2:
                    flag = 3
                    score = [0,0]
                    player_l.centery=boundary.centery
                    player_r.centery=boundary.centery
                    initialize_power()
                    target = TARGET
                elif flag == 0:
                    flag = 1
                    reset_ball()
                    pygame.time.delay(1000)
                elif flag == 1:
                    pause()
            elif ev.key == K_m:
                muted=1-muted
        elif ev.type == MOUSEBUTTONUP:
            if flag == 3:
                if s_rect.collidepoint(pygame.mouse.get_pos()):
                    flag = 0
                    ai = True
                elif m_rect.collidepoint(pygame.mouse.get_pos()):
                    flag = 0
                    ai = False
    
    show_score()
    draw_screen()
    bounce()
    move()
    lift_target()
    instruct()
    winner()
    if flag == 1 and not paused:
        show_powers()
        apply_powers()
        if ai:
            if strike:
                aimind = random.choice([AI_player1 for _ in range(50)]+[AI_player2 for _ in range(50)]+[AI_player3 for _ in range(50)]+[AI_player3 for _ in range(50)])
            else:
                aimind()

    if flag == 3:
        opening_screen()
        
    pygame.display.update()
    clock.tick(FPS)