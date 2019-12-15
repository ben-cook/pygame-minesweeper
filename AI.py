import sys
import os
import queue
import time
from random import randrange
import pygame
import win32api
import win32con

"""

All coordinates assume a screen resolution of 1920*1080, and my custom minesweeper starting at (100, 100)
x_pad = 100
y_pad = 100
Play area =  x_pad, y_pad, x_pad + GRID_WIDTH * TILE_WIDTH, GRID_HEIGHT * TILE_WIDTH
"""
os.environ['SDL_VIDEO_WINDOW_POS'] = "100, 100"

GRID_WIDTH = 32 # Default: 32
GRID_HEIGHT = 22 # Default: 22
TILE_WIDTH = 25
BOMB_DENSITY = 0.12
MOUSE_SPEED = 0.05 # seconds
INTERVALS = 100
CLICK_WAIT_TIME = 0 # seconds
EXPOSE_FLAGS = False

X_PAD = 100
Y_PAD = 100

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect((x, y), (TILE_WIDTH, TILE_WIDTH))
        self.image = pygame.image.load('unclicked_tile.png')
        self.clicked = False
        self.right_clicked = False

    def rightClick(self):
        self.image = pygame.image.load('flagged_tile.png')
        self.right_clicked = True

class BlankTile(Tile):
    surrounding_bombs = 0

    def __init__(self, x, y):
        super().__init__(x, y)
    
    def click(self):
        if self.surrounding_bombs == 0:
            self.image = pygame.image.load('clicked_tile.png')
        elif self.surrounding_bombs == 1:
            self.image = pygame.image.load('1.png')
        elif self.surrounding_bombs == 2:
            self.image = pygame.image.load('2.png')
        elif self.surrounding_bombs == 3:
            self.image = pygame.image.load('3.png')
        elif self.surrounding_bombs == 4:
            self.image = pygame.image.load('4.png')
        elif self.surrounding_bombs == 5:
            self.image = pygame.image.load('5.png')
        elif self.surrounding_bombs == 6:
            self.image = pygame.image.load('6.png')
        else:
            self.image = pygame.image.load('clicked_tile.png')
        
        self.clicked = True

class BombTile(Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        if EXPOSE_FLAGS:
            self.image = pygame.image.load('unclicked_bomb.png')

    def click(self):
        self.image = pygame.image.load('bomb.png')
        self.clicked = True

class GameOverImage:
    def __init__(self, x, y):
        self.rect = pygame.Rect((x, y), (100, 100))
        self.image = pygame.image.load('game_over.png')

class GameWinImage:
    def __init__(self, x, y):
        self.rect = pygame.Rect((x, y), (100, 100))
        self.image = pygame.image.load('game_win.png')

def calculate_surrounding_bombs(grid_array, tile_x, tile_y):
    surrounding_bombs = 0

    for (neighbour_x, neighbour_y) in get_surrounding_tiles(tile_x, tile_y):
        if grid_array[neighbour_y][neighbour_x].__class__.__name__ == "BombTile":
            surrounding_bombs += 1

    return surrounding_bombs

def get_surrounding_tiles(tile_x, tile_y):
    neighbours = []

    if tile_x > 0:
        neighbours.append((tile_x - 1, tile_y))
        if tile_y > 0:
            neighbours.append((tile_x - 1, tile_y - 1))
        if tile_y < GRID_HEIGHT - 1:
            neighbours.append((tile_x - 1, tile_y + 1))

    if tile_x < GRID_WIDTH - 1:
        neighbours.append((tile_x + 1, tile_y))
        if tile_y > 0:
            neighbours.append((tile_x + 1, tile_y - 1))
        if tile_y < GRID_HEIGHT - 1:
            neighbours.append((tile_x + 1, tile_y + 1))
    
    if tile_y > 0:
        neighbours.append((tile_x, tile_y - 1))
    
    if tile_y < GRID_HEIGHT - 1:
        neighbours.append((tile_x, tile_y + 1))

    return neighbours

def get_num_unmarked_neighbours(array_grid, tile_x, tile_y):
    num_unclicked_neighbours = 0
    for (neighbour_x, neighbour_y) in get_surrounding_tiles(tile_x, tile_y):
        if not array_grid[neighbour_y][neighbour_x].clicked or array_grid[neighbour_y][neighbour_x].right_clicked:
            num_unclicked_neighbours += 1
    
    return num_unclicked_neighbours

def get_num_searched_neighbours(array_grid, tile_x, tile_y):
    num_clicked_neighbours = 0
    for (neighbour_x, neighbour_y) in get_surrounding_tiles(tile_x, tile_y):
        if array_grid[neighbour_y][neighbour_x].clicked:
            num_clicked_neighbours += 1
    
    return num_clicked_neighbours

def get_num_flagged_neighbours(array_grid, tile_x, tile_y):
    num_flagged_neighbours = 0
    for (neighbour_x, neighbour_y) in get_surrounding_tiles(tile_x, tile_y):
        if array_grid[neighbour_y][neighbour_x].right_clicked:
            num_flagged_neighbours += 1
    
    return num_flagged_neighbours

def click_empty_tiles_bfs(grid_array, tile_x, tile_y):
    checked_tiles = [(tile_x, tile_y)]
    q = queue.Queue(maxsize = GRID_HEIGHT * GRID_WIDTH)
    q.put((tile_x, tile_y))

    while not q.empty():
        v = q.get()

        if grid_array[v[1]][v[0]].clicked == False:
            if grid_array[v[1]][v[0]].surrounding_bombs == 0:
                grid_array[v[1]][v[0]].click()
        
        for (neighbour_x, neighbour_y) in get_surrounding_tiles(v[0], v[1]):
            if grid_array[neighbour_y][neighbour_x].__class__.__name__ == 'BlankTile':
                if grid_array[neighbour_y][neighbour_x].surrounding_bombs == 0:
                    if (neighbour_x, neighbour_y) not in checked_tiles:
                        checked_tiles.append((neighbour_x, neighbour_y))
                        q.put((neighbour_x, neighbour_y))
                else:
                    grid_array[neighbour_y][neighbour_x].click()

def leftClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def rightClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)

def leftClickOnTile(target_tile):
    set_mouse_tile(target_tile[0], target_tile[1])
    leftClick()

def rightClickOnTile(target_tile):
    set_mouse_tile(target_tile[0], target_tile[1])
    rightClick()

def move_mouse(x, y):
    win32api.SetCursorPos((x,y))

def set_mouse_tile(tile_x, tile_y):
    mouse_glide_to(X_PAD + round((tile_x + 0.5) * TILE_WIDTH), Y_PAD + round((tile_y + 0.5) * TILE_WIDTH))

def get_cords():
    x, y = win32api.GetCursorPos()
    x = x - X_PAD
    y = y - Y_PAD
    print(x, y)

def mouse_glide_to(x,y):
    """Smooth glides mouse from current position to point x,y with default timing and speed"""
    x1, y1 = win32api.GetCursorPos()
    smooth_glide_mouse(x1, y1, x, y, MOUSE_SPEED, INTERVALS)
 
def smooth_glide_mouse(x1,y1,x2,y2, t, intervals):
    """Smoothly glides mouse from x1,y1, to x2,y2 in time t using intervals amount of intervals"""
    distance_x = x2-x1
    distance_y = y2-y1
    for n in range(0, intervals+1):
        move_mouse(round(x1 + n * (distance_x/intervals)), round(y1 + n * (distance_y/intervals)))
        time.sleep(t*1.0/intervals)

def main():
    print("Starting a new game (" + str(GRID_WIDTH) + " across by " + str(GRID_HEIGHT) + " down).")

    screen_width = GRID_WIDTH * TILE_WIDTH
    screen_height = GRID_HEIGHT * TILE_WIDTH

    grid = [[BlankTile(j * TILE_WIDTH, i * TILE_WIDTH) for j in range(GRID_WIDTH)] for i in range(GRID_HEIGHT)]

    num_bombs = round(GRID_WIDTH * GRID_HEIGHT * BOMB_DENSITY)
    bombs_added = 0
    
    while bombs_added < num_bombs:
        bomb_x = randrange(GRID_WIDTH)
        bomb_y = randrange(GRID_HEIGHT)

        if grid[bomb_y][bomb_x].__class__.__name__ == 'BlankTile':
            grid[bomb_y][bomb_x] = BombTile(grid[bomb_y][bomb_x].x, grid[bomb_y][bomb_x].y)
            bombs_added += 1
    
    print(str(bombs_added) + " bombs added.")

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x].__class__.__name__ == 'BlankTile':
                grid[y][x].surrounding_bombs = calculate_surrounding_bombs(grid, x, y)

    pygame.init()
    game_display = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    stop_running = False

    def draw_tile(tile):
        game_display.blit(tile.image, (tile.x, tile.y))

    white = (255, 255, 255)
    move_cursor_this_tick = 0
    num_turns = 0

    while not stop_running:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            stop_running = True

        clicked_bombs = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_running = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                for y in range(GRID_HEIGHT):
                    for x in range(GRID_WIDTH):
                        if grid[y][x].rect.collidepoint(mouse_x, mouse_y):
                            if grid[y][x].clicked == False:
                                if event.button == 1:
                                    grid[y][x].click()
                                    if grid[y][x].__class__.__name__ == 'BlankTile' and grid[y][x].surrounding_bombs == 0:
                                        click_empty_tiles_bfs(grid, x, y)
                                    if grid[y][x].__class__.__name__ == 'BombTile':
                                        draw_tile(grid[y][x])
                                        game_over_img = GameOverImage(round(screen_width / 2 - 2 * TILE_WIDTH), round(screen_height / 2 - 2 * TILE_WIDTH))
                                        game_display.blit(game_over_img.image, (game_over_img.rect.x, game_over_img.rect.y))
                                        pygame.display.update(grid[y][x].rect)
                                        pygame.display.update(game_over_img.rect)
                                        print("GAME OVER LOSER")
                                        print("You lost in", num_turns, "turns")
                                        time.sleep(2)
                                        main()
                                        return
                                elif event.button == 3:
                                    grid[y][x].rightClick()
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x].clicked or grid[y][x].right_clicked:
                    clicked_bombs += 1
                if clicked_bombs == GRID_HEIGHT * GRID_WIDTH:
                    game_win_img = GameWinImage(round(screen_width / 2 - 2 * TILE_WIDTH), round(screen_height / 2 - 2 * TILE_WIDTH))
                    game_display.blit(game_win_img.image, (game_win_img.rect.x, game_win_img.rect.y))
                    pygame.display.update(grid[y][x].rect)
                    pygame.display.update(game_win_img.rect)
                    pygame.display.update()
                    print("YOU WIN")
                    print("You won in", num_turns, "turns")
                    time.sleep(2)
                    main()
                    return
                draw_tile(grid[y][x])

        if move_cursor_this_tick == 1:
            time.sleep(CLICK_WAIT_TIME)

            found_a_target_tile = False

            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):

                    if grid[y][x].clicked == False and found_a_target_tile == False and grid[y][x].right_clicked == False:
                        if get_num_searched_neighbours(grid, x, y) == len(get_surrounding_tiles(x, y)):
                            found_a_target_tile = True
                            print("Found a tile surrounded by", len(get_surrounding_tiles(x, y)), "clicked tiles at (" + str(x) + ", " +  str(y) + ")")
                            target_tile = (x, y)
                            rightClickOnTile(target_tile)
                            break
                    
                    if grid[y][x].clicked == True and found_a_target_tile == False and grid[y][x].right_clicked == False:

                        if get_num_unmarked_neighbours(grid, x, y) == grid[y][x].surrounding_bombs:
                            for (neighbour_x, neighbour_y) in get_surrounding_tiles(x, y):
                                if not grid[neighbour_y][neighbour_x].clicked and not grid[neighbour_y][neighbour_x].right_clicked:
                                    found_a_target_tile = True
                                    print("Found a tile with that must be a bomb - unclicked neighbour of (" + str(x) + ", " +  str(y) + ") at (" + str(neighbour_x) + ", " +  str(neighbour_y) + ")")
                                    target_tile = (neighbour_x, neighbour_y)
                                    rightClickOnTile(target_tile)
                                    break

                    if grid[y][x].clicked == True and found_a_target_tile == False and grid[y][x].right_clicked == False:

                        if get_num_flagged_neighbours(grid, x, y) == grid[y][x].surrounding_bombs:
                            for (neighbour_x, neighbour_y) in get_surrounding_tiles(x, y):
                                if not grid[neighbour_y][neighbour_x].clicked and not grid[neighbour_y][neighbour_x].right_clicked:
                                    found_a_target_tile = True
                                    print("Found a tile with that must be safe - unclicked neighbour of (" + str(x) + ", " +  str(y) + ") at (" + str(neighbour_x) + ", " +  str(neighbour_y) + ")")
                                    target_tile = (neighbour_x, neighbour_y)
                                    leftClickOnTile(target_tile)
                                    break

            while not found_a_target_tile:
                target_tile = (randrange(GRID_WIDTH), randrange(GRID_HEIGHT))
                if not grid[target_tile[1]][target_tile[0]].clicked and not grid[target_tile[1]][target_tile[0]].right_clicked:
                    found_a_target_tile = True
                    print("Couldn't find a good tile so i'm randomly picking one.")
                    leftClickOnTile(target_tile)

            move_cursor_this_tick = 0
            num_turns += 1
            time.sleep(CLICK_WAIT_TIME)
        else:
            move_cursor_this_tick += 1

        pygame.display.update()
        clock.tick(10)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
