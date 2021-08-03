import click
import pdb;

@click.option('-x')
def foo(x):
    pass

@click.command()
def bar(x):
    print(x)
    pdb.set_trace()

for param in foo.__click_params__:
    bar.params.append(param)

if __name__ == '__main__':
    bar()

