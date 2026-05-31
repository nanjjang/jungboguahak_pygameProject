import pygame

# ---------------------------- #
#color set
#maybe..? later.....
# ---------------------------- #



# reset game
pygame.init()

# game screen set
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Kirby_By '지연쌤팬클럽' ")


# game loop variable
running = True
gameOver = False


# game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

            