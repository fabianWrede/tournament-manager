import json
import os

from data.json_serializer import DataJSONEncoder, decode_data_json

_path = 'resources/data/'
_ending = '.json'


def get_file_path(file):
    return _path + file + _ending


def save(data):
    os.makedirs(os.path.dirname(_path), exist_ok=True)
    f = get_file_path(data.id)

    with open(f, 'w') as outfile:
        json.dump(obj=data, fp=outfile, cls=DataJSONEncoder)


def load(id):
    f = get_file_path(id)
    with open(f, 'r') as infile:
        return json.load(fp=infile, object_hook=decode_data_json)
