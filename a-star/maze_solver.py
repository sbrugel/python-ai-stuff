import pygame, heapq, math, random, sys
from Tile import Tile
from pygame.locals import *

# ARG 1: density (lower means less obstacles)
    # Defaults to 25
    # Recommended 15 to 50
# ARG 2: board size (N x N)
    # Defaults to 50
    # Recommended at least 10
# ARG 3: diagonal movement allowed - 'Y' or 'N'
    # In comparison to diagonal movement not allowed, the chances of
        # solving a maze increase with diagonal movement allowed
sys.argv = sys.argv[1:]

DENSITY = 25 if not len(sys.argv) > 0 else int(sys.argv[0])
BOARD_SIZE = 50 if not len(sys.argv) > 1 else int(sys.argv[1])
if len(sys.argv) > 2:
    if sys.argv[2].lower()[0] == 'y':
        diagonal_allowed = True
    else:
        diagonal_allowed = False
else:
    diagonal_allowed = False

maze = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
path = []
run_algorithm = False

paths_tried = 0
current_msg = 'Click me to start'

WINDOW_SIZE = 800
PADDING = 40 # for text on the bottom
FPS = 60
TILE_SIZE = WINDOW_SIZE / BOARD_SIZE

BLACK = (0, 0, 0)
GREY = (127, 127, 127)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BORDER_COLOR = BLACK
OBSTACLE_COLOR = GREY
UNEXPLORED_COLOR = WHITE
OPEN_COLOR = GREEN
CLOSED_COLOR = RED
CURRENT_COLOR = BLUE

def main():
    """
    The display loop
    """
    global maze, FPSCLOCK, DISPLAY, BASIC_FONT, paths_tried, run_algorithm

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + PADDING))
    pygame.display.set_caption('Maze Solver')
    BASIC_FONT = pygame.font.Font('freesansbold.ttf', 20)

    setup_board()

    while True:
        if run_algorithm:
            a_star(maze)
        else:
            draw_board(current_msg)
            check_for_quit()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    if not run_algorithm and TEXT_RECT.collidepoint(event.pos):
                        run_algorithm = True
                        paths_tried = 0
                        setup_board()
            pygame.display.update()
            FPSCLOCK.tick(FPS)


def setup_board():
    """
    Sets up the maze's tiles
    """
    for i in range(len(maze)):
        for j in range(len(maze[i])):
            maze[i][j] = Tile(True if (random.randint(0, 100) < DENSITY) else False)
    maze[0][0] = Tile(False)
    maze[BOARD_SIZE - 1][BOARD_SIZE - 1] = Tile(False)

def draw_board(msg):
    """
    Draws the board on the screen based on the contents of the 'maze' matrix
    """
    global TEXT_RECT
    pygame.draw.rect(DISPLAY, BLACK, (0, WINDOW_SIZE, WINDOW_SIZE, PADDING))

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if (i, j) in path:
                pygame.draw.rect(DISPLAY, CURRENT_COLOR, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1))
            elif maze[i][j].open and run_algorithm:
                pygame.draw.rect(DISPLAY, OPEN_COLOR, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1))
            elif maze[i][j].closed and run_algorithm:
                pygame.draw.rect(DISPLAY, CLOSED_COLOR, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1))
            else:
                pygame.draw.rect(DISPLAY, OBSTACLE_COLOR if maze[i][j].obstacle else UNEXPLORED_COLOR, (i*TILE_SIZE, j*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1))
        TEXT_SURF, TEXT_RECT = make_text(msg, WHITE, BLUE, 0, WINDOW_SIZE)
        DISPLAY.blit(TEXT_SURF, TEXT_RECT)

def heuristic(x, y):
    """
    IF DIAGONAL MOVEMENT IS ALLOWED: Chebyshev Distance Heuristic - h = max(|x2 - x1|, |y2 - y1|)
        Diagonal movements have a cost of 1, like other movements.

    - x2 and y2 are given with the board size as these are for the goal
    - 'x' represents x1
    - 'y' represents y1

    ================================================================================================

    IF DIAGONAL MOVEMENT IS NOT ALLOWED: Manhattan Distance Heuristic - h = |x2 - x1| + |y2 - y1|

    - x2 and y2 are given with the board size as these are for the goal
    - 'x' represents x1
    - 'y' represents y1
    """
    if diagonal_allowed:
        return max(abs((BOARD_SIZE - 1) - x), abs((BOARD_SIZE - 1) - y))
    else:
        return abs((BOARD_SIZE - 1) - x) + abs((BOARD_SIZE - 1) - y)

def a_star(maze):
    """
    Runs the A* pathfinding algorithm on the 'maze' matrix
    """
    global current_msg, path, run_algorithm, paths_tried

    # Priority queue to store nodes we are going to explore
    open_list = []
    heapq.heappush(open_list, (0, (0, 0))) # push (0, 0) starting coords to open list with priority/cost 0
    maze[0][0].add_to_open()

    # The cost to reach each node (g value)
    cost_so_far = {(0, 0): 0}

    # The parents of each node
    parents = {(0, 0): None}

    while open_list:
        # If we have stuff in open list, expand the nodes
        current_cost, current_coords = heapq.heappop(open_list)
        maze[current_coords[0]][current_coords[1]].add_to_closed()
        paths_tried += 1

        current_msg = 'Solving...' + str(paths_tried) + ' movements so far'
        draw_board(current_msg)
        check_for_quit()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

        if current_coords[0] == BOARD_SIZE - 1 and current_coords[1] == BOARD_SIZE - 1:
            # This is the goal, reconstruct the path and return it
            run_algorithm = False
            path = []
            while current_coords:
                path.append(current_coords) # Append current coordinates
                current_coords = parents[current_coords] # Traverse to the parent of the tile we're on
            current_msg = 'SOLVED! Optimal path takes ' + str(len(path)) + ' moves (click to run again)'
            return
        
        possible_next_nodes = []
        if not diagonal_allowed:
            possible_next_nodes = [(current_coords[0]+1, current_coords[1]),
                                   (current_coords[0]-1, current_coords[1]),
                                   (current_coords[0], current_coords[1]+1),
                                   (current_coords[0], current_coords[1]-1)]
        else:
            possible_next_nodes = [(current_coords[0]+1, current_coords[1]),
                                   (current_coords[0]-1, current_coords[1]),
                                   (current_coords[0], current_coords[1]+1),
                                   (current_coords[0], current_coords[1]-1),
                                   (current_coords[0]+1, current_coords[1]+1),
                                   (current_coords[0]+1, current_coords[1]-1),
                                   (current_coords[0]-1, current_coords[1]+1),
                                   (current_coords[0]-1, current_coords[1]-1)]
        
        for next_row, next_col in possible_next_nodes:
            # Check the surrounding tiles (4 if diagonal movement not allowed, 8 if so)
            if next_row >= 0 and next_col >= 0 and next_row < BOARD_SIZE and next_col < BOARD_SIZE and not maze[next_row][next_col].obstacle:
                # Check only the valid tiles
                new_cost = cost_so_far[current_coords] + 1 # The cost is just 1 plus whatever the current node cost is
                if (next_row, next_col) not in cost_so_far or new_cost < cost_so_far[(next_row, next_col)]:
                    # Add to open if not visited, or has a lower cost
                    cost_so_far[(next_row, next_col)] = new_cost
                    priority = new_cost + heuristic(next_row, next_col)
                    heapq.heappush(open_list, (priority, (next_row, next_col)))
                    maze[current_coords[0]][current_coords[1]].add_to_open()
                    parents[(next_row, next_col)] = current_coords

                    # Update the path
                    path = []
                    current_node = current_coords
                    while current_node:
                        path.append(current_node)
                        current_node = parents[current_node]
                    path = path[::-1]

                    draw_board(current_msg)
                    check_for_quit()
                    pygame.display.update()
                    FPSCLOCK.tick(FPS)

    current_msg = 'No solution :( (click to run again)'
    run_algorithm = False

def make_text(text, color, bgcolor, top, left):
    """
    Creates text on the screen that is positioned on the topleft point of the location specified

    Params:
        text (string): The text to display
        color (ColorValue): The color of the font
        bgcolor (ColorValue): The background color
        top (int), left (int): Top-left x and y coords for this text

    Returns:
        (Surface, Rect): The surface and location of the text
    """
    text_surf = BASIC_FONT.render(text, True, color, bgcolor)
    text_rect = text_surf.get_rect()
    text_rect.topleft = (top, left)
    return (text_surf, text_rect)

def check_for_quit():
    """
    Quits the game if we click the top-right 'X' or press ESC
    """
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        pygame.event.post(event)

main()