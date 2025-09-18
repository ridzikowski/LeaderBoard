"""
Animated leaderboard in Pygame (modified)
- Team names configured in a list at the top.
- Higher resolution.
- Clouds move slower.
- Added animation for category 3: several logo3.png objects fall vertically from top with staggered delay.
"""

import pygame, sys, os, random
from pygame.locals import *

# ========== Configuration ==========
TEAM_NAMES = ['Alfa', 'Beta', 'Gamma', 'Delta', 'Epsilon']  # change as needed (max length <= MAX_TEAMS)
MAX_TEAMS = 5
NUM_CATEGORIES = 3
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

BACKGROUND_FILE = 'background.jpg'
CLOUD_FILE = 'h.png'
LOGO_SMALL = 'wit.png'
LOGO_LARGE = 'odra.png'
LOGO_FALL = 'pwr2.png'  

PADDING = 20
ROW_HEIGHT = 90
HEADER_HEIGHT = 140
COLUMN_GAP = 12
WHITE = (255,255,255)
GRAY = (200,200,200)
DARK_OVERLAY = (0,0,0,150)
HIGHLIGHT_COLOR = (255,215,0)
TIE_COLOR = (255,100,100)

pygame.init()
FONT = pygame.font.SysFont('arial', 22)
FONT_BOLD = pygame.font.SysFont('arial', 24, bold=True)
TITLE_FONT = pygame.font.SysFont('arial', 34, bold=True)

class Team:
    def __init__(self, idx, name):
        self.idx = idx
        self.name = f"{name} ({idx})"
        self.values = [0]*NUM_CATEGORIES

class Cloud:
    def __init__(self, img, y, speed, scale):
        self.image = pygame.transform.rotozoom(img,0,scale)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + 50
        self.rect.y = y
        self.speed = speed
    def update(self, dt):
        self.rect.x -= self.speed*dt
        if self.rect.right < -50:
            self.rect.left = SCREEN_WIDTH + 50
    def draw(self,s):
        s.blit(self.image,self.rect)

class ScaleAnim:
    def __init__(self,img,pos):
        self.img=img;self.x,self.y=pos;self.scale=0.2;self.growth=0.5;self.alive=True
    def update(self,dt):
        self.scale+=self.growth*dt
        if self.scale>5:self.alive=False
    def draw(self,s):
        surf=pygame.transform.rotozoom(self.img,0,self.scale)
        r=surf.get_rect(center=(self.x,self.y))
        s.blit(surf,r)

class SlideAnim:
    def __init__(self,img,y):
        self.img=img;self.x=SCREEN_WIDTH+10;self.y=y;self.speed=600;self.alive=True
    def update(self,dt):
        self.x-=self.speed*dt
        if self.x+self.img.get_width()<-100:self.alive=False
    def draw(self,s):
        s.blit(self.img,(int(self.x),int(self.y)))

class FallingLogo:
    def __init__(self,img,x):
        self.img=img;self.x=x;self.y=-random.randint(50,200);self.speed=random.randint(200,300);self.alive=True
    def update(self,dt):
        self.y+=self.speed*dt
        if self.y>SCREEN_HEIGHT+100:self.alive=False
    def draw(self,s):
        s.blit(self.img,(int(self.x),int(self.y)))

screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Leaderboard')
clock=pygame.time.Clock()

def load_image(name,fallback=(255,0,255)):
    if not os.path.exists(name):
        surf=pygame.Surface((100,60),pygame.SRCALPHA)
        surf.fill(fallback+(255,))
        return surf
    return pygame.image.load(name).convert_alpha()

background=pygame.transform.smoothscale(load_image(BACKGROUND_FILE),(SCREEN_WIDTH,SCREEN_HEIGHT))
cloud_img=load_image(CLOUD_FILE)
logo_small=load_image(LOGO_SMALL)
logo_large=load_image(LOGO_LARGE)
logo_fall=load_image(LOGO_FALL)

clouds=[Cloud(cloud_img,600,10,0.5)]

teams=[]
for i in range(MAX_TEAMS):
    nm = TEAM_NAMES[i] if i < len(TEAM_NAMES) else f"Team {i+1}"
    teams.append(Team(i+1,nm))

anims=[]
category_max=[0]*NUM_CATEGORIES
input_mode=False
input_text=''
msg_text='';msg_timer=0


def show_message(t,time_s=2):
    global msg_text,msg_timer
    msg_text=t;msg_timer=time_s


def update_records(idx,new_vals):
    global category_max,anims
    t=teams[idx-1]
    for ci in range(NUM_CATEGORIES):
        old=t.values[ci];new=new_vals[ci];t.values[ci]=new
        if new>category_max[ci]:
            row_y=HEADER_HEIGHT+(t.idx-1)*ROW_HEIGHT+ROW_HEIGHT//2
            if ci==0:
                anims.append(ScaleAnim(logo_small,(SCREEN_WIDTH//3,row_y)))
            elif ci==1:
                anims.append(SlideAnim(logo_large,SCREEN_HEIGHT/4))
            elif ci==2:
                # spawn several falling logos staggered
                for _ in range(5):
                    x=random.randint(100,SCREEN_WIDTH-100)
                    anims.append(FallingLogo(logo_fall,x))
            category_max[ci]=new

def compute_highlights():
    highlights=[set() for _ in range(NUM_CATEGORIES)]
    for ci in range(NUM_CATEGORIES):
        mx=max(t.values[ci] for t in teams)
        for t in teams:
            if t.values[ci]==mx and mx!=0:
                highlights[ci].add(t.idx)
    return highlights


def parse_input(text):
    p=text.strip().split()
    if not p:return
    try:num=int(p[0])
    except:show_message('Wrong team number');return
    if not(1<=num<=MAX_TEAMS):show_message('Out of range');return
    vals=[]
    for i in range(NUM_CATEGORIES):
        if 1+i<len(p):
            try:v=int(p[1+i])
            except:v=0
        else:v=teams[num-1].values[i]
        vals.append(v)
    update_records(num,vals)
    show_message(f'Updated {teams[num-1].name}')


def draw():
    screen.blit(background,(0,0))
    overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA)
    overlay.fill(DARK_OVERLAY)
    screen.blit(overlay,(0,0))
    for c in clouds:c.draw(screen)
    title=TITLE_FONT.render('Leaderboard',True,WHITE)
    screen.blit(title,(PADDING,10))
    team_col_w=300
    rem=SCREEN_WIDTH-team_col_w-3*PADDING
    col_w=max(120,rem//NUM_CATEGORIES)
    x=PADDING;y=HEADER_HEIGHT-60
    screen.blit(FONT_BOLD.render('Team',True,WHITE),(x,y))
    x+=team_col_w+COLUMN_GAP
    for ci in range(NUM_CATEGORIES):
        hdr=FONT_BOLD.render(f'Criterion {ci+1}',True,WHITE)
        screen.blit(hdr,(x+(col_w-hdr.get_width())//2,y))
        x+=col_w+COLUMN_GAP
    highlights=compute_highlights()
    for i,t in enumerate(teams):
        row_y=HEADER_HEIGHT+i*ROW_HEIGHT
        pygame.draw.rect(screen,(0,0,0,80),pygame.Rect(PADDING,row_y,SCREEN_WIDTH-2*PADDING,ROW_HEIGHT-8),border_radius=8)
        name_s=FONT.render(t.name,True,WHITE)
        screen.blit(name_s,(PADDING+8,row_y+(ROW_HEIGHT-name_s.get_height())//2))
        x=PADDING+team_col_w+COLUMN_GAP
        for ci in range(NUM_CATEGORIES):
            val=t.values[ci]
            is_high=t.idx in highlights[ci]
            color=WHITE;font=FONT
            if is_high:
                font=FONT_BOLD
                color=HIGHLIGHT_COLOR if len(highlights[ci])==1 else TIE_COLOR
            txt=font.render(str(val),True,color)
            screen.blit(txt,(x+(col_w-txt.get_width())//2,row_y+(ROW_HEIGHT-txt.get_height())//2))
            x+=col_w+COLUMN_GAP
    for a in anims:a.draw(screen)
    if input_mode:
        box_h=60
        rect=pygame.Rect(PADDING,SCREEN_HEIGHT-box_h-PADDING,SCREEN_WIDTH-2*PADDING,box_h)
        pygame.draw.rect(screen,(30,30,30,220),rect)
        screen.blit(FONT.render('Enter: <no_team> <k1> <k2> ...',True,WHITE),(rect.x+10,rect.y+6))
        screen.blit(FONT_BOLD.render(input_text,True,WHITE),(rect.x+10,rect.y+28))
    if msg_timer>0 and msg_text:
        m=FONT_BOLD.render(msg_text,True,WHITE)
        screen.blit(m,(SCREEN_WIDTH-m.get_width()-20,20))
    inst=FONT.render('I=edit, ESC=exit',True,GRAY)
    screen.blit(inst,(PADDING,SCREEN_HEIGHT-28))
    pygame.display.flip()

running=True
while running:
    dt=clock.tick(FPS)/1000.0
    for e in pygame.event.get():
        if e.type==QUIT:running=False
        elif e.type==KEYDOWN:
            if input_mode:
                if e.key==K_ESCAPE:
                    input_mode=False;input_text=''
                elif e.key in (K_RETURN,K_KP_ENTER):
                    parse_input(input_text);input_mode=False;input_text=''
                elif e.key==K_BACKSPACE:input_text=input_text[:-1]
                else:
                    if e.unicode:input_text+=e.unicode
            else:
                if e.key==K_i:input_mode=True;input_text=''
                elif e.key==K_ESCAPE:running=False
    for c in clouds:c.update(dt*60*0.5)  # slower clouds
    for a in anims:a.update(dt)
    anims=[a for a in anims if a.alive]
    if msg_timer>0:
        msg_timer-=dt
        if msg_timer<=0:msg_text=''
    draw()

pygame.quit();sys.exit()