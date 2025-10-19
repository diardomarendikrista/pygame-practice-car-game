import pygame, sys, random
from pygame.math import Vector2
import asyncio
# import pygwidgets

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (80, 80, 80)
WIDTH, HEIGHT = 1000, 820  # this is pixel

# auto adjust car position
ROAD_CENTER = WIDTH // 2
LANE_OFFSET = 150
CAR_Y_POSITION = 675

CAR_LEFT_POSITION = ROAD_CENTER - LANE_OFFSET
CAR_RIGHT_POSITION = ROAD_CENTER + LANE_OFFSET

class CAR:
    def __init__(self, position: Vector2, image):
        self.position = position
        self.image = image
        self.rect = self.image.get_rect(center=(self.position.x, self.position.y))

    def draw(self, screen):
        self.rect.center = (self.position.x, self.position.y)
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, RED, self.rect, 2)  # border for debug

    def update(self):
        pass

    def reset(self):
        pass


class CAR_ENEMY(CAR):
    def __init__(self, imgCarEnemy):
        super().__init__(
            Vector2(random.choice([CAR_LEFT_POSITION, CAR_RIGHT_POSITION]), -50),
            imgCarEnemy,
        )
        self.speed = 5

    def update(self):
        self.position.y += self.speed
        if self.position.y > HEIGHT + 200:
            self.position.y = -100
            self.position.x = random.choice([CAR_LEFT_POSITION, CAR_RIGHT_POSITION])
            self.speed += 1

            # if need speed limit
            # if self.speed > 5:
            #     self.speed = 5

    def reset(self):
        self.position.y = -100
        self.position.x = random.choice([CAR_LEFT_POSITION, CAR_RIGHT_POSITION])
        self.speed = 5


class CAR_PLAYER(CAR):
    def __init__(self, imgCarPlayer):
        super().__init__(Vector2(CAR_LEFT_POSITION, 675), imgCarPlayer)

    def reset(self):
        self.position = Vector2(CAR_LEFT_POSITION, 675)


class TRACK:
    def __init__(self):
        self.center_x = WIDTH // 2
        self.road_width = 600
        self.line_width = 5
        self.offset = 0

    def draw(self, screen):
        # gray asphalt
        pygame.draw.rect(
            screen,
            (GRAY),
            (
                self.center_x - self.road_width // 2,
                0,
                self.road_width,
                HEIGHT,
            ),
        )
        # road line
        pygame.draw.line(
            screen,
            WHITE,
            (self.center_x - self.road_width // 2 + 10, 0),
            (self.center_x - self.road_width // 2 + 10, HEIGHT),
            self.line_width,
        )
        pygame.draw.line(
            screen,
            WHITE,
            (self.center_x + self.road_width // 2 - 5, 0),
            (self.center_x + self.road_width // 2 - 5, HEIGHT),
            self.line_width,
        )
        # road mid line
        pygame.draw.line(
            screen,
            WHITE,
            (self.center_x, 0),
            (self.center_x, HEIGHT),
            self.line_width * 2,
        )


class GAME:
    def __init__(
        self, screen, imgCarPlayer, imgCarEnemy, bgm, sfx_drift, sfx_car_crash
    ):
        self.player = CAR_PLAYER(imgCarPlayer)
        self.enemy = CAR_ENEMY(imgCarEnemy)
        self.track = TRACK()
        self.state = "STOPPED"
        self.score = 0
        self.highest_score = 0
        # because of pygbag, we need to pass all of this
        self.screen = screen
        self.bgm = bgm
        self.sfx_drift = sfx_drift
        self.sfx_car_crash = sfx_car_crash

    def draw(self):
        self.track.draw(self.screen)
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)

    def update(self):
        if self.state != "STOPPED":
            self.enemy.update()
            self.check_collision_with_enemy()
            self.score += 1

    def check_collision_with_enemy(self):
        if self.player.rect.colliderect(self.enemy.rect):
            self.sfx_car_crash.play()
            self.game_over()

    def start(self):
        self.state = "RUNNING"
        self.score = 0
        self.enemy.reset()
        self.bgm.play(-1)

    def game_over(self):
        self.state = "STOPPED"
        self.bgm.stop()
        if self.score > self.highest_score:
            self.highest_score = self.score + 1


async def main():
    # for pygbag, all initialization must be here
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Car Game")

    imgCarPlayer = pygame.image.load("assets/image/car-player.png").convert_alpha()
    imgCarEnemy = pygame.image.load("assets/image/car-enemy.png").convert_alpha()

    bgm = pygame.mixer.Sound("assets/audio/bgm.ogg")
    sfx_drift = pygame.mixer.Sound("assets/audio/drift.ogg")
    sfx_car_crash = pygame.mixer.Sound("assets/audio/car-crash.ogg")

    bgm.set_volume(0.2)
    sfx_drift.set_volume(0.5)
    sfx_car_crash.set_volume(0.3)

    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, 10)

    game = GAME(screen, imgCarPlayer, imgCarEnemy, bgm, sfx_drift, sfx_car_crash)

    font_judul = pygame.font.Font(None, 50)
    font_skor = pygame.font.Font(None, 40)

    # game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_LEFT
                    and game.player.position.x > CAR_LEFT_POSITION
                ):
                    game.player.position = Vector2(CAR_LEFT_POSITION, 675)
                    sfx_drift.play()
                if (
                    event.key == pygame.K_RIGHT
                    and game.player.position.x < CAR_RIGHT_POSITION
                ):
                    game.player.position = Vector2(CAR_RIGHT_POSITION, 675)
                    sfx_drift.play()
                if game.state == "STOPPED":
                    game.start()

            if event.type == SCREEN_UPDATE:
                game.update()

        screen.fill(GREEN)
        game.draw()

        # pywidget not working, so we use pygame font
        title_surf = font_judul.render("CAR GAME", True, BLACK)
        score_text = f"Your Score: {game.score}"
        score_surf = font_skor.render(score_text, True, BLACK)
        high_score_text = f"Highest Score: {game.highest_score}"
        high_score_surf = font_skor.render(high_score_text, True, BLACK)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 10))
        screen.blit(score_surf, (10, 30))
        screen.blit(high_score_surf, (WIDTH - high_score_surf.get_width() - 10, 30))

        pygame.display.update()
        await asyncio.sleep(0)


asyncio.run(main())
