import pygame
import time
import random

# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Intersección de Tráfico Inteligente")

# Definimos colores
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)

# Cargar la imagen del coche
CAR_IMAGE = pygame.image.load("coche.png").convert_alpha()
CAR_IMAGE = pygame.transform.scale(CAR_IMAGE, (80, 55))

# Reloj para controlar FPS
clock = pygame.time.Clock()

class TrafficLight:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.state = "red"
        self.timer = 0
        self.base_time = 10  # Tiempo base para verde
        self.min_time = 5    # Tiempo mínimo para verde
        self.max_time = 30   # Tiempo máximo para verde

    def update(self, state, timer):
        self.state = state
        self.timer = timer
        
    def adjust_time(self, car_count, total_cars):
        """Ajusta el tiempo del semáforo basado en el conteo de autos"""
        if total_cars == 0:
            self.base_time = self.min_time
        else:
            # Calcula el tiempo proporcional al tráfico
            proportion = car_count / total_cars
            self.base_time = max(self.min_time, min(self.max_time, int(proportion * 60)))
        
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
        # Verificar colisión con otros coches
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

        # Verificar semáforo
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

        # Mover el coche si no está detenido
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

def ajustar_semaforo(conteo_autos):
    """
    Ajusta el tiempo del semáforo en una intersección según el conteo de autos.

    Args:
        conteo_autos: Un diccionario donde las claves son los nombres de los carriles
                      y los valores son el número de autos detectados en cada carril.
                      Ejemplo: {'carril_1': 10, 'carril_2': 5}

    Returns:
        Un diccionario con los tiempos de semáforo para cada carril.
        Ejemplo: {'carril_1': 20, 'carril_2': 10}
    """
    tiempos_semaforo = {}
    total_autos = sum(conteo_autos.values())

    if total_autos == 0:
        # Manejar el caso donde no hay autos, quizás un tiempo mínimo por defecto
        for carril, conteo in conteo_autos.items():
            tiempos_semaforo[carril] = 5  # Ejemplo: 5 segundos
        return tiempos_semaforo

    for carril, conteo in conteo_autos.items():
        # Calcula un tiempo proporcional al número de autos en cada carril
        tiempo = int((conteo / total_autos) * 60)  # 60 segundos como tiempo base total
        tiempos_semaforo[carril] = max(tiempo, 5)  # Se asegura un mínimo de 5 segundos

    return tiempos_semaforo

def adjust_traffic_lights(traffic_lights, lane_counters):
    """Ajusta los tiempos de los semáforos basado en el conteo de autos"""
    # Usar la función ajustar_semaforo para calcular los tiempos
    tiempos_semaforo = ajustar_semaforo(lane_counters)

    # Asignar el tiempo ajustado al semáforo correspondiente según su dirección
    for light in traffic_lights:
        light.adjust_time(lane_counters[light.direction], sum(lane_counters.values()))
        # Aquí usamos el método adjust_time de TrafficLight para que sea consistente

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
adjustment_interval = 2  # Ajustar semáforos cada 10 segundos
last_adjustment = time.time()

# Bucle principal
running = True
while running:
    screen.fill(GRAY)

    # Dibujar carreteras y divisores (sin cambios aquí)
    pygame.draw.rect(screen, BLACK, (0, HEIGHT // 2 - 100, WIDTH, 200))
    pygame.draw.rect(screen, BLACK, (WIDTH // 2 - 100, 0, 200, HEIGHT))
    pygame.draw.rect(screen, RED, (0, HEIGHT // 2 - 5, WIDTH // 2 - 100, 10))
    pygame.draw.rect(screen, RED, (WIDTH // 2 + 100, HEIGHT // 2 - 5, WIDTH // 2 - 100, 10))
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 5, 0, 10, HEIGHT // 2 - 100))
    pygame.draw.rect(screen, RED, (WIDTH // 2 - 5, HEIGHT // 2 + 100, 10, HEIGHT // 2 - 100))

    # Ajustar tiempos de semáforos periódicamente
    now = time.time()
    if now - last_adjustment > adjustment_interval:
        adjust_traffic_lights(traffic_lights, lane_counters)
        last_adjustment = now

    # Actualizar semáforos
    elapsed = now - last_change
    if elapsed > state_timer:
        if state == "green":
            state = "yellow"
            state_timer = 3  # Tiempo fijo para amarillo
        elif state == "yellow":
            state = "red"
            state_timer = 2  # Tiempo fijo para rojo
        elif state == "red":
            state = "green"
            # Usar el base_time del semáforo actual según su dirección
            state_timer = traffic_lights[current_light].base_time
            current_light = (current_light + 1) % len(traffic_lights)
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

    # Dibujar contadores
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                cars.append(Car(WIDTH // 2 -80, 0, "top-left"))
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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()