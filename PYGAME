import pygame
import heapq
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Pathfinding Game")

# Clock
clock = pygame.time.Clock()

# Directions for neighbors (up, down, left, right)
DIRECTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def heuristic(a, b):
    """Calculate the Manhattan distance between two points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, end):
    """A* algorithm implementation."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for direction in DIRECTIONS:
            neighbor = (current[0] + direction[0], current[1] + direction[1])

            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and not grid[neighbor[1]][neighbor[0]]:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []  # No path found

def draw_grid():
    """Draw the grid on the screen."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_button(text, x, y, width, height, color, action=None):
    """Draw a button on the screen."""
    pygame.draw.rect(screen, color, (x, y, width, height))
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(text_surf, text_rect)
    return pygame.Rect(x, y, width, height)

def main():
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    start = (0, 0)
    end = (GRID_SIZE - 1, GRID_SIZE - 1)
    path = []

    running = True
    placing_obstacles = True
    solving = False

    while running:
        screen.fill(WHITE)
        draw_grid()

        start_button = draw_button("Start", 50, HEIGHT - 50, 100, 40, YELLOW)
        stop_button = draw_button("Stop", 200, HEIGHT - 50, 100, 40, YELLOW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if start_button.collidepoint(x, y):
                    path = astar(grid, start, end)
                    solving = True
                elif stop_button.collidepoint(x, y):
                    path = []
                    solving = False
                else:
                    grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                    if placing_obstacles:
                        grid[grid_y][grid_x] = 1 - grid[grid_y][grid_x]

        # Draw the start and end points
        pygame.draw.rect(screen, GREEN, (start[0] * CELL_SIZE, start[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, RED, (end[0] * CELL_SIZE, end[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw obstacles
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x] == 1:
                    pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw the path
        if solving:
            for (x, y) in path:
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
