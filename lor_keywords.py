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
    card_sets = [x for x in Path('data').glob('set1*.json') if x.is_file()]
    sets = list()
    for card_set in card_sets:
        sets.append(pd.read_json(card_set))
    sets = pd.concat(sets)
    sets_kwr = pd.DataFrame(sets, columns=('cardCode','regions','keywords'))
    # convert region names to abbreviated names
    # multiple region cards count in both regions
    # print(sets)
    # sets.to_csv('database.csv', columns=DB_COLUMNS)

    # From this dataset, I just want a map:
    # region : { keyword : count },
    # region : ...
    with open("data/globals-en_us.json", "r") as gd_file:
        global_data = json.load(gd_file)

    # vocab = pd.DataFrame(global_data['vocabTerms'])
    # vocab_table = pd.DataFrame(columns=VOCAB_COLUMNS)
    # vocab_table['Vocab'] = vocab['name']
    # print(vocab_table)

    keywords = pd.DataFrame(global_data['keywords'])
    keyword_table = pd.DataFrame(columns=KW_COLUMNS)
    keyword_table[KW_COLUMNS[0]] = keywords['name']

    print(keyword_table)
    print(sets_kwr)

    print(f"1-region cards {len(sets_kwr[sets_kwr['regions'].apply(lambda x: len(x) == 1)])}")
    print(f"2-region cards {len(sets_kwr[sets_kwr['regions'].apply(lambda x: len(x) == 2)])}")

    print(f"1-keywords cards {len(sets_kwr[sets_kwr['keywords'].apply(lambda x: len(x) == 0)])}")
    print(f"2-keywords cards {len(sets_kwr[sets_kwr['keywords'].apply(lambda x: len(x) == 1)])}")
    print(f"3-keywords cards {len(sets_kwr[sets_kwr['keywords'].apply(lambda x: len(x) == 2)])}")
    print(f"4-keywords cards {len(sets_kwr[sets_kwr['keywords'].apply(lambda x: len(x) == 3)])}")


    sets_kwr['regions'] = sets_kwr['regions'].apply(lambda x : x if isinstance(x, list) else [x])
    sets_kwr['keywords'] = sets_kwr['keywords'].apply(lambda x : x if isinstance(x, list) else [x])
    sets_exploded = sets_kwr.explode('regions').explode('keywords')
    print(sets_exploded)

    sets_counts = sets_exploded.groupby(['regions', 'keywords']).size().reset_index(name='Counts')
    print(sets_counts)
    sets_counts.to_csv('kwxregion.csv')

