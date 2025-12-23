import pygame
import heapq
import sys
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
GRID_SIZE = 40
SIDEBAR_WIDTH = 300
CANVAS_WIDTH = WIDTH - SIDEBAR_WIDTH
CANVAS_HEIGHT = HEIGHT
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

# Terrain Types
TERRAINS = {
    'ROAD': {'color': WHITE, 'weight': 1, 'label': 'Road (1)'},
    'GRASS': {'color': (144, 238, 144), 'weight': 5, 'label': 'Grass (5)'},
    'WATER': {'color': (173, 216, 230), 'weight': 10, 'label': 'Water (10)'},
    'WALL': {'color': BLACK, 'weight': float('inf'), 'label': 'Wall'}
}

# Fonts
FONT = pygame.font.SysFont('Arial', 18)
HEADING_FONT = pygame.font.SysFont('Arial', 22, bold=True)
SMALL_FONT = pygame.font.SysFont('Arial', 16)

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * CELL_SIZE
        self.y = row * CELL_SIZE
        self.terrain = 'ROAD'
        self.color = WHITE
        self.neighbors = []
        self.is_obstacle = False
        self.parent = None
        self.g = float('inf')
        self.f = float('inf')

    def draw(self, screen):
        # Determine base color based on terrain
        if not self.is_obstacle and self.color == WHITE:
            draw_color = TERRAINS[self.terrain]['color']
        else:
            draw_color = self.color
        
        pygame.draw.rect(screen, draw_color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (self.x, self.y, CELL_SIZE, CELL_SIZE), 1)

    def update_neighbors(self, grid, diagonals=False):
        self.neighbors = []
        # Cardinal directions
        cardinal = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # Diagonal directions
        diagonal = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        dirs = cardinal + (diagonal if diagonals else [])
        
        for dr, dc in dirs:
            r, c = self.row + dr, self.col + dc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and not grid[r][c].is_obstacle:
                # Calculate cost: weight of neighbor + sqrt(2) if diagonal
                dist = 1.414 if abs(dr) == 1 and abs(dc) == 1 else 1
                self.neighbors.append((grid[r][c], dist))

    def reset(self, keep_terrain=True):
        if not keep_terrain:
            self.terrain = 'ROAD'
            self.is_obstacle = False
        self.color = WHITE if self.terrain == 'ROAD' else TERRAINS[self.terrain]['color']
        self.parent = None
        self.g = float('inf')
        self.f = float('inf')

def h(p1, p2, diagonals=False):
    if diagonals:
        # Octile distance
        dx = abs(p1.col - p2.col)
        dy = abs(p1.row - p2.row)
        return (dx + dy) + (1.414 - 2) * min(dx, dy)
    return abs(p1.row - p2.row) + abs(p1.col - p2.col)

def reconstruct_path(current, draw_callback, start):
    total_cost = 0
    while current.parent:
        total_cost += TERRAINS[current.terrain]['weight']
        node_to_color = current
        current = current.parent
        if node_to_color.color != RED and node_to_color.color != GREEN:
            node_to_color.color = BLUE
        draw_callback()
    return total_cost

def astar(grid, start, end, draw_callback, use_diagonals=False, use_heuristic=True):
    count = 0
    open_set = []
    heapq.heappush(open_set, (0, count, start))
    start.g = 0
    start.f = h(start, end, use_diagonals) if use_heuristic else 0

    open_set_hash = {start}
    start_time = time.time()
    nodes_visited = 0

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)
        nodes_visited += 1

        if current == end:
            path_cost = reconstruct_path(end, draw_callback, start)
            end.color = RED
            exec_time = (time.time() - start_time) * 1000
            return True, path_cost, nodes_visited, exec_time

        for neighbor, base_dist in current.neighbors:
            weight = TERRAINS[neighbor.terrain]['weight']
            temp_g = current.g + (weight * base_dist)

            if temp_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = temp_g
                h_score = h(neighbor, end, use_diagonals) if use_heuristic else 0
                neighbor.f = temp_g + h_score
                if neighbor not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:
                        neighbor.color = ORANGE

        draw_callback()

        if current != start:
            current.color = TURQUOISE

    return False, 0, nodes_visited, (time.time() - start_time) * 1000

def make_grid():
    return [[Node(i, j) for j in range(GRID_SIZE)] for i in range(GRID_SIZE)]

def draw_sidebar(screen, stats=None, settings=None):
    pygame.draw.rect(screen, DARK_GRAY, (CANVAS_WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))
    
    y = 20
    # Sections
    sections = [
        ("CONTROLS", [
            "SPACE: Run Search",
            "LMB: Draw Wall / Terrain",
            "RMB: Erase (Road)",
            "L-SHIFT + LMB: Cycle Terrain",
            "R: Reset Path",
            "C: Clear All",
            f"D: Diagonals [{'ON' if settings['diagonals'] else 'OFF'}]",
            f"A: Algorithm [{settings['algo']}]"
        ]),
        ("LEGEND", [
            ("Green: Start", GREEN),
            ("Red: End", RED),
            ("Black: Wall (Inf)", BLACK),
            ("Light Green: Grass (5)", TERRAINS['GRASS']['color']),
            ("Light Blue: Water (10)", TERRAINS['WATER']['color']),
            ("Orange: Open Set", ORANGE),
            ("Turquoise: Closed Set", TURQUOISE),
            ("Blue: Final Path", BLUE)
        ]),
        ("STATS", stats if stats else ["No data yet"])
    ]

    for title, lines in sections:
        surf = HEADING_FONT.render(title, True, TEXT_COLOR)
        screen.blit(surf, (CANVAS_WIDTH + 15, y))
        y += 30
        
        for line in lines:
            if isinstance(line, tuple):
                text, color = line
                surf = SMALL_FONT.render(text, True, TEXT_COLOR)
                pygame.draw.rect(screen, color, (CANVAS_WIDTH + 200, y + 2, 15, 15))
                pygame.draw.rect(screen, GRAY, (CANVAS_WIDTH + 200, y + 2, 15, 15), 1)
            else:
                surf = SMALL_FONT.render(line, True, TEXT_COLOR)
            
            screen.blit(surf, (CANVAS_WIDTH + 25, y))
            y += 24
        y += 15

def draw(screen, grid, stats=None, settings=None):
    screen.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(screen)
    draw_sidebar(screen, stats, settings)
    pygame.display.update()

def get_clicked_pos(pos):
    x, y = pos
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    return row, col

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Advanced A* Pathfinding Visualization")

    grid = make_grid()
    start = grid[5][5]
    end = grid[GRID_SIZE - 6][GRID_SIZE - 6]
    start.color = GREEN
    end.color = RED

    settings = {'diagonals': False, 'algo': 'A*'}
    stats = []
    run = True
    dragging_start = False
    dragging_end = False

    terrain_cycle = ['WALL', 'GRASS', 'WATER']
    current_terrain_idx = 0

    while run:
        draw(screen, grid, stats, settings)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Input Handling
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
                            if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                                # Cycle terrain on Shift+Click
                                node.is_obstacle = False
                                node.terrain = terrain_cycle[current_terrain_idx]
                                if node.terrain == 'WALL':
                                    node.is_obstacle = True
                                    node.color = BLACK
                                else:
                                    node.color = TERRAINS[node.terrain]['color']
                            else:
                                # Default to Wall
                                node.is_obstacle = True
                                node.terrain = 'WALL'
                                node.color = BLACK
                    
                    if dragging_start and node != end:
                        start.reset()
                        start = node
                        start.color = GREEN
                    elif dragging_end and node != start:
                        end.reset()
                        end = node
                        end.color = RED

            elif pygame.mouse.get_pressed()[2]: # Right Click
                pos = pygame.mouse.get_pos()
                if pos[0] < CANVAS_WIDTH:
                    row, col = get_clicked_pos(pos)
                    node = grid[row][col]
                    if node != start and node != end:
                        node.reset(keep_terrain=False)

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_start = False
                dragging_end = False
                if pygame.key.get_mods() & pygame.KMOD_LSHIFT:
                    current_terrain_idx = (current_terrain_idx + 1) % len(terrain_cycle)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid, settings['diagonals'])
                            node.reset()
                    
                    success, cost, visited, time_ms = astar(
                        grid, start, end, 
                        lambda: draw(screen, grid, stats, settings),
                        use_diagonals=settings['diagonals'],
                        use_heuristic=(settings['algo'] == 'A*')
                    )
                    
                    if success:
                        stats = [
                            f"Path Cost: {cost:.1f}",
                            f"Nodes Visited: {visited}",
                            f"Time: {time_ms:.1f}ms"
                        ]
                    else:
                        stats = ["No Path Found", f"Nodes Visited: {visited}"]

                if event.key == pygame.K_d:
                    settings['diagonals'] = not settings['diagonals']
                
                if event.key == pygame.K_a:
                    settings['algo'] = 'Dijkstra' if settings['algo'] == 'A*' else 'A*'

                if event.key == pygame.K_c:
                    grid = make_grid()
                    start = grid[5][5]
                    end = grid[GRID_SIZE - 6][GRID_SIZE - 6]
                    start.color = GREEN
                    end.color = RED
                    stats = []

                if event.key == pygame.K_r:
                    for row in grid:
                        for node in row:
                            node.reset()
                    stats = []

    pygame.quit()

if __name__ == "__main__":
    main()
