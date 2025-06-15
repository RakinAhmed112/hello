import pygame
import random

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = SCREEN_WIDTH // BLOCK_SIZE
ROWS = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],                                # I
    [[1, 0, 0], [1, 1, 1]],                        # J
    [[0, 0, 1], [1, 1, 1]],                        # L
    [[1, 1], [1, 1]],                              # O
    [[0, 1, 1], [1, 1, 0]],                        # S
    [[0, 1, 0], [1, 1, 1]],                        # T
    [[1, 1, 0], [0, 1, 1]],                        # Z
]

# Game classes
class Piece:
    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    for i, row in enumerate(piece.shape):
        for j, val in enumerate(row):
            if val:
                positions.append((piece.x + j, piece.y + i))
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(x, y) for x in range(COLUMNS) if grid[y][x] == BLACK] for y in range(ROWS)]
    accepted_positions = [pos for row in accepted_positions for pos in row]
    formatted = convert_shape_format(piece)
    return all(pos in accepted_positions and pos[1] >= 0 for pos in formatted)

def check_lost(positions):
    return any(y < 1 for _, y in positions)

def clear_rows(grid, locked):
    lines_cleared = 0
    for i in range(ROWS - 1, -1, -1):
        if BLACK not in grid[i]:
            lines_cleared += 1
            ind = i
            for j in range(COLUMNS):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if lines_cleared > 0:
        for key in sorted(locked, key=lambda k: k[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + lines_cleared)
                locked[newKey] = locked.pop(key)
    return lines_cleared

def get_shape():
    idx = random.randint(0, len(SHAPES) - 1)
    return Piece(COLUMNS // 2 - 2, 0, SHAPES[idx], COLORS[idx])

def draw_grid(surface, grid):
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for x in range(COLUMNS):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render(f"Score: {score}", 1, WHITE)
    surface.blit(label, (10, 10))

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    grid = create_grid()
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    locked_positions = {}
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
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
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True

        shape_pos = convert_shape_format(current_piece)

        for x, y in shape_pos:
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            score += clear_rows(grid, locked_positions) * 10
            change_piece = False

        draw_window(screen, grid, score)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    pygame.quit()
if __name__ == "__main__":
 main()
