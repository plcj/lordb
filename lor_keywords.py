from pathlib import Path

import json
import pandas as pd

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

def card_sets_df(filename_pattern):
    """
    return card sets matching filename_pattern in the data directory as a dataframe
    """
    set_files = [x for x in Path('data').glob(filename_pattern) if x.is_file()]
    sets = list()
    for s in set_files:
        sets.append(pd.read_json(s))
    return pd.concat(sets)


def globals_json():
    """
    All globals. Each must be extracted to its own dataframe.
    """
    with open("data/globals-en_us.json", "r") as gd_file:
        global_data = json.load(gd_file)
    # print(global_data)
    return global_data


def region_nm_abbr_map(global_data):
    """
    return dict of name to abbreviation region mapping
    """
    r_map = pd.DataFrame(global_data['regions'], columns=('name', 'abbreviation'))
    r_map = r_map.set_index('name')['abbreviation'].to_dict()
    # print(r_map)
    return r_map


def kw_count_by_region(sets_df, global_data):
    """
    return a dataframe of keywords and their frequency in each region
    """
    cards_with_kw_and_reg = pd.DataFrame(sets_df, columns=('cardCode','regions','keywords'))
    # print(cards_with_kw_and_reg)
    # print(cards_with_kw_and_reg['regions'])
    # print(cards_with_kw_and_reg['keywords'])
    kw_and_reg_exploded = cards_with_kw_and_reg.explode('regions').explode('keywords')
    kw_and_reg_exploded = kw_and_reg_exploded.fillna("None")
    # print(kw_and_reg_exploded)

    kw_reg_count = kw_and_reg_exploded.groupby(['regions', 'keywords']).size().reset_index(name='Count')
    kw_reg_count['regions'] = kw_reg_count['regions'].replace(region_nm_abbr_map(global_data))
    # print(kw_reg_count)

    regions = kw_reg_count['regions'].unique()
    keywords = kw_reg_count['keywords'].unique()
    final_result_frame = pd.DataFrame([(r, k) for r in regions for k in keywords], columns=['regions', 'keywords'])
    result = pd.merge(final_result_frame, kw_reg_count, on=['regions', 'keywords'], how='left')
    result['Count'] = result['Count'].fillna(0).astype(int)
    # print(result)
    return result


# todo: function to download set data and extract it
# todo: look in description for keywords, not just the keywords list
# todo: filter by only cards in standard

if __name__ == '__main__':

    sets = card_sets_df('set*.json')
    global_data = globals_json()

    keywords_by_region = kw_count_by_region(sets, global_data)
    keywords_by_region.to_csv('keywords_by_region.csv')
