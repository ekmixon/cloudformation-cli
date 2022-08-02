import json
import logging

import cfnlint.config
import cfnlint.core

from .module_fragment_reader import _get_fragment_file

LOG = logging.getLogger(__name__)


def print_cfn_lint_warnings(fragment_dir):
    if lint_warnings := __get_cfn_lint_matches(fragment_dir):
        LOG.warning(
            "Module fragment might be valid, but there are "
            "warnings from cfn-lint "
            "(https://github.com/aws-cloudformation/cfn-python-lint):"
        )
        for lint_warning in lint_warnings:
            print(f"\t{lint_warning.message} (from rule {lint_warning.rule})")

    else:
        LOG.warning("Module fragment is valid.")


def __get_cfn_lint_matches(fragment_dir):
    filepath = _get_fragment_file(fragment_dir)
    try:
        try:
            template = cfnlint.decode.cfn_json.load(filepath)
        except json.decoder.JSONDecodeError:
            template = cfnlint.decode.cfn_yaml.load(filepath)
    except Exception as e:  # pylint: disable=broad-except
        LOG.error(
            "Skipping cfn-lint validation due to an internal error.\n"
            "Please report this issue to the team (include rpdk.log file)\n"
            "Issue tracker: github.com/aws-cloudformation/cloudformation-cli/issues"
        )
        LOG.error(str(e))
        return []

    # Initialize the ruleset to be applied (no overrules, no excludes)
    rules = cfnlint.core.get_rules([], [], [], [], False, [])

    # Default region used by cfn-lint
    regions = ["us-east-1"]

    return cfnlint.core.run_checks(filepath, template, rules, regions)
