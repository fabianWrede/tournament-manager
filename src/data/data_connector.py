import json
import os
from pathlib import Path

from data.json_serializer import DataJSONEncoder, decode_data_json

_path = 'tournament-manager/data/'
_ending = '.json'


def get_file_path(file):
    return os.path.join(str(Path.home()), _path, file + _ending)


def save(data):   
    f = get_file_path(data.id)
    os.makedirs(os.path.dirname(f), exist_ok=True)

    with open(f, 'w') as outfile:
        json.dump(obj=data, fp=outfile, cls=DataJSONEncoder)


def load(id):
    f = get_file_path(id)
    with open(f, 'r') as infile:
        return json.load(fp=infile, object_hook=decode_data_json)
