import random

import numpy as np
import pygame

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
COMBINATION = ["v", "h"]
COLORS = {UP: (200, 200, 0), DOWN: (200, 0, 0), LEFT: (0, 0, 200), RIGHT: (0, 200, 0)}
EASING = 1 / 15


class Tile:
    tiles = {}

    def __init__(self, x, y, direction):
        self._id = len(Tile.tiles) + 2
        Tile.tiles[self._id] = self
        self._x = x
        self._y = y
        self._direction = direction
        self._w = 1
        self._h = 1
        self._ease = 0
        self._moving = False
        if direction in (UP, DOWN):
            self._w = 2
        else:
            self._h = 2

    def blocked(self):
        for tile_id, tile in Tile.tiles.items():
            if tile != self:
                if (tile.x, tile.y) == (self._x + self._direction[0], self._y + self._direction[1]):
                    if (tile.direction, self._direction) in [(UP, DOWN), (DOWN, UP), (LEFT, RIGHT), (RIGHT, LEFT)]:
                        return True
        return False

    def evolve(self):
        self._x += 1
        self._y += 1

    def move(self):
        self._ease += EASING
        if int(self._ease) != 1:
            self._moving = True
            self._x += self._direction[0] * EASING
            self._y += self._direction[1] * EASING
        else:
            self._ease = 0
            self._moving = False

    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._w

    @property
    def height(self):
        return self._h

    @property
    def color(self):
        return COLORS[self._direction]

    @property
    def direction(self):
        return self._direction

    @property
    def moving(self):
        return self._moving


class Grid:
    def __init__(self):
        self._grid = np.ones((2, 2))
        self.set_new_tiles()
        self._block_free_grid = None

    def _set_new_tile(self, x, y):
        if random.choice(COMBINATION) == "v":
            t1 = Tile(x, y, LEFT)
            t2 = Tile(x + 1, y, RIGHT)
        else:
            t1 = Tile(x, y, UP)
            t2 = Tile(x, y + 1, DOWN)
        self.place_tile(t1.id)
        self.place_tile(t2.id)

    def place_tile(self, tile_id):
        tile = Tile.tiles[tile_id]
        if tile.direction in (LEFT, RIGHT):
            self._grid[tile.y:tile.y + 2, tile.x:tile.x + 1] = np.ones((2, 1)) * tile.id
        else:
            self._grid[tile.y:tile.y + 1, tile.x:tile.x + 2] = np.ones((1, 2)) * tile.id

    def move_tiles(self):
        n = self._grid.shape[0]
        new_grid = self._grid.copy()
        new_grid = np.vectorize(lambda x: min(max(0, x), 1))(new_grid)
        for y in range(n):
            for x in range(n):
                tile_id = int(self._grid[y, x])
                if tile_id in Tile.tiles:
                    origin_tile = Tile.tiles[tile_id]
                    d_x, d_y = origin_tile.direction
                    destination = y + d_y, x + d_x
                    dest_id = int(self._grid[destination])
                    blocked = False
                    if dest_id in Tile.tiles:
                        destination_tile = Tile.tiles[dest_id]
                        if (origin_tile.direction, destination_tile.direction) in [(UP, DOWN), (DOWN, UP),
                                                                                   (LEFT, RIGHT), (RIGHT, LEFT)]:
                            blocked = True
                    if not blocked:
                        new_grid[destination] = tile_id
        self._grid = new_grid

    def set_new_tiles(self):
        n = self._grid.shape[0]
        for y in range(n):
            for x in range(n):
                if np.array_equal(self._grid[y:y + 2, x:x + 2], np.ones((2, 2))):
                    self._set_new_tile(x, y)

    def evolve(self):
        size = self._grid.shape
        n = size[0]
        new_grid = np.zeros((n + 2, n + 2))
        new_grid[1:-1, 1:-1] = self._grid
        sub_n = n // 2 + 1
        new_grid[:sub_n, :sub_n] += np.rot90(np.eye(sub_n))
        new_grid[sub_n:, :sub_n] += np.eye(sub_n)
        new_grid[:sub_n, sub_n:] += np.eye(sub_n)
        new_grid[sub_n:, sub_n:] += np.rot90(np.eye(sub_n))
        self._grid = new_grid
        return self

    def __call__(self):

        return self._grid

    @property
    def size(self):
        return self._grid.shape[0]


if __name__ == '__main__':
    grid = Grid()
    pygame.init()
    w, h = 600, 600
    screen = pygame.display.set_mode((w, h))
    terminated = False
    clk = pygame.time.Clock()
    action_cycle = ["evolve", "move", "remove"]
    action = 0
    moving = False
    easing = 0
    while not terminated:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                terminated = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if easing == 0:
                    if action_cycle[action] == "evolve":
                        grid.evolve()
                    elif action_cycle[action] == "remove":
                        grid.set_new_tiles()
                    elif action_cycle[action] == "move":
                        grid.move_tiles()
                        easing = 1
                    action += 1
                    action %= len(action_cycle)

        pressed = pygame.key.get_pressed()
        sq_length = w // grid.size
        offset_x = (w - sq_length * grid.size) // 2
        offset_y = (h - sq_length * grid.size) // 2
        for j in range(grid.size):
            for i in range(grid.size):
                entry = grid()[i, j]
                if entry == 0:
                    pygame.draw.rect(screen, (0,0,0),
                                 pygame.Rect(i * sq_length + offset_x, j * sq_length + offset_y, sq_length,
                                             sq_length))
                else:
                    pygame.draw.rect(screen, (255,255,255),
                                 pygame.Rect(i * sq_length + offset_x, j * sq_length + offset_y, sq_length,
                                             sq_length))

        if easing > 0:
            easing -= EASING
            easing = max(easing, 0)
        for j in range(grid.size):
            for i in range(grid.size):
                entry = grid()[i, j]
                if entry > 1:
                    tile = Tile.tiles[entry]
                    d_y, d_x = tile.direction
                    move_ease = easing
                    pygame.draw.rect(screen, tile.color,
                                     pygame.Rect((i-move_ease*d_x) * sq_length + offset_x, (j-move_ease*d_y) * sq_length + offset_y, sq_length,
                                                 sq_length))


        pygame.display.flip()
        clk.tick(30)
