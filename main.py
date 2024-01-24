from pyray import *
import random

WIDTH  = 448
HEIGHT = 512
TARGET_FPS = 60
DRAW_FPS=True
init_window(WIDTH, HEIGHT, 'Space Invaders')
# set_target_fps(TARGET_FPS) # Uncomment to limit FPS to TARGET_FPS

gameState='menu'

ICON = load_image("Sprites/Icon.png")
set_window_icon(ICON)

PLAYER_IMAGE = load_texture("Sprites/Player.png")
SMALL_ALIEN_IMAGE_0 = load_texture("Sprites/Small Alien.png")
SMALL_ALIEN_IMAGE_1 = load_texture("Sprites/Small Alien Anim.png")
MEDIUM_ALIEN_IMAGE_0 = load_texture("Sprites/Medium Alien.png")
MEDIUM_ALIEN_IMAGE_1 = load_texture("Sprites/Medium Alien Anim.png")
LARGE_ALIEN_IMAGE_0 = load_texture("Sprites/Large Alien.png")
LARGE_ALIEN_IMAGE_1 = load_texture("Sprites/Large Alien Anim.png")

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

PLAYER_SPEED=220
BULLET_SPEED=500

ALIEN_HORIZONTAL_STEP=5
ALIEN_VERTICAL_STEP=20
ALIEN_MOVE_DELAY=0.65

level=1

alienDirection=1 # positive=move right  negative=move left
alienMoveTimer=0.0
alienAnimation = 0
alienSpeedMultiplier = 1

enemies = []
bullets = []

def AABB(x1, y1, w1, h1, x2, y2, w2, h2):
    return x1<x2+w2 and x1+w1>x2 and y1<y2+h2 and y1+h1>y2

def countEnemies():
    count = 0
    for i in range(len(enemies)):
        for j in range(len(enemies[i])):
            count += 1
    return count

class Bullet():
    def __init__(self, x, y, shooter):
        self.x=x
        self.y=y
        self.w=2
        self.h=8
        self.speed=BULLET_SPEED
        self.shooter=shooter # Who fired the bullet, player or alien

    def move(self):
        if self.shooter=='player':
            self.y-=self.speed*get_frame_time()
        else:
            self.y+=self.speed*get_frame_time()
    
    def die(self):
        if self.y<-self.h or self.y>HEIGHT:
            bullets.remove(self)

class Enemy():
    def __init__(self, x, y, size):
        self.x=x
        self.y=y
        self.w=24
        self.h=16
        self.size=size # Size is only visual, hitboxes are the same for all sizes
        self.shootDelay = 100 if random.random()>0.5 else (random.random()+10-level)*4
        self.shootTimer=random.random()*self.shootDelay/2

    def shoot(self):
        self.shootTimer+=get_frame_time()

        if self.shootTimer>=self.shootDelay:
            bullets.append(Bullet(int(self.x+self.w/2), self.y, 'alien'))
            self.shootTimer=0.0

    def hurt(self):
        for bullet in bullets:
            if bullet.shooter=='player':
                if AABB(self.x, self.y, self.w, self.h, bullet.x, bullet.y, bullet.w, bullet.h):
                    for row in enemies:
                        try:
                            row.remove(self)
                        except:
                            pass
                    bullets.remove(bullet)

class Player():
    def __init__(self):
        self.x=int(WIDTH/2)
        self.y=432
        self.w=26
        self.h=16
        self.speed=PLAYER_SPEED
        self.lives=3
        self.respawnTimer=1.0

    def move(self):
        if is_key_down(KeyboardKey.KEY_LEFT):
            self.x-=self.speed*get_frame_time()
        if is_key_down(KeyboardKey.KEY_RIGHT):
            self.x+=self.speed*get_frame_time()
        
        if self.x<0:
            self.x=0
        if self.x>WIDTH-self.w:
            self.x=WIDTH-self.w

    def shoot(self):
        bulletAlive=False
        for bullet in bullets:
            if bullet.shooter=='player':
                bulletAlive=True

        if is_key_pressed(KeyboardKey.KEY_UP) and not bulletAlive:
            bullets.append(Bullet(self.x+self.w//2, self.y, 'player'))

    def hurt(self):
        for bullet in bullets:
            if AABB(self.x, self.y, self.w, self.h, bullet.x, bullet.y, bullet.w, bullet.h) and not bullet.shooter=='player':
                bullets.remove(bullet)
                self.lives-=1
                self.respawnTimer=0.0
        if self.respawnTimer<1:
            self.x=-2000
player=Player()

def spawnEnemies():
    for y in range(5):
        enemies.append([])
        for x in range(11):
            enemies[y].append(Enemy(x * 34 + 40, y * 34 + 50, min(2, (y + 1) // 2)))

def levelUp():
    global alienSpeedMultiplier, level

    level+=1
    alienSpeedMultiplier+=0.25

    wait_time(1)
    spawnEnemies()

def moveEnemies():
    global alienMoveTimer, alienAnimation, alienDirection

    if alienMoveTimer>=ALIEN_MOVE_DELAY*(countEnemies()/55/2+0.5):
        for row in enemies:
            for enemy in row:
                enemy.x+=ALIEN_HORIZONTAL_STEP*alienDirection*alienSpeedMultiplier
        alienAnimation=0 if alienAnimation else 1
        alienMoveTimer=0.0

    for row in enemies:
        for enemy in row:
            if enemy.x<10 and alienDirection<0 or enemy.x>WIDTH-enemy.w-10 and alienDirection>0:
                alienDirection=-alienDirection
                for row in enemies:
                    for enemy in row:
                        enemy.x+=ALIEN_HORIZONTAL_STEP*alienDirection*alienSpeedMultiplier
                        enemy.y+=ALIEN_VERTICAL_STEP

def render():
    global SMALL_ALIEN_IMAGE_0
    global SMALL_ALIEN_IMAGE_1
    global MEDIUM_ALIEN_IMAGE_0
    global MEDIUM_ALIEN_IMAGE_1
    global LARGE_ALIEN_IMAGE_0
    global LARGE_ALIEN_IMAGE_1
    global alienAnimation

    begin_drawing()
    clear_background(BLACK)

    match gameState:
        case 'game':
            for bullet in bullets:
                draw_rectangle(round(bullet.x), round(bullet.y), bullet.w, bullet.h, WHITE)
            
            draw_texture(PLAYER_IMAGE, round(player.x), round(player.y), WHITE)
            
            for i in range(len(enemies)):
                for j in range(len(enemies[i])):
                    match(enemies[i][j].size):
                        case 0:
                            draw_texture(eval(f'SMALL_ALIEN_IMAGE_{alienAnimation}'), round(enemies[i][j].x), round(enemies[i][j].y), WHITE)
                        case 1:
                            draw_texture(eval(f'MEDIUM_ALIEN_IMAGE_{alienAnimation}'), round(enemies[i][j].x), round(enemies[i][j].y), WHITE)
                        case 2:
                            draw_texture(eval(f'LARGE_ALIEN_IMAGE_{alienAnimation}'), round(enemies[i][j].x), round(enemies[i][j].y), WHITE)

            for i in range(player.lives - 1):
                draw_texture(PLAYER_IMAGE, 6 + i*32, HEIGHT-24, (255, 255, 255, 125))

        case 'menu':
            draw_text('Space Invaders', int(WIDTH / 2 - measure_text('Space Invaders', 40) / 2), 40, 40, WHITE)
            draw_text('PRESS UP-ARROW TO BEGIN', int(WIDTH / 2 - measure_text('PRESS UP-ARROW TO BEGIN', 20) / 2), 100, 20, (75, 75, 75, 255))

    draw_text(f'FPS {get_fps()}' if DRAW_FPS else '', 2, 1, 10, WHITE)
    end_drawing()

def main():
    global alienMoveTimer
    global gameState
    while not window_should_close():
        match gameState:
            case 'game':
                if countEnemies() == 0:
                    levelUp()

                player.move()
                player.shoot()
                player.hurt()
                player.respawnTimer+=get_frame_time()

                moveEnemies()
                for row in enemies:
                    for enemy in row:
                        enemy.shoot()
                        enemy.hurt()
                alienMoveTimer+=get_frame_time()

                for bullet in bullets:
                    bullet.move()
                    bullet.die()

                if player.lives<=0:
                    gameState='menu'
                
            case 'menu':
                if is_key_down(KeyboardKey.KEY_UP):
                    gameState='game'
                    spawnEnemies()
                    player.lives=3

        render()

if __name__ == "__main__":
    main()
