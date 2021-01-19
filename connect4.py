# Simple pygame program

# Import and initialize the pygame library
import pygame

pygame.init()

clock = pygame.time.Clock()
# Set up the drawing window
screen = pygame.display.set_mode([745, 745])
pygame.display.set_caption("Connect 4")

WIN_HEIGHT = 745
WIN_WIFTH = 745
UNIT_RADIUS = 35

# Some color code used for
SILVER = (192, 192, 192)
LIGHT_GREY = (211, 211, 211)
GREY = (128, 128, 128)
LIGHT_YELLOW = (224, 226, 75)
LIGHT_RED = (250, 103, 103)
LIGHT_BLUE = (0, 0, 100)
CYAN = (0, 255, 255)

block = {}

for i in range(10):
    for j in range(10):
        block[(i, j)] = [GREY, 0, False]

prev_pointed = ()
# Run until the user asks to quit
running = True
while running:
    pygame.time.delay(100)

    # Fill the background with white
    screen.fill(SILVER)

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            x = x//75
            y = y // 75
            if not block[(x, y)][2]:
                block[(x, y)] = [LIGHT_YELLOW, 1, True]
                # block[(x+1, y+1)] = [LIGHT_RED, 1, True]
        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            x = x // 75
            y = y // 75

            if block.get(prev_pointed) and not block[prev_pointed][2]:
                block[prev_pointed] = [GREY, 0, False]
            if not block[(x, y)][2]:
                block[(x, y)] = [LIGHT_GREY, 0, False]
            prev_pointed = (x, y)

    # Draw a solid blue circle in the center
    for i in range(10):
        for j in range(10):
            color = block[(i, j)][0]
            pygame.draw.circle(screen, color,
                               (75*i + 35, 75*j + 35), UNIT_RADIUS)

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
