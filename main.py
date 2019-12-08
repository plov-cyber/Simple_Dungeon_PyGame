# Импорт необходимых библиотек
import os
import pygame

pygame.init()


def load_image(name, colorkey=None):
    """Загружает картинку. Использует colorkey в качестве фонового цвета или делает прозрачный фон."""
    fullname = os.path.join('sources', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Изображение', name, 'отсутствует.')
        exit(0)
    if colorkey:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image = image.convert()
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Button(pygame.sprite.Sprite):
    """Класс кнопки. Принимает значение ординаты y и текст самой кнопки."""

    def __init__(self, group, y, txt):
        super().__init__(group)
        self.image = BTN_IMGS[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIN_WIDTH // 2 - 250, y
        self.title = txt
        self.text = pygame.font.SysFont('comicsansms', 40, bold=True).render(txt, 1, pygame.Color('white'))

    def update(self):
        """Меняет фоновое изображение кнопки при наведении на неё."""
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = BTN_IMGS[1]
        else:
            self.image = BTN_IMGS[0]
        menu_screen.blit(self.text, (self.rect.x + (self.rect.width - self.text.get_width()) // 2,
                                     self.rect.y + (self.rect.height - self.text.get_height()) // 2))


# Константы.
WIN_WIDTH = 1280
WIN_HEIGHT = 720
FPS = 60
MENU_SCREEN = 'menu_screen'
ABOUT_SCREEN = 'about_screen'
now_screen = MENU_SCREEN

# Инициализация экрана, установка оглавление и иконки приложения.
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption('Simple Dungeon')
pygame.display.set_icon(pygame.image.load('sources/icon.bmp').convert_alpha())
clock = pygame.time.Clock()

# Загрузка изображений.
BTN_IMGS = [load_image('btn.png', pygame.Color('white')), load_image('btn_act.png', pygame.Color('white'))]
BACKGROUND = load_image('background.png')

# Экран с титрами(О НАС).
about_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
about_screen.blit(BACKGROUND, (0, 0))
titre_y = WIN_HEIGHT

# Главное меню игры.
menu_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
menu_screen.blit(BACKGROUND, (0, 0))
title_size = 120
title_text = pygame.font.SysFont('comicsansms', title_size, bold=True).render('Simple Dungeon', 1,
                                                                              pygame.Color('white'))
menu_screen.blit(title_text, ((WIN_WIDTH - title_text.get_width()) // 2, 5))

SCREENS = {MENU_SCREEN: menu_screen, ABOUT_SCREEN: about_screen}

# Инициализация кнопок и объединение их в группу.
BTN_TITLES = ['НАЧАТЬ ИГРУ', 'О НАС', 'ВЫЙТИ']
buttons = pygame.sprite.Group()
for i in range(3):
    button = Button(buttons, i * 150 + 250, BTN_TITLES[i])

# Флаги.
running = True
flag = True

# Главный цикл игры.
while running:
    # Код для главного меню игры.
    if now_screen == MENU_SCREEN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons.sprites():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos):
                    if btn.title == 'ВЫЙТИ':
                        running = False
                    elif btn.title == 'О НАС':
                        now_screen = ABOUT_SCREEN

        menu_screen.blit(BACKGROUND, (0, 0))
        if flag and title_size < 140:
            title_size += 0.33
        else:
            flag = False
        if not flag and title_size > 120:
            title_size -= 0.33
        else:
            flag = True
        title_text = pygame.font.SysFont('comicsansms', int(title_size), bold=True).render('Simple Dungeon', 1,
                                                                                           pygame.Color('white'))
        menu_screen.blit(title_text, ((WIN_WIDTH - title_text.get_width()) // 2, 10))
        buttons.draw(menu_screen)
        buttons.update()

    # Код для экрана с титрами.
    elif now_screen == ABOUT_SCREEN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                titre_y = WIN_HEIGHT
                now_screen = MENU_SCREEN

        about_screen.blit(BACKGROUND, (0, 0))
        text_y = 0
        with open('sources/titres.txt', encoding='utf-8') as f:
            for s in f.readlines():
                text = pygame.font.SysFont('comicsansms', 50).render(s.strip(), 1, pygame.Color('white'))
                about_screen.blit(text, ((WIN_WIDTH - text.get_width()) // 2, titre_y + text_y))
                text_y += text.get_height()
        titre_y -= 1

    # Обновление экрана
    screen.blit(SCREENS[now_screen], (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
