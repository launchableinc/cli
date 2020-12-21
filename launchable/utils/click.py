import click

# click.Group has the notion of hidden commands but it doesn't allow us to easily add
# the same command under multiple names and hide all but one.
class GroupWithAlias(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.aliases = {}

    def get_command(self, ctx, cmd_name):
        return super().get_command(ctx, cmd_name) or self.aliases.get(cmd_name)

    def add_alias(self, name, cmd):
        self.aliases[name] = cmd
