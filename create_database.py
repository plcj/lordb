import csv
import json
from pathlib import Path

# Todo: function to download set data and extract it

# Provides names of keys for accessing JSON card objects from Riot set data.
# Also allows changing column order in CSV output by changing the order of items in the tuple.
COLUMNS = (
    'cardCode',
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
    'collectible'
)


def tabulate_card(card_as_json):
    """
    :param card_as_json: JSON representation of a card, from Riot data.
    :return: card in tabular format.
    """
    card_as_dict = convert_json_card_to_dict(card_as_json)

    tabular_card = list()
    for col in COLUMNS:
        tabular_card.append(card_as_dict[col])

    return tabular_card


def convert_json_card_to_dict(card_as_json):
    """
    :param card_as_json: JSON representation of a card
    :return: Just the interesting parts, as a dict
    """
    card_as_dict = dict()

    for card_key in COLUMNS:
        try:
            card_as_dict[card_key] = card_as_json[card_key]
        except KeyError as e:
            # Set 1 has 'region' instead of 'regions'
            if 'regions' in e.args:
                card_as_dict[card_key] = card_as_json['region']
            else:
                raise e

    return card_as_dict


def tabulate_all_cards_in_set(card_set_file_path):
    """
    :param card_set_file_path: Path to card set data from Riot (JSON).
    :return: Data for all cards in the set in tabular format.
    """
    with open(card_set_file_path, 'rb') as input_file:
        card_set = json.load(input_file)

    tabular_set = list()
    for card in card_set:
        tabular_set.append(tabulate_card(card))

    return tabular_set


def create():
    """
    Create a tabular representation of card set data from Riot.
    """
    set_data_files = [x for x in Path('data').glob('set*.json') if x.is_file()]

    rows = list()
    for data_file in set_data_files:
        rows.extend(tabulate_all_cards_in_set(data_file))

    with open('lor-database.csv', 'w') as database:
        writer = csv.writer(database)
        writer.writerow(COLUMNS)
        writer.writerows(rows)


if __name__ == '__main__':
    create()
