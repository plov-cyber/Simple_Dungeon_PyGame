import pygame

pygame.init()


class Button:
    def __init__(self, x, y, width, height, txt, sc):
        self.bg = pygame.transform.scale(pygame.image.load('sources/button.png').convert(), (width, height))
        self.bg.set_colorkey(WHITE)
        self.pos = (x, y)
        self.width = width
        self.height = height
        self.text = txt
        sc.blit(self.bg, self.pos)
        font = pygame.font.Font(None, 50)
        text = font.render(self.text, 1, WHITE)
        sc.blit(text, (
            self.pos[0] + (self.width - text.get_width()) // 2, self.pos[1] + (self.height - text.get_height()) // 2))


WIN_WIDTH = 1280
WIN_HEIGHT = 720
FPS = 60
WHITE = (255, 255, 255)

clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('Simple Dungeon')
pygame.display.set_icon(pygame.image.load('sources/icon.bmp').convert_alpha())
main_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
# main_screen.blit(pygame.image.load('').convert(), (0, 0))
button = Button(100, 50, 200, 100, 'test text', main_screen)

screen.blit(main_screen, (0, 0))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
