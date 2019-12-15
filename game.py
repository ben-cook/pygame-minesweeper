import sys
import queue
import time
from random import randrange
import pygame

GRID_WIDTH = 32
GRID_HEIGHT = 22
TILE_WIDTH = 25
BOMB_DENSITY = 0.12

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect((x, y), (TILE_WIDTH, TILE_WIDTH))
        self.image = pygame.image.load('unclicked_tile.png')
        self.clicked = False

    def rightClick(self):
        self.image = pygame.image.load('flagged_tile.png')

class BlankTile(Tile):
    surrounding_bombs = 0

    def __init__(self, x, y):
        super().__init__(x, y)
    
    def click(self):
        #print("Surrounding bombs ", self.surrounding_bombs)
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

    def click(self):
        self.image = pygame.image.load('bomb.png')
        self.clicked = True

class GameOverImage:
    def __init__(self, x, y):
        self.rect = pygame.Rect((x, y), (100, 100))
        self.image = pygame.image.load('game_over.png')

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
    running = False

    def draw_tile(tile):
        game_display.blit(tile.image, (tile.x, tile.y))

    white = (255, 255, 255)

    while not running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = True
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                #print("clicked at " + str(x) + " " + str(y))
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
                                        game_over_img = GameOverImage(round(screen_width/2 - 2 * TILE_WIDTH), round(screen_height/2 - 2 * TILE_WIDTH))
                                        game_display.blit(game_over_img.image, (game_over_img.rect.x, game_over_img.rect.y))
                                        pygame.display.update(grid[y][x].rect)
                                        pygame.display.update(game_over_img.rect)
                                        print("GAME OVER LOSER")
                                        time.sleep(3)
                                        main()
                                        return
                                elif event.button == 3:
                                    grid[y][x].rightClick()

        game_display.fill(white)
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                draw_tile(grid[y][x])
        
            
        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()

main()
