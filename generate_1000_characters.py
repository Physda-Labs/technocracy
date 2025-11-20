#!/usr/bin/env python3
"""
Generate 1000 Unique LPC Characters
Creates 1000 unique characters, each in their own directory with sprite sheets and a description.
"""

import os
import sys
import random
import json
import io
import contextlib
from simple_sprite_generator import generate_sprite, get_layers_for_animation, ANIMATIONS

# Color options for character generation (using only colors that exist in the sprite files)
SKIN_COLORS = ["light","light","light","light","light","light","light", "amber", "olive", "taupe", "bronze", "brown", "black"]
HAIR_COLORS = ["dark_brown", "dark_brown", "dark_brown", "dark_brown", "dark_brown", "blonde","blonde","blonde", "black", "white", "green",  "orange", "gray", "strawberry", "chestnut","chestnut","chestnut","chestnut", "raven"]
SHIRT_COLORS = ["white", "black", "blue", "red", "green", "yellow", "purple", "orange", "brown", "gray", "maroon", "teal", "navy", "lavender", "pink", "charcoal", "forest", "slate", "rose", "sky"]
LEG_COLORS = ["blue", "black", "brown", "gray", "tan", "green", "red", "white", "navy", "maroon", "purple", "teal", "charcoal", "forest", "slate"]
SHOE_COLORS = ["black", "brown", "white", "gray", "red", "blue", "maroon", "navy", "green", "tan", "leather"]
LEG_TYPES = ["pants", "skirt", "leggings"]

# Hair style names for descriptions
FEMALE_HAIR_NAMES = {
    "long": "long hair",
    "long_messy": "long messy hair",
    "long_messy2": "long messy hair",
    "long_straight": "long straight hair",
    "curly_long": "long curly hair",
    "curtains_long": "long curtained hair",
    "dreadlocks_long": "long dreadlocks",
    "pigtails": "pigtails",
    "pigtails_bangs": "pigtails with bangs",
    "lob": "a lob haircut",
    "bangslong": "long hair with bangs",
    "loose": "loose hair",
    "half_up": "half-up hair",
    "idol": "idol-style hair",
    "bangs": "bangs",
    "bangs_bun": "a bun with bangs",
    "bob": "a bob haircut",
    "bob_side_part": "a side-parted bob",
    "parted_side_bangs": "side-parted hair with bangs",
    "parted_side_bangs2": "side-parted hair with bangs"
}

MALE_HAIR_NAMES = {
    "natural": "natural hair",
    "plain": "plain hair",
    "bedhead": "bedhead hair",
    "messy1": "messy hair",
    "messy2": "messy hair",
    "messy3": "messy hair",
    "unkempt": "unkempt hair",
    "buzzcut": "a buzzcut",
    "balding": "balding hair",
    "shorthawk": "a short mohawk",
    "flat_top_straight": "a flat-top",
    "curly_short": "short curly hair",
    "curly_short2": "short curly hair",
    "bangsshort": "short hair with bangs",
    "bob": "a bob haircut",
    "bob_side_part": "a side-parted bob",
    "parted": "parted hair",
    "parted2": "parted hair",
    "parted3": "parted hair",
    "cowlick": "hair with a cowlick",
    "curtains": "curtained hair",
    "mop": "a mop of hair",
    "swoop": "swooped hair",
    "swoop_side": "side-swooped hair",
    "relm_short": "short hair",
    "high_and_tight": "a high and tight cut",
    "jewfro": "an afro",
    "afro": "an afro",
    "cornrows": "cornrows",
    "dreadlocks_short": "short dreadlocks",
    "twists_fade": "twisted hair with fade",
    "twists_straight": "straight twists"
}

def generate_character_description(gender, skin_color, hair_color, hair_style, shirt_color, leg_color, shoe_color, leg_type):
    """Generate a plain English description of the character."""
    
    # Gender descriptor
    gender_desc = "boy" if gender == "male" else "girl"
    
    # Get hair style name
    hair_names = MALE_HAIR_NAMES if gender == "male" else FEMALE_HAIR_NAMES
    hair_style_desc = hair_names.get(hair_style, "hair")
    
    # Skin descriptor
    skin_desc_map = {
        "light": "light",
        "amber": "amber",
        "olive": "olive",
        "taupe": "taupe",
        "bronze": "bronze",
        "brown": "brown",
        "black": "dark"
    }
    skin_desc = skin_desc_map.get(skin_color, skin_color)
    
    # Leg type descriptor
    leg_type_desc = {
        "pants": "trousers",
        "skirt": "skirt",
        "leggings": "leggings"
    }[leg_type]
    
    # Build description
    description = f"A {gender_desc} with {skin_desc} skin, {hair_color.replace('_', ' ')} {hair_style_desc}, "
    description += f"wearing a {shirt_color} shirt, {leg_color} {leg_type_desc}, and {shoe_color} shoes."
    
    return description

def generate_character(character_id, base_output_dir="char_x1000"):
    """Generate a single character with all animations in its own directory."""
    
    # Randomly select character attributes
    gender = random.choice(["male", "female"])
    skin_color = random.choice(SKIN_COLORS)
    hair_color = random.choice(HAIR_COLORS)
    shirt_color = random.choice(SHIRT_COLORS)
    leg_color = random.choice(LEG_COLORS)
    shoe_color = random.choice(SHOE_COLORS)
    leg_type = random.choice(LEG_TYPES) if gender == "female" else "pants"
    
    # Create character directory
    char_dir = os.path.join(base_output_dir, f"character_{character_id:04d}")
    os.makedirs(char_dir, exist_ok=True)
    
    # Store hair style to use consistently across animations
    hair_style_used = None
    
    # Generate sprites for each animation
    success_count = 0
    for animation in ANIMATIONS:
        layers, leg_type_result, hair_style = get_layers_for_animation(
            animation,
            gender=gender,
            skin_color=skin_color,
            hair_color=hair_color,
            shirt_color=shirt_color,
            leg_color=leg_color,
            shoe_color=shoe_color,
            leg_type=leg_type,
            hair_style=hair_style_used
        )
        
        # Store hair style from first animation
        if hair_style_used is None:
            hair_style_used = hair_style
        
        # Generate the sprite (suppress output by redirecting stdout)
        output_filename = f"{animation}.png"
        with contextlib.redirect_stdout(io.StringIO()):
            result = generate_sprite(layers, output_filename=output_filename, output_dir=char_dir)
        
        if result:
            success_count += 1
    
    # Generate character description
    description = generate_character_description(
        gender, skin_color, hair_color, hair_style_used,
        shirt_color, leg_color, shoe_color, leg_type
    )
    
    # Save description to text file
    desc_path = os.path.join(char_dir, "description.txt")
    with open(desc_path, 'w') as f:
        f.write(description)
    
    # Save detailed character data
    char_data = {
        "id": character_id,
        "gender": gender,
        "skin_color": skin_color,
        "hair_color": hair_color,
        "hair_style": hair_style_used,
        "shirt_color": shirt_color,
        "leg_color": leg_color,
        "shoe_color": shoe_color,
        "leg_type": leg_type,
        "description": description
    }
    
    data_path = os.path.join(char_dir, "character_data.json")
    with open(data_path, 'w') as f:
        json.dump(char_data, f, indent=2)
    
    return success_count == len(ANIMATIONS), description

def main():
    """Generate 1000 unique characters."""
    
    print("=" * 70)
    print("Generating 1000 Unique LPC Characters")
    print("=" * 70)
    print()
    
    base_dir = "char_x1000"
    os.makedirs(base_dir, exist_ok=True)
    
    success_count = 0
    failed_chars = []
    
    for i in range(1, 1001):
        print(f"[{i}/1000] Generating character {i:04d}...", end=" ")
        
        try:
            success, description = generate_character(i, base_dir)
            if success:
                print(f"✓")
                success_count += 1
                
                # Print description every 100 characters
                if i % 100 == 0:
                    print(f"    └─ {description}")
            else:
                print(f"✗ (partial)")
                failed_chars.append(i)
        except Exception as e:
            print(f"✗ Error: {e}")
            failed_chars.append(i)
    
    # Summary
    print()
    print("=" * 70)
    print("Generation Complete!")
    print("=" * 70)
    print(f"✓ Successfully generated: {success_count}/1000 characters")
    
    if failed_chars:
        print(f"✗ Failed characters: {len(failed_chars)}")
        print(f"  IDs: {failed_chars[:10]}{'...' if len(failed_chars) > 10 else ''}")
    
    print(f"\nCharacters saved to: {os.path.abspath(base_dir)}/")
    print("\nEach character directory contains:")
    print("  • idle.png - Idle animation spritesheet")
    print("  • walk.png - Walking animation spritesheet")
    print("  • sit.png - Sitting animation spritesheet")
    print("  • description.txt - Plain English description")
    print("  • character_data.json - Detailed character attributes")
    
    return 0 if success_count == 1000 else 1

if __name__ == "__main__":
    exit(main())
