# Импорт необходимых библиотек
import os
import pygame

pygame.init()


def terminate():
    """Выход из игры"""
    pygame.quit()
    exit(0)


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


class Hero(pygame.sprite.Sprite):
    """Класс главного героя. Принимает координаты."""
    def __init__(self, group):
        super().__init__(group)


class Button(pygame.sprite.Sprite):
    """Класс кнопки. Принимает значение ординаты y, текст и цвет текста самой кнопки."""

    def __init__(self, screen, group, y, txt, txt_color):
        super().__init__(group)
        self.color = txt_color
        self.screen = screen
        self.image = BTN_IMGS[0]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = WIN_WIDTH // 2 - 250, y
        self.title = txt
        self.text = BUTTON_FONT.render(txt, 1, self.color)

    def update(self):
        """Меняет фоновое изображение кнопки при наведении на неё."""
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = BTN_IMGS[1]
        else:
            self.image = BTN_IMGS[0]
        self.screen.blit(self.text, (self.rect.x + (self.rect.width - self.text.get_width()) // 2,
                                     self.rect.y + (self.rect.height - self.text.get_height()) // 2))


# Константы.
WIN_WIDTH = 1280
WIN_HEIGHT = 720
FPS = 60
MENU_SCREEN = 'menu_screen'
ABOUT_SCREEN = 'about_screen'
LVL_CH_SCREEN = 'level_choice_screen'
now_screen = MENU_SCREEN
with open('sources/titres.txt', encoding='utf-8') as f:
    TITRES_TEXT = [i.strip() for i in f.readlines()]
BUTTON_FONT = pygame.font.SysFont('comicsansms', 40, bold=True)
TITRES_FONT = pygame.font.SysFont('comicsansms', 50)

# Инициализация экрана, установка оглавление и иконки приложения.
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
screen_rect = screen.get_rect()
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

# Экран для выбора уровня.
l_ch_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
l_ch_screen.blit(BACKGROUND, (0, 0))
LVL_CH_TITLE = pygame.font.SysFont('comicsansms', 120, bold=True).render('Выберите уровень', 1,
                                                                         pygame.Color('black'))
l_ch_screen.blit(LVL_CH_TITLE, ((WIN_WIDTH - LVL_CH_TITLE.get_width()) // 2, 5))

SCREENS = {MENU_SCREEN: menu_screen, ABOUT_SCREEN: about_screen, LVL_CH_SCREEN: l_ch_screen}

# Инициализация кнопок и объединение их в группы.
MENU_BTN_TITLES = ['НАЧАТЬ ИГРУ', 'О НАС', 'ВЫЙТИ']
menu_buttons = pygame.sprite.Group()
LEVEL_BTN_TITLES = ['Уровень 1', 'Уровень 2', 'Уровень 3']
level_buttons = pygame.sprite.Group()
for i in range(3):
    Button(menu_screen, menu_buttons, i * 150 + 250, MENU_BTN_TITLES[i], pygame.Color('white'))
    Button(l_ch_screen, level_buttons, i * 150 + 250, LEVEL_BTN_TITLES[i], pygame.Color('black'))

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
            for btn in menu_buttons:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos):
                    if btn.title == 'ВЫЙТИ':
                        terminate()
                    elif btn.title == 'О НАС':
                        now_screen = ABOUT_SCREEN
                    elif btn.title == 'НАЧАТЬ ИГРУ':
                        now_screen = LVL_CH_SCREEN

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
        menu_buttons.draw(menu_screen)
        menu_buttons.update()

    # Код для экрана с титрами.
    elif now_screen == ABOUT_SCREEN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.KEYUP:
                titre_y = WIN_HEIGHT
                now_screen = MENU_SCREEN

        about_screen.blit(BACKGROUND, (0, 0))
        text_y = 0
        for s in TITRES_TEXT:
            text = TITRES_FONT.render(s.strip(), 1, pygame.Color('white'))
            about_screen.blit(text, ((WIN_WIDTH - text.get_width()) // 2, titre_y + text_y))
            text_y += text.get_height()
        titre_y -= 1

    # Код для экрана выбора уровня
    elif now_screen == LVL_CH_SCREEN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        l_ch_screen.blit(BACKGROUND, (0, 0))
        l_ch_screen.blit(LVL_CH_TITLE, ((WIN_WIDTH - LVL_CH_TITLE.get_width()) // 2, 10))
        level_buttons.draw(l_ch_screen)
        level_buttons.update()

    # Обновление экрана
    screen.blit(SCREENS[now_screen], (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
