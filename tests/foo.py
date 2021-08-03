import abc
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

        self.invoke(self.format_test_path,'a=b/c=d')
        pass

    def split_subset(self):
        pass

    def subroutine1(self):
        pass

    def invoke(self, f, *args):
        # TODO: invoke f by stuffing all the click arguments
        pass

    @abc.abstractmethod
    def format_test_path(self, test_path):
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

    # reality
    @click.option('--bare')
    def format_test_path(self, x, bare):
        if bare:
            return x[0]['name']
        else:
            return "--tests {}".format(x[0]['name'])



