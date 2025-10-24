import pygame
import json
import os

class NPC:
    def __init__(self, obj):
        self.id = obj.type  # piem. npc1
        self.name = getattr(obj, "name", self.id)
        self.rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
        self.image = pygame.image.load("textures/map/npc.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(obj.width), int(obj.height)))
        self.dialogue_index = 0
        self.in_dialogue = False
        self.active_responses = []
        self.selected_response = 0

        # Ielādē NPC JSON datus
        path = os.path.join("npc", f"{self.id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.dialogue = data.get("dialogue", [])
            self.responses = data.get("responses", [])
            self.reactions = data.get("reactions", {})
        else:
            self.dialogue = ["..."]
            self.responses = []
            self.reactions = {}

    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))

    def interact(self):
        self.in_dialogue = True
        self.dialogue_index = 0
        self.active_responses = self.responses
        self.selected_response = 0

    def handle_input(self, event):
        if not self.in_dialogue:
            return

        # Izvēļu kontrole
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_response = (self.selected_response - 1) % len(self.active_responses)
            elif event.key == pygame.K_DOWN:
                self.selected_response = (self.selected_response + 1) % len(self.active_responses)
            elif event.key == pygame.K_RETURN:
                self.apply_response()

            elif event.key == pygame.K_ESCAPE:
                self.in_dialogue = False

    def apply_response(self):
        """Izpilda spēlētāja izvēlēto atbildi"""
        if not self.active_responses:
            self.in_dialogue = False
            return

        choice = self.active_responses[self.selected_response]
        if choice in self.reactions:
            self.dialogue = self.reactions[choice].get("dialogue", self.dialogue)
            self.responses = self.reactions[choice].get("responses", [])
            self.active_responses = self.responses
            self.dialogue_index = 0
            if not self.responses:
                self.in_dialogue = False
        else:
            self.in_dialogue = False

    def draw_dialogue(self, screen):
        """Zīmē dialoga logu"""
        if not self.in_dialogue:
            return

        font = pygame.font.SysFont(None, 24)
        box_rect = pygame.Rect(20, screen.get_height() - 120, screen.get_width() - 40, 100)
        pygame.draw.rect(screen, (20, 20, 20), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)

        if self.dialogue:
            text = font.render(self.dialogue[self.dialogue_index], True, (255, 255, 255))
            screen.blit(text, (box_rect.x + 10, box_rect.y + 10))

        # Spēlētāja atbildes
        for i, response in enumerate(self.active_responses):
            color = (255, 255, 0) if i == self.selected_response else (200, 200, 200)
            r_text = font.render(response, True, color)
            screen.blit(r_text, (box_rect.x + 20, box_rect.y + 40 + i * 20))
