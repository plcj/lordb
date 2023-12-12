from pathlib import Path

import pandas as pd

COLUMNS = (
    'cardCode',
    'formats',
    'collectible',
    'rarity',
    'regions',
    'name',
    'supertype',
    'type',
    'cost',
    'attack',
    'health',
    'keywords',
    'spellSpeed',
    'subtypes',
    'associatedCardRefs',
    'descriptionRaw',
    'levelupDescriptionRaw',
    'set'
)

if __name__ == '__main__':
    # Todo: function to download set data and extract it (optionally)
    card_sets = [x for x in Path('data').glob('set*.json') if x.is_file()]
    dfs = list()
    for card_set in card_sets:
        dfs.append(pd.read_json(card_set))
    all_sets = pd.concat(dfs)
    all_sets.to_csv('database.csv', columns=COLUMNS)
