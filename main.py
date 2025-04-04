import pygame
import time
import random

# Inicializar Pygame
try:
    pygame.init()
except Exception as e:
    print(f"Error al inicializar Pygame: {e}")
    exit()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Intersección de Tráfico Inteligente")
except Exception as e:
    print(f"Error al configurar la pantalla: {e}")
    exit()

# Definimos colores
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)

# Cargar la imagen del coche
try:
    CAR_IMAGE = pygame.image.load("coche.png").convert_alpha()
    CAR_IMAGE = pygame.transform.scale(CAR_IMAGE, (80, 55))
except Exception as e:
    print(f"Error al cargar la imagen 'coche.png': {e}")
    exit()

# Reloj para controlar FPS
clock = pygame.time.Clock()

class TrafficLight:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.state = "red"
        self.timer = 0
        self.base_time = 5   # Tiempo base inicial
        self.min_time = 5    # Tiempo mínimo para verde
        self.max_time = 30   # Tiempo máximo para verde

    def update(self, state, timer):
        self.state = state
        self.timer = timer
        
    def adjust_time(self, car_count):
        """Ajusta el tiempo del semáforo basado en el conteo de autos en el carril"""
        self.base_time = max(self.min_time, min(self.max_time, 5 + car_count * 3))
        print(f"{self.direction}: car_count={car_count}, base_time={self.base_time}")
        
    def draw(self, screen):
        color = RED if self.state == "red" else (YELLOW if self.state == "yellow" else GREEN)
        pygame.draw.circle(screen, color, (self.x, self.y), 20)
        font = pygame.font.Font(None, 36)
        timer_text = font.render(str(self.timer), True, WHITE)
        screen.blit(timer_text, (self.x - 10, self.y + 30))

class Car:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 2
        self.stopped = False
        if self.direction == "bottom-left":
            self.image = CAR_IMAGE
        elif self.direction == "bottom-right":
            self.image = pygame.transform.rotate(CAR_IMAGE, 90)
        elif self.direction == "top-left":
            self.image = pygame.transform.rotate(CAR_IMAGE, 270)
        elif self.direction == "top-right":
            self.image = pygame.transform.rotate(CAR_IMAGE, 180)

    def update(self, traffic_lights, all_cars):
        for other_car in all_cars:
            if other_car != self and other_car.direction == self.direction:
                if self.direction == "top-left":
                    distance = other_car.y - self.y
                elif self.direction == "bottom-left":
                    distance = other_car.x - self.x
                elif self.direction == "bottom-right":
                    distance = self.y - other_car.y
                elif self.direction == "top-right":
                    distance = self.x - other_car.x
                if 0 < distance <= 85:
                    self.stopped = True
                    return

        for light in traffic_lights:
            if light.direction == self.direction:
                if self.direction == "top-left":
                    distance = light.y - self.y
                elif self.direction == "bottom-left":
                    distance = light.x - self.x
                elif self.direction == "bottom-right":
                    distance = self.y - light.y
                elif self.direction == "top-right":
                    distance = self.x - light.x
                
                if distance <= 50 and light.state in ["red", "yellow"]:
                    self.stopped = True
                    return
                else:
                    self.stopped = False

        if not self.stopped:
            if self.direction == "top-left":
                self.y += self.speed
            elif self.direction == "bottom-left":
                self.x += self.speed
            elif self.direction == "bottom-right":
                self.y -= self.speed
            elif self.direction == "top-right":
                self.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Crear semáforos
traffic_lights = [
    TrafficLight(WIDTH // 2 - 50, HEIGHT // 2 - 120, "top-left"),
    TrafficLight(280, HEIGHT // 2 + 50, "bottom-left"),
    TrafficLight(WIDTH // 2 + 50, HEIGHT // 2 + 120, "bottom-right"),
    TrafficLight(WIDTH - 280, HEIGHT // 2 - 50, "top-right"),
]

# Listas y contadores
cars = []
lane_counters = {"top-left": 0, "bottom-left": 0, "bottom-right": 0, "top-right": 0}

# Control del ciclo
current_light = 0
state = "red"
state_timer = 2
last_change = time.time()

# Bucle principal
running = True
while running:
    screen.fill(GRAY)

    # Dibujar carreteras y divisores
    pygame.draw.rect(screen, BLACK, (0, HEIGHT // 2 - 100, WIDTH, 200))
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 100, 0, 200, HEIGHT))
    pygame.draw.rect(screen, RED, (0, HEIGHT // 2 - 5, WIDTH // 2 - 100, 10))
    pygame.draw.rect(screen, RED, (WIDTH // 2 + 100, HEIGHT // 2 - 5, WIDTH // 2 - 100, 10))
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 5, 0, 10, HEIGHT // 2 - 100))
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 5, HEIGHT // 2 + 100, 10, HEIGHT // 2 - 100))

    # Actualizar semáforos
    now = time.time()
    elapsed = now - last_change
    if elapsed > state_timer:
        if state == "green":
            state = "yellow"
            state_timer = 3
        elif state == "yellow":
            state = "red"
            state_timer = 2
        elif state == "red":
            state = "green"
            current_light = (current_light + 1) % len(traffic_lights)
            car_count = lane_counters[traffic_lights[current_light].direction]
            traffic_lights[current_light].adjust_time(car_count)
            state_timer = traffic_lights[current_light].base_time
            print(f"Cambio a verde en {traffic_lights[current_light].direction}, state_timer={state_timer}")
        last_change = now

    # Actualizar y dibujar los semáforos
    for i, light in enumerate(traffic_lights):
        if i == current_light:
            light.update(state, int(state_timer - elapsed))
        else:
            light.update("red", 0)
        light.draw(screen)

    # Actualizar y dibujar coches
    cars_to_remove = []
    for i, car in enumerate(cars):
        car.update(traffic_lights, cars)
        car.draw(screen)
        if (car.direction == "top-left" and car.y > HEIGHT) or \
           (car.direction == "bottom-left" and car.x > WIDTH) or \
           (car.direction == "bottom-right" and car.y < -55) or \
           (car.direction == "top-right" and car.x < -80):
            cars_to_remove.append(i)

    for index in sorted(cars_to_remove, reverse=True):
        lane_counters[cars[index].direction] -= 1
        del cars[index]

    # Dibujar contadores (corregido)
    font = pygame.font.Font(None, 36)
    top_left_text = font.render(str(lane_counters["top-left"]), True, WHITE)
    screen.blit(top_left_text, (WIDTH // 2 - 80, 10))
    bottom_left_text = font.render(str(lane_counters["bottom-left"]), True, WHITE)
    screen.blit(bottom_left_text, (10, HEIGHT // 2 + 30))
    bottom_right_text = font.render(str(lane_counters["bottom-right"]), True, WHITE)
    screen.blit(bottom_right_text, (WIDTH // 2 + 30, HEIGHT - 25))
    top_right_text = font.render(str(lane_counters["top-right"]), True, WHITE)
    screen.blit(top_right_text, (WIDTH - 35, HEIGHT // 2 - 80))

    # Eventos
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    cars.append(Car(WIDTH // 2 - 80, 0, "top-left"))
                    lane_counters["top-left"] += 1
                elif event.key == pygame.K_d:
                    cars.append(Car(0, HEIGHT // 2 + 30, "bottom-left"))
                    lane_counters["bottom-left"] += 1
                elif event.key == pygame.K_w:
                    cars.append(Car(WIDTH // 2 + 30, HEIGHT - 55, "bottom-right"))
                    lane_counters["bottom-right"] += 1
                elif event.key == pygame.K_a:
                    cars.append(Car(WIDTH - 80, HEIGHT // 2 - 80, "top-right"))
                    lane_counters["top-right"] += 1
    except Exception as e:
        print(f"Error en el bucle de eventos: {e}")
        running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()