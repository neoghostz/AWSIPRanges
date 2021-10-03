import json
import os

import yaml
from pytest import fixture
from helpers import _load_resource_as_json, _string_to_yaml

from macro import handler

@fixture
def builder():
    return handler


def test_vpc_builder_base(builder, template="base.json"):
    cfn_fragment = _load_resource_as_json(f'requests/{template}')
    actual_resources = builder(cfn_fragment, "object")

    expected_resources = _load_resource_as_json(f'responses/{template}')
    assert actual_resources == expected_resources
