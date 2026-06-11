import pygame
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 120, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake - Juego Nuevo')
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 24)


def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (40, 40, 40), (0, y), (WIDTH, y))


def draw_snake(snake):
    for cell in snake:
        pygame.draw.rect(screen, GREEN, (cell[0] * CELL_SIZE, cell[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_food(food):
    pygame.draw.rect(screen, RED, (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def draw_score(score):
    text = font.render(f'Puntos: {score}', True, WHITE)
    screen.blit(text, (10, 10))


def place_food(snake):
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        if (x, y) not in snake:
            return (x, y)


def game_over_screen(score):
    screen.fill(BLACK)
    msg = font.render('Fin del juego', True, BLUE)
    score_text = font.render(f'Tu puntaje: {score}', True, WHITE)
    restart_text = font.render('Presiona R para jugar otra vez', True, WHITE)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 80))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 40))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()


def main():
    snake = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2), (COLS // 2 - 2, ROWS // 2)]
    direction = (1, 0)
    food = place_food(snake)
    score = 0
    speed = 10
    running = True
    paused = False
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_r:
                    return main()
                if not game_over:
                    if event.key == pygame.K_UP and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key == pygame.K_DOWN and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key == pygame.K_LEFT and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                        direction = (1, 0)
                    elif event.key == pygame.K_p:
                        paused = not paused

        if not paused and not game_over:
            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
            if (
                new_head[0] < 0 or new_head[0] >= COLS or
                new_head[1] < 0 or new_head[1] >= ROWS or
                new_head in snake
            ):
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    food = place_food(snake)
                    if score % 5 == 0:
                        speed = min(20, speed + 1)
                else:
                    snake.pop()

        screen.fill(BLACK)
        draw_grid()
        draw_food(food)
        draw_snake(snake)
        draw_score(score)

        if paused:
            pause_text = font.render('Pausado - P para continuar', True, BLUE)
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 12))
        if game_over:
            game_over_screen(score)
        else:
            pygame.display.flip()

        clock.tick(speed)

    pygame.quit()


if __name__ == '__main__':
    main()
