import json
import os

class ArmorManager:
    def __init__(self, path, equipment_ids=None):
        """
        path: ceļš uz armor JSON failu
        equipment_ids: saraksts ar ID, kurus Player aprīko sākumā (no character.json equipment["armor"])
        """
        self.armors = self.load_armors(path)
        self.current_armor = None

        # Aprīko pirmo bruņu ID no equipment saraksta
        if equipment_ids:
            for armor_id in equipment_ids:
                if self.equip_armor(armor_id):
                    break
        elif self.armors:
            # default: pirmā bruņu sarakstā
            self.current_armor = self.armors[0]

    def load_armors(self, path):
        """Ielādē bruņas no JSON faila"""
        if not os.path.exists(path):
            # print(f"[⚠️] Armor file not found: {path}")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            # print(f"[⚠️] Error loading armor file: {e}")
            return []

    def equip_armor(self, armor_id):
        """Aprīko konkrētas bruņas pēc ID"""
        armor = next((a for a in self.armors if a["id"] == armor_id), None)
        if armor:
            self.current_armor = armor
            # print(f"[🛡️] Equipped armor: {armor['name']} ({int(armor['damage-reduce']*100)}%)")
            return True
        else:
            # print(f"[⚠️] Armor '{armor_id}' not found!")
            return False

    def get_damage_reduction(self):
        """Atgriež damage reduction no pašreizējās bruņas"""
        if self.current_armor and "damage-reduce" in self.current_armor:
            return self.current_armor["damage-reduce"]
        return 0

    def get_armor_info(self):
        """Atgriež aprakstu par bruņām GUI"""
        if self.current_armor:
            return f"{self.current_armor['name']} ({int(self.current_armor['damage-reduce']*100)}%)"
        return "None"

    def get_current_armor_id(self):
        """Atgriež pašreiz aprīkoto armor ID"""
        if self.current_armor:
            return self.current_armor["id"]
        return None
