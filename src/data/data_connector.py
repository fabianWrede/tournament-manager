import json
import os
from pathlib import Path

from data.json_serializer import DataJSONEncoder, decode_data_json

_path = 'data/'
_ending = '.json'


def _get_file_path(filename):
    path = os.environ.get('SNAP_USER_COMMON',
               default=str(Path.home()) + 'tournament-manager/')
    return os.path.join(path, _path, filename + _ending)


def save(data):
    f = _get_file_path(data.id)
    os.makedirs(os.path.dirname(f), exist_ok=True)

    with open(f, 'w') as outfile:
        json.dump(obj=data, fp=outfile, cls=DataJSONEncoder)


def load(id):
    f = _get_file_path(id)
    with open(f, 'r') as infile:
        return json.load(fp=infile, object_hook=decode_data_json)
