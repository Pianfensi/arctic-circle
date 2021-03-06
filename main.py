import random

import numpy as np
import pygame

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
probability = 0.5
COLORS = {UP: (200, 200, 0), DOWN: (200, 0, 0), LEFT: (0, 0, 200), RIGHT: (0, 200, 0)}
EASING = 1 / 15


def arrow_polygon(x, y, w, h, direction):
    path = None
    if direction == LEFT:
        path = ((x + w * 0.5, y + h * 0.1), (x + w * 0.4, y + h * 0.25), (x + w * 0.45, y + h * 0.25),
                (x + w * 0.45, y + h * 0.9), (x + w * 0.55, y + h * 0.9), (x + w * 0.55, y + h * 0.25),
                (x + w * 0.6, y + h * 0.25))
    if direction == RIGHT:
        path = ((x + w * 0.5, y + h * 0.9), (x + w * 0.4, y + h * 0.75), (x + w * 0.45, y + h * 0.75),
                (x + w * 0.45, y + h * 0.1), (x + w * 0.55, y + h * 0.1), (x + w * 0.55, y + h * 0.75),
                (x + w * 0.6, y + h * 0.75))
    if direction == UP:
        path = ((x + w * 0.1, y + h * 0.5), (x + w * 0.25, y + h * 0.6), (x + w * 0.25, y + h * 0.55),
                (x + w * 0.9, y + h * 0.55), (x + w * 0.9, y + h * 0.45), (x + w * 0.25, y + h * 0.45),
                (x + w * 0.25, y + h * 0.4))
    if direction == DOWN:
        path = ((x + w * 0.9, y + h * 0.5), (x + w * 0.75, y + h * 0.6), (x + w * 0.75, y + h * 0.55),
                (x + w * 0.1, y + h * 0.55), (x + w * 0.1, y + h * 0.45), (x + w * 0.75, y + h * 0.45),
                (x + w * 0.75, y + h * 0.4))
    return tuple([(round(x), round(y)) for x, y in path])


class Tile:
    tiles = {}
    auto_increment = 2

    def __init__(self, x, y, direction):
        self._id = Tile.auto_increment
        Tile.tiles[self._id] = self
        Tile.auto_increment += 1
        self._x = x
        self._y = y
        self._direction = direction
        self._w = 1
        self._h = 1
        if direction in (LEFT, RIGHT):
            self._w = 2
        else:
            self._h = 2

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


class Grid:
    def __init__(self):
        self._grid = np.ones((2, 2))
        self.set_new_tiles()
        self._block_free_grid = None
        self._new_grid = None

    def _set_new_tile(self, x, y):
        if random.random() < probability:
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

    def remove_collision(self):
        n = self._grid.shape[0]
        self._new_grid = self._grid.copy()
        self._new_grid = np.where(self._new_grid >= 1, 1, 0)
        self._block_free_grid = self._new_grid.copy()
        collision_detected = False
        blocked_ids = set()
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
                            collision_detected = True
                            blocked_ids.add(tile_id)
                            blocked_ids.add(dest_id)
                    if not blocked:
                        self._block_free_grid[y, x] = tile_id
                        self._new_grid[destination] = tile_id
        self._grid = self._block_free_grid
        for blocked_id in blocked_ids:
            del Tile.tiles[blocked_id]
        return collision_detected

    def move_tiles(self):
        self._grid = self._new_grid

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
    print("Just press space bar to go through the states")
    grid = Grid()
    pygame.init()
    w, h = 600, 600
    slider_x, slider_y = (20, h-40)
    screen = pygame.display.set_mode((w, h))
    terminated = False
    clk = pygame.time.Clock()
    action_cycle = ["evolve", "unblock", "move", "insert"]
    action = 0
    moving = False
    easing = 0
    gen = 1
    def next_action():
        global easing, action, gen
        if easing == 0:
            if action_cycle[action] == "evolve":
                grid.evolve()
                gen += 1
            elif action_cycle[action] == "unblock":
                if not grid.remove_collision():
                    grid.move_tiles()
                    easing = 1
                    action += 1
            elif action_cycle[action] == "move":
                grid.move_tiles()
                easing = 1
            elif action_cycle[action] == "insert":
                grid.set_new_tiles()
            action += 1
            action %= len(action_cycle)


    pygame.time.set_timer(pygame.USEREVENT + 1, 500)
    automated = False
    while not terminated:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                terminated = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not automated:
                    next_action()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                automated = not automated
            if event.type == pygame.USEREVENT + 1:
                if automated:
                    next_action()

        pressed = pygame.key.get_pressed()
        sq_length = w // grid.size
        offset_x = (w - sq_length * grid.size) // 2
        offset_y = (h - sq_length * grid.size) // 2
        for j in range(grid.size):
            for i in range(grid.size):
                entry = grid()[i, j]
                if entry >= 1:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     pygame.Rect(round(i * sq_length + offset_x), round(j * sq_length + offset_y),
                                                 round(sq_length),
                                                 round(sq_length)))

        if easing > 0:
            easing -= EASING
            easing = max(easing, 0)
        already_drawn = []
        for j in range(grid.size):
            for i in range(grid.size):
                entry = grid()[i, j]
                if entry > 1 and entry not in already_drawn:
                    tile = Tile.tiles[entry]
                    d_y, d_x = tile.direction
                    move_ease = easing
                    x = round((i - move_ease * d_x) * sq_length + offset_x)
                    y = round((j - move_ease * d_y) * sq_length + offset_y)
                    t_w = round(sq_length * tile.width)
                    t_h = round(sq_length * tile.height)
                    pygame.draw.polygon(screen, tile.color, ((x, y), (x + t_w, y), (x + t_w, y + t_h), (x, y + t_h)))
                    if gen < 70:
                        pygame.draw.lines(screen, (0, 0, 0), True, ((x, y), (x + t_w, y), (x + t_w, y + t_h), (x, y + t_h)),
                                          2)
                    if gen < 50:
                        pygame.draw.polygon(screen, (50, 50, 50), arrow_polygon(x, y, t_w, t_h, tile.direction))
                    already_drawn.append(entry)

        screen.blit(pygame.font.SysFont('arial', 30).render(f"A({gen})", True, (128, 128, 128)), (10, 10))
        screen.blit(pygame.font.SysFont('arial', 20).render(f"horizontally splits", True, (128, 128, 128)), (slider_x, slider_y-30))
        pygame.draw.polygon(screen, (128,128,128), ((slider_x, slider_y), (slider_x+100, slider_y), (slider_x+100, slider_y+10), (slider_x, slider_y+10)))
        pygame.draw.circle(screen, (192,192,192), (round(probability*100)+slider_x, slider_y+5), 5)
        screen.blit(
            pygame.font.SysFont('arial', 20).render(f"{round(probability*100):02d} %", True, (128, 128, 128)),
            (round(probability*100)+slider_x, slider_y+10))
        if pygame.mouse.get_pressed()[0] == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if slider_x <= mouse_x <= slider_x+100 and slider_y <= mouse_y <= slider_y+10:
                probability = (mouse_x-slider_x)/100
        pygame.display.flip()
        clk.tick(30)
