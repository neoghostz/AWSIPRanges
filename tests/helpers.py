import os
import yaml
import json

def _load_resource_as_json(path_under_resources):
    path = os.path.join(os.path.dirname(__file__), 'resources', path_under_resources)

    with open(path) as json_file:
        data = json.load(json_file)
    return data


def _string_to_yaml(string_to_convert):
    return yaml.load(string_to_convert, Loader=yaml.FullLoader)
