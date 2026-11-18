#!/usr/bin/env python3
#
#   Copyright (c) 2023, Monaco F. J. <monaco@usp.br>
#
#   This file is part of KobraPy.
#
#   KobraPy is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random
import sys
from pathlib import Path

import pygame


# Game settings.
# Change these values to customize the game without changing its rules.

WIDTH, HEIGHT = 800, 800  # Game screen dimensions.
GRID_SIZE = 50  # Side length of each grid cell.

HEAD_COLOR = "#00aa00"
DEAD_HEAD_COLOR = "#4b0082"
TAIL_COLOR = "#00ff00"
APPLE_COLOR = "#aa0000"
ARENA_COLOR = "#202020"
GRID_COLOR = "#3c3c3b"
SCORE_COLOR = "#ffffff"
MESSAGE_COLOR = "#808080"

WINDOW_TITLE = "KobraPy"
GAME_SPEED = 7  # Game-loop iterations per second.


# Set up Pygame.
# The window and fonts are used later to draw the game and its messages.

pygame.init()

clock = pygame.time.Clock()
arena = pygame.display.set_mode((WIDTH, HEIGHT))

# Resolve assets relative to this file, so the game can be started from
# any working directory.
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
FONT_PATH = ASSETS_DIR / "font" / "GetVoIP-Grotesque.ttf"

BIG_FONT = pygame.font.Font(FONT_PATH, int(WIDTH / 8))
SMALL_FONT = pygame.font.Font(FONT_PATH, int(WIDTH / 20))

pygame.display.set_caption(WINDOW_TITLE)

game_on = 1


# Helper functions.
# These functions draw reusable parts of the screen.
def center_prompt(title, subtitle):
    """Display a prompt and wait for a key or quit event."""
    center_title = BIG_FONT.render(title, True, MESSAGE_COLOR)
    center_title_rect = center_title.get_rect(
        center=(WIDTH / 2, HEIGHT / 2)
    )
    arena.blit(center_title, center_title_rect)

    center_subtitle = SMALL_FONT.render(subtitle, True, MESSAGE_COLOR)
    center_subtitle_rect = center_subtitle.get_rect(
        center=(WIDTH / 2, HEIGHT * 2 / 3)
    )
    arena.blit(center_subtitle, center_subtitle_rect)

    pygame.display.update()

    # Pause here until the player presses a key. The same prompt is used
    # when a new game starts and when a game ends.
    # The window-close event must also work while we are waiting.
    while (event := pygame.event.wait()):
        if event.type == pygame.KEYDOWN:
            break
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if event.key == pygame.K_q:
        pygame.quit()
        sys.exit()


def draw_grid():
    """Draw the arena grid."""
    for x in range(0, WIDTH, GRID_SIZE):
        for y in range(0, HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(arena, GRID_COLOR, rect, 1)

# Game objects.
# A snake is made of a head and a list of tail segments.
class Snake:
    """Track the snake's segments, movement, and collisions."""

    def __init__(self):
        self.x, self.y = GRID_SIZE, GRID_SIZE

        # Each movement component tells how many grid cells to advance:
        # -1 for left/up, 0 for no movement, and 1 for right/down.
        # Starting with (1, 0) makes the snake move to the right.
        self.xmov = 1
        self.ymov = 0

        # Rect stores a segment's position and size. The tail is a list
        # of earlier head positions, with the newest segment first.
        self.head = pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE)
        self.tail = []
        self.alive = True
        self.got_apple = False

    def update(self):
        """Check collisions and move the snake."""
        # Calculate the next position before moving.
        next_x = self.head.x + self.xmov * GRID_SIZE
        next_y = self.head.y + self.ymov * GRID_SIZE

        # Check whether the entire head would cross an arena boundary.
        if (
            next_x < 0
            or next_x + GRID_SIZE > WIDTH
            or next_y < 0
            or next_y + GRID_SIZE > HEIGHT
        ):
            self.alive = False
            return

        # Check collision with the snake's own tail.
        for square in self.tail:
            if self.head.x == square.x and self.head.y == square.y:
                self.alive = False
                return

        # Move the tail and grow when an apple was collected.
        if self.xmov or self.ymov:
            self.tail.insert(
                0, pygame.Rect(self.head.x, self.head.y, GRID_SIZE, GRID_SIZE)
            )

            if self.got_apple:
                self.got_apple = False
            else:
                self.tail.pop()

            # Apply the validated position.
            self.head.x = next_x
            self.head.y = next_y


class Apple:
    """Represent an apple in the arena."""

    def __init__(self):
        # Apples occupy grid cells, just like the snake's segments.
        self.x = int(random.randint(0, WIDTH) / GRID_SIZE) * GRID_SIZE
        self.y = int(random.randint(0, HEIGHT) / GRID_SIZE) * GRID_SIZE
        self.rect = pygame.Rect(self.x, self.y, GRID_SIZE, GRID_SIZE)

    def update(self):
        """Draw the apple."""
        pygame.draw.rect(arena, APPLE_COLOR, self.rect)


# Start a game.
# Set up the score's screen position, create the objects, and wait for
# the player to start. The main loop below will reuse these objects.
score_rect = BIG_FONT.render("1", True, MESSAGE_COLOR).get_rect(
    center=(WIDTH / 2, HEIGHT / 20 + HEIGHT / 30)
)

draw_grid()

snake = Snake()
apple = Apple()

center_prompt(WINDOW_TITLE, "Press to start")


# Main game loop.
# Each iteration reads input, advances the game (unless paused), draws
# the screen, and limits the pace. Keeping these steps visible makes
# it easier to understand how keyboard actions affect what appears on screen.

while True:
    # Handle input and window events first, so keys can affect this turn.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_p:
                game_on = not game_on
            # Ignore movement keys while paused.
            elif not game_on:
                continue
            elif event.key == pygame.K_DOWN:
                snake.ymov = 1
                snake.xmov = 0
            elif event.key == pygame.K_UP:
                snake.ymov = -1
                snake.xmov = 0
            elif event.key == pygame.K_RIGHT:
                snake.ymov = 0
                snake.xmov = 1
            elif event.key == pygame.K_LEFT:
                snake.ymov = 0
                snake.xmov = -1

    # While paused, do not advance the snake or redraw the arena.
    # The existing objects are still displayed below.
    if game_on and snake.alive:
        snake.update()

    arena.fill(ARENA_COLOR)
    draw_grid()

    if snake.alive:
        apple.update()

    # Draw tail segments first and the head last, so the head is visible.
    for square in snake.tail:
        pygame.draw.rect(arena, TAIL_COLOR, square)

    if snake.alive:
        pygame.draw.rect(arena, HEAD_COLOR, snake.head)
    else:
        pygame.draw.rect(arena, DEAD_HEAD_COLOR, snake.head)

    # The tail length represents the number of apples collected.
    score = BIG_FONT.render(f"{len(snake.tail)}", True, SCORE_COLOR)
    arena.blit(score, score_rect)

    # Collecting an apple schedules growth on the next snake update.
    # A new apple then appears for the player to collect.
    if snake.alive and snake.head.x == apple.x and snake.head.y == apple.y:
        snake.got_apple = True
        apple = Apple()

    # Show this frame and limit how often the loop runs. GAME_SPEED
    # currently controls both drawing and movement.
    pygame.display.update()
    clock.tick(GAME_SPEED)

    # Wait for the player to restart after Game Over.
    if not snake.alive:
        center_prompt("Game Over", "Press to restart")
        snake = Snake()
        apple = Apple()
