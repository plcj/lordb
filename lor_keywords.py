import re
from pathlib import Path

import json
import pandas as pd


def card_sets_df(filename_pattern):
    """
    return card sets matching filename_pattern in the data directory as a dataframe
    """
    set_files = [x for x in Path('data').glob(filename_pattern) if x.is_file()]
    all_sets = list()
    for s in set_files:
        all_sets.append(pd.read_json(s))
    return pd.concat(all_sets)


def globals_json():
    """
    All globals. Each must be extracted to its own dataframe.
    """
    with open("data/globals-en_us.json", "r") as gd_file:
        lor_globals = json.load(gd_file)
    # todo filter globals.name == Missing Translation
    # print(global_data)
    return lor_globals


def keyword_refs(lor_globals):
    """
    return list of all keywordRefs
    """
    refs = pd.DataFrame(lor_globals['keywords'])
    refs = refs['nameRef']
    # print(refs)
    return refs


def description_keywords(description, keywords):
    """
    return list of keywords found in description
    """
    matches = re.findall(r'<link=keyword.(.*?)>', description)
    matches = [match.replace(" ", "") for match in matches] # because <link=keyword.Last Breath> is a thing
    # print(matches)
    return matches


def region_abbreviation_map(lor_globals):
    """
    return dict of name to abbreviation region mapping
    """
    r_map = pd.DataFrame(lor_globals['regions'], columns=['nameRef', 'abbreviation'])
    r_map = r_map.set_index('nameRef')['abbreviation'].to_dict()
    # print(r_map)
    return r_map


def kw_count_by_region(sets_df, lor_globals):
    """
    return a dataframe of keywords and their frequency in each region
    """
    cards = pd.DataFrame(sets_df, columns=['cardCode', 'formats', 'regionRefs', 'keywordRefs', 'description'])

    # Limit cards to those in Standard
    standard_cards = cards[cards['formats'].apply(lambda formats: isinstance(formats, list) and 'Standard' in formats)].copy()
    ## Why isinstance(formats, list)?
    ## https://github.com/RiotGames/developer-relations/issues/785
    # print(cards['formats'].apply(type).unique())
    # float_rows = cards['formats'].apply(lambda x: isinstance(x, float))
    # print(cards[float_rows])

    # todo filter out associated cards of champions. Formats are not updated on them, so they can have Standard in their formats even if the champ is not in Standard.
    # todo filter RU region

    # Collect keywords from both description and keywordRefs
    keywords = keyword_refs(lor_globals)
    standard_cards['all_keywords'] = standard_cards['description'].apply(lambda description: description_keywords(description, keywords)) + standard_cards['keywordRefs']

    # Remove duplicates
    standard_cards['all_keywords'] = standard_cards['all_keywords'].apply(lambda x: list(set(x)))

    # Explode keywords and regions
    kw_by_region = standard_cards.explode('regionRefs').explode('all_keywords')
    kw_by_region = kw_by_region.fillna("None")
    # print(kw_by_region)

    # Count keywords by region
    kw_by_reg_counted = kw_by_region.groupby(['regionRefs', 'all_keywords']).size().reset_index(name='Count')

    # Replace regionRefs with abbreviations
    kw_by_reg_counted['regionRefs'] = kw_by_reg_counted['regionRefs'].replace(region_abbreviation_map(lor_globals))
    # print(kw_by_reg_counted)

    regions = kw_by_reg_counted['regionRefs'].unique()
    final_result_frame = pd.DataFrame([(r, k) for r in regions for k in keywords], columns=['regionRefs', 'all_keywords'])
    result = pd.merge(final_result_frame, kw_by_reg_counted, on=['regionRefs', 'all_keywords'], how='left')
    result['Count'] = result['Count'].fillna(0).astype(int)
    # print(result)
    return result


# todo: optionally download set data and extract it

if __name__ == '__main__':
    sets = card_sets_df('set*.json')
    global_data = globals_json()

    keywords_by_region = kw_count_by_region(sets, global_data)
    keywords_by_region.to_csv('keywords_by_region.csv')
