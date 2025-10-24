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

        # --- Ielādē NPC datus ---
        npc_data_path = os.path.join("npc", f"{self.id}.json")
        if os.path.exists(npc_data_path):
            with open(npc_data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.dialogue = data.get("dialogue", [])
            self.responses = data.get("responses", [])
            self.reactions = data.get("reactions", {})
        else:
            self.dialogue = ["..."]
            self.responses = []
            self.reactions = {}

        # --- Saglabāšanas fails ---
        self.progress_file = os.path.join("game_info", "npc.json")
        self._load_progress()

    # ==========================
    #       SAGLABĀŠANA
    # ==========================
    def _load_progress(self):
        if not os.path.exists("game_info"):
            os.makedirs("game_info")

        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r", encoding="utf-8") as f:
                all_progress = json.load(f)
            npc_progress = all_progress.get(self.id, {})
            self.dialogue_index = npc_progress.get("dialogue_index", 0)
            self.dialogue = npc_progress.get("dialogue", self.dialogue)
            self.responses = npc_progress.get("responses", self.responses)
        else:
            self._save_progress()  # izveido failu

    def _save_progress(self):
        if not os.path.exists("game_info"):
            os.makedirs("game_info")

        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r", encoding="utf-8") as f:
                all_progress = json.load(f)
        else:
            all_progress = {}

        all_progress[self.id] = {
            "dialogue_index": self.dialogue_index,
            "dialogue": self.dialogue,
            "responses": self.responses
        }

        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(all_progress, f, ensure_ascii=False, indent=4)

    # ==========================
    #       GALV. FUNKCIJAS
    # ==========================
    def draw(self, screen, camera):
        screen.blit(self.image, (self.rect.x - camera.offset.x, self.rect.y - camera.offset.y))

    def interact(self):
        """Atver dialogu, ja spēlētājs spiež T"""
        self.in_dialogue = True
        self.active_responses = self.responses
        self.selected_response = 0

    def handle_input(self, event):
        if not self.in_dialogue:
            return

        if event.type == pygame.KEYDOWN:
            # Ja NAV izvēļu, Enter pārslēdz nākamo teikumu
            if not self.active_responses:
                if event.key == pygame.K_RETURN:
                    self.dialogue_index += 1
                    if self.dialogue_index >= len(self.dialogue):
                        self.in_dialogue = False
                    self._save_progress()
                elif event.key == pygame.K_ESCAPE:
                    self.in_dialogue = False
                return

            # Ja IR izvēles
            if event.key == pygame.K_UP:
                self.selected_response = (self.selected_response - 1) % len(self.active_responses)
            elif event.key == pygame.K_DOWN:
                self.selected_response = (self.selected_response + 1) % len(self.active_responses)
            elif event.key == pygame.K_RETURN:
                self.apply_response()
            elif event.key == pygame.K_ESCAPE:
                self.in_dialogue = False

    def apply_response(self):
        """Izpilda spēlētāja izvēlēto atbildi un saglabā progresu"""
        if not self.active_responses:
            self.in_dialogue = False
            self._save_progress()
            return

        choice = self.active_responses[self.selected_response]
        if choice in self.reactions:
            reaction = self.reactions[choice]
            self.dialogue = reaction.get("dialogue", self.dialogue)
            self.responses = reaction.get("responses", [])
            self.active_responses = self.responses
            self.dialogue_index = 0
            if not self.responses:
                # Atļauj izlasīt līdz beigām
                self.in_dialogue = True
        else:
            self.in_dialogue = False

        self._save_progress()

    def draw_dialogue(self, screen):
        """Zīmē dialoga logu"""
        if not self.in_dialogue:
            return

        font = pygame.font.SysFont(None, 24)
        box_rect = pygame.Rect(20, screen.get_height() - 120, screen.get_width() - 40, 100)
        pygame.draw.rect(screen, (20, 20, 20), box_rect)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 2)

        # NPC teksts
        if self.dialogue and self.dialogue_index < len(self.dialogue):
            text = font.render(self.dialogue[self.dialogue_index], True, (255, 255, 255))
            screen.blit(text, (box_rect.x + 10, box_rect.y + 10))

        # Spēlētāja atbildes (ja ir)
        if self.active_responses:
            for i, response in enumerate(self.active_responses):
                color = (255, 255, 0) if i == self.selected_response else (200, 200, 200)
                r_text = font.render(response, True, color)
                screen.blit(r_text, (box_rect.x + 20, box_rect.y + 40 + i * 20))
