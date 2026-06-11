import os
import random

import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 640, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Space Invaders - Juego de Aliens')
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont('arial', 28)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 240)
PURPLE = (190, 0, 255)

PLAYER_SIZE = 50
ALIEN_SIZE = 40
BULLET_SIZE = 6
POWERUP_SIZE = 24
POWERUP_FALL_SPEED = 3
POWERUP_TYPES = ['vida', 'rapido', 'puntos']
MUSIC_FILE = os.path.join(BASE_DIR, 'musica_aliens1.mp3')
MUSIC_LOADED = False

class Player:
    def __init__(self):
        self.x = WIDTH // 2 - PLAYER_SIZE // 2
        self.y = HEIGHT - PLAYER_SIZE - 20
        self.speed = 7
        self.lives = 5
        self.max_bullets = 3
        self.rapid_fire_timer = 0
        self.powerup_name = ''

    def draw(self):
        pygame.draw.rect(SCREEN, BLUE, (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE // 2))
        pygame.draw.polygon(SCREEN, BLUE, [
            (self.x + PLAYER_SIZE // 2, self.y - PLAYER_SIZE // 2),
            (self.x + 10, self.y),
            (self.x + PLAYER_SIZE - 10, self.y)
        ])
        if self.rapid_fire_timer > 0:
            pygame.draw.rect(SCREEN, (180, 180, 255), (self.x - 4, self.y - 8, PLAYER_SIZE + 8, PLAYER_SIZE // 2 + 12), 2)

    def move(self, dx):
        self.x = max(0, min(WIDTH - PLAYER_SIZE, self.x + dx * self.speed))

class Alien:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

    def draw(self):
        pygame.draw.rect(SCREEN, GREEN, (self.x, self.y, ALIEN_SIZE, ALIEN_SIZE))
        pygame.draw.rect(SCREEN, BLACK, (self.x + 8, self.y + 10, 8, 8))
        pygame.draw.rect(SCREEN, BLACK, (self.x + 24, self.y + 10, 8, 8))
        pygame.draw.rect(SCREEN, BLACK, (self.x + 14, self.y + 24, 12, 8))

class Boss:
    def __init__(self, level):
        self.width = 140
        self.height = 70
        self.x = WIDTH // 2 - self.width // 2
        self.y = 70
        self.health = 8 + (level // 5) * 3
        self.alive = True
        self.level = level

    def draw(self):
        pygame.draw.rect(SCREEN, RED, (self.x, self.y, self.width, self.height), border_radius=10)
        pygame.draw.rect(SCREEN, BLACK, (self.x + 10, self.y + 10, self.width - 20, self.height - 20), border_radius=8)

        bar_width = self.width - 40
        bar_height = 12
        bar_x = self.x + 20
        bar_y = self.y + self.height + 10
        health_ratio = max(0, self.health) / max(1, 8 + (self.level // 5) * 3)
        fill_width = int(bar_width * health_ratio)

        pygame.draw.rect(SCREEN, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=6)
        pygame.draw.rect(SCREEN, BLACK, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        pygame.draw.rect(SCREEN, GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=5)

        health_text = FONT.render(f'Jefe: {self.health}', True, YELLOW)
        text_x = self.x + self.width // 2 - health_text.get_width() // 2
        SCREEN.blit(health_text, (text_x, bar_y + bar_height + 6))

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False

class Minion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.alive = True

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, (self.x, self.y, ALIEN_SIZE, ALIEN_SIZE), border_radius=6)
        pygame.draw.rect(SCREEN, BLACK, (self.x + 8, self.y + 10, 8, 8))
        pygame.draw.rect(SCREEN, BLACK, (self.x + 24, self.y + 10, 8, 8))
        pygame.draw.rect(SCREEN, BLACK, (self.x + 14, self.y + 24, 12, 8))

    def update(self, dx):
        self.x += dx

class Bullet:
    def __init__(self, x, y, dy, color=YELLOW):
        self.x = x
        self.y = y
        self.dy = dy
        self.color = color

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, (self.x, self.y, BULLET_SIZE, BULLET_SIZE * 3))

    def update(self):
        self.y += self.dy
        return 0 <= self.y <= HEIGHT

class PowerUp:
    def __init__(self, x, y, type_name):
        self.x = x
        self.y = y
        self.type_name = type_name
        self.color = GREEN if type_name == 'vida' else BLUE if type_name == 'rapido' else YELLOW

    def draw(self):
        pygame.draw.rect(SCREEN, self.color, (self.x, self.y, POWERUP_SIZE, POWERUP_SIZE))
        symbol = '+' if self.type_name == 'vida' else '>' if self.type_name == 'rapido' else '$'
        label = FONT.render(symbol, True, BLACK)
        SCREEN.blit(label, (self.x + 6, self.y + 1))

    def update(self):
        self.y += POWERUP_FALL_SPEED
        return self.y <= HEIGHT


def draw_text(text, x, y, color=WHITE):
    render = FONT.render(text, True, color)
    SCREEN.blit(render, (x, y))


def create_aliens(rows=4, cols=8):
    aliens = []
    start_x = 60
    start_y = 80
    gap_x = 70
    gap_y = 60
    for row in range(rows):
        for col in range(cols):
            aliens.append(Alien(start_x + col * gap_x, start_y + row * gap_y))
    return aliens


def create_boss(level):
    return Boss(level)


def create_boss_minions(boss):
    colors = [ORANGE, CYAN, PURPLE]
    offsets = [-80, 0, 80]
    minions = []
    for index, offset in enumerate(offsets):
        minions.append(Minion(boss.x + boss.width // 2 + offset - ALIEN_SIZE // 2, boss.y + boss.height + 20, colors[index]))
    return minions


def main():
    global MUSIC_LOADED
    if os.path.exists(MUSIC_FILE):
        try:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            MUSIC_LOADED = True
        except pygame.error as e:
            print('Error cargando musica:', e)
            MUSIC_LOADED = False
    else:
        print('Archivo de musica no encontrado:', MUSIC_FILE)
        MUSIC_LOADED = False

    player = Player()
    aliens = create_aliens()
    boss = None
    boss_minions = []
    bullets = []
    alien_bullets = []
    powerups = []
    alien_direction = 1
    alien_speed = 0.8
    boss_direction = 1
    boss_speed = 1.5
    level = 1
    score = 0
    running = True
    game_over = False

    while running:
        CLOCK.tick(60)
        SCREEN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return main()
                if not game_over:
                    if event.key == pygame.K_SPACE and len(bullets) < player.max_bullets:
                        speed = -12 if player.rapid_fire_timer > 0 else -8
                        bullets.append(Bullet(player.x + PLAYER_SIZE // 2 - BULLET_SIZE // 2, player.y, speed))

        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT]:
                player.move(-1)
            if keys[pygame.K_RIGHT]:
                player.move(1)

        if not game_over:
            alive_aliens = [alien for alien in aliens if alien.alive]
            boss_alive = boss and boss.alive
            minions_alive = any(minion.alive for minion in boss_minions) if boss else False
            if boss_alive:
                if boss.x <= 20 and boss_direction == -1:
                    boss_direction = 1
                elif boss.x + boss.width >= WIDTH - 20 and boss_direction == 1:
                    boss_direction = -1
                boss.x += boss_direction * boss_speed
                for minion in boss_minions:
                    if minion.alive:
                        minion.update(boss_direction * boss_speed)
                        if random.random() < min(0.005, 0.001 + level * 0.0003):
                            alien_bullets.append(Bullet(minion.x + ALIEN_SIZE // 2, minion.y + ALIEN_SIZE, 5, RED))
                if random.random() < min(0.015, 0.002 + level * 0.0005):
                    alien_bullets.append(Bullet(boss.x + boss.width // 2, boss.y + boss.height, 6, RED))
                if boss.y + boss.height >= player.y:
                    game_over = True
            elif minions_alive:
                for minion in boss_minions:
                    if minion.alive:
                        minion.update(boss_direction * boss_speed)
                        if random.random() < min(0.005, 0.001 + level * 0.0003):
                            alien_bullets.append(Bullet(minion.x + ALIEN_SIZE // 2, minion.y + ALIEN_SIZE, 5, RED))
            elif alive_aliens:
                min_x = min(alien.x for alien in alive_aliens)
                max_x = max(alien.x for alien in alive_aliens)
                if max_x + ALIEN_SIZE >= WIDTH - 20 and alien_direction == 1:
                    alien_direction = -1
                    for alien in alive_aliens:
                        alien.y += 20
                elif min_x <= 20 and alien_direction == -1:
                    alien_direction = 1
                    for alien in alive_aliens:
                        alien.y += 20
                for alien in alive_aliens:
                    alien.x += alien_direction * alien_speed
                    if random.random() < min(0.008, 0.001 + level * 0.0003):
                        alien_bullets.append(Bullet(alien.x + ALIEN_SIZE // 2, alien.y + ALIEN_SIZE, 5, RED))
                    if alien.y + ALIEN_SIZE >= player.y:
                        game_over = True
            else:
                if boss is None and level % 5 == 0:
                    boss = create_boss(level)
                    boss_minions = create_boss_minions(boss)
                    bullets = []
                    alien_bullets = []
                    powerups = []
                else:
                    level += 1
                    boss = None
                    boss_minions = []
                    alien_speed = min(4, alien_speed + 0.3)
                    aliens = create_aliens()
                    bullets = []
                    alien_bullets = []
                    powerups = []

        bullets = [bullet for bullet in bullets if bullet.update()]
        powerups = [powerup for powerup in powerups if powerup.update()]
        alien_bullets = [bullet for bullet in alien_bullets if bullet.update()]

        for bullet in bullets[:]:
            if boss and boss.alive and boss.x < bullet.x < boss.x + boss.width and boss.y < bullet.y < boss.y + boss.height:
                boss.hit()
                if bullet in bullets:
                    bullets.remove(bullet)
                score += 50
                if not boss.alive and random.random() < 0.75:
                    powerups.append(PowerUp(boss.x + boss.width // 2 - POWERUP_SIZE // 2, boss.y + boss.height, random.choice(POWERUP_TYPES)))
                continue
            for minion in boss_minions:
                if minion.alive and minion.x < bullet.x < minion.x + ALIEN_SIZE and minion.y < bullet.y < minion.y + ALIEN_SIZE:
                    minion.alive = False
                    if bullet in bullets:
                        bullets.remove(bullet)
                    score += 20
                    if random.random() < 0.35:
                        powerups.append(PowerUp(minion.x + ALIEN_SIZE // 2 - POWERUP_SIZE // 2, minion.y + ALIEN_SIZE, random.choice(POWERUP_TYPES)))
                    break
            else:
                for alien in aliens:
                    if alien.alive and alien.x < bullet.x < alien.x + ALIEN_SIZE and alien.y < bullet.y < alien.y + ALIEN_SIZE:
                        alien.alive = False
                        if bullet in bullets:
                            bullets.remove(bullet)
                        score += 10
                        if random.random() < 0.35:
                            powerups.append(PowerUp(alien.x + ALIEN_SIZE // 2 - POWERUP_SIZE // 2, alien.y + ALIEN_SIZE, random.choice(POWERUP_TYPES)))
                        break

        for bullet in alien_bullets[:]:
            if player.x < bullet.x < player.x + PLAYER_SIZE and player.y < bullet.y < player.y + PLAYER_SIZE:
                alien_bullets.remove(bullet)
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True

        for powerup in powerups[:]:
            if player.x < powerup.x + POWERUP_SIZE and player.x + PLAYER_SIZE > powerup.x and player.y < powerup.y + POWERUP_SIZE and player.y + PLAYER_SIZE > powerup.y:
                powerups.remove(powerup)
                if powerup.type_name == 'vida':
                    player.lives += 1
                    player.powerup_name = 'Vida +1'
                elif powerup.type_name == 'rapido':
                    player.rapid_fire_timer = 600
                    player.max_bullets = 5
                    player.powerup_name = 'Disparo rapido'
                elif powerup.type_name == 'puntos':
                    score += 50
                    player.powerup_name = 'Puntos bonus'

        if player.rapid_fire_timer > 0:
            player.rapid_fire_timer -= 1
            if player.rapid_fire_timer <= 0:
                player.max_bullets = 3
                player.powerup_name = ''

        player.draw()
        if boss and boss.alive:
            boss.draw()
        for minion in boss_minions:
            if minion.alive:
                minion.draw()
        for alien in aliens:
            if alien.alive:
                alien.draw()
        for bullet in bullets:
            bullet.draw()
        for bullet in alien_bullets:
            bullet.draw()
        for powerup in powerups:
            powerup.draw()

        draw_text(f'Puntaje: {score}', 20, 20)
        draw_text(f'Nivel: {level}', WIDTH // 2 - 50, 20)
        draw_text(f'Vidas: {player.lives}', WIDTH - 150, 20)
        if player.powerup_name:
            draw_text(f'Power-up: {player.powerup_name}', WIDTH // 2 - 100, 50, YELLOW)
        if not MUSIC_LOADED:
            draw_text('Musica no disponible', WIDTH // 2 - 120, 80, RED)

        if game_over:
            draw_text('GAME OVER', WIDTH // 2 - 100, HEIGHT // 2 - 40, RED)
            draw_text('Presiona R para reiniciar', WIDTH // 2 - 180, HEIGHT // 2 + 10, WHITE)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
