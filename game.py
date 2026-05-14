import pygame
import sys
import random
import time
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from collections import deque

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GAME_DURATION = 300

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
BROWN = (139, 69, 19)

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2

class CharacterState(Enum):
    IDLE = 1
    MOVING = 2

class CustomerState(Enum):
    WAITING_TO_ENTER = 1
    WAITING_FOR_SEAT = 2
    SEATED = 3
    ORDERING = 4
    WAITING_FOR_FOOD = 5
    EATING = 6
    LEAVING = 7

@dataclass
class MenuItem:
    name: str
    cook_time: float
    points: int

MENU_ITEMS = [
    MenuItem("Burger", 8, 10),
    MenuItem("Pizza", 12, 15),
    MenuItem("Salad", 5, 8),
    MenuItem("Pasta", 10, 12),
    MenuItem("Chicken", 15, 20),
]

@dataclass
class Order:
    items: List[MenuItem]
    table_number: int
    start_time: float
    ready_time: Optional[float] = None
    delivered: bool = False

@dataclass
class Table:
    number: int
    x: int
    y: int
    occupied: bool = False
    customer: Optional['Customer'] = None
    order: Optional[Order] = None

@dataclass
class Customer:
    id: int
    state: CustomerState
    x: float
    y: float
    target_x: float
    target_y: float
    speed: float = 2.0
    seated_table: Optional[Table] = None
    order: Optional[List[MenuItem]] = None
    order_time: float = 0
    satisfaction: float = 1.0

class Character:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.state = CharacterState.IDLE
        self.speed = 3.0
        self.size = 15
        self.holding_order: Optional[Order] = None
        self.interaction_radius = 30
        self.holding_menu = False
        
    def move_to(self, x: float, y: float):
        self.target_x = x
        self.target_y = y
        self.state = CharacterState.MOVING
        
    def update(self, dt: float):
        if self.state == CharacterState.MOVING:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < self.speed * dt:
                self.x = self.target_x
                self.y = self.target_y
                self.state = CharacterState.IDLE
            else:
                ratio = (self.speed * dt) / distance
                self.x += dx * ratio
                self.y += dy * ratio
                
    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, BLUE, (int(self.x), int(self.y)), self.size)
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        if dx**2 + dy**2 > 1:
            dist = (dx**2 + dy**2)**0.5
            end_x = self.x + (dx / dist) * self.size
            end_y = self.y + (dy / dist) * self.size
            pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), 2)
            
        if self.holding_order:
            pygame.draw.circle(surface, RED, (int(self.x + 20), int(self.y)), 5)
        if self.holding_menu:
            pygame.draw.circle(surface, YELLOW, (int(self.x - 20), int(self.y)), 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Restaurant Manager - 5 Minute Challenge")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        self.game_state = GameState.PLAYING
        self.start_time = time.time()
        self.score = 0
        self.orders_completed = 0
        
        self.setup_floor_plan()
        self.character = Character(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.customers: List[Customer] = []
        self.next_customer_time = time.time() + random.uniform(2, 5)
        self.customer_id_counter = 0
        
        self.waiting_queue: deque = deque()
        self.kitchen_queue: List[Order] = []
        self.pending_deliveries: List[Order] = []
        
    def setup_floor_plan(self):
        self.entrance_x = 50
        self.entrance_y = 100
        
        self.kitchen_rect = pygame.Rect(900, 50, 250, 200)
        self.toilet_rect = pygame.Rect(900, 550, 150, 150)
        
        self.tables: List[Table] = []
        table_num = 1
        
        for row in range(2):
            for col in range(4):
                x = 150 + col * 150
                y = 200 + row * 200
                self.tables.append(Table(table_num, x, y))
                table_num += 1
                
    def spawn_customer(self):
        customer = Customer(
            id=self.customer_id_counter,
            state=CustomerState.WAITING_TO_ENTER,
            x=self.entrance_x,
            y=self.entrance_y,
            target_x=100,
            target_y=100
        )
        self.customer_id_counter += 1
        self.customers.append(customer)
        self.waiting_queue.append(customer)
        
    def update(self, dt: float):
        if self.game_state != GameState.PLAYING:
            return
            
        elapsed = time.time() - self.start_time
        
        if elapsed > GAME_DURATION:
            self.game_state = GameState.GAME_OVER
            return
            
        current_time = time.time()
        if current_time > self.next_customer_time and len(self.customers) < 20:
            self.spawn_customer()
            self.next_customer_time = current_time + random.uniform(2, 5)
            
        self.character.update(dt)
        self.update_customers(dt, current_time)
        self.update_kitchen(current_time)
        self.handle_character_interactions(current_time)
        
        self.customers = [c for c in self.customers if c.state != CustomerState.LEAVING]
        
    def update_customers(self, dt: float, current_time: float):
        for customer in self.customers:
            if customer.state == CustomerState.WAITING_TO_ENTER:
                customer.x += (100 - customer.x) * 0.05
                customer.y += (100 - customer.y) * 0.05
                
            elif customer.state == CustomerState.WAITING_FOR_FOOD:
                customer.satisfaction -= dt * 0.05
                customer.satisfaction = max(0, customer.satisfaction)
                
            elif customer.state == CustomerState.EATING:
                customer.order_time -= dt
                if customer.order_time <= 0:
                    customer.state = CustomerState.LEAVING
                    
            elif customer.state == CustomerState.LEAVING:
                if customer.seated_table:
                    customer.seated_table.occupied = False
                    customer.seated_table.customer = None
                    customer.seated_table.order = None
                    
    def update_kitchen(self, current_time: float):
        for order in self.kitchen_queue[:]:
            if order.ready_time is None:
                order.ready_time = current_time + sum(item.cook_time for item in order.items)
                
            if current_time >= order.ready_time and order.ready_time is not None:
                self.kitchen_queue.remove(order)
                self.pending_deliveries.append(order)
                
    def handle_character_interactions(self, current_time: float):
        if self.waiting_queue:
            first_customer = self.waiting_queue[0]
            dist = ((self.character.x - first_customer.x)**2 + 
                   (self.character.y - first_customer.y)**2)**0.5
            
            if dist < self.character.interaction_radius and self.character.state == CharacterState.IDLE:
                available_table = next((t for t in self.tables if not t.occupied), None)
                if available_table:
                    self.waiting_queue.popleft()
                    first_customer.state = CustomerState.SEATED
                    first_customer.seated_table = available_table
                    available_table.occupied = True
                    available_table.customer = first_customer
                    first_customer.target_x = available_table.x
                    first_customer.target_y = available_table.y
                    self.character.move_to(available_table.x, available_table.y)
                    
        for table in self.tables:
            if table.occupied and table.customer.state == CustomerState.SEATED:
                dist = ((self.character.x - table.x)**2 + 
                       (self.character.y - table.y)**2)**0.5
                
                if dist < self.character.interaction_radius and self.character.state == CharacterState.IDLE:
                    if not self.character.holding_menu:
                        self.character.holding_menu = True
                        table.customer.state = CustomerState.ORDERING
                        num_items = random.randint(1, 3)
                        order_items = random.sample(MENU_ITEMS, num_items)
                        table.customer.order = order_items
                        table.customer.order_time = 30
                        
                        order = Order(order_items, table.number, current_time)
                        table.order = order
                        self.kitchen_queue.append(order)
                        self.character.move_to(self.kitchen_rect.centerx, self.kitchen_rect.centery)
                        self.character.holding_menu = False
                        
        for order in self.pending_deliveries[:]:
            table = next((t for t in self.tables if t.number == order.table_number), None)
            if table and table.customer:
                dist = ((self.character.x - table.x)**2 + 
                       (self.character.y - table.y)**2)**0.5
                
                if dist < self.character.interaction_radius and self.character.state == CharacterState.IDLE:
                    if not self.character.holding_order:
                        self.character.holding_order = order
                        self.character.move_to(table.x, table.y)
                    elif self.character.holding_order == order:
                        table.customer.state = CustomerState.EATING
                        table.customer.satisfaction = 1.0
                        self.pending_deliveries.remove(order)
                        order.delivered = True
                        self.character.holding_order = None
                        self.score += sum(item.points for item in order.items)
                        self.orders_completed += 1
                        
    def draw(self):
        self.screen.fill(LIGHT_GRAY)
        self.draw_floor_plan()
        
        for table in self.tables:
            color = RED if table.occupied else GREEN
            pygame.draw.circle(self.screen, color, (table.x, table.y), 20)
            table_text = self.font_small.render(str(table.number), True, BLACK)
            self.screen.blit(table_text, (table.x - 5, table.y - 5))
            
        for customer in self.customers:
            pygame.draw.circle(self.screen, ORANGE, (int(customer.x), int(customer.y)), 10)
            
        self.character.draw(self.screen)
        
        kitchen_text = self.font_small.render(f"Kitchen: {len(self.kitchen_queue)}", True, BLACK)
        self.screen.blit(kitchen_text, (self.kitchen_rect.x, self.kitchen_rect.y - 20))
        
        delivery_text = self.font_small.render(f"Ready: {len(self.pending_deliveries)}", True, BLACK)
        self.screen.blit(delivery_text, (self.kitchen_rect.x, self.kitchen_rect.y - 40))
        
        queue_text = self.font_small.render(f"Waiting: {len(self.waiting_queue)}", True, BLACK)
        self.screen.blit(queue_text, (50, 30))
        
        self.draw_ui()
        
    def draw_floor_plan(self):
        pygame.draw.rect(self.screen, YELLOW, (20, 80, 60, 40))
        entrance_text = self.font_small.render("ENTER", True, BLACK)
        self.screen.blit(entrance_text, (25, 95))
        
        pygame.draw.rect(self.screen, BROWN, self.kitchen_rect)
        kitchen_text = self.font_medium.render("KITCHEN", True, WHITE)
        self.screen.blit(kitchen_text, (self.kitchen_rect.x + 40, self.kitchen_rect.y + 60))
        
        pygame.draw.rect(self.screen, LIGHT_BLUE, self.toilet_rect)
        toilet_text = self.font_small.render("TOILETS", True, BLACK)
        self.screen.blit(toilet_text, (self.toilet_rect.x + 20, self.toilet_rect.y + 60))
        
        pygame.draw.rect(self.screen, BLACK, (100, 150, 700, 400), 2)
        
    def draw_ui(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, GAME_DURATION - elapsed)
        minutes = int(remaining) // 60
        seconds = int(remaining) % 60
        
        score_text = self.font_large.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        timer_text = self.font_large.render(f"Time: {minutes}:{seconds:02d}", True, RED if remaining < 30 else BLACK)
        self.screen.blit(timer_text, (SCREEN_WIDTH - 300, 10))
        
        stats_text = self.font_medium.render(f"Orders: {self.orders_completed}", True, BLACK)
        self.screen.blit(stats_text, (10, SCREEN_HEIGHT - 30))
        
        if self.game_state == GameState.GAME_OVER:
            self.draw_game_over()
            
    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(DARK_GRAY)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("GAME OVER!", True, RED)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100))
        
        final_score_text = self.font_medium.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
        
        stats_text = self.font_medium.render(f"Orders Completed: {self.orders_completed}", True, WHITE)
        self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50))
        
        restart_text = self.font_small.render("Press SPACE to restart or ESC to quit", True, YELLOW)
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 150))
        
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if event.key == pygame.K_SPACE and self.game_state == GameState.GAME_OVER:
                    return self.restart()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.character.move_to(mouse_x, mouse_y)
                
        return True
        
    def restart(self):
        self.__init__()
        return True
        
    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            running = self.handle_input()
            self.update(dt)
            self.draw()
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
