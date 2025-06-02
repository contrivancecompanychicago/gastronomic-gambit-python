import time
import random

# --- Game State Variables ---
game_state = {
    'restaurant_name': "The Obsidian Spatula",
    'condition': "Dilapidated",
    'funds': 200,
    'reputation': 0,
    'game_time': 10 * 60,  # In minutes, starting 10:00 AM
    'inventory': {},  # {'ingredient_name': quantity}
    'kitchen_layout': [
        ['Fridge', 'Wall', 'Wall'],
        ['Stove', 'Prep Table', 'Oven'],
        ['Crates', 'Wall', 'Wall']
    ],
    'kitchen_efficiency_bonus': 0, # % bonus
    'unlocked_recipes': ['Spaghetti & Meatballs'],
    'current_dish_blueprint': {
        'dish_name': '',
        'nodes': [],
        'flavor_profile': {},
        'final_quality': 0,
        'prep_time': 0
    },
    'grimoire_unlocked_entries': [],
    'has_met_thorne': False,
    'current_day': 1
}

# --- Game Data ---
INGREDIENTS = {
    'Tomatoes': {'price': 5, 'quality': 'High', 'flavor': {'Sweet': 2, 'Sour': 1, 'Earthy': 1}},
    'Onions': {'price': 3, 'quality': 'Standard', 'flavor': {'Aromatic': 2, 'Sweet': 1}},
    'Ground Beef': {'price': 12, 'quality': 'Standard', 'flavor': {'Savory': 3, 'Umami': 2, 'Earthy': 1}},
    'Pasta': {'price': 4, 'quality': 'Basic', 'flavor': {}},
    'Garlic': {'price': 2, 'quality': 'Standard', 'flavor': {'Aromatic': 3, 'Spicy': 1}}
}

RECIPES = {
    'Spaghetti & Meatballs': {
        'ingredients_needed': {'Ground Beef': 1, 'Onions': 1, 'Garlic': 2, 'Tomatoes': 1, 'Pasta': 1},
        'base_quality': 50,
        'base_prep_time': 15,
        'cost_per_dish': 25,
        'blueprint_steps': [
            {'name': 'Meatballs (Ground Beef, Onion, Garlic)', 'flavor': {'Savory': 3, 'Aromatic': 2, 'Umami': 2}, 'time': 5, 'quality': 20, 'ingredients_consumed': {'Ground Beef': 1, 'Onions': 1, 'Garlic': 1}},
            {'name': 'Sauce (Tomatoes, Garlic)', 'flavor': {'Sweet': 2, 'Sour': 1, 'Aromatic': 1, 'Umami': 1}, 'time': 7, 'quality': 25, 'ingredients_consumed': {'Tomatoes': 1, 'Garlic': 1}},
            {'name': 'Pasta (Boil & Plate)', 'flavor': {}, 'time': 3, 'quality': 5, 'ingredients_consumed': {'Pasta': 1}}
        ]
    }
}

CUSTOMER_TYPES = [
    {'type': 'Elderly Couple', 'preference': {'Savory': 3, 'Umami': 2, 'Traditional': 1}, 'patience': 80, 'review_base': "Ah, just like mama used to make. Excellent!"},
    {'type': 'Young Professional', 'preference': {'Fast': 1, 'Balanced': 1}, 'patience': 60, 'review_base': "Decent. Got the job done."},
    {'type': 'Foodie Novice', 'preference': {'Aromatic': 2, 'Sweet': 1}, 'patience': 70, 'review_base': "Interesting flavors!"},
    {'type': 'Generic Customer', 'preference': {}, 'patience': 50, 'review_base': "It was food."},
    {'type': 'Picky Critic', 'preference': {'Complex': 1, 'Unique': 1}, 'patience': 90, 'review_base': "Hmm, room for improvement.", 'is_critic': True}
]

# --- Utility Functions ---
def clear_screen():
    # Clears the terminal screen
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear_screen()
    print("-" * 50)
    print(f"| {title.center(46)} |")
    print("-" * 50)

def print_game_state():
    print("\n" + "=" * 50)
    print(f"Restaurant: {game_state['restaurant_name']} ({game_state['condition']})")
    print(f"Funds: ${game_state['funds']}")
    print(f"Reputation: {game_state['reputation']}/100 ({get_reputation_rank(game_state['reputation'])})")
    print(f"Day: {game_state['current_day']}")
    print(f"Time: {format_time(game_state['game_time'])}")
    print("--- Inventory ---")
    if game_state['inventory']:
        for item, qty in game_state['inventory'].items():
            print(f"- {item}: {qty}")
    else:
        print("Empty")
    print("=" * 50 + "\n")

def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    ampm = "AM" if hours < 12 else "PM"
    formatted_hours = hours % 12
    if formatted_hours == 0: formatted_hours = 12
    return f"{formatted_hours:02d}:{mins:02d} {ampm}"

def get_reputation_rank(rep):
    if rep < 20: return 'Unknown'
    if rep < 50: return 'Local Favorite'
    if rep < 80: return 'Rising Star'
    return 'Culinary Legend'

def get_player_choice(prompt, options):
    while True:
        print("\n" + prompt)
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        try:
            choice = int(input("Enter your choice: "))
            if 1 <= choice <= len(options):
                return choice
            else:
                print("Invalid choice. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def advance_time(minutes):
    game_state['game_time'] += minutes
    if game_state['game_time'] >= 24 * 60:
        game_state['game_time'] %= (24 * 60)
        game_state['current_day'] += 1 # Advance to next day if time wraps
        print(f"\n--- A new day begins! Day {game_state['current_day']} ---\n")
    time.sleep(0.5) # Pause for readability

# --- Game Phases / Scenes ---

def intro_phase():
    print_header("Welcome to The Gastronomic Gambit")
    print("The air in \"The Obsidian Spatula\" is thick with the scent of dust and faded dreams. Sunlight, weak through grime-streaked windows, illuminates motes dancing in the stillness. A single, rickety fan creaks overhead, stirring little more than nostalgic silence. This is it: your inheritance from the enigmatic Chef Alistair Blackwood.")
    print("\nYou glance at the worn brass plaque above the doorframe: \"The Obsidian Spatula - Where Flavor Transcends.\" A laughably grand statement for what is now a crumbling edifice. Your eyes fall on a heavy, leather-bound journal on the counter, its pages brittle with age – Blackwood’s Gastronomic Grimoire. Beside it, a single, gleaming kitchen knife, its handle carved from what looks like dark, volcanic rock. The only thing of true value, perhaps.")
    print("\nObjective: Assess the Kitchen and Prepare for Opening")
    print("\nYou tap the screen (conceptually), and the view shifts to a top-down layout of your dilapidated kitchen. It's small, inefficient, and clearly hasn't seen a deep clean in decades.")
    print("\nA tutorial prompt appears: \"Drag and drop kitchen stations to optimize your workflow. Efficiency impacts prep time and dish quality. You can only move items into adjacent empty squares (represented by 'Wall' or 'Crates').\"")
    input("\nPress Enter to continue...")
    kitchen_layout_phase()

def print_kitchen_layout():
    print("\n--- Current Kitchen Layout ---")
    for row in game_state['kitchen_layout']:
        print("| " + " | ".join(f"{item:<10}" for item in row) + " |")
    print("------------------------------")
    print(f"Current Kitchen Efficiency Bonus: +{game_state['kitchen_efficiency_bonus']}%")

def kitchen_layout_phase():
    print_header("Kitchen Layout")
    print_kitchen_layout()

    options = []
    # Find movable items
    movable_items = []
    for r_idx, row in enumerate(game_state['kitchen_layout']):
        for c_idx, item in enumerate(row):
            if item in ['Fridge', 'Stove', 'Crates']: # Items that can be moved
                movable_items.append((item, r_idx, c_idx))

    # Add specific move options
    if any(item == 'Fridge' for item, _, _ in movable_items):
        options.append("Move Fridge closer to Prep Table (Efficiency +5%)")
    if any(item == 'Stove' for item, _, _ in movable_items):
        options.append("Move Stove closer to Prep Table (Efficiency +3%)")
    options.append("Proceed to Market (Done with layout)")

    choice = get_player_choice("What do you want to do?", options)

    if choice == 1 and "Move Fridge" in options[0]: # Assumes order
        move_item_in_kitchen('Fridge', 'Prep Table', 5)
        kitchen_layout_phase() # Loop back to allow more changes
    elif choice == 2 and "Move Stove" in options[1]: # Assumes order
        move_item_in_kitchen('Stove', 'Prep Table', 3)
        kitchen_layout_phase() # Loop back to allow more changes
    elif (choice == 1 and "Proceed to Market" in options[0]) or \
         (choice == 2 and "Proceed to Market" in options[1]) or \
         (choice == 3 and "Proceed to Market" in options[2]): # Handles different button orders
        go_to_market_phase()

def move_item_in_kitchen(item_to_move, target_item_name, efficiency_gain):
    item_pos = None
    target_pos = None
    empty_spot_pos = None

    # Find positions
    for r_idx, row in enumerate(game_state['kitchen_layout']):
        for c_idx, item in enumerate(row):
            if item == item_to_move:
                item_pos = (r_idx, c_idx)
            elif item == target_item_name:
                target_pos = (r_idx, c_idx)
            elif item == 'Wall' or item == 'Crates': # Eligible empty spots
                empty_spot_pos = (r_idx, c_idx) # Just find the first one for simplicity

    if not item_pos:
        print(f"Error: {item_to_move} not found in layout.")
        return
    if not target_pos:
        print(f"Error: {target_item_name} not found in layout.")
        return

    # Check if already adjacent (simplified check)
    if abs(item_pos[0] - target_pos[0]) + abs(item_pos[1] - target_pos[1]) == 1:
        print(f"{item_to_move} is already adjacent to {target_item_name}. No change made.")
        return

    # Simple move logic: swap with an 'empty' spot that's adjacent to target
    # This is highly simplified. A real game needs robust pathfinding/placement.
    moved = False
    for r_diff in [-1, 0, 1]:
        for c_diff in [-1, 0, 1]:
            if abs(r_diff) + abs(c_diff) == 1: # Only adjacent (not diagonal)
                check_r, check_c = target_pos[0] + r_diff, target_pos[1] + c_diff
                if 0 <= check_r < len(game_state['kitchen_layout']) and 0 <= check_c < len(game_state['kitchen_layout'][0]):
                    if game_state['kitchen_layout'][check_r][check_c] in ['Wall', 'Crates']:
                        # Perform the swap: move item_to_move to check_r, check_c
                        # And move what was at check_r, check_c to item_pos
                        temp_item = game_state['kitchen_layout'][check_r][check_c]
                        game_state['kitchen_layout'][check_r][check_c] = item_to_move
                        game_state['kitchen_layout'][item_pos[0]][item_pos[1]] = temp_item
                        game_state['kitchen_efficiency_bonus'] += efficiency_gain
                        print(f"Successfully moved {item_to_move}! Kitchen Efficiency +{efficiency_gain}%.")
                        moved = True
                        break
        if moved:
            break

    if not moved:
        print(f"Could not find a valid adjacent spot to move {item_to_move} near {target_item_name}.")
    input("Press Enter to continue...")

def go_to_market_phase():
    print_header("The Daily Market")
    advance_time(30) # Travel time
    print_game_state()
    print("You step out onto the cobbled street. The bustling Daily Market awaits.")
    print("Objective: Acquire Basic Ingredients for a Simple Dish")

    cart = {}

    while True:
        print("\n--- Market Offerings ---")
        market_options = []
        item_keys = list(INGREDIENTS.keys())
        for i, item_name in enumerate(item_keys):
            item_data = INGREDIENTS[item_name]
            market_options.append(f"{item_name} (${item_data['price']}/unit) - {item_data['quality']} Quality")
        market_options.append("Confirm Purchases and Return to Kitchen")
        market_options.append("Cancel (Return to Kitchen without buying)")

        choice = get_player_choice("What do you want to buy?", market_options)

        if choice == len(market_options): # Cancel
            print("You decide not to buy anything for now.")
            break
        elif choice == len(market_options) - 1: # Confirm
            total_cost = sum(cart[item] * INGREDIENTS[item]['price'] for item in cart)
            if total_cost > game_state['funds']:
                print(f"Insufficient funds! You need ${total_cost} but only have ${game_state['funds']}. Adjust your cart.")
                cart = {} # Clear cart if not enough funds, forcing re-selection
                input("Press Enter to continue...")
            else:
                game_state['funds'] -= total_cost
                for item, qty in cart.items():
                    game_state['inventory'][item] = game_state['inventory'].get(item, 0) + qty
                print(f"Purchases confirmed! Spent ${total_cost}.")
                print("Your current cart has been added to your inventory.")
                cart = {}
                break # Exit market loop
        else:
            selected_item_name = item_keys[choice - 1]
            try:
                qty = int(input(f"How many units of {selected_item_name} do you want to buy? "))
                if qty > 0:
                    item_cost = qty * INGREDIENTS[selected_item_name]['price']
                    if item_cost > game_state['funds']:
                        print(f"You don't have enough money for {qty} units of {selected_item_name} (Cost: ${item_cost}).")
                    else:
                        cart[selected_item_name] = cart.get(selected_item_name, 0) + qty
                        print(f"Added {qty} {selected_item_name} to cart. Current cart: {cart}")
                else:
                    print("Quantity must be greater than 0.")
            except ValueError:
                print("Invalid quantity. Please enter a number.")
        input("Press Enter to continue...")

    advance_time(30) # Return trip
    print("You return to \"The Obsidian Spatula\" with your ingredients.")
    go_to_dish_creation_phase()

def go_to_dish_creation_phase():
    print_header("Dish Creation: Spaghetti & Meatballs")
    print_game_state()
    print("You're focusing on the \"Dish Blueprint\" system. Every dish is a canvas!")
    print("Objective: Create Your First Dish Blueprint (Spaghetti & Meatballs)")

    blueprint = {
        'dish_name': 'Spaghetti & Meatballs',
        'nodes': [],
        'flavor_profile': {},
        'final_quality': RECIPES['Spaghetti & Meatballs']['base_quality'],
        'prep_time': RECIPES['Spaghetti & Meatballs']['base_prep_time']
    }
    game_state['current_dish_blueprint'] = blueprint

    print("\n--- Current Dish Blueprint Status ---")
    print(f"Flavor Profile: {blueprint['flavor_profile']}")
    print(f"Quality: {blueprint['final_quality']}/100")
    print(f"Prep Time: {blueprint['prep_time']} minutes")
    print("\nAvailable Ingredients (from Inventory):")
    if game_state['inventory']:
        for item, qty in game_state['inventory'].items():
            print(f"- {item}: {qty}")
    else:
        print("No ingredients in inventory!")

    options = []
    recipe_steps = RECIPES['Spaghetti & Meatballs']['blueprint_steps']
    for step in recipe_steps:
        options.append(f"Add: {step['name']}")
    options.append("Finalize Dish Blueprint")

    while True:
        choice = get_player_choice("Choose blueprint step:", options)
        if choice == len(options): # Finalize
            if not blueprint['nodes']: # Must have added at least one step
                 print("Your dish blueprint is too simple! Add at least one component.")
                 continue
            break
        else:
            selected_step = recipe_steps[choice - 1]
            can_add = True
            for ing, qty_needed in selected_step['ingredients_consumed'].items():
                if game_state['inventory'].get(ing, 0) < qty_needed:
                    print(f"Not enough {ing} to add {selected_step['name']}!")
                    can_add = False
                    break
            if can_add:
                blueprint['nodes'].append(selected_step['name'])
                for ing, qty_consumed in selected_step['ingredients_consumed'].items():
                    game_state['inventory'][ing] -= qty_consumed

                for flavor, val in selected_step['flavor'].items():
                    blueprint['flavor_profile'][flavor] = blueprint['flavor_profile'].get(flavor, 0) + val
                blueprint['final_quality'] += selected_step['quality']
                blueprint['prep_time'] += selected_step['time']
                print(f"Added '{selected_step['name']}'.")
                print(f"Current Quality: {blueprint['final_quality']}, Current Prep Time: {blueprint['prep_time']}")
                input("Press Enter to continue...")
            else:
                input("Press Enter to continue...")


    print(f"\nYour \"{blueprint['dish_name']}\" blueprint is complete!")
    print(f"Calculated Quality: {blueprint['final_quality']}/100")
    print(f"Calculated Prep Time: {blueprint['prep_time']} minutes")
    advance_time(blueprint['prep_time']) # Time for blueprint creation
    dialogue_phase()

def dialogue_phase():
    print_header("An Unexpected Visitor")
    print("\nA sharp rap echoes from the front door. You walk out to find a stern-faced woman in a pristine, tailored suit standing on your doorstep.")
    print("Her name tag reads: \"Cassian Thorne - Aethelred's Acquisitions.\"")

    print("\n\"So, the prodigal heir returns,\" she states, her voice cold as ice. \"I am Cassian Thorne. Your relative, Alistair Blackwood, was... an associate. This establishment, however, is a stain on the culinary landscape. Aethelred's is prepared to make a generous offer to acquire this property. For old times' sake, of course.\"")
    print("\nShe glances around, a dismissive sneer touching her lips. \"This place is a relic. Your grandfather's 'flavor alchemy' was a fool's errand. True efficiency, true taste, comes from standardization. From science. From us.\"")
    print("\nShe hands you a sleek, silver business card. \"Think about it. We can make this all go away. Or you can flounder, just like Blackwood did in the end.\"")
    print("\nShe turns and walks away, her footsteps echoing ominously down the street.")
    game_state['has_met_thorne'] = True

    print("\nYou hold the silver business card. Her words echo in your mind. This is more than just about cooking. It's about a battle for flavor itself.")
    input("\nPress Enter to continue...")
    game_state['game_time'] = 18 * 60 # Set time to 6:00 PM for dinner service
    dinner_service_phase()

def dinner_service_phase():
    print_header("Dinner Service Begins!")
    print_game_state()
    print("The clock ticks forward to 6:00 PM. The first customers begin to trickle in.")
    print("Objective: Serve Customers during Dinner Service")

    served_customers = 0
    total_reputation_gain = 0
    dishes_to_serve = 5 # Simplified: serve 5 dishes for the demo

    for i in range(dishes_to_serve):
        customer = random.choice(CUSTOMER_TYPES)
        print(f"\n--- Serving Customer {i+1} ({customer['type']}) ---")
        time.sleep(1)

        review = ""
        rep_gain = 0
        dish_quality_adjusted = game_state['current_dish_blueprint']['final_quality'] * (1 + game_state['kitchen_efficiency_bonus'] / 100)

        # Base review based on quality
        if dish_quality_adjusted >= 70:
            review = customer['review_base']
            rep_gain = 10
        elif dish_quality_adjusted >= 40:
            review = customer['review_base']
            rep_gain = 3
        else:
            review = customer['review_base']
            rep_gain = -5

        # Preference matching (simplified)
        preference_match_score = 0
        for flavor, customer_pref_val in customer['preference'].items():
            if game_state['current_dish_blueprint']['flavor_profile'].get(flavor, 0) >= customer_pref_val:
                preference_match_score += 1
        if preference_match_score > 0:
            rep_gain += (preference_match_score * 2)
            review += f" (Customer enjoyed specific flavors! +{preference_match_score*2} rep)"

        game_state['funds'] += RECIPES['Spaghetti & Meatballs']['cost_per_dish']
        game_state['reputation'] += rep_gain
        total_reputation_gain += rep_gain
        served_customers += 1

        print(f"Customer's Comment: \"{review}\"")
        print(f"Reputation Change: {rep_gain}, Funds: +${RECIPES['Spaghetti & Meatballs']['cost_per_dish']}")
        input("Press Enter to continue...")

    advance_time(180) # 3 hours for dinner service
    print("\n--- End of Dinner Service ---")
    print(f"The evening progresses. You served {served_customers} dishes.")
    print(f"At {format_time(game_state['game_time'])}, the last customer leaves.")
    input("Press Enter to continue...")
    end_day_summary_phase(total_reputation_gain)

def end_day_summary_phase(total_reputation_gain):
    print_header("End of Day Summary")
    print(f"Total Revenue Today: ${game_state['funds']}")
    print(f"Daily Reputation Change: {total_reputation_gain}")
    print(f"Current Total Reputation: {game_state['reputation']}/100 ({get_reputation_rank(game_state['reputation'])})")

    print("\n--- Grimoire Entry Unlocked ---")
    print("Chef Blackwood's Notes: \"The Essence of Savory\"")
    print("The foundation of all comfort. Found in meats, aged cheeses, fermented grains. When truly mastered, it can calm the anxious mind and evoke forgotten joys. Thorne believes it can be synthesized. He is gravely mistaken. The genuine article demands respect for the earth and the beast.")
    print("New Blueprint Action Unlocked: \"Slow Roast\" (improves Savory and Umami attributes over longer cook time).")
    game_state['grimoire_unlocked_entries'].append("The Essence of Savory")

    print("\nObjective: Research \"Slow Roast\" Technique and Upgrade Kitchen Station.")
    print("Objective: Investigate Blackwood's Hidden Cellar.")

    print("\nYou look at the silver business card from Cassian Thorne, then at the glowing new entry in the Gastronomic Grimoire. A cold shiver runs down your spine, but it's quickly replaced by a spark of excitement. This isn't just about cooking. It's about a battle for flavor itself.")

    print("\n--- DEMO END ---")
    print("Thank you for playing the Python demo of The Gastronomic Gambit: A Culinary Legacy!")
    input("Press Enter to exit.")
    exit()

# --- Game Start ---
if __name__ == "__main__":
    intro_phase()
