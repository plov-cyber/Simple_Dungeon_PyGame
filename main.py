# Импорт необходимых библиотек
import os
import pygame
import random

pygame.init()


def win():
    """Функция выигрыша."""

    global now_screen, win_bg
    win_bg = lvl_sc.copy()
    now_screen = WIN_SCREEN
    reset_level()


def play_level(num):
    """Функция запуска уровня."""

    global now_level, now_screen
    if num == 0:
        now_level = LEVELS[num]
        now_screen = LVL
        pygame.mouse.set_visible(False)


def pause():
    """Функция для паузы игры."""

    global now_screen, pause_bg
    pygame.mouse.set_visible(True)
    now_screen = PAUSE_SCREEN
    pause_bg = lvl_sc.copy()


def play_music(name, volume):
    """Функция проигрывания музыки."""

    global now_music
    if not pygame.mixer_music.get_busy() or name != now_music:
        load_sound(0, name)
        pygame.mixer_music.play(-1)
        pygame.mixer_music.set_volume(volume)
        now_music = name


def game_over():
    """Функция для выхода в главное меню после проигрыша."""

    global now_screen, game_over_bg
    now_screen = GAME_OVER
    game_over_bg = lvl_sc.copy()
    reset_level()


def reset_level():
    """Функция выхода с уровня."""

    pygame.mouse.set_visible(True)
    now_level.reset()
    hero.reset()


def terminate():
    """Выход из игры"""

    pygame.quit()
    exit(0)


def load_sound(type, name):
    """Загружает звук или музыку."""

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


class Monster(pygame.sprite.Sprite):
    """Класс монстра. Принимает значения координаты, атаки, здоровья."""

    def __init__(self, x, dmg, health, d, img):
        """Инициализация монстра."""

        super().__init__(monsters, all_sprites)
        self.image = img
        self.image0 = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, Y0 + hero.rect.height - self.rect.height
        self.x0 = x
        self.X0 = x
        self.vx = 1
        self.death_vy = 2
        self.dmg = dmg
        self.health = health
        self.full_health = health
        self.range = d
        self.right = True
        self.ticks = 0

    def update(self):
        """Двигает мостра в пределах указанных координат. Наносит урон игроку."""

        if self.health <= 0:
            self.image.set_alpha(250)
            self.rect.y += self.death_vy
        else:

            collider = pygame.sprite.spritecollideany(self, hero_group)
            if not collider:
                if self.right and self.x0 + self.range > self.rect.x:
                    self.rect.x += self.vx
                else:
                    self.right = False

                if not self.right and self.rect.x > self.x0:
                    self.rect.x -= self.vx
                else:
                    self.right = True
            elif self.ticks % 20 == 0:
                collider.health -= self.dmg
            self.image = pygame.transform.flip(self.image0, not self.right, 0)
            self.ticks = (self.ticks + 1) % 120

    def reset(self):
        """Сброс монстра."""

        self.health = self.full_health
        self.rect.x, self.rect.y = self.X0, Y0 + hero.rect.height - self.rect.height
        self.x0 = self.X0
        self.right = True
        self.ticks = 0


class Platform(pygame.sprite.Sprite):
    """Класс платформ"""

    def __init__(self, x, y):
        """Инициализация платформы."""

        super().__init__(platforms, all_sprites)
        self.image = PLATF_IMG
        self.rect = self.image.get_rect()
        self.pos0 = (x, y)
        self.x0 = 0
        self.rect.x, self.rect.y = x, y

    def reset(self):
        """Сброс платформы."""

        self.rect.x = self.pos0[0]


class MovingPlatform(Platform):
    """Класс двигающейся платформы."""

    def __init__(self, x, y, range):
        """Инициализация платформы."""

        super().__init__(x, y)
        self.range = range
        self.right = True
        self.x0 = x
        self.X0 = x
        self.vx = 1

    def update(self):
        """Движение платформы."""

        if self.right and self.x0 + self.range > self.rect.x:
            self.rect.x += self.vx
        else:
            self.right = False

        if not self.right and self.rect.x > self.x0:
            self.rect.x -= self.vx
        else:
            self.right = True

    def reset(self):
        """Сброс платформы."""

        self.x0 = self.X0
        self.rect.x = self.pos0[0]


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
        self.enemies = pygame.sprite.Group(enemies)
        self.platforms = pygame.sprite.Group(platforms)

    def update(self):
        """Обновление всех спрайтов уровня."""

        if 625 <= hero.x <= 5489:
            self.diff = hero.x - hero.rect.x + self.rect.x
            self.rect.x = -(hero.x - hero.rect.x)
        else:
            self.diff = 0

        for pl in self.platforms:
            pl.rect.x -= self.diff
            pl.x0 -= self.diff

        for en in self.enemies:
            en.rect.x -= self.diff
            en.x0 -= self.diff

    def reset(self):
        """Сброс уровня."""

        self.diff = 0
        self.rect.x = 0
        for enemy in self.enemies:
            enemy.reset()
        for pl in self.platforms:
            pl.reset()


class Hero(pygame.sprite.Sprite):
    """Класс главного героя. Принимает координаты."""

    def __init__(self, group, x, y, dmg, health):
        """Инициализация персонажа"""

        super().__init__(group)
        self.image = PLAYER_IMGS[2]
        self.img_count = 0
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x = x
        self.pos0 = (x, y)
        self.safe_x = (self.x, self.rect.x)
        self.y0 = Y0
        self.attack = False
        self.left = False
        self.jump = False
        self.platform = False
        self.moving = False
        self.jump_height = 60
        self.jump_count = 0
        self.vx = 4
        self.full_health = health
        self.health = health
        self.freq = 15
        self.ticks = 0
        self.angle = 0
        self.dmg = dmg
        self.hole = False
        self.hole_coords = ()

    def move(self, x, y):
        """Движение персонажа."""

        self.moving = True
        if x < self.x and not self.left:
            self.left = True
        elif x > self.x:
            self.left = False

        if not pygame.sprite.spritecollideany(self, now_level.platforms):
            self.safe_x = (self.x, self.rect.x)

        if 6114 >= x >= 0 and (
                (self.rect.y > Y0 and self.hole_coords[0] < x < self.hole_coords[1]) or self.rect.y <= Y0):
            self.x = x
            if 0 <= self.x <= 625:
                self.rect.x = self.x
            elif 5489 <= self.x <= 6114:
                self.rect.x = (self.x + 256) % 1280

        if pygame.sprite.spritecollideany(self, now_level.platforms):
            self.x, self.rect.x = self.safe_x

    def update(self):
        """Обновление координат персонажа при взаимодействии с ним."""

        if self.health <= 0 or self.rect.y >= 530:
            self.death()
        elif self.x >= 6000:
            win()
        else:
            self.platform = False
            for platform in now_level.platforms:
                if platform.rect.x < self.rect.x + self.rect.width \
                        and platform.rect.x + platform.rect.width > self.rect.x \
                        and self.rect.y + self.rect.height <= platform.rect.y:
                    self.y0 = platform.rect.y - self.rect.height
                    self.platform = True

            self.hole = False
            for i, j in HOLES_COORD:
                if i < self.x < j:
                    if not self.platform:
                        self.y0 = 530
                    self.hole_coords = (i, j)
                    self.hole = True
                    break

            if not self.platform and not self.hole:
                self.y0 = Y0

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

            if self.ticks % self.freq == 0:
                if self.attack:
                    enemy = pygame.sprite.spritecollideany(self, now_level.enemies)
                    if enemy:
                        enemy.health -= self.dmg
                    self.image = pygame.transform.flip(PLAYER_IMGS[self.img_count + 2], self.left, 0)
                    self.img_count = (self.img_count + 1) % 2
                elif not self.attack and self.moving:
                    self.image = pygame.transform.flip(PLAYER_IMGS[self.img_count], self.left, 0)
                    self.img_count = (self.img_count + 1) % 2
            if not self.moving and not self.attack:
                self.image = pygame.transform.flip(PLAYER_IMGS[2], self.left, 0)
            self.attack = False
            self.moving = False
            self.ticks = (self.ticks + 1) % 120

    def death(self):
        """Смерть персонажа."""

        if self.angle < 90:
            self.angle += 2
            self.image = pygame.transform.rotate(PLAYER_IMGS[2], self.angle)
            self.rect.y += 1
        else:
            game_over()

    def reset(self):
        """Сброс персонажа."""

        self.hole = False
        self.ticks = 0
        self.freq = 15
        self.angle = 0
        self.jump_count = 0
        self.y0 = Y0
        self.rect.x, self.rect.y = self.pos0
        self.x = self.pos0[0]
        self.safe_x = (self.x, self.rect.x)
        self.left = False
        self.jump = False
        self.platform = False
        self.moving = False
        self.health = self.full_health


class Button(pygame.sprite.Sprite):
    """Класс кнопки. Принимает значение ординаты y, текст и цвет текста самой кнопки."""

    def __init__(self, screen, group, y, txt, txt_color):
        """Инициализация экземпляра кнопки."""

        super().__init__(group, all_sprites)
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


class Health(pygame.sprite.Sprite):
    """Класс шкалы здоровья игрока."""

    def __init__(self, x, y, screen, img, color):
        """Инициализация спрайта."""

        super().__init__(heart_group)
        self.color = color
        self.screen = screen
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        """Обновление шкалы здоровья."""

        if self.color == (255, 0, 0):
            self.screen.blit(self.image, (self.rect.x, self.rect.y))
            pygame.draw.rect(self.screen, self.color,
                             (self.rect.x + self.rect.width + 10, self.rect.y + self.rect.height // 4, hero.full_health * 2,
                              self.rect.height // 2), 1)

            if hero.health >= 0:
                pygame.draw.rect(self.screen, self.color,
                                 (self.rect.x + self.rect.width + 10, self.rect.y + self.rect.height // 4, hero.health * 2,
                                  self.rect.height // 2))

        collider = pygame.sprite.spritecollideany(hero, now_level.enemies)
        if collider and self.color == (0, 0, 0):
            self.screen.blit(self.image, (self.rect.x, self.rect.y))
            pygame.draw.rect(self.screen, self.color,
                             (self.rect.x - 10 - collider.full_health * 2, self.rect.y + self.rect.height // 4,
                              collider.full_health * 2,
                              self.rect.height // 2), 1)
            if collider.health >= 0:
                pygame.draw.rect(self.screen, self.color, (
                    self.rect.x - 10 - collider.health * 2, self.rect.y + self.rect.height // 4, collider.health * 2,
                    self.rect.height // 2))


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
PAUSE_SCREEN = 'pause_screen'
WIN_SCREEN = 'win_screen'
now_screen = MENU_SCREEN
with open('sources/titres.txt', encoding='utf-8') as f:
    TITRES_TEXT = [i.strip() for i in f.readlines()]
BUTTON_FONT = pygame.font.SysFont('comicsansms', 40, bold=True)
TITRES_FONT = pygame.font.SysFont('comicsansms', 50)
MENU_BTN_TITLES = ['НАЧАТЬ ИГРУ', 'О НАС', 'ВЫЙТИ']
LEVEL_BTN_TITLES = ['Уровень 1', 'Уровень 2', 'Уровень 3']
PAUSE_BTN_TITLES = ['ПРОДОЛЖИТЬ', 'В ГЛАВНОЕ МЕНЮ']
GAME_OVER_BTN_TITLES = ['ИГРАТЬ ЗАНОВО', 'В ГЛАВНОЕ МЕНЮ']
WIN_BTN_TITLES = ['СЛЕДУЮЩИЙ УРОВЕНЬ', 'В ГЛАВНОЕ МЕНЮ']
HOLES_COORD = [(535, 685), (1095, 1125), (1280, 1530), (2190, 2540),
               (3130, 3385), (3930, 3960), (4235, 4485),
               (4855, 4885)]

# Инициализация групп спрайтов.
all_sprites = pygame.sprite.Group()
pause_buttons = pygame.sprite.Group()
menu_buttons = pygame.sprite.Group()
level_buttons = pygame.sprite.Group()
win_buttons = pygame.sprite.Group()
game_over_buttons = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
heart_group = pygame.sprite.Group()
level = pygame.sprite.Group()
clouds = pygame.sprite.Group()
platforms = pygame.sprite.Group()
monsters = pygame.sprite.Group()

# Инициализация экрана, установка оглавления и иконки приложения.
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
PLAYER_IMGS = [pygame.transform.scale(load_image('knight1.png'), (30, 80)),
               pygame.transform.scale(load_image('knight2.png'), (30, 80)),
               pygame.transform.scale(load_image('knight.png'), (30, 80)),
               pygame.transform.scale(load_image('knight3.png'), (42, 80))]
MNSTR_IMGS = [load_image('slime.png'), pygame.transform.scale(load_image('boss.png', (255, 255, 255)), (50, 80)),
              pygame.transform.scale(load_image('ghost.png'), (30, 60))]
LVL_IMGS = [load_image('level_1.png')]
HEART_IMGS = [pygame.transform.scale(load_image('heart.png'), (80, 80)),
              pygame.transform.scale(load_image('bl_heart.png'), (80, 80))]

# Загрузка звуков и музыки.
btn_sound = load_sound(1, 'btn_sound.wav')
title_mc = 'title_menu_music.wav'
level_mc = 'level_music.wav'
now_music = title_mc

# Главный герой.
hero = Hero(hero_group, 5, 445, 30, 100)

# Экран с титрами(О НАС).
about_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
titre_y = WIN_HEIGHT

# Главное меню игры.
menu_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
title_size = 120
title_text = pygame.font.SysFont('comicsansms', title_size, bold=True).render('Simple Dungeon', 1,
                                                                              pygame.Color('white'))

# Экран для выбора уровня.
l_ch_screen = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
LVL_CH_TITLE = pygame.font.SysFont('comicsansms', 120, bold=True).render('Выберите уровень', 1,
                                                                         pygame.Color('black'))

# Уровень.
lvl_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
heart = Health(10, 10, lvl_sc, HEART_IMGS[0], (255, 0, 0))
bl_heart = Health(1190, 10, lvl_sc, HEART_IMGS[1], (0, 0, 0))
level_x = 0
now_level = None
level_num = None
LEVELS = [Level(pygame.transform.scale(LVL_IMGS[0], (6144, 1440)),
                [Monster(710, 20, 50, 200, MNSTR_IMGS[0]), Monster(1600, 30, 100, 350, MNSTR_IMGS[1]),
                 Monster(2755, 40, 150, 250, MNSTR_IMGS[2])],
                [Platform(552, 496), Platform(650, 476),
                 Platform(1296, 496), Platform(1394, 476), Platform(1488, 454),
                 Platform(2214, 486), Platform(2306, 454), Platform(2404, 476), Platform(2500, 454),
                 MovingPlatform(3163, 476, 190),
                 Platform(4250, 496), Platform(4348, 476), Platform(4444, 496)])]
ticks = 0

# Экран для game over'а.
game_over_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
game_over_bg = LVL_IMGS[0]
fog = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
fog.fill((0, 0, 0))
fog.set_alpha(150)
GAME_OVER_TITLE = pygame.font.SysFont('comicsansms', 180, bold=True).render('GAME OVER', 1, pygame.Color('white'))

# Экран паузы.
pause_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
pause_bg = LVL_IMGS[0]
PAUSE_TITLE = pygame.font.SysFont('comicsansms', 180, bold=True).render('ПАУЗА', 1, pygame.Color('darkgrey'))

# Экран выигрыша.
win_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
win_bg = LVL_IMGS[0]
WIN_TITLE = pygame.font.SysFont('comicsansms', 150, bold=True).render('ВЫ ПОБЕДИЛИ', 1, pygame.Color('darkblue'))

# Экраны.
SCREENS = {MENU_SCREEN: menu_screen, ABOUT_SCREEN: about_screen, LVL_CH_SCREEN: l_ch_screen, LVL: lvl_sc,
           GAME_OVER: game_over_sc, PAUSE_SCREEN: pause_sc, WIN_SCREEN: win_sc}

# Инициализация кнопок и объединение их в группы.
for i in range(3):
    Button(menu_screen, menu_buttons, i * 150 + 250, MENU_BTN_TITLES[i], pygame.Color('white'))
    Button(l_ch_screen, level_buttons, i * 150 + 250, LEVEL_BTN_TITLES[i], pygame.Color('black'))
    if i < 2:
        Button(pause_sc, pause_buttons, i * 150 + 350, PAUSE_BTN_TITLES[i], pygame.Color('grey'))
        Button(game_over_sc, game_over_buttons, i * 150 + 350, GAME_OVER_BTN_TITLES[i], pygame.Color('white'))
        Button(win_sc, win_buttons, i * 150 + 350, WIN_BTN_TITLES[i], pygame.Color('black'))

# Флаги.
running = True
flag = True

# Главный цикл игры.
while running:
    # Код для главного меню игры.
    if now_screen == MENU_SCREEN:

        play_music(title_mc, 0.3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            for btn in menu_buttons:
                if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos)) \
                        or (event.type == pygame.KEYUP and event.key == pygame.K_SPACE
                            and btn.rect.collidepoint(pygame.mouse.get_pos())):
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

        play_music(title_mc, 0.3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
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

    # Код для экрана выбора уровня.
    elif now_screen == LVL_CH_SCREEN:

        play_music(title_mc, 0.3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                btn_sound.play()
                now_screen = MENU_SCREEN

            for btn in level_buttons:
                if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos)) \
                        or (event.type == pygame.KEYUP and event.key == pygame.K_SPACE
                            and btn.rect.collidepoint(pygame.mouse.get_pos())):
                    btn_sound.play()
                    if btn.title == 'Уровень 1':
                        level_num = 0
                    elif btn.title == 'Уровень 2':
                        level_num = 1
                    elif btn.title == 'Уровень 3':
                        level_num = 2
                    play_level(level_num)

        l_ch_screen.blit(BACKGROUND, (0, 0))
        l_ch_screen.blit(LVL_CH_TITLE, ((WIN_WIDTH - LVL_CH_TITLE.get_width()) // 2, 10))
        level_buttons.draw(l_ch_screen)
        level_buttons.update()

    # Код для уровней.
    elif now_screen == LVL:

        play_music(level_mc, 0.3)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                btn_sound.play()
                pause()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and hero.rect.y == hero.y0:
            hero.jump = True
        if keys[pygame.K_d]:
            hero.move(hero.x + hero.vx, hero.rect.y)
        if keys[pygame.K_a]:
            hero.move(hero.x - hero.vx, hero.rect.y)
        if keys[pygame.K_LSHIFT]:
            hero.vx = 5
            hero.freq = 10
        else:
            hero.vx = 3
            hero.freq = 15
        hero.attack = True if keys[pygame.K_w] else False

        level.draw(lvl_sc)
        now_level.platforms.draw(lvl_sc)
        now_level.enemies.draw(lvl_sc)
        hero_group.draw(lvl_sc)
        if ticks == random.randint(0, 75):
            Cloud()
        clouds.draw(lvl_sc)
        heart_group.update()
        hero_group.update()
        now_level.enemies.update()
        now_level.platforms.update()
        level.update()
        clouds.update()
        ticks = (ticks + 1) % 75

    # Код для GAME OVER.
    elif now_screen == GAME_OVER:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in [pygame.MOUSEBUTTONUP, pygame.KEYUP]:
                btn_sound.play()
                now_screen = MENU_SCREEN

            for btn in game_over_buttons:
                if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos)) \
                        or (event.type == pygame.KEYUP and event.key == pygame.K_SPACE
                            and btn.rect.collidepoint(pygame.mouse.get_pos())):
                    btn_sound.play()
                    if btn.title == 'ИГРАТЬ ЗАНОВО':
                        play_level(level_num)
                    elif btn.title == 'В ГЛАВНОЕ МЕНЮ':
                        now_screen = MENU_SCREEN

        game_over_sc.blit(game_over_bg, (0, 0))
        game_over_sc.blit(fog, (0, 0))
        game_over_sc.blit(GAME_OVER_TITLE, ((WIN_WIDTH - GAME_OVER_TITLE.get_width()) // 2, 80))
        game_over_buttons.draw(game_over_sc)
        game_over_buttons.update()

    # Код для меню паузы.
    elif now_screen == PAUSE_SCREEN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                btn_sound.play()
                play_level(level_num)

            for btn in pause_buttons:
                if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos)) \
                        or (event.type == pygame.KEYUP and event.key == pygame.K_SPACE
                            and btn.rect.collidepoint(pygame.mouse.get_pos())):
                    btn_sound.play()
                    if btn.title == 'ПРОДОЛЖИТЬ':
                        now_screen = LVL
                    elif btn.title == 'В ГЛАВНОЕ МЕНЮ':
                        now_screen = MENU_SCREEN
                        reset_level()

        pause_sc.blit(pause_bg, (0, 0))
        pause_sc.blit(PAUSE_TITLE, ((WIN_WIDTH - PAUSE_TITLE.get_width()) // 2, 80))
        pause_buttons.draw(pause_sc)
        pause_buttons.update()

    # Код для выигрыша.
    elif now_screen == WIN_SCREEN:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            for btn in pause_buttons:
                if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and btn.rect.collidepoint(event.pos)) \
                        or (event.type == pygame.KEYUP and event.key == pygame.K_SPACE
                            and btn.rect.collidepoint(pygame.mouse.get_pos())):
                    btn_sound.play()
                    if btn.title == 'СЛЕДУЮЩИЙ УРОВЕНЬ':
                        pass
                    elif btn.title == 'В ГЛАВНОЕ МЕНЮ':
                        now_screen = MENU_SCREEN

        win_sc.blit(win_bg, (0, 0))
        win_sc.blit(WIN_TITLE, ((WIN_WIDTH - WIN_TITLE.get_width()) // 2, 80))
        win_buttons.draw(win_sc)
        win_buttons.update()

    # Обновление экрана.
    screen.blit(SCREENS[now_screen], (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
