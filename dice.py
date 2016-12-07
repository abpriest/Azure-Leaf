from random import randrange
from _static import *
from character import loadSingleCharSheet

class DiceParserException(Exception):
    pass

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
    
def rollDice(dice_string):
    """ Expects a string of format XdY where X is a number of dice to roll and
        Y is the number of sides to the die to be rolled.
    """
    dice = dice_string.split('d')
    try:
        test = int(''.join(dice))
        del test
    except ValueError as e: # player passed us something other than XdY
        print e
        raise DiceParserException(dice_string)
    else: # player passed us a roll without a d
        if dice[0] == dice_string:
            raise DiceParserException(dice_string)
    
    count, sides = int(dice[0]), int(dice[1])
    return sum([randrange(sides) + 1 for die in count])
    
def rollParser(msg, session):
    tokens = msg.split()
    for j in len(tokens):
        # rolling a skill check
        if tokens[j] == '/roll' and tokens[j+1] in skills:
            skillcheck = generateSkillCheck(
                loadCharacterSheets(session['username'], session['is_dm'])[0]['id'],
                tokens[j+1]
            )
            tokens[j] = tokens[j+1].upper()
            tokens[j+1] = str(skillcheck)
            
        # rolling some other kind of di(c)e
        elif tokens[j] == '/roll' and tokens[j+1] not in skills:
            try:
                outcome = rollDice(tokens[j+1])
            except DiceParserException as e:
                print e
                tokens[j+1] = str(e)
            else:
                tokens[j+1] = "%s, %s" % (tokens[j+1], outcome)
                
    return ' '.join(tokens) # return the message with the new values stitched in
    
    
    
    