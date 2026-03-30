def format_plural_singular(word, following_word):
    if following_word.lower()[-1] == 's':
        return word + 's'
    else:
        return word

def format_masculine_feminine(word):
    lower_word = word.lower()

    exceptions = {
        'sistema': 'el',
        'mapa': 'el',
        'día': 'el',
        'dirección': 'la',
        'edición': 'la',
    }

    if lower_word in exceptions:
        return exceptions[lower_word]

    article = ''
    if lower_word.endswith('a'):
        article = 'la'
    elif lower_word.endswith('as'):
        article = 'las'
    elif lower_word.endswith('os'):
        article = 'los'
    else:
        article = 'el'

    return article



# TODO function that removes any invalid character from a string for
# Alpinejs sake such as: ' '' & \n