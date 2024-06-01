import json
import eaeu_settings
import requests

file_name = 'eaeu_addresses/eaeu_addressees.json'
settings = eaeu_settings.get_processor_settings()


def update_eaeu_ref():
    pass


def get_eaeu_code(id):
    with open(f'{file_name}', 'r', encoding='utf-8') as fh:  # открываем файл на чтение
        data = json.load(fh)
    res = None
    for elem in range(len(data)):
        print(data[elem])
        if data[elem]['@attributes']['ИД'] == id:
            return data[elem]['АдресЕАЭС']
    return res


def get_gosedo_uid(adress):
    with open(f'{file_name}', 'r', encoding='utf-8') as fh:  # открываем файл на чтение
        data = json.load(fh)
    res = None
    for elem in range(len(data)):
        if data[elem]['АдресЕАЭС'] == adress:
            res = data[elem]['@attributes']['ИД']
    return res


def refresh_json():
    response = requests.post('http://127.0.0.1:84/api/nsi-reference',
                             json={'action': 'gettableItems', 'filter': {'id': 'Cat01-003-00004'}})
    with open('eaeu_addresses/eaeu_addressees.json', 'w') as file:
        json.dump(response.content.decode("utf-8"), file)
    return response.content.decode("utf-8")

# создать adresses папку на машине для json adresses