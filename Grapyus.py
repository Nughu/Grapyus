import os, sys, contextlib
from time import sleep, time
from random import randint, choice
with contextlib.redirect_stdout(None):
    import pygame
from pygame import font
from pygame.locals import *
from colorama import Fore, Style

# -----------------------------------------------------------------------------------------------------------------------------

# General Settings
width, height = 1280, 720
music_volume = 0.7

# -----------------------------------------------------------------------------------------------------------------------------

# Constants
CENTER = width//2, height//2
IMG_DIR = ".\\Images\\"
SOUND_DIR = ".\\Sounds\\"
SAVE_DIR = ".\\Save\\"
TEXT_YELLOW = Fore.YELLOW
TEXT_GREEN = Fore.GREEN
TEXT_RED = Fore.RED
TEXT_CYAN = Fore.CYAN
SHIP_SCALE = width//17, height//17                      # Scale to fit aspect ratio of sprite
FLAME_SCALE = width//17, (width//17)*0.8666             # Scale to fit aspect ratio of sprite
ARROW_SCALE = width//11, (width//11)*0.5625             # Scale to fit aspect ratio of sprite
YELLOW_SCALE = width//11, (width//11)*0.875             # Scale to fit aspect ratio of sprite
GREY_SCALE = width//17, height//17                      # Scale to fit aspect ratio of sprite
STARS_WIDTH, STARS_HEIGHT = 1498, 1060
STARS_SCALE = 1.5
STARS_EXITFRAME = 0 - (STARS_WIDTH * STARS_SCALE)
MOVE_SPEED = 4
ARROW_SPEED = 7
ARROW_POINTS = 10
YELLOW_SPEED = 1
YELLOW_POINTS = 30
GREY_SPEED = 3
GREY_POINTS = 50
PLAYER_SHOT_SPEED = 10
YELLOW_SHOT_SPEED = 6
GREY_SHOT_SPEED = 7
SHIPEXP_FRAME_DELAY = 5
NORMAL_FIRERATE = 0.4                                   # delay between shots in normal fire mode (in seconds)

# -----------------------------------------------------------------------------------------------------------------------------

# Pygame Init
pygame.init()
screen = pygame.display.set_mode((width, height), display=0, vsync=0)
pygame.display.set_caption("Grapyus")

# Initial terminal clear
clear = lambda: os.system('cls')
clear()

# -----------------------------------------------------------------------------------------------------------------------------

# Classes
class BackgroundFader:
    def __init__(self):
        self.background = [1, 1, 1]
        self.R_fade = True
        self.R_fade_up = True
        self.G_fade = False
        self.G_fade_up = False
        self.B_fade = False
        self.B_fade_up = False
        self.fade_tick = True
    def fade(self):
        # Background Color Fade
        if self.R_fade:
            if self.R_fade_up:
                if self.fade_tick:
                    self.background[0] += 1
                    self.fade_tick = False
                else:
                    self.fade_tick = True
            else:
                if self.fade_tick:
                    self.background[0] -= 1
                    self.fade_tick = False
                else:
                    self.fade_tick = True
            if self.background[0] == 0:
                self.R_fade_up = True
                self.R_fade = False
                self.G_fade = True
            if self.background[0] == 40:
                self.R_fade_up = False
                self.R_fade = False
                self.G_fade = True
        if self.G_fade:
            if  self.G_fade_up:
                if self.fade_tick:
                    self.background[1] += 1
                    self.fade_tick = False
                else:
                    self.fade_tick = True
            else:
                if self.fade_tick:
                    self.background[1] -= 1
                    self.fade_tick = False
                else:
                    self.fade_tick = True
            if self.background[1] == 0:
                self.G_fade_up = True
                self.G_fade = False
                self.B_fade = True
            if self.background[1] == 40:
                self.G_fade_up = False
                self.G_fade = False
                self.B_fade = True
        if self.B_fade:
            if self.B_fade_up:
                if self.fade_tick:
                    self.background[2] += 1
                    self.fade_tick = False
                else:
                    self.fade_tick = True
            else:
                if self.fade_tick:
                    self.background[2]  -= 1
                    self.fade_tick = False
                else:
                    self.fade_tick = True
            if self.background[2] == 0:
                self.B_fade_up = True
                self.B_fade = False
                self.R_fade = True
            if self.background[2] == 40:
                self.B_fade_up = False
                self.B_fade = False
                self.R_fade = True
        screen.fill(self.background)

class StarsMover:
    def __init__(self):
        self.stars1 = LoadImg("Stars.png", (STARS_WIDTH * STARS_SCALE, STARS_HEIGHT * STARS_SCALE))
        self.stars1_curpos_x, self.stars1_curpos_y = 0, 0
        self.stars2 = LoadImg("Stars.png", (STARS_WIDTH * STARS_SCALE, STARS_HEIGHT * STARS_SCALE))
        self.stars2_curpos_x, self.stars2_curpos_y = (STARS_WIDTH * STARS_SCALE), 0
    def move(self):
        # Move back to start
        if self.stars1_curpos_x <= STARS_EXITFRAME:
            self.stars1_curpos_x, self.stars1_curpos_y = (STARS_WIDTH * STARS_SCALE), 0
        if self.stars2_curpos_x <= STARS_EXITFRAME:
            self.stars2_curpos_x, self.stars2_curpos_y = (STARS_WIDTH * STARS_SCALE), 0
        # Do movement
        if "Right" in held_keys:
            self.stars1_curpos_x -= 4
            self.stars2_curpos_x -= 4
        elif "Left" in held_keys:
            self.stars1_curpos_x -= 2
            self.stars2_curpos_x -= 2
        else:
            self.stars1_curpos_x -= 3
            self.stars2_curpos_x -= 3
        # Flicker
        self.stars1.set_alpha(randint(170, 175))
        self.stars2.set_alpha(randint(170, 175))
        # Draw Stars
        screen.blit(self.stars1, [self.stars1_curpos_x, self.stars1_curpos_y])
        screen.blit(self.stars2, [self.stars2_curpos_x, self.stars2_curpos_y])

class HUD:
    def __init__(self):
        global point_count
        global level
        self.points_font = pygame.font.Font(IMG_DIR + "KodeMono.ttf", 20)
        self.pause_font = pygame.font.Font(IMG_DIR + "KodeMono.ttf", 40)
        self.levelstr = self.points_font.render("Level: ", True, (255, 255, 255))
        self.pointstr = self.points_font.render("Points: ", True, (255, 255, 255))
    def ShowPoints(self):
        self.points = self.points_font.render(str(point_count), True, (0, 255, 0))
        self.level = self.points_font.render(str(level), True, (0, 255, 0))
        screen.blit(self.pointstr, (10, 10))
        screen.blit(self.points, (self.pointstr.get_width() + 10, 10))
        screen.blit(self.levelstr, (width - (self.levelstr.get_width() + self.level.get_width() + 10), 10))
        screen.blit(self.level, (width - (self.level.get_width() + 10), 10))
    def Pause(self):
        screen.fill("white")
        screen.blit(self.pause_font.render("- PAUSED -", True, (0, 0, 0)), (width//2 - self.pause_font.size("- PAUSED -")[0]//2, height//2 - self.pause_font.size("- PAUSED -")[1]//2))
        pygame.display.flip()

class PlayerProjectile:
    def __init__(self, x, y, color, size_x, size_y, speed):
        self.rect = pygame.Rect(x, y, size_x, size_y)
        self.color = color
        self.speed = speed
    def update(self):
        self.rect.x += self.speed
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
    def check(self):
        for enemy in enemies:
            if self.rect.colliderect(enemy.hitbox):
                explosions.append(Explosion(enemy.rect.center, enemy.explosion_frames))
                global point_count
                point_count += enemy.points
                DifficultyCheck()
                if self in player_projectiles:
                    player_projectiles.remove(self)
                enemies.remove(enemy)
                ExplosionSound()

class EnemyProjectile:
    def __init__(self, x, y, color, size_x, size_y, speed):
        self.rect = pygame.Rect(x, y, size_x, size_y)
        self.color = color
        self.speed = speed
    def update(self):
        self.rect.x -= self.speed
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

class TargetedEnemyProjectile:
    def __init__(self, x, y, color, size_x, size_y,target_x, target_y, speed):
        self.rect = pygame.Rect(x, y, size_x, size_y)
        self.color = color
        dx = target_x - x
        dy = target_y - y
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        self.velocity_x = dx / distance * speed
        self.velocity_y = dy / distance * speed
    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

class Explosion:
    def __init__(self, center, frames, frame_delay=3, is_player=False):
        self.is_player = is_player
        self.frames = frames
        self.frame_index = 0
        self.tick = 0
        self.frame_delay = frame_delay
        self.rect = self.frames[0].get_rect(center=center)

    def update(self):
        self.tick += 1
        if self.tick >= self.frame_delay:
            self.tick = 0
            self.frame_index += 1
        if self.frame_index >= len(self.frames):
            explosions.remove(self)
            if self.is_player:
                GameOver()
    
    def draw(self):
        if self.frame_index < len(self.frames):
            screen.blit(self.frames[self.frame_index], self.rect)

class Arrow:
    def __init__(self, x, y, size, speed):
        self.explosion_frames = ARROW_EXPLOSION_FRAMES
        self.points = ARROW_POINTS
        self.sprite = ARROW_SPRITE
        self.flame = ARROW_FLAME
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.size_x = size[0]
        self.size_y = size[1]
        self.hitbox = self.rect.inflate(
            -self.rect.width * 0.1,
            -self.rect.height * 0.1
        )
        self.speed = speed
    def update(self):
        self.rect.x -= self.speed
        self.rect.y += randint(-1, 1)                           # Vertical wiggle
        self.flame.set_alpha(randint(150, 190))
        self.hitbox.center = self.rect.center
    def draw(self):
        screen.blit(self.sprite, self.rect)
        screen.blit(self.flame, (self.rect.x + self.size_x, self.rect.y))

class Yellow:
    def __init__(self, x, y, size, speed):
        self.explosion_frames = YELLOW_EXPLOSION_FRAMES
        self.points = YELLOW_POINTS
        self.sprite = YELLOW_SPRITE
        self.flame = YELLOW_FLAME
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.size_x = size[0]
        self.size_y = size[1]
        self.hitbox = self.rect.inflate(
            -self.rect.width * 0.1,
            -self.rect.height * 0.1
        )
        self.speed = speed
        self.shot_count = 0
        self.move_delay = 0
        if self.rect.y < height // 2:
            self.move_y = 1
        else:
            self.move_y = -1
    def update(self):
        self.move_delay += 1
        if self.move_delay == 2:
            self.rect.y += self.move_y
            self.move_delay = 0
        self.rect.x -= self.speed
        self.flame.set_alpha(randint(150, 190))
        self.hitbox.center = self.rect.center
        self.shoot()
    def draw(self):
        screen.blit(self.sprite, self.rect)
        screen.blit(self.flame, (self.rect.x + self.size_x * 0.875, self.rect.y))
    def shoot(self):
        self.shot_count += 1
        if self.shot_count == 90:
            enemy_projectiles.append(
                EnemyProjectile(
                    self.rect.x,                                # Projectile X in front of ship
                    self.rect.centery - self.size_y // 3,       # Projectile Y at middle of ship height
                    [255, 30, 30],                              # Projectile color
                    height // 50,
                    height // 105,
                    YELLOW_SHOT_SPEED                           # Projectile
                )
            )
            enemy_projectiles.append(
                EnemyProjectile(
                    self.rect.x,                                # Projectile X in front of ship
                    self.rect.centery + self.size_y // 3,       # Projectile Y at middle of ship height
                    [255, 30, 30],                              # Projectile color
                    height // 50,
                    height // 105,
                    YELLOW_SHOT_SPEED                           # Projectile
                )
            )
            pygame.mixer.Sound.play(choice(YELLOW_SHOOT_SOUNDS))
            self.shot_count = 0

class Grey:
    def __init__(self, x, y, size, speed):
        self.explosion_frames = GREY_EXPLOSION_FRAMES
        self.points = GREY_POINTS
        self.sprite = GREY_SPRITE
        self.flame = GREY_FLAME
        self.rect = self.sprite.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.size_x = size[0]
        self.size_y = size[1]
        self.hitbox = self.rect.inflate(
            -self.rect.width * 0.1,
            -self.rect.height * 0.1
        )
        self.speed = speed
        self.shot_count = 0
        self.move_delay = 0
        if self.rect.y < height // 2:
            self.move_y = 1
        else:
            self.move_y = -1
    def update(self):
        self.rect.x -= self.speed
        self.move_delay += 1
        if self.move_delay == 20:
            self.rect.y += self.move_y
            self.move_delay = 0
        self.flame.set_alpha(randint(150, 190))
        self.hitbox.center = self.rect.center
        if self.rect.x > ship_rect.x + ship_size_x * 3:
            self.shoot()
    def draw(self):
        screen.blit(self.sprite, self.rect)
        screen.blit(self.flame, (self.rect.x + self.size_x, self.rect.y))
    def shoot(self):
        self.shot_count += 1
        if self.shot_count == 100:
            enemy_projectiles.append(
                TargetedEnemyProjectile(
                    self.rect.x,                         # Projectile X in front of ship
                    self.rect.centery,
                    (50, 50, 255),
                    height // 60,
                    height // 60,
                    ship_rect.centerx,
                    ship_rect.centery,
                    GREY_SHOT_SPEED
                )
            )
            pygame.mixer.Sound.play(choice(YELLOW_SHOOT_SOUNDS))
            self.shot_count = 0

# -----------------------------------------------------------------------------------------------------------------------------

# Functions
def LoadImg(image, size):
    img_unscaled = pygame.image.load(IMG_DIR + image)
    img_unscaled.convert()
    img = pygame.transform.scale(img_unscaled, size) 
    return img

def LoadGame():
    if os.path.exists(SAVE_DIR + "save.lol"):
        with open((SAVE_DIR + "save.lol"), "r") as savefile:
            loaded_game = savefile.read()
            savefile.close()
            return int(loaded_game)
    else:
        if not os.path.exists(SAVE_DIR):
            os.mkdir(SAVE_DIR)
        return 0

def SaveGame():
    with open ((SAVE_DIR + "save.lol"), "w") as savefile:
        savefile.write(str(point_count))
        savefile.close()

def ClearFont():
    print(Style.RESET_ALL + "")

def GameExit(end_screen=-1):
    PlayMusic("gameover.ogg")
    if end_screen == -1:
        end_screen = LoadImg("EndScreen.png", (width, height))
    else:
        end_screen = LoadImg(end_screen, (width, height))
    screen.fill([255, 255, 255])
    screen.blit(end_screen, (0, 0))
    clock.tick(60)
    pygame.display.flip()
    time_end = time()
    clear()
    SaveGame()
    print(TEXT_YELLOW + "- GAME END -\n")
    print(TEXT_YELLOW + "Points collected:  " + TEXT_GREEN + str(point_count))
    print(TEXT_YELLOW + "Time survived:  " + TEXT_GREEN + str(int(time_end - time_start)) + " Seconds")
    if point_count > high_score:
            print(TEXT_GREEN + "New Highscore!")
            SaveGame()
    ClearFont()
    sleep(5)
    pygame.quit()
    sys.exit(0)

def GameOver():
    pygame.mixer.music.stop()
    screen.fill("red")
    pygame.display.flip()
    time_end = time()
    clear()
    print(TEXT_RED + "- GAME OVER -")
    print(TEXT_YELLOW + "Points collected:  " + TEXT_GREEN + str(point_count))
    print(TEXT_YELLOW + "Time survived:  " + TEXT_GREEN + str(int(time_end - time_start)) + " Seconds")
    if point_count > high_score:
            print(TEXT_GREEN + "New Highscore!")
            SaveGame()
    sleep(1)
    PlayMusic("gameover.ogg")
    ClearFont()
    end_screen = LoadImg("EndScreen.png", (width, height))
    screen.fill("white")
    screen.blit(end_screen, (0, 0))
    pygame.display.flip()
    # gameover_cycle = True
    # while gameover_cycle:
    #     sleep(0.1)
    #     background[1] += 5
    #     background[2] += 5
    #     screen.fill(background)
    #     screen.blit(end_screen, (0, 0))
    #     pygame.display.flip()
    #     if background[1] == 255:
    #         gameover_cycle = False
    sleep(5)
    pygame.quit()
    os._exit(0)

def PlayerDead():
    global game_over
    game_over = True
    explosions.append(Explosion(ship_rect.center, SHIP_EXPLOSION_FRAMES, SHIPEXP_FRAME_DELAY, is_player=True))
    ExplosionSound("player")

def PlayMusic(track, duration=-1):
    if track == "fadeout":
        pygame.mixer.music.fadeout(int(duration*1000))
    elif isinstance(track, int):
        pygame.mixer.music.load((SOUND_DIR + "Music\\" + MUSIC_PLAYLIST[track-1]))
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1, 0.0)
    elif isinstance(track, str):
        pygame.mixer.music.load((SOUND_DIR + "Music\\" + track))
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1, 0.0)

def PlayerShoot(projectile_mode):
    if projectile_mode == "normal":
        player_projectiles.append(
            PlayerProjectile(
                ship_rect.x + ship_size_x,          # Projectile X in front of ship
                ship_rect.y + ship_size_y // 2,     # Projectile Y at middle of ship height
                [25, 235, 255],                     # Projectile color light blue
                height // 100,                      # Projectile width a hundredth of screen height
                height // 100,
                PLAYER_SHOT_SPEED
            )
        )
        pygame.mixer.Sound.play(SHOOT_SOUND_NORMAL)

def ExplosionSound(type=-1):
    if type == "player":
        pygame.mixer.Sound.play(PLAYER_EXPLOSION_SOUND)
    else:
        pygame.mixer.Sound.play(choice(EXPLOSION_SOUNDS))

def SpawnArrow():
    enemies.append(
        Arrow(
            width,                                  # Arrow X on right side of screen
            randint(0, height - ARROW_SCALE[0]),    # Arrow Y somewhere on screen
            ARROW_SCALE,                            # Arrow size at ARROW_SCALE
            ARROW_SPEED                             # Arrow speed at ARROW_SPEED
        )
    )

def SpawnYellow():
    enemies.append(
        Yellow(
            width,
            randint(0, height - YELLOW_SCALE[0]),
            YELLOW_SCALE,
            YELLOW_SPEED
        )
    )

def SpawnGrey():
    enemies.append(
        Grey(
            width,
            randint(0, height - GREY_SCALE[0]),
            GREY_SCALE,
            GREY_SPEED
        )
    )

def EnemySpawner(enemy_type, spawn_rate):
    # increment the count for the enemy type
    EnemySpawner.cnt[enemy_type] += 1
    # if the count for the enemy type has reached the spawn rate, spawn the enemy and reset the count
    if EnemySpawner.cnt[enemy_type] == spawn_rate:
        if enemy_type == "arrow":
            SpawnArrow()
            EnemySpawner.cnt[enemy_type] = 0
        elif enemy_type == "yellow":
            SpawnYellow()
            EnemySpawner.cnt[enemy_type] = 0
        elif enemy_type == "grey":
            SpawnGrey()
            EnemySpawner.cnt[enemy_type] = 0

def LevelManager():
        global level
        global frame_counter
        if level == 10:
            pass
        elif level == 9:
            pass
        elif level == 8:
            pass
        elif level == 7:
            pass
        elif level == 6.5:
            LevelTransition(7)
        elif level == 6:
            pass
        elif level == 5.5:
            LevelTransition(6)
        elif level == 5:
            pass
        elif level == 4.5:
            LevelTransition(5)
        elif level == 4:
            EnemySpawner("arrow", 360)
            EnemySpawner("yellow", 150)
            EnemySpawner("grey", 180)
        elif level == 3.5:
            LevelTransition(4)
        elif level == 3:
            EnemySpawner("arrow", 180)
            EnemySpawner("grey", 90)
        elif level == 2.5:
            LevelTransition(3)
        elif level == 2:
            EnemySpawner("arrow", 180)
            EnemySpawner("yellow", 250)
        elif level == 1.5:
            LevelTransition(2)
        elif level == 1:
            EnemySpawner("arrow", 30)
        elif level == 0:
            frame_counter += 1
            if frame_counter == 150:
                level = 1
                frame_counter = 0

def LevelTransition(next_level):
    global frame_counter
    global level
    frame_counter += 1
    if frame_counter == 150:
        level = next_level
        frame_counter = 0
        PlayMusic(next_level)

def DifficultyCheck():
    global level
    global frame_counter
    if level == 10:
        pass
    elif level == 9.5:
        LevelTransition(10)
    elif level == 9:
        pass
    elif level == 8.5:
        LevelTransition(9)
    elif level == 8:
        pass
    elif level == 7.5:
        LevelTransition(8)
    elif level == 7:
        pass    
    elif level == 6.5:
        LevelTransition(7)
    elif level == 6:
        pass
    elif level == 5.5:
        LevelTransition(6)
    elif level == 5:
        pass
    elif level == 4:
        if point_count >= 1350:
            frame_counter = 0
            level = 4.5
            PlayMusic("fadeout", 2.5)
    elif level == 3:
        if point_count >= 800:
            frame_counter = 0
            level = 3.5
            PlayMusic("fadeout", 2.5)
    elif level == 2:
        if point_count >= 500:
            frame_counter = 0
            level = 2.5
            PlayMusic("fadeout", 2.5)
    elif level == 1:
        if point_count >= 200:
            frame_counter = 0
            level = 1.5
            PlayMusic("fadeout", 2.5)
    
# -----------------------------------------------------------------------------------------------------------------------------

# Enemy list
EnemySpawner.cnt = {}
for enemy in ["arrow", "yellow", "grey"]:
    EnemySpawner.cnt[enemy] = 0

# Enemy Sprites
ARROW_SPRITE = LoadImg("Arrow.png", ARROW_SCALE)
ARROW_FLAME = LoadImg("ArrowFlame.png", ARROW_SCALE)
YELLOW_SPRITE = LoadImg("YellowFighter.png", YELLOW_SCALE)
YELLOW_FLAME = LoadImg("YellowFlame.png", YELLOW_SCALE)
GREY_SPRITE = LoadImg("GreyFighter.png", GREY_SCALE)
GREY_FLAME = LoadImg("GreyFlame.png", GREY_SCALE)

# Explosion Frames
ARROW_EXPLOSION_SCALE = width//13, width//13
ARROW_EXPLOSION_FRAMES = [
    LoadImg("Explosions\\Arrow\\1.png", ARROW_EXPLOSION_SCALE),
    LoadImg("Explosions\\Arrow\\2.png", ARROW_EXPLOSION_SCALE),
    LoadImg("Explosions\\Arrow\\3.png", ARROW_EXPLOSION_SCALE),
    LoadImg("Explosions\\Arrow\\4.png", ARROW_EXPLOSION_SCALE)
]
SHIP_EXPLOSION_SCALE = width//10, width//10
SHIP_EXPLOSION_FRAMES = [
    LoadImg("Explosions\\Ship\\1.png", SHIP_EXPLOSION_SCALE),
    LoadImg("Explosions\\Ship\\2.png", SHIP_EXPLOSION_SCALE),
    LoadImg("Explosions\\Ship\\3.png", SHIP_EXPLOSION_SCALE),
    LoadImg("Explosions\\Ship\\4.png", SHIP_EXPLOSION_SCALE)
]
YELLOW_EXPLOSION_SCALE = width//12, width//12
YELLOW_EXPLOSION_FRAMES = [
    LoadImg("Explosions\\YellowFighter\\1.png", YELLOW_EXPLOSION_SCALE),
    LoadImg("Explosions\\YellowFighter\\2.png", YELLOW_EXPLOSION_SCALE),
    LoadImg("Explosions\\YellowFighter\\3.png", YELLOW_EXPLOSION_SCALE),
    LoadImg("Explosions\\YellowFighter\\4.png", YELLOW_EXPLOSION_SCALE)
]
GREY_EXPLOSION_SCALE = width//11, width//11
GREY_EXPLOSION_FRAMES = [
    LoadImg("Explosions\\Grey\\1.png", GREY_EXPLOSION_SCALE),
    LoadImg("Explosions\\Grey\\2.png", GREY_EXPLOSION_SCALE),
    LoadImg("Explosions\\Grey\\3.png", GREY_EXPLOSION_SCALE),
    LoadImg("Explosions\\Grey\\4.png", GREY_EXPLOSION_SCALE)
]

# Sounds
SHOOT_SOUND_NORMAL = pygame.mixer.Sound(SOUND_DIR + "Player\\shoot_normal.ogg")
EXPLOSION_SOUNDS = [
    pygame.mixer.Sound(SOUND_DIR + "Explosion\\1.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Explosion\\2.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Explosion\\3.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Explosion\\4.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Explosion\\5.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Explosion\\6.ogg")
]
PLAYER_EXPLOSION_SOUND = pygame.mixer.Sound(SOUND_DIR + "Player\\explode.ogg")
YELLOW_SHOOT_SOUNDS = [
    pygame.mixer.Sound(SOUND_DIR + "Yellow\\Shoot\\1.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Yellow\\Shoot\\2.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Yellow\\Shoot\\3.ogg"),
    pygame.mixer.Sound(SOUND_DIR + "Yellow\\Shoot\\4.ogg")
]

# Music List
MUSIC_PLAYLIST = [
    "1.ogg",
    "2.ogg",
    "3.ogg",
    "4.ogg",
    "5.ogg",
    "6.ogg",
    "7.ogg",
    "8.ogg"
    ]

# Variables
point_count = 0
level = 2.5                  # Game starts at this level
frame_counter = 0
game_over = False
firemode = "normal"
held_keys = []
player_projectiles = []
enemy_projectiles = []
enemies = []
explosions = []


# -----------------------------------------------------------------------------------------------------------------------------

# Background Fade init
background_fader = BackgroundFader()

# Stars Init
stars_mover = StarsMover()

# Game Init
clock = pygame.time.Clock()
last_shot = time()
shoot_delay = NORMAL_FIRERATE
time_start = time()
hud = HUD()

# Ship Init
ship = LoadImg("Ship_sideways.png", SHIP_SCALE)
ship_size_x, ship_size_y = ship.get_size()
ship_rect = ship.get_rect()
ship_rect.x, ship_rect.y = (ship_size_x * 2), height//2
ship_hitbox = ship_rect.inflate(- ship_size_x * 0.2, - ship_size_y * 0.2)
ship_velocity_x = 0
ship_velocity_y = 0

# Flame Init
flame = LoadImg("ThrusterFlame.png", FLAME_SCALE)
flame_size_x, flame_size_y = FLAME_SCALE
flame_rect = flame.get_rect()
flame_light = LoadImg("ThrusterFlame_light.png", FLAME_SCALE)
flame_light_size_x, flame_light_size_y = FLAME_SCALE
flame_light_rect = flame_light.get_rect()

# -----------------------------------------------------------------------------------------------------------------------------

# Start Game
pygame.display.set_icon(LoadImg("Grapyus.ico", (16, 16)))
PlayMusic("intro.ogg")
print(TEXT_GREEN + "\n- GAME START -")
running = True
high_score = LoadGame()
ClearFont()
start_screen = LoadImg("StartScreen.png", (width, height))
screen.fill([255, 255, 255])
screen.blit(start_screen, (0, 0))
pygame.display.flip()
clock.tick(60)
sleep(2)
time_start = time()
PlayMusic(1)

# -----------------------------------------------------------------------------------------------------------------------------

# Main Game Loop
while running:

    # Draw Background
    background_fader.fade()                                 # blit included
    stars_mover.move()                                     # blit included

    # -----------------------------------------------------------------------------------------------------------------------------

    # Keyboard Input
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            # Movement Keys
            if event.key == K_a:
                held_keys.append("Left")
            if event.key == K_d:
                held_keys.append("Right")
            if event.key == K_w:
                held_keys.append("Up")
            if event.key == K_s:
                held_keys.append("Down")
            # Action Keys
            if event.key == K_SPACE:
                held_keys.append("Space")
            # Exit Game
            if event.key == K_ESCAPE:
                GameExit()
            # Pause Game
            if event.key == K_TAB:
                paused = True
                hud.Pause()
                PlayMusic("fadeout", 0.5)
                while paused:
                    for event in pygame.event.get():
                        if event.type == KEYDOWN:
                            if event.key == K_TAB:
                                paused = False
                                pygame.mixer.music.play(-1, 0.0, 250)
                            if event.key == K_ESCAPE:
                                GameExit()
        elif event.type == KEYUP:
            # Movement
            if event.key == K_a:
                held_keys.remove("Left")
            if event.key == K_d:
                held_keys.remove("Right")
            if event.key == K_w:
                held_keys.remove("Up")
            if event.key == K_s:
                held_keys.remove("Down")
            # Action Keys
            if event.key == K_SPACE:
                held_keys.remove("Space")

    # -----------------------------------------------------------------------------------------------------------------------------

    # Actions
    if not game_over:

        # Movement
        ship_velocity_x, ship_velocity_y = 0, 0
        flame.set_alpha(0)
        flame_light.set_alpha(0)
        if "Up" in held_keys:
            ship_velocity_y -= MOVE_SPEED
            flame_light.set_alpha(randint(140, 160))
        if "Down" in held_keys:
            ship_velocity_y += MOVE_SPEED
            flame_light.set_alpha(randint(140, 160))
        if "Left" in held_keys:
            ship_velocity_x -= MOVE_SPEED
            flame_light.set_alpha(randint(60, 80))
        if "Right" in held_keys:
            ship_velocity_x += MOVE_SPEED
            flame.set_alpha(randint(170, 210))
            flame_light.set_alpha(0)
        elif "Up" not in held_keys and "Down" not in held_keys and "Left" not in held_keys:
            flame_light.set_alpha(randint(100, 120))
        ship_rect.x += ship_velocity_x
        ship_rect.y += ship_velocity_y
        if ship_rect.x <= 0:
            ship_rect.x = 0
        if ship_rect.y <=0:
            ship_rect.y = 0
        if ship_rect.x >= width - ship_size_x:
            ship_rect.x = width - ship_size_x
        if ship_rect.y >= height - ship_size_y:
            ship_rect.y = height - ship_size_y
        ship_hitbox.center = ship_rect.center

        if "Space" in held_keys:
            if time() - last_shot > shoot_delay:
                PlayerShoot(firemode)
                last_shot = time()

        # -----------------------------------------------------------------------------------------------------------------------------

        # Update Ship Thruster Flame
        flame_rect.midright = ship_rect.midleft
        flame_light_rect.midright = ship_rect.midleft

        # Update Ship
        screen.blit(ship, (ship_rect.x, ship_rect.y))
        screen.blit(flame, flame_rect)
        screen.blit(flame_light, flame_light_rect)

    # -----------------------------------------------------------------------------------------------------------------------------

    # Update Player Projectiles
    for projectile in player_projectiles[:]:
        projectile.update()
        projectile.draw()
        projectile.check()
        if projectile.rect.x > width:
            if projectile in player_projectiles:
                player_projectiles.remove(projectile)
    
    # Update Enemies
    for enemy in enemies[:]:
        enemy.update()
        enemy.draw()
        if enemy.rect.x < (0 - enemy.size_x) or enemy.rect.y < (0 - enemy.size_y) or enemy.rect.y > height:
            enemies.remove(enemy)
        if enemy.hitbox.colliderect(ship_hitbox):
            PlayerDead()
    
    # Update Enemy Projectiles
    for projectile in enemy_projectiles[:]:
        projectile.update()
        projectile.draw()
        if projectile.rect.colliderect(ship_hitbox):
            PlayerDead()
            enemy_projectiles.remove(projectile)

    # Update Explosions
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw()

    # -----------------------------------------------------------------------------------------------------------------------------

    # Spawn Enemies
    if not game_over:
        LevelManager()

    # -----------------------------------------------------------------------------------------------------------------------------

    hud.ShowPoints()
    pygame.display.flip()
    clock.tick(60)

    # -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
