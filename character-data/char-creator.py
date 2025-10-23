import json
import os
import re

CLASS_DIR = "class"

def list_classes():
    return [d for d in os.listdir(CLASS_DIR) if os.path.isdir(os.path.join(CLASS_DIR, d))]

def load_class_data(class_name, level):
    class_path = os.path.join(CLASS_DIR, class_name)
    character_data = {"class": class_name, "level": level}

    # Ielādē spell count un detalizētos spelli
    spell_file = os.path.join(class_path, "spells.json")
    if os.path.exists(spell_file):
        with open(spell_file, "r") as f:
            spells_data = json.load(f)
    else:
        spells_data = {}

    for file_name in os.listdir(class_path):
        if file_name.endswith(".json") and file_name != "spells.json":
            key = file_name.replace(".json", "")
            file_path = os.path.join(class_path, file_name)
            with open(file_path, "r") as f:
                data = json.load(f)
                level_key = f"level{level}"
                value = data.get(level_key, None)

                # Apstrādā Spells-lvX ierakstus damage-type
                if key == "damage-type" and value:
                    spells_info = {}
                    new_value = []
                    for dt in value:
                        match = re.match(r"Spells-lv([\d\.]+)", dt)
                        if match:
                            lv_name = match.group(0)  # piemēram "Spells-lv2"
                            # count no spells.json
                            lv_number = match.group(1)  # "2"
                            available_spells = spells_data.get(f"level{lv_number}", [])
                            count = len(available_spells)
                            spells_info[lv_name] = count
                        else:
                            new_value.append(dt)
                    character_data[key] = new_value
                    if spells_info:
                        character_data["spells"] = spells_info
                else:
                    character_data[key] = value
    return character_data

def choose_from_list(options, prompt="Choose an option: "):
    for i, opt in enumerate(options):
        print(f"{i+1}. {opt}")
    while True:
        choice = input(prompt)
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]
        print("Invalid choice. Try again.")

def choose_spells(character, class_path):
    if "spells" not in character:
        return

    spells_file = os.path.join(class_path, "spells.json")
    if not os.path.exists(spells_file):
        return

    with open(spells_file, "r") as f:
        spells_data = json.load(f)

    selected_spells = {}

    for lv_key, count in character["spells"].items():
        match = re.search(r"lv([\d\.]+)", lv_key)
        if not match:
            continue
        lv_number = match.group(1)
        available_spells = spells_data.get(f"level{lv_number}", [])
        if not available_spells or count <= 0:
            continue

        print(f"\nYou can choose {count} spell(s) from {lv_key}:")
        for i, spell in enumerate(available_spells):
            print(f"{i+1}. {spell['name']} ({spell['type']}, damage: {spell['damage']})")

        chosen = []
        while len(chosen) < count:
            choice = input(f"Select spell {len(chosen)+1} by number (or skip): ").strip()
            if choice.lower() in ("skip", ""):
                break
            if choice.isdigit() and 1 <= int(choice) <= len(available_spells):
                spell_chosen = available_spells[int(choice)-1]
                if spell_chosen not in chosen:
                    chosen.append(spell_chosen)
                else:
                    print("Already chosen.")
            else:
                print("Invalid choice.")
        if chosen:
            selected_spells[lv_key] = chosen

    if selected_spells:
        character["spell"] = selected_spells

def create_character():
    classes = list_classes()
    if not classes:
        print("No classes found in 'class/' directory.")
        return

    print("Available classes:")
    class_name = choose_from_list(classes, "Select a class by number: ")

    class_path = os.path.join(CLASS_DIR, class_name)
    levels = set()
    for file_name in os.listdir(class_path):
        if file_name.endswith(".json") and file_name != "spells.json":
            with open(os.path.join(class_path, file_name), "r") as f:
                data = json.load(f)
                levels.update(int(k.replace("level","")) for k in data.keys() if k.replace("level","").isdigit())
    levels = sorted(levels)

    print("Available levels:", levels)
    while True:
        level_input = input("Select level: ").strip()
        if level_input.isdigit() and int(level_input) in levels:
            level = int(level_input)
            break
        print("Invalid level, try again.")

    character = load_class_data(class_name, level)

    name = input("Enter character name: ").strip()
    character["name"] = name if name else class_name

    choose_spells(character, class_path)

    with open("character.json", "w") as f:
        json.dump(character, f, indent=4)

    print("\nCharacter saved to character.json!")
    print(json.dumps(character, indent=4))

if __name__ == "__main__":
    create_character()
