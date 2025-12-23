import pygame
import heapq
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 30
SIDEBAR_WIDTH = 200
CANVAS_WIDTH = WIDTH - SIDEBAR_WIDTH
CELL_SIZE = CANVAS_WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREEN = (46, 204, 113)      # Start
RED = (231, 76, 60)         # End
BLUE = (52, 152, 219)       # Path
TURQUOISE = (26, 188, 156)  # Closed set
ORANGE = (243, 156, 18)     # Open set
GRAY = (149, 165, 166)      # Grid lines
DARK_GRAY = (44, 62, 80)    # Sidebar
TEXT_COLOR = (236, 240, 241)

# Fonts
FONT = pygame.font.SysFont('Arial', 20)
HEADING_FONT = pygame.font.SysFont('Arial', 24, bold=True)

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * CELL_SIZE
        self.y = row * CELL_SIZE
        self.color = WHITE
        self.neighbors = []
        self.is_obstacle = False
        self.parent = None
        self.g = float('inf')
        self.f = float('inf')

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (self.x, self.y, CELL_SIZE, CELL_SIZE), 1)

    def update_neighbors(self, grid):
        self.neighbors = []
        # Up, Down, Left, Right
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and not grid[r][c].is_obstacle:
                self.neighbors.append(grid[r][c])

    def reset(self):
        if not self.is_obstacle:
            self.color = WHITE
        self.parent = None
        self.g = float('inf')
        self.f = float('inf')

def h(p1, p2):
    return abs(p1.row - p2.row) + abs(p1.col - p2.col)

def reconstruct_path(current, draw_callback):
    while current.parent:
        current = current.parent
        if current.color != GREEN:  # Don't color the start node
            current.color = BLUE
        draw_callback()

def astar(grid, start, end, draw_callback):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    start.g = 0
    start.f = h(start, end)

    open_set_hash = {start}

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(end, draw_callback)
            end.color = RED
            return True

        for neighbor in current.neighbors:
            temp_g = current.g + 1

            if temp_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = temp_g
                neighbor.f = temp_g + h(neighbor, end)
                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:
                        neighbor.color = ORANGE

        draw_callback()

        if current != start:
            current.color = TURQUOISE

    return False

def make_grid():
    return [[Node(i, j) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

def draw_sidebar(screen):
    pygame.draw.rect(screen, DARK_GRAY, (CANVAS_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
    
    y_offset = 20
    texts = [
        ("Controls", HEADING_FONT),
        ("", FONT),
        ("SPACE: Run A*", FONT),
        ("R: Reset Path", FONT),
        ("C: Clear All", FONT),
        ("", FONT),
        ("LMB: Draw Wall", FONT),
        ("RMB: Erase Wall", FONT),
        ("", FONT),
        ("Drag Start/End", FONT),
        ("points to move", FONT),
    ]

    for text, font in texts:
        if text == "":
            y_offset += 15
            continue
        surf = font.render(text, True, TEXT_COLOR)
        screen.blit(surf, (CANVAS_WIDTH + 10, y_offset))
        y_offset += 30

def draw(screen, grid):
    screen.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(screen)
    draw_sidebar(screen)
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    return row, col

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("A* Pathfinding Visualization")

    grid = make_grid()
    start = grid[5][5]
    end = grid[GRID_SIZE - 6][GRID_SIZE - 6]
    start.color = GREEN
    end.color = RED

    run = True
    dragging_start = False
    dragging_end = False

    while run:
        draw(screen, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # Left Click
                pos = pygame.mouse.get_pos()
                if pos[0] < CANVAS_WIDTH:
                    row, col = get_clicked_pos(pos)
                    node = grid[row][col]
                    
                    if not dragging_start and not dragging_end:
                        if node == start:
                            dragging_start = True
                        elif node == end:
                            dragging_end = True
                        elif node != end and node != start:
                            node.is_obstacle = True
                            node.color = BLACK
                    
                    if dragging_start:
                        if node != end:
                            start.reset()
                            start = node
                            start.color = GREEN
                    elif dragging_end:
                        if node != start:
                            end.reset()
                            end = node
                            end.color = RED

            elif pygame.mouse.get_pressed()[2]: # Right Click
                pos = pygame.mouse.get_pos()
                if pos[0] < CANVAS_WIDTH:
                    row, col = get_clicked_pos(pos)
                    node = grid[row][col]
                    if node != start and node != end:
                        node.is_obstacle = False
                        node.color = WHITE

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_start = False
                dragging_end = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                            node.reset()
                    
                    astar(grid, start, end, lambda: draw(screen, grid))

                if event.key == pygame.K_c:
                    grid = make_grid()
                    start = grid[5][5]
                    end = grid[GRID_SIZE - 6][GRID_SIZE - 6]
                    start.color = GREEN
                    end.color = RED

                if event.key == pygame.K_r:
                    for row in grid:
                        for node in row:
                            node.reset()

    pygame.quit()

if __name__ == "__main__":
    main()
