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
    'Keep',
    'Look',
    'Never',
    'Only',
    'Remember',
    'Stay',
    'Take',
    'Try',
]


def wikihow(**params):
    return requests.get('https://www.wikihow.com/index.php', params=params)


def wikihow_api(**params):
    params.update({'format': 'json'})
    return requests.get('https://www.wikihow.com/api.php', params=params,
                        allow_redirects=False).json()


def get_advice(max_length=118):
    titles = []

    for attempt in range(10):
        article, = wikihow_api(action='query', list='random', rnnamespace=0,
                               rnlimit=1)['query']['random']
        titles.append(article['title'])
        article_id = article['id']
        content = wikihow_api(
            action='query', format='json', prop='revisions',
            curtimestamp=1, pageids=article_id, rvslots='*', rvprop='content',
        )['query']['pages'][
            str(article_id)]['revisions'][0]['slots']['main']['*']

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
            candidate = sentence + ' while playing Pokémon GO' + terminator
            if len(candidate) <= max_length:
                return candidate

    raise ValueError('could not find any good advice; tried:\n\n{}'.format(
        '\n'.join(titles)
    ))


if __name__ == '__main__':
    print(get_advice())
