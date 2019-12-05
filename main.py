import pygame

pygame.init()


class Button:
    def __init__(self, x, y, width, height, txt, sc):
        self.bg = pygame.transform.scale(BTN_IMGS[0].convert(), (width, height))
        self.pos = (x, y)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sc = sc
        self.title = txt
        self.text = pygame.font.SysFont('comicsansms', 30, bold=True).render(txt, 1, WHITE)
        self.update()

    def change_state(self):
        if self.is_focused(pygame.mouse.get_pos()):
            self.bg = pygame.transform.scale(BTN_IMGS[1].convert(), (self.width, self.height))
        else:
            self.bg = pygame.transform.scale(BTN_IMGS[0].convert(), (self.width, self.height))
        self.update()

    def update(self):
        self.sc.blit(self.bg, self.pos)
        self.sc.blit(self.text, (
            self.pos[0] + (self.width - self.text.get_width()) // 2,
            self.pos[1] + (self.height - self.text.get_height()) // 2))

    def is_focused(self, pos):
        x, y = pos
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            return True
        return False


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BTN_IMGS = [pygame.image.load('sources/btn.png'), pygame.image.load('sources/btn_act.png')]
BACKGROUND = pygame.image.load('sources/background.png')
for btn in BTN_IMGS:
    btn.set_colorkey(WHITE)
WIN_WIDTH = 1280
WIN_HEIGHT = 720
FPS = 60
MENU_SCREEN = 'menu_screen'
ABOUT_SCREEN = 'about_screen'

screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('Simple Dungeon')
pygame.display.set_icon(pygame.image.load('sources/icon.bmp').convert_alpha())
clock = pygame.time.Clock()

now_screen = MENU_SCREEN

about_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
about_screen.blit(BACKGROUND.convert(), (0, 0))
titre_y = WIN_HEIGHT

menu_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
menu_screen.blit(BACKGROUND.convert(), (0, 0))
title_size = 120
title_text = pygame.font.SysFont('comicsansms', title_size, bold=True).render('Simple Dungeon', 1, WHITE)
menu_screen.blit(title_text, ((WIN_WIDTH - title_text.get_width()) // 2, 5))

SCREENS = {MENU_SCREEN: menu_screen, ABOUT_SCREEN: about_screen}
BUTTONS = [Button(WIN_WIDTH // 2 - 150, 250, 300, 100, 'НАЧАТЬ ИГРУ', menu_screen),
           Button(WIN_WIDTH // 2 - 150, 400, 300, 100, 'О НАС', menu_screen),
           Button(WIN_WIDTH // 2 - 150, 550, 300, 100, 'ВЫЙТИ', menu_screen)]

running = True
flag = True

while running:
    if now_screen == MENU_SCREEN:
        menu_screen.blit(BACKGROUND.convert(), (0, 0))
        if flag and title_size < 140:
            title_size += 0.5
        else:
            flag = False
        if not flag and title_size > 120:
            title_size -= 0.5
        else:
            flag = True
        title_text = pygame.font.SysFont('comicsansms', int(title_size), bold=True).render('Simple Dungeon', 1, WHITE)
        menu_screen.blit(title_text, ((WIN_WIDTH - title_text.get_width()) // 2, 10))

        for btn in BUTTONS:
            btn.change_state()
    elif now_screen == ABOUT_SCREEN:
        about_screen.blit(BACKGROUND.convert(), (0, 0))
        text_y = 0
        with open('sources/titres.txt', encoding='utf-8') as f:
            for s in f.readlines():
                text = pygame.font.SysFont('comicsansms', 50).render(s.strip(), 1, WHITE)
                about_screen.blit(text, ((WIN_WIDTH - text.get_width()) // 2, titre_y + text_y))
                text_y += text.get_height()
        titre_y -= 2

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if now_screen == MENU_SCREEN:
            for btn in BUTTONS:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.is_focused(event.pos):
                    if btn.title == 'ВЫЙТИ':
                        running = False
                    elif btn.title == 'О НАС':
                        now_screen = ABOUT_SCREEN

        elif now_screen == ABOUT_SCREEN:
            if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                now_screen = MENU_SCREEN

    screen.blit(SCREENS[now_screen], (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
