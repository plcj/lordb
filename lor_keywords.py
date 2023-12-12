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
    # print(global_data)
    return lor_globals


def relevant_keywords(lor_globals):
    """
    return list of all keywords, with some exceptions
    """
    keywords = pd.DataFrame(lor_globals['keywords'])
    keywords = keywords[keywords['name'] != "Missing Translation"]

    regions = pd.DataFrame(lor_globals['regions'])
    keywords = keywords[~keywords['name'].isin(regions['name'])]  # todo might need to also look at nameRefs
    return keywords


def description_keywords(description, keywords):
    """
    return list of keywords found in description
    names or nameRefs may be used. Try nameRef first, if not found, use name.
    """
    matches = re.findall(r'<link=keyword.(.*?)>', description)
    nameref_list = []
    for match in matches:
        nameref_values = keywords.loc[keywords['name'] == match, 'nameRef'].values
        nameref_list.append(nameref_values[0] if nameref_values.size > 0 else match)
    return nameref_list


def region_abbreviation_map(lor_globals):
    """
    return dict of name to abbreviation region mapping
    """
    r_map = pd.DataFrame(lor_globals['regions'], columns=['nameRef', 'abbreviation'])
    r_map = r_map.set_index('nameRef')['abbreviation'].to_dict()
    # print(r_map)
    return r_map


# todo preprocess card data to make format consistent across associated cards

def kw_count_by_region(sets_df, lor_globals):
    """
    return a dataframe of keywords and their frequency in each region
    """
    # Get cards. Limit to those in Standard
    cards = pd.DataFrame(sets_df, columns=['cardCode', 'formats', 'regionRefs', 'keywordRefs', 'description'])
    standard_cards = cards[cards['formats'].apply(lambda formats: isinstance(formats, list) and 'Standard' in formats)].copy()
    ## Why isinstance(formats, list)? https://github.com/RiotGames/developer-relations/issues/785 When not present, pandas makes it NaN, which internally is a float

    ## Preprocessing before counting
    keywords = relevant_keywords(lor_globals)
    # Collect keywords from both description and keywordRefs of each card
    standard_cards['all_keywords'] = standard_cards['description'].apply(lambda description: description_keywords(description, keywords)) + standard_cards['keywordRefs']
    standard_cards['all_keywords'] = standard_cards['all_keywords'].apply(lambda x: list(set(x)))  # Remove duplicates
    standard_cards = standard_cards.explode('regionRefs').explode('all_keywords')  # Explode lists into rows
    standard_cards = standard_cards.fillna("None")  # not all cards have keywords, and we don't want them showing up as NaN
    standard_cards = standard_cards.query('regionRefs != "Runeterra"')  # Remove Runeterra region
    standard_cards = standard_cards.replace(region_abbreviation_map(lor_globals)) # Replace region names with abbreviations

    ## Count keywords by region
    kw_by_reg_with_count = standard_cards.groupby(['regionRefs', 'all_keywords']).size().reset_index(name='Count')
    regions = kw_by_reg_with_count['regionRefs'].unique()
    final_result_frame = pd.DataFrame([(r, k) for r in regions for k in keywords['nameRef']], columns=['regionRefs', 'all_keywords'])
    result = pd.merge(final_result_frame, kw_by_reg_with_count, on=['regionRefs', 'all_keywords'], how='left')
    result = result.rename(columns={'regionRefs': 'Region', 'all_keywords': 'Keyword'})
    result['Count'] = result['Count'].fillna(0).astype(int)

    return result


# todo: optionally download set data and extract it

if __name__ == '__main__':
    sets = card_sets_df('set*.json')
    global_data = globals_json()

    keywords_by_region = kw_count_by_region(sets, global_data)
    keywords_by_region.to_csv('keywords_by_region.csv')
