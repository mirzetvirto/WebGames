import pygame
import random
import numpy as np

pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    pygame.mixer.set_num_channels(16)
except pygame.error:
    pass

# Audio helpers
SAMPLE_RATE = 44100


def make_sound(frequency, duration=0.18, volume=0.2):
    if pygame.mixer.get_init() is None:
        return None
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.sin(2 * np.pi * frequency * t)
    envelope = np.linspace(0.0, 1.0, len(wave)) * np.linspace(1.0, 0.0, len(wave))
    wave = wave * envelope * volume
    samples = np.int16(wave * 32767)
    stereo = np.column_stack((samples, samples))
    return pygame.sndarray.make_sound(stereo)


def make_chord(frequencies, duration=0.3, volume=0.2):
    if pygame.mixer.get_init() is None:
        return None
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.zeros_like(t)
    for freq in frequencies:
        wave += np.sin(2 * np.pi * freq * t)
    wave /= len(frequencies)
    envelope = np.linspace(0.0, 1.0, len(wave)) * np.linspace(1.0, 0.0, len(wave))
    wave = wave * envelope * volume
    samples = np.int16(wave * 32767)
    stereo = np.column_stack((samples, samples))
    return pygame.sndarray.make_sound(stereo)


def make_background_loop():
    if pygame.mixer.get_init() is None:
        return None
    notes = [220, 246, 261, 294, 329, 349, 392, 440]
    piece = []
    for i, freq in enumerate(notes):
        duration = 0.18
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
        tone = np.sin(2 * np.pi * freq * t) * np.linspace(0.0, 1.0, len(t)) * np.linspace(1.0, 0.0, len(t))
        piece.append(tone)
    wave = np.concatenate(piece)
    wave = wave * 0.18
    samples = np.int16(wave * 32767)
    stereo = np.column_stack((samples, samples))
    return pygame.sndarray.make_sound(stereo)

# Game settings
WIDTH, HEIGHT = 300, 600
ROWS, COLS = 20, 10
CELL_SIZE = WIDTH // COLS
TOP_LEFT_X = 50
TOP_LEFT_Y = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BOMB_COLOR = (200, 200, 0)
COLORS = [
    (0, 255, 255),
    (0, 0, 255),
    (255, 165, 0),
    (255, 255, 0),
    (0, 255, 0),
    (128, 0, 128),
    (255, 0, 0),
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[2, 2, 0], [0, 2, 2]],
    [[0, 3, 3], [3, 3, 0]],
    [[4, 4], [4, 4]],
    [[5, 0, 0], [5, 5, 5]],
    [[0, 0, 6], [6, 6, 6]],
    [[7, 7, 7], [0, 7, 0]],
]

class Piece:
    def __init__(self, x, y, shape, is_bomb=False):
        self.x = x
        self.y = y
        self.shape = shape
        self.is_bomb = is_bomb
        if is_bomb:
            self.color = BOMB_COLOR
        else:
            self.color = COLORS[SHAPES.index(shape)]

    def image(self):
        return self.shape

    def rotate(self):
        if not self.is_bomb:
            self.shape = [
                [self.shape[len(self.shape) - j - 1][i] for j in range(len(self.shape))]
                for i in range(len(self.shape[0]))
            ]


def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for row in range(ROWS):
        for col in range(COLS):
            if (col, row) in locked_positions:
                grid[row][col] = locked_positions[(col, row)]
    return grid


def convert_shape_format(piece):
    positions = []
    shape = piece.image()
    if not shape:
        return positions
    if isinstance(shape[0], int):
        shape = [shape]
    for i, line in enumerate(shape):
        if isinstance(line, int):
            row = [line]
        else:
            row = list(line)
        for j, column in enumerate(row):
            if column != 0:
                positions.append((piece.x + j, piece.y + i))
    return positions


def valid_space(piece, grid):
    accepted_positions = [(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == BLACK]
    formatted = convert_shape_format(piece)
    for pos in formatted:
        x, y = pos
        if y < 0:
            continue
        if x < 0 or x >= COLS or y >= ROWS or (x, y) not in accepted_positions:
            return False
    return True


def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    if random.random() < 0.1:
        return Piece(COLS // 2 - 1, -2, [[8]], is_bomb=True)
    shape = random.choice(SHAPES)
    shape = [row.copy() for row in shape]
    return Piece(COLS // 2 - len(shape[0]) // 2, -2, shape)


def explode_bomb(x, y, locked):
    removed = 0
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if (nx, ny) in locked:
                    del locked[(nx, ny)]
                    removed += 1
    return removed * 50


def clear_rows(grid, locked):
    cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            for j in range(COLS):
                locked.pop((j, i), None)
        elif cleared > 0:
            for j in range(COLS):
                if (j, i) in locked:
                    locked[(j, i + cleared)] = locked.pop((j, i))
    return cleared


def draw_grid(surface, grid):
    for i in range(ROWS):
        pygame.draw.line(surface, GRAY, (TOP_LEFT_X, TOP_LEFT_Y + i * CELL_SIZE), (TOP_LEFT_X + WIDTH, TOP_LEFT_Y + i * CELL_SIZE))
        for j in range(COLS):
            pygame.draw.line(surface, GRAY, (TOP_LEFT_X + j * CELL_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j * CELL_SIZE, TOP_LEFT_Y + HEIGHT))


def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', 1, WHITE)
    surface.blit(label, (TOP_LEFT_X + WIDTH + 20, TOP_LEFT_Y))

    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j],
                             (TOP_LEFT_X + j * CELL_SIZE, TOP_LEFT_Y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

    draw_grid(surface, grid)
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, WIDTH, HEIGHT), 5)


def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 25)
    label = font.render('Next:', 1, WHITE)
    start_x = TOP_LEFT_X + WIDTH + 20
    start_y = TOP_LEFT_Y + 80
    surface.blit(label, (start_x, start_y))
    shape = piece.image()

    for i, line in enumerate(shape):
        for j, column in enumerate(line):
            if column != 0:
                pygame.draw.rect(surface, piece.color,
                                 (start_x + j * CELL_SIZE, start_y + 30 + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)


def main():
    win = pygame.display.set_mode((WIDTH + 250, HEIGHT + 100))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0

    locked_positions = {}
    grid = create_grid(locked_positions)

    current_piece = get_shape()
    next_piece = get_shape()
    change_piece = False
    run = True

    rotate_sound = make_sound(880, 0.08, 0.18)
    lock_sound = make_chord([220, 330], 0.12, 0.18)
    clear_sound = make_chord([440, 660, 880], 0.2, 0.22)
    drop_sound = make_sound(330, 0.08, 0.18)
    background = make_background_loop()
    if background:
        background.play(loops=-1)

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 10:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.02

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()
                        current_piece.rotate()
                        current_piece.rotate()
                    if rotate_sound:
                        rotate_sound.play()
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                    if drop_sound:
                        drop_sound.play()

        shape_pos = convert_shape_format(current_piece)
        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            if current_piece.is_bomb:
                bomb_score = explode_bomb(shape_pos[0][0], shape_pos[0][1], locked_positions)
                score += bomb_score
                if clear_sound:
                    clear_sound.play()
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            cleared = clear_rows(grid, locked_positions)
            score += cleared * 100
            if cleared > 0 and clear_sound:
                clear_sound.play()
            elif lock_sound:
                lock_sound.play()

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
