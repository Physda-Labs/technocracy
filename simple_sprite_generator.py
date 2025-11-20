    #!/usr/bin/env python3
"""
Simple LPC Sprite Generator
This script generates a character sprite by layering PNG images from the spritesheets directory.
"""

from PIL import Image
import os
import datetime
import json
import random
import argparse

# Base directory for spritesheets
SPRITESHEET_DIR = "lpc-char-gen/spritesheets"

# Define the animations we want to generate
ANIMATIONS = ["idle", "walk", "sit"]

# Hair styles categorized by length (only styles with idle/walk/sit animations)
FEMALE_HAIR_STYLES = [
    "long", "long_messy", "long_messy2", "long_straight",
    "curly_long", "curtains_long", "dreadlocks_long",
    "pigtails", "pigtails_bangs", "lob",
    "bangslong", "loose", "half_up", "idol",
    "bangs", "bangs_bun", "bob", "bob_side_part",
    "parted_side_bangs", "parted_side_bangs2"
]

MALE_HAIR_STYLES = ["natural", "natural", "natural", "natural", "natural", "natural", "natural", "natural", 
    "plain", "bedhead", "messy1", "messy2", "messy3", "unkempt",
    "buzzcut", "balding", "shorthawk", "flat_top_straight",
    "curly_short", "curly_short2", "bangsshort", "bob", "bob_side_part",
    "parted", "parted2", "parted3", "cowlick", 
    "curtains", "mop", "swoop", "swoop_side", "relm_short",
    "high_and_tight", "jewfro", "afro", "cornrows", "dreadlocks_short",
    "twists_fade", "twists_straight", "natural"
]

def get_layers_for_animation(animation, gender="male", skin_color="light", hair_color="dark_brown", 
                             shirt_color="white", leg_color="blue", shoe_color="black", leg_type=None, hair_style=None):
    """
    Generate the layer paths for a specific animation with custom colors.
    
    Args:
        animation: Animation type (idle, walk, sit, etc.)
        gender: "male" or "female"
        skin_color: Skin tone (light, amber, olive, taupe, bronze, brown, black, etc.)
        hair_color: Hair color (dark_brown, blonde, black, red, etc.)
        shirt_color: Shirt color (white, black, blue, red, etc.)
        leg_color: Color for pants/skirt/leggings
        shoe_color: Shoe color (black, brown, white, etc.)
        leg_type: For female only - "pants", "skirt", or "leggings". If None, randomly chosen.
        hair_style: Hair style name. If None, randomly chosen based on gender.
    
    Returns:
        Tuple of (layer paths list, leg_type used, hair_style used)
    """
    
    # For female characters, randomly pick leg type if not specified
    if gender == "female" and leg_type is None:
        leg_type = random.choice(["pants", "skirt", "leggings"])
    elif gender == "male":
        leg_type = "pants"
    
    # Randomly select hair style based on gender if not specified
    if hair_style is None:
        if gender == "female":
            hair_style = random.choice(FEMALE_HAIR_STYLES)
        else:
            hair_style = random.choice(MALE_HAIR_STYLES)
    
    # Determine leg path based on type and animation availability
    # Note: Female body type uses "thin" for many leg garments that support idle/sit
    # Skirts have limited animations (walk, shoot, slash, spellcast, thrust, hurt only)
    leg_path = None
    
    # Determine the body type to use for legs
    # Female characters use "thin" body type for legs with idle/sit support
    leg_body_type = "thin" if gender == "female" else gender
    
    if leg_type == "skirt":
        # Skirts typically available for: walk, shoot, slash, spellcast, thrust, hurt
        if animation in ["walk", "shoot", "slash", "spellcast", "thrust", "hurt"]:
            leg_path = f"legs/skirts/plain/{gender}/{animation}/{leg_color}.png"
        # For idle/sit, use leggings as fallback (looks like tights/stockings under skirt)
        elif animation in ["idle", "sit"]:
            leg_path = f"legs/leggings/thin/{animation}/{leg_color}.png"
    elif leg_type == "leggings":
        # Leggings available for all animations using "thin" body type
        leg_path = f"legs/leggings/{leg_body_type}/{animation}/{leg_color}.png"
    else:  # pants
        # Pants: use gender-specific for walk, thin for idle/sit
        if animation in ["walk", "shoot", "slash", "spellcast", "thrust", "hurt"] and gender == "female":
            leg_path = f"legs/pants/{gender}/{animation}/{leg_color}.png"
        else:
            leg_path = f"legs/pants/{leg_body_type}/{animation}/{leg_color}.png"
    
    # Shoes: female characters should use "thin" body type from "revised" shoes for proper alignment
    # Male characters can use basic shoes
    if gender == "female":
        shoe_path = f"feet/shoes/revised/thin/{animation}/{shoe_color}.png"
    else:
        shoe_path = f"feet/shoes/basic/male/{animation}/{shoe_color}.png"
    
    # Build the layer templates
    layers = [
        f"body/bodies/{gender}/{animation}/{skin_color}.png",                            # Base body
        f"head/heads/human/{gender}/{animation}/{skin_color}.png",                       # Head
        f"head/nose/big/adult/{animation}/{skin_color}.png",                             # Nose
        f"eyes/human/adult/default/{animation}/brown.png",                               # Eyes
        f"hair/{hair_style}/adult/{animation}/{hair_color}.png",                         # Hair (with random style)
        f"torso/clothes/longsleeve/longsleeve/{gender}/{animation}/{shirt_color}.png",  # Shirt
    ]
    
    # Add leg layer if available for this animation
    if leg_path:
        layers.append(leg_path)
    
    # Add shoes
    layers.append(shoe_path)
    
    return layers, leg_type, hair_style

def generate_sprite(layers, output_filename="generated_character.png", output_dir="generated_sprites"):
    """
    Generate a character sprite by layering images.
    
    Args:
        layers: List of sprite layer paths relative to spritesheets directory
        output_filename: Name of the output PNG file
        output_dir: Directory to save the generated sprite
    """
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the base image (first layer)
    base_image = None
    composite_image = None
    
    print("Generating sprite...")
    print("-" * 50)
    
    for i, layer_path in enumerate(layers):
        full_path = os.path.join(SPRITESHEET_DIR, layer_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            print(f"⚠ Warning: Layer not found: {full_path}")
            print(f"  Skipping layer {i+1}/{len(layers)}: {layer_path}")
            continue
        
        try:
            # Load the layer image
            layer_img = Image.open(full_path).convert("RGBA")
            print(f"✓ Loaded layer {i+1}/{len(layers)}: {layer_path}")
            
            # Initialize base image with first valid layer
            if composite_image is None:
                composite_image = layer_img
                base_image = layer_img.copy()
            else:
                # Composite this layer on top of the base
                composite_image = Image.alpha_composite(composite_image, layer_img)
                
        except Exception as e:
            print(f"✗ Error loading {full_path}: {e}")
            continue
    
    if composite_image is None:
        print("\n✗ Error: No valid layers could be loaded!")
        return None
    
    # Save the generated sprite
    output_path = os.path.join(output_dir, output_filename)
    composite_image.save(output_path, "PNG")
    
    print("-" * 50)
    print(f"✓ Sprite saved to: {output_path}")
    print(f"  Size: {composite_image.size}")
    
    # Save a simple credits file
    timestamp = datetime.datetime.now().isoformat()
    credits = {
        "sprite_name": output_filename.replace(".png", ""),
        "generated": timestamp,
        "layers": layers,
        "note": "This is a generated sprite using the LPC assets. See CREDITS.csv for full attribution."
    }
    
    credits_path = os.path.join(output_dir, output_filename.replace(".png", "_info.json"))
    with open(credits_path, 'w') as f:
        json.dump(credits, f, indent=2)
    
    print(f"✓ Credits saved to: {credits_path}")
    
    return output_path

def main():
    """Main function to generate character sprites for multiple animations."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate LPC character sprites with custom colors')
    parser.add_argument('--gender', type=str, default='male', choices=['male', 'female'],
                       help='Character gender (default: male)')
    parser.add_argument('--skin', type=str, default='light',
                       help='Skin color: light, amber, olive, taupe, bronze, brown, black, etc. (default: light)')
    parser.add_argument('--hair', type=str, default='dark_brown',
                       help='Hair color: dark_brown, blonde, black, red, etc. (default: dark_brown)')
    parser.add_argument('--shirt', type=str, default='white',
                       help='Shirt color: white, black, blue, red, etc. (default: white)')
    parser.add_argument('--legs', type=str, default='blue',
                       help='Leg wear color (pants/skirt/leggings) (default: blue)')
    parser.add_argument('--shoes', type=str, default='black',
                       help='Shoe color: black, brown, white, etc. (default: black)')
    parser.add_argument('--leg-type', type=str, choices=['pants', 'skirt', 'leggings'],
                       help='For female only: specify pants, skirt, or leggings (default: random)')
    parser.add_argument('--output-dir', type=str, default='generated_sprites',
                       help='Output directory (default: generated_sprites)')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("LPC Simple Sprite Generator")
    print("=" * 50)
    print(f"\nConfiguration:")
    print(f"  Gender: {args.gender}")
    print(f"  Skin: {args.skin}")
    print(f"  Hair: {args.hair}")
    print(f"  Shirt: {args.shirt}")
    print(f"  Legs: {args.legs}")
    print(f"  Shoes: {args.shoes}")
    if args.gender == "female" and args.leg_type:
        print(f"  Leg Type: {args.leg_type}")
    elif args.gender == "female":
        print(f"  Leg Type: random")
    print()
    
    generated_files = []
    leg_type_used = None
    hair_style_used = None
    
    # Generate sprites for each animation
    for animation in ANIMATIONS:
        print(f"\n>>> Generating {animation.upper()} animation...")
        layers, leg_type, hair_style = get_layers_for_animation(
            animation,
            gender=args.gender,
            skin_color=args.skin,
            hair_color=args.hair,
            shirt_color=args.shirt,
            leg_color=args.legs,
            shoe_color=args.shoes,
            leg_type=args.leg_type if args.gender == "female" else None,
            hair_style=hair_style_used  # Use same hair style for all animations
        )
        
        if leg_type_used is None:
            leg_type_used = leg_type
        if hair_style_used is None:
            hair_style_used = hair_style
        
        result = generate_sprite(
            layers,
            output_filename=f"character_{args.gender}_{animation}.png",
            output_dir=args.output_dir
        )
        
        if result:
            generated_files.append(result)
        else:
            print(f"\n✗ Warning: Failed to generate {animation} sprite.")
    
    # Summary
    print("\n" + "=" * 50)
    if generated_files:
        print(f"✓ Success! Generated {len(generated_files)} animation(s):")
        for file in generated_files:
            print(f"  • {file}")
        print(f"\n  Hair style: {hair_style_used}")
        if args.gender == "female" and not args.leg_type:
            print(f"  Randomly selected leg type: {leg_type_used}")
    else:
        print("✗ Failed to generate any sprites.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
