import click, sys

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


class PercentageType(click.ParamType):
    name = "percentage"

    def convert(self, value: str, param, ctx):
        try:
            if value.endswith('%'):
                x = float(value[:-1])/100
                if 0 <= x <= 100:
                    return x
        except ValueError:
            pass

        self.fail("Expected percentage like 50% but got '{}'".format(
            value), param, ctx)


PERCENTAGE = PercentageType()

# Can the output deal with Unicode emojis?
try:
    '\U0001f389'.encode(sys.stdout.encoding or "ascii")
    # If stdout encoding is unavailable, such as in case of pipe, err on the safe side (EMOJI=False)
    # This is a judgement call, but given that emojis do not serve functional purposes and purely decorative
    # erring on the safe side seems like a reasonable call.
    EMOJI = True
except UnicodeEncodeError as e:
    EMOJI = False

def emoji(s: str, fallback: str = ''):
    """
    Used to safely use Emoji where we can.

    Returns 's' in an environment where stdout can deal with emojis, but 'fallback' otherwise.
    """
    return s if EMOJI else fallback
