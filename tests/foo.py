from typing import Callable

import click

# placeholder of the subset function in subset.py
@click.group()
def subset():
    pass

@click.group()
def split_subset():
    pass

# comparable logic currently in __main__.py
def foo():
    for plugin in plugin_list():
        # e.g. plugin==Gradle
        subset.command(name=plugin.name)(Optimize.as_command(plugin.cls, Optimize.split))
        #
        # @subset.command('gradle')
        # @click.option()  # appropriate set of options
        # ...
        # def gradle(context):
        #    Gradle(context).subset()

        split_subset.command(name=plugin.name)(Optimize.as_command(plugin.cls, Optimize.split_subset))
        #
        # @subset.command('gradle')
        # @click.option()  # appropriate set of options
        # ...
        # def gradle(context):
        #    Gradle(context).split_subset()

####

def plugin_list():
    pass


class Optimize:
    def subset(self):
        # meat of the subset command here

        # self.invoke(self.enumerate_tests)
        pass

    def split_subset(self):
        pass

    def subroutine1(self):
        pass

    def invoke(self, f):
        # TODO: invoke f by stuffing all the click arguments
        pass

    # entry point from click command invocation at, say, 'launchable subset gradle`
    def run(self, **kwargs):
        pass

    @classmethod
    def as_command(cls, run_method :Callable) -> click.Command:   # Callable[[Optimize],None]
        # Equivalent of ...
        @click.pass_context
        def f(context):
            run_method(cls(context))

        # TODO: lift click decorations from cls.enumerate_tests and cls.init and create a click.Command
        f = click.option(name='--bare')(f)
        f = click.option(name='--help')(f)
        return f



class Gradle(Optimize):
    @click.option('--x')
    def enumerate_tests(self, x):
        pass

    @click.option('--bare')
    def init(self, bare):
        pass


