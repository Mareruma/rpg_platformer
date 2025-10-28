import json
import os

class PlayerStats:
    def __init__(self):
        self.data = self.load_data()

        self.name = self.data.get("name", "Unknown")
        self.char_class = self.data.get("class", "Adventurer")
        self.level = self.data.get("level", 1)
        self.hp = self.data.get("hp", 10)
        self.damage = self.data.get("damage", 1)
        self.damage_type = self.data.get("damage-type", [])

        # Armor saraksts var būt tikai nosaukumi
        self.armor = self.data.get("armor", [])

        self.spells = self.data.get("spells", {})
        self.spell_data = self.data.get("spell", {})

        # ✅ Ielādējam equipment tieši no JSON faila
        self.equipment = self.data.get("equipment", {})
        if "armor" not in self.equipment:
            self.equipment["armor"] = []  # default tukšs saraksts

    def load_data(self):
        path = os.path.join(os.path.dirname(__file__), "../character-data/character.json")
        if not os.path.exists(path):
            # print("[⚠️] Nav atrasts character.json, izmanto noklusējuma vērtības.")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_spell_list(self):
        spells = []
        for level_key, spell_list in self.spell_data.items():
            spells.extend(spell_list)
        return spells
