import pygame
import random
import math
import matplotlib.pyplot as plt

# 설정값 
SCREEN_WIDTH = 860     #1440 780
SCREEN_HEIGHT = 780
BG_COLOR = (255, 255, 255)
FOOD_COLOR = (255, 255, 0)
ORGANISM_COLOR = (0, 255, 0)
FONT_COLOR = (0, 0, 0)
FOOD_SIZE = 10

#개수
FOOD_COUNT = 90
INITIAL_ORGANISM_COUNT = 30

#돌연변이
MUTATION_PROBABILITY = 0.2
MUTATION_RANGE = 0.2

# 시뮬레이션 매개변수
x = 2.5 # 초안에 못먹으면 죽음
REPRODUCTION_TIME = x*1.3
MAX_LIFE_DURATION = x*1.5*0.028  # 개체의 최대 수명 (0.1->3.3초)

MIN_DISTANCE_FOR_REPRODUCTION = 180

#크기
SQUARE_SIZE = 1
initial_size_min = 5  # 초기 개체 크기 최솟값
initial_size_max = 21 # 초기 개체 크기 최댓값

#이속
initial_speed_min = 1  # 초기 개체 이동 속도 최솟값
initial_speed_max = 8 # 초기 개체 이동 속도 최댓값

#방향전환주기
direction_change_interval_min = 1400  # 초기 개체 방향 전환 주기 최솟값
direction_change_interval_max = 3000  # 초기 개체 방향 전환 주기 최댓값

organism_count_history = []
# 화면 초기화
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NS Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# 개체 클래스
class Organism(pygame.sprite.Sprite):
    def __init__(self, x, y, MAX_LIFE_DURATION):  #  매개변수 추가
        super().__init__()
        self.size = random.uniform(initial_size_min, initial_size_max)  # 초기 크기 랜덤 설정
        self.image = pygame.Surface((self.size, self.size))  # 이미지 크기를 설정한 크기로 생성
        self.image.fill(ORGANISM_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = random.uniform(initial_speed_min, initial_speed_max)  # 초기 속도 랜덤 설정
        self.direction = random.uniform(0, math.pi * 2)  # 초기 방향 랜덤 설정
        self.direction_change_interval = random.randint(direction_change_interval_min, direction_change_interval_max)  # 초기 방향 전환 주기 랜덤 설정
        self.life = MAX_LIFE_DURATION * 1000  # 밀리초 단위, 수명 설정
        self.last_direction_change = pygame.time.get_ticks()
        self.last_eat = pygame.time.get_ticks()
        self.birth_time = pygame.time.get_ticks()  # 생성 시간

    def update(self):
        self.life -= 1  # 수명 감소

        if self.life <= 0:  # 수명이 0 이하인 경우 개체 사망
            self.kill()

        if pygame.time.get_ticks() - self.last_direction_change > self.direction_change_interval:
            self.direction_change()
            self.last_direction_change = pygame.time.get_ticks()

        self.move()

        if pygame.time.get_ticks() - self.last_eat > x * 1000: #last_eat
            self.kill()

        if pygame.time.get_ticks() - self.birth_time > REPRODUCTION_TIME * 1000:
            self.birth()

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(ORGANISM_COLOR)


    def birth(self):
        # 가장 가까운 개체를 찾기 위한 변수 초기화
        closest_distance = float('inf')
        closest_organism = None

        # 현재 개체와의 거리를 계산하여 가장 가까운 개체 찾기
        for other_organism in organisms:
            if other_organism != self:
                distance = math.sqrt((self.rect.x - other_organism.rect.x) ** 2 + (self.rect.y - other_organism.rect.y) ** 2)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_organism = other_organism

        if closest_organism and closest_distance < MIN_DISTANCE_FOR_REPRODUCTION:
            for _ in range(2):
                # 가장 가까운 개체와의 평균 능력치를 계산하여 자식 개체의 능력치 설정
                new_size = (self.size+ closest_organism.size) / 2
                new_speed = (self.speed+ closest_organism.speed) / 2
                new_direction_change_interval = (self.direction_change_interval+ closest_organism.direction_change_interval) / 2

                # 새로운 자식 개체 생성
                new_organism = Organism(self.rect.x, self.rect.y, MAX_LIFE_DURATION)  # 수명은 최대 수명으로 설정
                new_organism.size = new_size
                new_organism.speed = new_speed
                new_organism.direction_change_interval = new_direction_change_interval

                # 돌연변이 적용
                if random.random() < MUTATION_PROBABILITY:
                    new_organism.size +=MUTATION_RANGE * new_organism.size
                    new_organism.speed += MUTATION_RANGE * new_organism.speed
                    new_organism.direction_change_interval -=MUTATION_RANGE * new_organism.direction_change_interval

                # 새로운 자식 개체를 그룹에 추가
                organisms.add(new_organism)
                all_sprites.add(new_organism)
                self.birth_time = pygame.time.get_ticks()


    def move(self):
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        # 맵 끝에 닿으면 반대 방향으로 움직임
        if new_x < 0 or new_x > SCREEN_WIDTH - SQUARE_SIZE:
            self.direction = math.pi - self.direction
            dx = math.cos(self.direction) * self.speed  # 방향 변경 후 새로운 이동량 계산
        if new_y < 0 or new_y > SCREEN_HEIGHT - SQUARE_SIZE:
            self.direction = -self.direction
            dy = math.sin(self.direction) * self.speed  # 방향 변경 후 새로운 이동량 계산

        self.rect.x += dx
        self.rect.y += dy

    def direction_change(self):
        self.direction = random.uniform(0, math.pi * 2)

    def eat(self):
        self.last_eat = pygame.time.get_ticks()

# 먹이 클래스
class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((FOOD_SIZE, FOOD_SIZE))
        self.image.fill(FOOD_COLOR)
        self.rect = self.image.get_rect(center=(x, y))

# 개체와 먹이 그룹
organisms = pygame.sprite.Group()
foods = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# 초기화면 생성
for _ in range(FOOD_COUNT):
    food = Food(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
    foods.add(food)
    all_sprites.add(food)

for _ in range(INITIAL_ORGANISM_COUNT):
    organism = Organism(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), MAX_LIFE_DURATION)
    organisms.add(organism)
    all_sprites.add(organism)

# 시뮬레이션 루프
running = True
start_time = pygame.time.get_ticks()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 사용자가 게임 창을 닫을 때
            running = False  # 시뮬레이션 종료

    screen.fill(BG_COLOR)

    # 시간 표시
    elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
    time_text = font.render("Time: {:.1f}".format(elapsed_time), True, FONT_COLOR)
    screen.blit(time_text, (10, 10))

    # 실시간 전체 개체 수 표시
    organism_count_text = font.render("Organisms: {}".format(len(organisms)), True, FONT_COLOR)
    screen.blit(organism_count_text, (10, 40))

    # 개체 업데이트
    all_sprites.update()

    # 개체 충돌 체크
    for organism in organisms:
        food_collisions = pygame.sprite.spritecollide(organism, foods, True)
        for food in food_collisions:
            organism.eat()
            new_food = Food(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            foods.add(new_food)
            all_sprites.add(new_food)

    # 화면 업데이트
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(30)

    organism_count_history.append(len(organisms))

pygame.quit()

plt.plot(organism_count_history)
plt.xlabel('Time')
plt.ylabel('Organism Count')
plt.title('Organism Population Over Time')
plt.show()