# Einführung in die Programmierung WiSe 21/22 Markus Menth und Martin Gropp
# Benedikt Prisett
# Aufgabe 4.1 - Snake
import pygame
import random
from typing import List, Tuple

TILE_SIZE = 20


class Item:
    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    # Rückgabe ob übergebene Koordinaten die des Item sind
    def occupies(self, x: int, y: int) -> bool:
        return self._x == x and self._y == y


class Brick(Item):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

    # Zeichnen eines Bricks mit der entsprechenden TILE_SIZE
    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(
            (139, 69, 19),
            pygame.Rect(
                self._x*TILE_SIZE,
                self._y*TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
        )


class Snake:
    def __init__(self, x: int, y: int) -> None:
        self._occupies = [(x, y)]
        self._direction = (1, 0)
        self._grow = 0
        self.grow(2)
        self._last_direction = (1, 0)

    # Rückgabe eines Tuple mit der Position des Head der Schlange
    def get_head(self) -> Tuple:
        return self._occupies[0]

    # Rückgabe ob übergebene Koordinaten teil der Schlange sind
    def occupies(self, x: int, y: int) -> bool:
        for i in range(len(self._occupies)):
            if self._occupies[i][0] == x and self._occupies[i][1] == y:
                return True
        return False

    # Zeichnen der Schlange
    def draw(self, surface: pygame.Surface) -> None:
        for i in range(len(self._occupies)):
            surface.fill(
                (0, 0, 255),
                pygame.Rect(
                    self._occupies[i][0] * TILE_SIZE,
                    self._occupies[i][1] * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
            )

    # Änderung der Bewegungsrichtung der Schlange, diese kann nicht die bisherige Richtung sein
    def set_direction(self, x: int, y: int) -> None:
        if self._last_direction[0] is not x and self._last_direction[1] is not y:
            self._direction = (x, y)

    # Wachsen der Schlange
    def grow(self, n: int) -> None:
        self._grow = self._grow + n

    # Bewegungschritt der Schlange
    def step(self, forbidden: List[Item]) -> bool:
        head_position = self.get_head()
        head_position_next = (head_position[0] + self._direction[0], head_position[1] + self._direction[1])

        # Prüfen ob Schlange mit einem Item aus der Forbidden-List zusammenstößt
        for item in forbidden:
            if item.occupies(head_position_next[0], head_position_next[1]):
                return False
        # Prüfen ob Schlange mit sich selbst zusammenstößt
        if self.occupies(head_position_next[0], head_position_next[1]):
            return False
        # Schlange soll nicht wachsen oder wächst und _grow wird daher verringert
        if self._grow == 0:
            self._occupies.pop(len(self._occupies) - 1)
        else:
            self._grow -= 1
        # Schlange bewegt sich ein Schritt
        self._occupies.insert(0, head_position_next)
        self._last_direction = self._direction
        return True


class Cherry(Item):
    def __init__(self) -> None:
        super().__init__(0, 0)

    # Zeichnen einer Cherry
    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.ellipse(
            surface,
            (255, 0, 0),
            pygame.Rect(
                self._x*TILE_SIZE,
                self._y*TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
        )

    # Verschieben der Cherry an eine neue, valide zufällige Position
    def move(self, wall: List[Brick], snake: Snake, width: int, height: int) -> None:
        valid = False
        while not valid:
            # Zufällige Koordinaten für eine mögliche nächste Position
            potential_x = random.randint(0, width-1)
            potential_y = random.randint(0, height-1)
            # Prüfen ob Koordinaten Teil der Schlange sind
            if not snake.occupies(potential_x, potential_y):
                valid = True
            else:
                valid = False
            # Falls nicht Teil der Schalnge
            if valid is not False:
                # Prüfen ob Koordinaten Teil der Mauer sind
                for item in wall:
                    if item.occupies(potential_x, potential_y):
                        valid = False
                        break
                    else:
                        valid = True
        # Koordinaten sind valide und werden nun die Koordinaten der nächsten Kopf-Position
        self._x = potential_x
        self._y = potential_y


def main():
    width = 20
    height = 15
    speed = 7
    wall = []

    # Erstellen der Mauer
    for x in range(width):
        wall.append(Brick(x, 0))
        wall.append(Brick(x, height-1))
    for y in range(height):
        wall.append(Brick(0, y))
        wall.append(Brick(width-1, y))

    pygame.init()
    screen = pygame.display.set_mode((
        TILE_SIZE * width,
        TILE_SIZE * height
    ))

    clock = pygame.time.Clock()

    # Schlange und erste Cherry erstellen und platzieren
    snake = Snake(round(width / 2), round(height / 2))
    cherry = Cherry()
    cherry.move(wall, snake, width, height)

    running = True
    while running:
        screen.fill((20, 20, 20))

        # Zeichnen der Mauer auf dem Spielfeld
        for brick in wall:
            brick.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Spiel beenden
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    # Richtung: nach links
                    snake.set_direction(-1, 0)
                    pass
                elif event.key == pygame.K_RIGHT:
                    # Richtung: nach rechts
                    snake.set_direction(1, 0)
                    pass
                elif event.key == pygame.K_UP:
                    # Richtung: nach oben
                    snake.set_direction(0, -1)
                    pass
                elif event.key == pygame.K_DOWN:
                    # Richtung: nach unten
                    snake.set_direction(0, 1)
                    pass

        if not running:
            break

        # Schlange bewegen
        if not snake.step(wall):
            break

        # Schlange zeichnen
        snake.draw(screen)
        # Ueberpruefen, ob die Kirsche erreicht wurde, falls ja, wachsen und Kirsche bewegen.
        if cherry.occupies(snake.get_head()[0], snake.get_head()[1]):
            cherry.move(wall, snake, width, height)
            snake.grow(1)
        # Kirsche zeichnen
        cherry.draw(screen)

        pygame.display.flip()
        clock.tick(speed)

    pygame.display.quit()
    pygame.quit()


if __name__ == '__main__':
    main()
