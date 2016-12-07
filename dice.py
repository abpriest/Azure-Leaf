from random import randrange
from _static import *
from character import loadSingleCharSheet

def generateSkillCheck(char_id, skill):
    """generates a value for a skill check for a character with the id passed"""
    print skill
    roll = randrange(0, 20) + 1 # generate [0, 19] and add 1
    char = loadSingleCharSheet(char_id)[0]
    ability = ''
    
    for key in skill_ability_map:
        if skill in skill_ability_map[key]:
            ability = key
            break
    print ability
    roll += abilityModifier(char[ability])
    
    print(char)
    if char[skill.lower()]:
        roll += proficiencyBonus(char['level'])
    return roll
    
def generateAbility(threshold=7):
    """ Returns a randomly generated integer between threshold and 18 according
        to a 4d6d1 dice distribution.
    """
    score = 0
    while score <= threshold:
        # ability score = sum(4d6, drop lowest die)
		score = sum(sorted([randrange(6)+1 for die in xrange(4)])[1:])
    return score
    
def proficiencyBonus(level, expertise=False):
    """ Return proficiency bonus for a given level to apply to a skill. """
    return (((level - 1) / 4) + 2) * (1, 2)[expertise]
    
def abilityModifier(score):
    """ Generate ability score modifier """
    return (score - 10) / 2