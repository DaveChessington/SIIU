def format_plural_singular(word, following_word):
    if following_word.lower()[-1] == 's':
        return word + 's'
    else:
        return word

def format_masculine_feminine(word):
    exceptions = {
        'sistema': 'el',
        'mapa': 'el',
        'día': 'el',
        'dirección': 'la',
        'edición': 'la',
    }

    if word.lower() in exceptions:
        return exceptions[word.lower()]

    article = ''
    if word.lower().endswith('a'):
        article = 'la'
    elif word.lower().endswith('as'):
        article = 'las'
    elif word.lower().endswith('os'):
        article = 'los'
    else:
        article = 'el'

    return article

# TODO function that removes any invalid character from a string for
# Alpinejs sake such as: ' '' & \n