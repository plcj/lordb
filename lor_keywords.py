from pathlib import Path

import json
import pandas as pd


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
    cards = pd.DataFrame(sets_df, columns=('cardCode','formats', 'regions','keywords'))
    ## https://github.com/RiotGames/developer-relations/issues/785
    # print(cards['formats'].apply(type).unique())
    # float_rows = cards['formats'].apply(lambda x: isinstance(x, float))
    # float_data = cards[float_rows]
    # print(float_data)
    cards = cards[cards['formats'].apply(lambda formats: isinstance(formats, list) and 'Standard' in formats)]
    # print(cards)
    # print(cards['regions'])
    # print(cards['keywords'])
    cards_exploded = cards.explode('regions').explode('keywords')
    cards_exploded = cards_exploded.fillna("None")
    # print(cards_exploded)

    kw_reg_count = cards_exploded.groupby(['regions', 'keywords']).size().reset_index(name='Count')
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

if __name__ == '__main__':

    sets = card_sets_df('test.json')
    global_data = globals_json()

    keywords_by_region = kw_count_by_region(sets, global_data)
    keywords_by_region.to_csv('keywords_by_region.csv')
