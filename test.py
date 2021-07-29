import click

@click.option('-x')
def foo(x):
    pass

@click.command()
def bar(x):
    print(x)

for param in foo.__click_params__:
    bar.params.append(param)

if __name__ == '__main__':
    bar()

