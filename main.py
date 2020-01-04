# Импорт необходимых библиотек
import os
import pygame
import random

pygame.init()


def terminate():
    """Выход из игры"""

    pygame.quit()
    exit(0)


def load_sound(type, name):
    """Загружает звук или музыку. Использует type для определения типа(музыка, звук)."""

    fullname = os.path.join('sounds', name)
    sound = None
    try:
        if type == 0:
            pygame.mixer_music.load(fullname)
        elif type == 1:
            sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print('Звук', name, 'отсутствует.')
        exit(0)
    if sound:
        return sound


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


class Platform(pygame.sprite.Sprite):
    """Класс платформ"""

    def __init__(self, x, y):
        """Инициализация платформы."""
        super().__init__(platforms, all_sprites)
        self.image = PLATF_IMG
        self.rect = self.image.get_rect()
        self.pos0 = (x, y)
        self.rect.x, self.rect.y = x, y


class Cloud(pygame.sprite.Sprite):
    """Класс облаков."""

    def __init__(self):
        """Инициализация облака."""
        super().__init__(clouds, all_sprites)
        self.image = random.choice(CLOUD_IMGS)
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([now_level.rect.x - self.rect.width, now_level.rect.x + 6144])
        self.rect.y = random.randint(0, 150)
        self.vx = random.choice([-2, -1, 1, 2])

    def update(self):
        """Обновление координат облака."""
        if self.rect.x < now_level.rect.x - self.rect.width or self.rect.x > 6144:
            self.kill()
        else:
            self.rect.x += self.vx - now_level.diff


class Level(pygame.sprite.Sprite):
    """Класс уровня."""

    def __init__(self, image, enemies, platforms):
        """Инициализация уровня."""
        super().__init__(level, all_sprites)
        self.image = image
        self.diff = 0
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, -500
        self.enemies = enemies
        self.platforms = platforms

    def update(self):
        """Обновление всех спрайтов уровня."""
        if 625 <= hero.x <= 5489:
            self.diff = hero.x - hero.rect.x + self.rect.x
            self.rect.x = -(hero.x - hero.rect.x)
        else:
            self.diff = 0

        for pl in self.platforms:
            pl.rect.x = pl.pos0[0] + self.rect.x


class AnimatedSprite(pygame.sprite.Sprite):
    """Класс анимированного спрайта."""

    def __init__(self, group, sheet, columns, rows, x, y):
        """Инициализация анимированного спрайта"""
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        """Разрезание большой картинки на маленькие."""
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        """Обновление картинки для анимацци"""
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Hero(pygame.sprite.Sprite):
    """Класс главного героя. Принимает координаты."""

    def __init__(self, group, x, y):
        """Инициализация персонажа"""
        super().__init__(group)
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x = x
        self.y0 = Y0
        self.turn = False
        self.jump = False
        self.platform = False
        self.jump_height = 50
        self.jump_count = 0
        self.vx = 5

    def move(self, x, y):
        """Движение персонажа."""
        if x < self.x and not self.turn:
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.turn = True
        elif x > self.x and self.turn:
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.turn = False

        if 6114 >= x >= 0:
            self.x = x
            if 0 <= self.x <= 625:
                self.rect.x = self.x
            elif 5489 <= self.x <= 6114:
                self.rect.x = (self.x + 256) % 1280

    def update(self):
        """Обновление координат персонажа при взаимодействии с ним."""
        global now_screen
        self.platform = False
        for platform in now_level.platforms:
            if platform.rect.x < self.rect.x + self.rect.width \
                    and platform.rect.x + platform.rect.width > self.rect.x \
                    and self.rect.y + self.rect.height <= platform.rect.y:
                self.y0 = platform.rect.y - self.rect.height
                self.platform = True
        if not self.platform:
            if 2280 < self.x < 2550:
                self.y0 = 530
            else:
                self.y0 = Y0
                now_screen = GAME_OVER

        if self.jump and self.jump_count + 3 < self.jump_height:
            self.rect.y -= 3
            self.jump_count += 3
        elif not self.jump and self.rect.y <= self.y0 - 3:
            self.rect.y += 3
            if self.y0 - self.rect.y < 3:
                self.rect.y = self.y0
        else:
            self.jump = False
            self.jump_count = 0


class Button(pygame.sprite.Sprite):
    """Класс кнопки. Принимает значение ординаты y, текст и цвет текста самой кнопки."""

    def __init__(self, screen, group, y, txt, txt_color):
        """Инициализация экземпляра."""
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
Y0 = 445
MENU_SCREEN = 'menu_screen'
ABOUT_SCREEN = 'about_screen'
LVL_CH_SCREEN = 'level_choice_screen'
LVL = 'level_screen'
GAME_OVER = 'game_over'
now_screen = MENU_SCREEN
with open('sources/titres.txt', encoding='utf-8') as f:
    TITRES_TEXT = [i.strip() for i in f.readlines()]
BUTTON_FONT = pygame.font.SysFont('comicsansms', 40, bold=True)
TITRES_FONT = pygame.font.SysFont('comicsansms', 50)
MENU_BTN_TITLES = ['НАЧАТЬ ИГРУ', 'О НАС', 'ВЫЙТИ']
LEVEL_BTN_TITLES = ['Уровень 1', 'Уровень 2', 'Уровень 3']
menu_buttons = pygame.sprite.Group()
level_buttons = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
level = pygame.sprite.Group()
clouds = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# Инициализация экрана, установка оглавление и иконки приложения.
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
screen_rect = screen.get_rect()
pygame.display.set_caption('Simple Dungeon')
pygame.display.set_icon(pygame.image.load('sources/icon.bmp').convert_alpha())
clock = pygame.time.Clock()

# Загрузка изображений.
BTN_IMGS = [load_image('btn.png', pygame.Color('white')), load_image('btn_act.png', pygame.Color('white'))]
BACKGROUND = load_image('background.png')
CLOUD_IMGS = [load_image('cloud1.png', (95, 205, 228)), load_image('cloud2.png', (95, 205, 228)),
              load_image('cloud3.png', (95, 205, 228))]
PLATF_IMG = pygame.transform.scale(load_image('platform.png', (95, 205, 228)), (54, 16))
PLAYER_IMG = pygame.transform.scale(load_image('knight.png'), (30, 80))

# Загрузка звуков и музыки.
load_sound(0, 'title_menu_music.mp3')
pygame.mixer_music.set_volume(0.3)
pygame.mixer_music.play(-1)
btn_sound = load_sound(1, 'btn_sound.wav')

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

# Уровень.
lvl_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
level_x = 0
now_level = None
LEVELS = [Level(pygame.transform.scale(load_image('level_1.png'), (6144, 1440)), [],
                [Platform(2306, 496), Platform(2405, 476), Platform(2497, 454)])]
ticks = 0

# Экран для game over'а.
game_over_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

# Главный герой.
hero = Hero(hero_group, 5, 445)

# Экраны.
SCREENS = {MENU_SCREEN: menu_screen, ABOUT_SCREEN: about_screen, LVL_CH_SCREEN: l_ch_screen, LVL: lvl_sc, GAME_OVER: game_over_sc}

# Инициализация кнопок и объединение их в группы.
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

        pygame.mixer_music.unpause()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in menu_buttons:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos):
                    btn_sound.play()
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

        pygame.mixer_music.unpause()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 5:
                    titre_y -= 30
                else:
                    titre_y = WIN_HEIGHT
                    now_screen = MENU_SCREEN
            elif event.type == pygame.KEYUP:
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

        pygame.mixer_music.unpause()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                now_screen = MENU_SCREEN
            for btn in level_buttons:
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos):
                    btn_sound.play()
                    pygame.mouse.set_visible(False)
                    if btn.title == 'Уровень 1':
                        now_level = LEVELS[0]
                        now_screen = LVL
                    elif btn.title == 'Уровень 2':
                        pass
                    elif btn.title == 'Уровень 3':
                        pass

        l_ch_screen.blit(BACKGROUND, (0, 0))
        l_ch_screen.blit(LVL_CH_TITLE, ((WIN_WIDTH - LVL_CH_TITLE.get_width()) // 2, 10))
        level_buttons.draw(l_ch_screen)
        level_buttons.update()

    # Код для уровней.
    elif now_screen == LVL:

        pygame.mixer_music.pause()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                pygame.mouse.set_visible(True)
                now_screen = LVL_CH_SCREEN

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and hero.rect.y == hero.y0:
            hero.jump = True
        if keys[pygame.K_RIGHT]:
            hero.move(hero.x + hero.vx, hero.rect.y)
        if keys[pygame.K_LEFT]:
            hero.move(hero.x - hero.vx, hero.rect.y)

        level.draw(lvl_sc)
        platforms.draw(lvl_sc)
        hero_group.draw(lvl_sc)
        if ticks == random.randint(0, 75):
            Cloud()
        clouds.draw(lvl_sc)
        hero_group.update()
        level.update()
        clouds.update()
        ticks += 1
        if ticks > 75:
            ticks = 0

    # Обновление экрана
    screen.blit(SCREENS[now_screen], (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
