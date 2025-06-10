embed
<drac2>
wild_cc = "Wild Shape"
status_cc = "Starry Form: Dragon"

# Flavor text with explicit newline escapes
flavor = "*A constellation of a wise dragon shimmers across Quortlo’s shell, the eyes glowing with ancient knowledge.*\n'I feel the wisdom of the stars guiding me... steady, like the roots of an old tree.'"

# Mechanical effect description
mechanical = "Bonus Action. When you make an Intelligence or a Wisdom check or a Constitution saving throw to maintain Concentration, you can treat a roll of 9 or lower on the d20 as a 10."

ch = character()
c = combat()

# Ensure the Wild Shape counter exists (max set here to 5)
if not ch.cc_exists(wild_cc):
    ch.create_cc_nx(wild_cc, 0, 5, "short", "bubble")

# Get current wild shapes remaining
curr_shapes = ch.get_cc(wild_cc)

if curr_shapes <= 0:
    diff = "**Underflow!**"
else:
    ch.mod_cc(wild_cc, -1)
    diff = "-1"
    if c:
        com = c.get_combatant(ch.name)
        if com:
            com.add_effect('Starry Form: Dragon', duration=100, desc=mechanical)

# Get the counter's bubble display (it should show your current count)
shapes_display = ch.cc_str(wild_cc)

# Build the description from parts
description = flavor + "\n\n" + mechanical
</drac2>
-title "{{status_cc}}"
-desc "{{description}}"
-f "Wild Shapes {{shapes_display}} {{diff}}"
-color 0x663399
-thumb https://i.imgur.com/AbPZp7J.jpeg
