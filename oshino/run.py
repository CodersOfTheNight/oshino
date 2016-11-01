import click
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


@click.command()
def main():
    pass


if __name__ == "__main__":
    main()
