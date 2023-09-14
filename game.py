import pygame

pygame.init()

ScrWidth = 800
ScrHeight = 600

screen = pygame.display.set_mode((ScrWidth, ScrHeight))

# Create a rectangle((Position, Position, Size, Size))
player = pygame.Rect((300,250,50,50))

run = True
While run:

  # Screen color 
  screen.fill((0,0,0))

  pygame.draw.rect(screen, (255, 0, 0), player)

  key = pygame.key.get_presssed()
  if key[pygame.K_a] == True:
    player.move_ip(-1,0)
    # If user hits a, then the player will move left
  elif key[pygame.K_d] == True:
    player.move_ip(1,0)
  elif key[pygame.K_s] == True:
    player.move_ip(0,-1)
  elif key[pygame.K_w] == True:
    player.move_ip(0,1)

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False

  pygame.display.update()

pygame.quit()
