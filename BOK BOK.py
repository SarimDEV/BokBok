import pygame
import math
import random
#This makes the sprites work on any computer
from os import path
img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

screen_width = 480
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
FPS = 120
gamename = "Bok Bok!"
done = False
font_ariel = pygame.font.match_font('arial')
pygame.display.set_caption(gamename)

#settings we can customize later using an options page

fruitspawnrate = 8
bulletdelay = 250
lowest_speed = 1
max_speed = 10
bg_vol = 0.125


#Function to draw text.

def draw_text(surf, text, size, x, y, colour):
    font = pygame.font.Font(font_ariel, size)
    text_surface = font.render(text, True, colour)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

#In the game, once a fruit is off the screen it respawns on the top of screen
#When the chicken gets hit by a fruit or hits one the fruit is killed, so it doesnt exist anymore, so this respawns another one

def newfruit():
    m = fruit()
    all_sprites.add(m)
    fruits.add(m)

#Health bar
def draw_healthbar(surf,x,y,percentage):
    if percentage < 0:
        percentage = 0
    length = 100
    height = 15
    fill = (percentage/100) * length
    outline_rect = pygame.Rect(x,y,length,height)
    inner_rect = pygame.Rect(x,y,fill,height)
    pygame.draw.rect(surf, GREEN, inner_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


class Bokbok(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bokbok_img, (65, 85))                   #Scales the image so that it's massive
        self.image.set_colorkey(RED)                                                #Fixes the chicken sprite
        self.rect = self.image.get_rect()
        self.radius = 27                                                            #Circular radius
        #pygame.draw.circle(self.image, GREEN, self.rect.center, self.radius)       #this is used for collision checking, we're using circular collision between chicken and fruit, so it is far more accurate
        self.rect.centerx = screen_width/2
        self.rect.bottom = screen_height - 10
        self.speedx = 0
        self.health = 100                                                           #Player health
        self.last_bullet = pygame.time.get_ticks()                                  #This gets the time when player last shot, this is important to bullet delays and used later in shoot function
        self.bullet_delay = bulletdelay

    def shoot(self):
        time = pygame.time.get_ticks()
        if time - self.last_bullet > self.bullet_delay:
            self.last_bullet = time
            bullet = Bullet(self.rect.centerx - 22, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            bullet_sound.play()
    #Movement command
    def update(self):
        self.speedx = 0
        keypress = pygame.key.get_pressed()
        if keypress[pygame.K_LEFT]:
            self.speedx = -5
        if keypress[pygame.K_RIGHT]:
            self.speedx = 5
        if keypress[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        elif self.rect.left < 0:
            self.rect.left = 0



class fruit(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_1 = random.choice(fruit_images)              #original image
        self.image_1.set_colorkey(BLACK)
        self.image = self.image_1.copy() #Copy of image
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 /2)
        #pygame.draw.circle(self.image, GREEN, self.rect.center, self.radius)       #this is used for collision checking, we're using circular collision between chicken and fruit, so it is far more accruate
        self.rect.x = random.randrange(0, screen_width - self.rect.width)
        self.rect.y = random.randrange(-150,-100)
        self.speedy = random.randrange(lowest_speed, max_speed)
        self.speedx = random.randrange(-3, 3)
        self.rotat = 0
        self.rotat_speed = random.randrange(-4,15)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):                       #This function creates the rotation effect on the fruits
        time = pygame.time.get_ticks()
        if time - self.last_update > 50:
            self.last_update = time
            self.rotat = (self.rotat + self.rotat_speed) % 360
            previous_image = pygame.transform.rotate(self.image_1, self.rotat)
            previous_center = self.rect.center
            self.image = previous_image
            self.rect = self.image.get_rect()
            self.rect.center = previous_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        #spawns the fruit within the screen width and height, x and y cordinates are radom with screen limitations and yspeed (horrizontal movement) is in a random range
        if self.rect.top > screen_height + 10 or self.rect.left < -90 or self.rect.right > screen_width + 90:   #spawns the fruit within the screen width and height
            self.rect.x = random.randrange(0, screen_width - self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(1, 8)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosionanim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_frame = pygame.time.get_ticks()
        self.FPS = 50

    def update(self):
        #This makes it so that the images filp through really fast at a constant rate
        #if the last time the current time is greater than the frame rate then it will flip to another frame
        time = pygame.time.get_ticks()
        if time - self.last_frame > self.FPS:
            self.last_frame = time
            self.frame += 1
            if self.frame == len(explosionanim[self.size]):
                self.kill()
            else:
                #centers the animation so that it's not just anywhere but at the center
                center = self.rect.center
                self.image = explosionanim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(laser_img, (6, 54))           #This can change if we want to change the laser size a little more
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10 #negative beacuse it goes upwards

    def update(self):
        self.rect.y += self.speedy
        #Delete bullet if bottom of sprite hits top of screen
        if self.rect.bottom < 0:
            self.kill()
#Main
score = 0
#Game graphics loading
bg = pygame.image.load(path.join(img_dir, "gizKWGp.jpg")).convert()
bg_rect = bg.get_rect()
cluckinpoints_img = pygame.image.load(path.join(img_dir, "cluckin points.png")).convert()
bokbok_img = pygame.image.load(path.join(img_dir, "bokbok.png")).convert()
laser_img = pygame.image.load(path.join(img_dir, "laserBlue01.png")).convert()


explosionanim = {}
explosionanim['big'] = []
explosionanim['small'] = []
for i in range(12):              #11 frame animation
    filename = 'explosion_{}.png'.format(i)      #in each {} there the number i which correlates with the image file name
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_big = pygame.transform.scale(img, (75,75))      #Two types of images, 1 big for when it hits fruits and 1 small for when it hits chicken bokbok man
    explosionanim['big'].append(img_big)
    img_small = pygame.transform.scale(img, (32, 32))
    explosionanim['small'].append(img_small)

fruit_images =[]
fruit_list = ['grape.png', 'apple.png', 'grape_BIG.png',        #this is a list of images of fruit varying in size (randomized later)
            'banana.png', 'watermalon.png', 'watermalon_BIG.png',
            'pineapple.png',]
for i in fruit_list:
    fruit_images.append(pygame.image.load(path.join(img_dir, i)).convert())

#Sound loading
bullet_sound = pygame.mixer.Sound(path.join(snd_dir, 'BokBok.wav'))
chicken_hurt_sound = pygame.mixer.Sound(path.join(snd_dir, 'hurt.wav'))
explo_sound_list = []
for snd in ['splat1.wav', 'splat2.wav']:                                      #list of two sounds possible (randomized later)
    explo_sound_list.append(pygame.mixer.Sound(path.join(snd_dir, snd)))

#Background sound
pygame.mixer.music.load(path.join(snd_dir, 'POL-galactic-chase-short.wav'))
pygame.mixer.music.set_volume(bg_vol)



all_sprites = pygame.sprite.Group()
fruits = pygame.sprite.Group()                                                #all fruits are grouped together
bullets = pygame.sprite.Group()                                               #all bullets are grouped together

bokbok = Bokbok()

all_sprites.add(bokbok)



for i in range(fruitspawnrate):           #Spawns a new fruit
    newfruit()
    
pygame.mixer.music.play(loops=-1)       #loops background music forever

while not done:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    #update section
    all_sprites.update()

    #Collision checking if bullet hits 33s (GROUP COLLISION)
    collide = pygame.sprite.groupcollide(fruits, bullets, True, True)
    for x in collide:           #fruit Collision
        score += 50 - x.radius
        random.choice(explo_sound_list).play()
        #Explosion animation BIG EXPLOSION DUSHHH
        explosion = Explosion(x.rect.center, 'big')
        all_sprites.add(explosion)
        newfruit()
    #Collision checking if fruit hits chicken (bokbok)
    collide = pygame.sprite.spritecollide(bokbok, fruits, True, pygame.sprite.collide_circle)  #creates a list of collions
    for xy in collide:
        bokbok.health -= xy.radius * 2          #radius of fruit multiplied by 2, so the larger the fruit the greater damage you take (CAN ADD SPEED MAYBE?)
        #Explosion animation when being hit SMALL EXPLOSION SWOOSH
        chicken_hurt_sound.play()
        explosion = Explosion(xy.rect.center, 'small')
        all_sprites.add(explosion)
        newfruit()
        if bokbok.health <=0:
            done = True         #ends game (WILL CHANGE)

    #render
    screen.fill(BLACK)
    screen.blit(bg, bg_rect)
    all_sprites.draw(screen)
    draw_text(screen, "CLUCKIN' POINTS: " + str(score), 18, 110, 10, WHITE)
    cluckinpoints_img.set_colorkey(BLACK)
    screen.blit(cluckinpoints_img,(5,10))
    draw_healthbar(screen, screen_width-110, 5, bokbok.health)
    draw_text(screen, str(bokbok.health), 12, screen_width - 60,5, BLACK)

    pygame.display.flip()

pygame.quit()
