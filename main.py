# Импорт необходимых библиотек
import os
import pygame
import random

pygame.init()


def pause():
    """Функция для паузы игры."""

    global now_screen, pause_bg
    now_screen = PAUSE_SCREEN
    pause_bg = lvl_sc.copy()


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


class Monster(pygame.sprite.Sprite):
    """Класс монстра. Принимает значения координаты, атаки, здоровья."""

    def __init__(self, x, dmg, health, d):
        """Инициализация монстра."""

        super().__init__(monsters, all_sprites)
        self.image = random.choice(MNSTR_IMGS)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, Y0 + hero.rect.height - self.rect.height
        self.x0 = x
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
            elif self.ticks % 30 == 0:
                collider.health -= self.dmg
            self.ticks = (self.ticks + 1) % 120

    def reset(self):
        self.health = self.full_health
        self.rect.x = self.x0
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
            pl.rect.x = pl.pos0[0] + self.rect.x

        for en in self.enemies:
            en.rect.x -= self.diff
            en.x0 -= self.diff

    def reset(self):
        """Сброс уровня."""

        self.diff = 0
        self.rect.x = 0
        for enemy in self.enemies:
            enemy.reset()


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
        self.left = False
        self.jump = False
        self.platform = False
        self.moving = False
        self.jump_height = 50
        self.jump_count = 0
        self.vx = 4
        self.full_health = health
        self.health = health
        self.freq = 15
        self.ticks = 0
        self.dmg = dmg

    def move(self, x, y):
        """Движение персонажа."""

        self.moving = True
        if x < self.x and not self.left:
            self.left = True
        elif x > self.x:
            self.left = False

        if 6114 >= x >= 0:
            self.x = x
            if 0 <= self.x <= 625:
                self.rect.x = self.x
            elif 5489 <= self.x <= 6114:
                self.rect.x = (self.x + 256) % 1280

        if not pygame.sprite.spritecollideany(self, now_level.platforms) or self.rect.y == self.y0:
            self.safe_x = (self.x, self.rect.x)
        else:
            self.x, self.rect.x = self.safe_x

    def update(self):
        """Обновление координат персонажа при взаимодействии с ним."""

        if self.health <= 0 or self.rect.y == 530:
            game_over()

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

        if self.moving and self.ticks % self.freq == 0:
            self.image = pygame.transform.flip(PLAYER_IMGS[self.img_count], self.left, 0)
            self.img_count = (self.img_count + 1) % 2
            self.moving = False
        elif not self.moving:
            self.image = pygame.transform.flip(PLAYER_IMGS[2], self.left, 0)
        self.ticks = (self.ticks + 1) % 120

    def attack(self):
        """Функция атаки персонажа."""

        enemy = pygame.sprite.spritecollideany(self, now_level.enemies)
        if enemy and self.ticks % self.freq == 0:
            enemy.health -= self.dmg
        if self.ticks % (self.freq // 2) == 0:
            self.image = pygame.transform.flip(PLAYER_IMGS[self.img_count + 2], self.left, 0)
            self.img_count = (self.img_count + 1) % 2
        self.ticks = (self.ticks + 1) % 120

    def reset(self):
        """Сброс персонажа."""

        self.ticks = 0
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
now_screen = MENU_SCREEN
with open('sources/titres.txt', encoding='utf-8') as f:
    TITRES_TEXT = [i.strip() for i in f.readlines()]
BUTTON_FONT = pygame.font.SysFont('comicsansms', 40, bold=True)
TITRES_FONT = pygame.font.SysFont('comicsansms', 50)
MENU_BTN_TITLES = ['НАЧАТЬ ИГРУ', 'О НАС', 'ВЫЙТИ']
LEVEL_BTN_TITLES = ['Уровень 1', 'Уровень 2', 'Уровень 3']
PAUSE_BTN_TITLES = ['ПРОДОЛЖИТЬ', 'В ГЛАВНОЕ МЕНЮ']

# Инициализация групп спрайтов.
all_sprites = pygame.sprite.Group()
pause_buttons = pygame.sprite.Group()
menu_buttons = pygame.sprite.Group()
level_buttons = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
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
               pygame.transform.scale(load_image('slime.png'), (30, 80))]
MNSTR_IMGS = [load_image('slime.png')]
LVL_IMGS = [load_image('level_1.png')]

# Загрузка звуков и музыки.
btn_sound = load_sound(1, 'btn_sound.wav')

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
level_x = 0
now_level = None
LEVELS = [Level(pygame.transform.scale(LVL_IMGS[0], (6144, 1440)), [Monster(710, 10, 50, 200)],
                [Platform(2306, 496), Platform(2405, 476), Platform(2497, 454)])]
ticks = 0

# Экран для game over'а.
game_over_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
game_over_sc.set_alpha(150)
game_over_bg = LVL_IMGS[0]
fog = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
fog.fill((0, 0, 0))
fog.set_alpha(150)
GAME_OVER_TITLE = pygame.font.SysFont('comicsansms', 180, bold=True).render('GAME OVER', 1, pygame.Color('white'))
game_over_txt = pygame.font.SysFont('comicsansms', 50).render('Нажмите любую клавишу', 1, pygame.Color('white'))

# Экран паузы.
pause_sc = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

# Экраны.
SCREENS = {MENU_SCREEN: menu_screen, ABOUT_SCREEN: about_screen, LVL_CH_SCREEN: l_ch_screen, LVL: lvl_sc,
           GAME_OVER: game_over_sc, PAUSE_SCREEN: pause_sc}

# Инициализация кнопок и объединение их в группы.
for i in range(3):
    Button(menu_screen, menu_buttons, i * 150 + 250, MENU_BTN_TITLES[i], pygame.Color('white'))
    Button(l_ch_screen, level_buttons, i * 150 + 250, LEVEL_BTN_TITLES[i], pygame.Color('black'))
    if i < 2:
        Button(pause_sc, pause_buttons, i * 150 + 300, PAUSE_BTN_TITLES[i], pygame.Color('grey'))

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
                    if btn.title == 'Уровень 1':
                        now_level = LEVELS[0]
                        pygame.mouse.set_visible(False)
                        now_screen = LVL
                    elif btn.title == 'Уровень 2':
                        pass
                    elif btn.title == 'Уровень 3':
                        pass
                    level.add(now_level)

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
                pause()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and hero.rect.y == hero.y0:
            hero.jump = True
        if keys[pygame.K_d]:
            hero.move(hero.x + hero.vx, hero.rect.y)
        if keys[pygame.K_a]:
            hero.move(hero.x - hero.vx, hero.rect.y)
        if keys[pygame.K_TAB]:
            hero.rect.y -= 100
        if keys[pygame.K_LSHIFT]:
            hero.vx = 5
            hero.freq = 10
        else:
            hero.vx = 3
            hero.freq = 15
        if keys[pygame.K_w] and not(keys[pygame.K_d] or keys[pygame.K_a]):
            hero.attack()

        level.draw(lvl_sc)
        now_level.platforms.draw(lvl_sc)
        now_level.enemies.draw(lvl_sc)
        hero_group.draw(lvl_sc)
        if ticks == random.randint(0, 75):
            Cloud()
        clouds.draw(lvl_sc)
        hero_group.update()
        now_level.enemies.update()
        level.update()
        clouds.update()
        ticks = (ticks + 1) % 75

    # Код для GAME OVER.
    elif now_screen == GAME_OVER:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type in [pygame.MOUSEBUTTONUP, pygame.KEYUP]:
                now_screen = MENU_SCREEN

        game_over_sc.blit(game_over_bg, (0, 0))
        game_over_sc.blit(fog, (0, 0))
        game_over_sc.blit(GAME_OVER_TITLE, ((WIN_WIDTH - GAME_OVER_TITLE.get_width()) // 2, 80))
        game_over_sc.blit(game_over_txt, ((WIN_WIDTH - game_over_txt.get_width()) // 2, 300))

    # Обновление экрана
    screen.blit(SCREENS[now_screen], (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
