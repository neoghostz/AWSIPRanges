import json
import os

import yaml
import cfnlint.core
from pytest import fixture
from helpers import _load_resource_as_json, _string_to_yaml

from macro import handler



@fixture
def builder():
    return handler


def test_aws_ip_ranges_cfn_lint(builder, template="base.json"):
    template_path = "tests"
    template_filename = "template.json"
    cfn_fragment = _load_resource_as_json(f'requests/{template}')
    actual_resources = builder(cfn_fragment, "object")

    with open(os.path.join(template_path, template_filename), "w") as fh:
        fh.write(json.dumps(actual_resources['fragment'], sort_keys=True, indent=4, separators=(',', ': ')))

    template = cfnlint.decode.cfn_json.load(template_path + "/" + template_filename)

    rules = cfnlint.core.get_rules([], ['W2001'], [])

    results = []
    results.extend(
        cfnlint.core.run_checks(
            template_filename, template, rules, ['us-east-1']))

    assert results == []