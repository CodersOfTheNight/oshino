import click
from dotenv import load_dotenv, find_dotenv
from .config import load
from .core.heart import start_loop

load_dotenv(find_dotenv())


@click.command()
@click.option("--config", help="Config file", default="config.yaml")
def main(config):
    cfg = load(config)
    start_loop(cfg)


if __name__ == "__main__":
    main()
