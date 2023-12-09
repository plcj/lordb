from pathlib import Path

import json
import pandas as pd

KW_COLUMNS = (
    'Keyword',
    'BC',
    'BW',
    'DE',
    'FR',
    'IO',
    'MT',
    'NX',
    'PZ',
    'SH',
    'SI'
)

VOCAB_COLUMNS = (
    'Vocab',
    'BC',
    'BW',
    'DE',
    'FR',
    'IO',
    'MT',
    'NX',
    'PZ',
    'SH',
    'SI'
)

DB_COLUMNS = (
    'cardCode',
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
    # function to load sets
    card_sets = [x for x in Path('data').glob('set*.json') if x.is_file()]
    sets = list()
    for card_set in card_sets:
        sets.append(pd.read_json(card_set))
    sets = pd.concat(sets)
    # convert region names to abbreviated names
    # multiple region cards count in both regions
    # print(sets)
    # sets.to_csv('database.csv', columns=DB_COLUMNS)

    # From this dataset, I just want a map:
    # region : {keyword : (maindeck_count, generated_count), keyword...}
    with open("data/globals-en_us.json", "r") as gd_file:
        global_data = json.load(gd_file)

    vocab = pd.DataFrame(global_data['vocabTerms'])
    keywords = pd.DataFrame(global_data['keywords'])
    vocab_table = pd.DataFrame(columns=VOCAB_COLUMNS)
    vocab_table['Vocab'] = vocab['name']
    keyword_table = pd.DataFrame(columns=KW_COLUMNS)
    keyword_table['Keyword'] = keywords['name']

    print(vocab_table)
    print(keyword_table)
