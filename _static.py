# names of fields for data verification purposes
# made immutable and moved to global scope for function legibility

static_character_data = (
    'name',
    'class',
    'race',
    'level',
    'campaign',
    'id'
)

abilities = (
    'strength',
    'constitution',
    'dexterity',
    'intelligence',
    'wisdom',
    'charisma'
)
    
skills = (
    'Athletics',
    'Acrobatics',
    'Sleight_of_Hand',
    'Stealth',
    'Arcana',
    'History',
    'Investigation',
    'Nature',
    'Religion',
    'Animal_Handling',
    'Insight',
    'Medicine',
    'Perception',
    'Survival',
    'Deception',
    'Intimidation',
    'Performance',
    'Persuasion'
)

skill_ability_map = {
    'strength': (
        'Athletics',
    ), 
    'dexterity': (
        'Acrobatics',
        'Sleight_of_Hand',
        'Stealth'
    ), 
    'intelligence': (
        'Arcana',
        'History',
        'Investigation',
        'Nature',
        'Religion'
    ), 
    'wisdom': (
        'Animal_Handling',
        'Insight',
        'Medicine',
        'Perception',
        'Survival'
    ), 
    'charisma': (
        'Deception',
        'Intimidation',
        'Performance',
        'Persuasion'
    )
}