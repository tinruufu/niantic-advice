import re
from random import choice

import requests


PREFIXES = [
    'Always',
    'Avoid',
    'Be',
    'Do not',
    "Don't",
    'Expect',
    'Feel',
    'Get',
    'Look',
    'Never',
    'Only',
    'Stay',
    'Take',
    'Try',
]


def wikihow(**params):
    return requests.get('http://www.wikihow.com/index.php', params=params,
                        allow_redirects=False)


def get_advice(max_length=118):
    titles = []

    for attempt in range(10):
        title = (
            wikihow(title='Special:Randomizer').headers['Location']
            .replace('http://www.wikihow.com/', '')
        )
        titles.append(title)

        content = wikihow(title=title, action='raw').content.decode('utf-8')

        # replace link syntax with raw text
        content = re.sub(r'\[\[[^|:\]]+\|([^\]]+)\]\]', lambda m: m.group(1),
                         content)
        # ignore emphasis
        content = re.sub(r"('''?)(.*)\1", lambda m: m.group(2),
                         content)

        matches = [(s, t) for s, t in re.findall(
            r'(?:\. +|[\*#>]|^) *'  # start of line or end of previous sentence
            r'('  # start sentence-matching group
            r'\b(?:[A-Z])'  # the sentence should start with a capital letter
            r"['a-zA-Z0-9 ]+"  # sentence content, avoiding most punctuation
            r')'  # end sentence-matching group
            r'(\.|!)',  # retain punctuation from the end of the sentence
            content,
        ) if any((s.startswith(p + ' ') for p in PREFIXES))]

        if matches:
            sentence, terminator = choice(matches)
            candidate = sentence + ' while playing Pokémon GO' + terminator
            if len(candidate) <= max_length:
                return candidate

    raise ValueError('could not find any good advice; tried:\n\n{}'.format(
        '\n'.join(titles)
    ))


if __name__ == '__main__':
    print(get_advice())
