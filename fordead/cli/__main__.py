#!/usr/bin/env python
# dest \= "(\w+)",
import click
import collections
from fordead.cli.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.cli.step2_train_model import train_model
from fordead.cli.step3_decline_detection import decline_detection
from fordead.cli.step4_compute_forest_mask import compute_forest_mask
from fordead.cli.step5_export_results import export_results

class OrderedGroup(click.Group):
    # ref: https://stackoverflow.com/questions/47972638/how-can-i-define-the-order-of-click-sub-commands-in-help
    def __init__(self, name=None, commands=None, **attrs):
        super(OrderedGroup, self).__init__(name, commands, **attrs)
        #: the registered subcommands by their exported names.
        self.commands = commands or collections.OrderedDict()

    def list_commands(self, ctx):
        return self.commands

@click.group(cls=OrderedGroup, context_settings={'help_option_names': ['-h', '--help']})
def fordead():
    """
    fordead - Remote sensing time series processing to detect forest anomalies

    The usual workflow is :
        masked_vi --> train_model --> detect --> forest_mask --> export_results
    """
fordead.add_command(compute_masked_vegetationindex)
fordead.add_command(train_model)
fordead.add_command(decline_detection)
fordead.add_command(compute_forest_mask)
fordead.add_command(export_results)

if __name__ == '__main__':  # pragma: no cover
    fordead()