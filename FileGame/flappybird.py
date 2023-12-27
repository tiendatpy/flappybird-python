import pygame, sys
from pygame.locals import *
import random

from pygame.sprite import AbstractGroup
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.init()
clock = pygame.time.Clock()
fps = 70

screen_width = 480
screen_height = 640
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Flappy Bird Game')
# define font
font_score = pygame.font.SysFont('Bauhaus 93', 60)
font_text = pygame.font.SysFont('Bauhaus 93', 30)
# define color
white = (255, 255, 255)
black = (0, 0, 0)
orange = (255, 140, 0)
# music
sound = pygame.mixer.Sound('FileGame/sound/backgroundsound1.wav')
#define variable
ground_scroll = 0
ground_speed = 2
flying = False
game_over = False
pipe_gap = 170
pipe_frequency = 2000
last_pipe = pygame.time.get_ticks()
score = 0
hight_score = -1
pass_pipe = False

# load images
bg = pygame.image.load('FileGame/assets/2.jpg')
ground = pygame.image.load('FileGame/assets/ground.png')
button_img = pygame.image.load('FileGame/assets/restart.png')
load_start_img = pygame.image.load('FileGame/assets/message.png')
start_img = pygame.transform.scale2x(load_start_img)
game_over_img = pygame.image.load('FileGame/assets/gameover.png')
# text outline
_circle_cache = {}
def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points
def render(text, font, gfcolor=pygame.Color(white), ocolor=(black), opx=2):
    textsurface = font.render(text, True, gfcolor).convert_alpha()
    w = textsurface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textsurface, (opx, opx))
    return surf

def reset_game():
  pipe_group.empty()
  flappy.rect.x = 100
  flappy.rect.y = int(screen_height/2)
  score = 0
  pipe_frequency = 2000
  pipe_gap = 170
  return score, pipe_frequency, pipe_gap


class Bird(pygame.sprite.Sprite):
  def __init__(self, x, y):
    pygame.sprite.Sprite.__init__(self)
    self.images = []
    self.index = 0
    self.counter = 0
    for num in range(1, 4):
      img = pygame.image.load(f'FileGame/assets/bird{num}.png')
      self.images.append(img)
    self.image = self.images[self.index]
    self.rect = self.image.get_rect()
    self.rect.center = [x, y]
    self.gravity = 0
    self.clicked = False
  def update(self):
    # gravity
    if flying == True:
      self.gravity += 0.5
      if self.gravity > 5:
        self.gravity = 5
      if self.rect.bottom < 540 and not game_over:
        self.rect.y += int(self.gravity)
      else: 
        self.rect.y += 8
    if game_over == False:
      # jump
      keys = pygame.key.get_pressed()
      mouse_click = pygame.mouse.get_pressed()[0]
      if self.clicked == False:
        if keys[K_SPACE] == 1 or mouse_click == 1:
          self.clicked = True
          self.gravity = -10
          if self.rect.y < 10:
            self.rect.y = 10
      if mouse_click == 0 and keys[K_SPACE] == 0:
        self.clicked = False

      # handle the animation
      self.counter += 1
      flap_cooldown = 6
      if self.counter > flap_cooldown:
        self.index += 1
        self.counter = 0
        if self.index >= len(self.images):
          self.index = 0
      self.image = self.images[self.index]
      # rotate the bird
      self.image = pygame.transform.rotate(self.images[self.index], self.gravity * (-2))
    else:
      self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
  def __init__(self, x, y, pos, gap):
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load(f'FileGame/assets/pipe.png')
    self.rect = self.image.get_rect()
    # vi tri: 1 ong o tren, 2 ong o duoi
    if pos == 1:
      self.image = pygame.transform.flip(self.image, False, True)
      self.rect.bottomleft = [x, y - int(gap / 2)]
    if pos == -1: 
      self.rect.topleft = [x, y + int(gap) / 2]
  def update(self):
    self.rect.x -= ground_speed
    if self.rect.left < -100:
      self.kill()
class Button():
  def __init__(self, x, y, image):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.bottomleft = (x, y)
  def draw(self):
    active = False
    screen.blit(self.image, (self.rect.x, self.rect.y))
    if pygame.key.get_pressed()[K_SPACE] == 1:
      active = True
    else:
      pos = pygame.mouse.get_pos()
      if self.rect.collidepoint(pos):
        if pygame.mouse.get_pressed()[0] == 1:
          active = True
    return active




bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_height)/2)
button = Button(screen_width //2 - 50, screen_height // 2 + 50, button_img)

bird_group.add(flappy)

run = True
while run:
  clock.tick(fps)
  screen.blit(bg,(0,0))

  pipe_group.draw(screen)
  bird_group.draw(screen)
  bird_group.update()
  # draw the ground
  screen.blit(ground,(ground_scroll,550))

  # check the score
  if len(pipe_group) > 0:
    if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
      and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
      and pass_pipe == False:
        pass_pipe = True
    if pass_pipe == True and bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
      pass_pipe = False
      score += 1

  # hight score
  if hight_score < score:
    hight_score = score
    
  # hard level
  if score > 10 and score < 30: # decrease pipe_gap
    pipe_gap = 160
  elif score >= 30:
    pipe_gap = 150
    
  if score > 20 and score < 40: # decrease pipe_frequency
    pipe_frequency = 1800
  elif score >= 40:
    pipe_frequency = 1700
  # end hard level
      

  # collision
  if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
    game_over = True

  # restart game
  if game_over == True:
    screen.blit(game_over_img, (150, screen_height/2 - 50)) #gameover image
    screen.blit(render(str(f'SCORE : {score}'), font_text, white, black), (175, 180))  # high_score
    screen.blit(render('BEST :', font_text, white, orange), (175, 220))  
    screen.blit(render(str(hight_score), font_text, white, black), (293, 220))  # high_score
    sound.stop()
    if button.draw() == True:
      game_over = False
      score, pipe_frequency, pipe_gap = reset_game()

  # check game over
  if flappy.rect.bottom >= 540:
    game_over = True
    flying = False
  if game_over == False:
    sound.play()
    # draw img when start game
    start_game = pygame.time.get_ticks()
    if start_game  > 0 and start_game < 2000:
      screen.blit(start_img, (100, 60))
    if flying == True:
      time_now = pygame.time.get_ticks()
      # generate new pipes
      if time_now - last_pipe > pipe_frequency:
        pipe_height = random.randint(-100, 100)
        bot_pipe = Pipe(screen_width, int(screen_height)/2 + pipe_height, -1, pipe_gap)
        top_pipe = Pipe(screen_width, int(screen_height)/2 + pipe_height, 1, pipe_gap)
        pipe_group.add(bot_pipe)
        pipe_group.add(top_pipe)
        last_pipe = time_now
      # draw score when play
      screen.blit(render(str(score), font_score), (220, 50))

    # scroll the ground
    ground_scroll -= ground_speed
    if abs(ground_scroll) > 35:
      ground_scroll = 0
    pipe_group.update()
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False
    if (event.type == pygame.MOUSEBUTTONDOWN or
        (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)) and not flying and not game_over:
        flying = True
  pygame.display.update()
pygame.quit()
sys.exit()