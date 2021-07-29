import click


class Optimize:
    def subset(self):
        self.invoke(self.enumerate_tests)
        pass

    def split(self):
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
    def to_command(cls):
        # TODO: lift click decorations from cls.enumerate_tests and cls.init and create a click.Command
        pass



class Gradle(Optimize):
    @click.option('--x')
    def enumerate_tests(self, x):
        pass

    @click.option('--bare')
    def init(self, bare):
        pass


