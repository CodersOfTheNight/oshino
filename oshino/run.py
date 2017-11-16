import click
from dotenv import load_dotenv, find_dotenv
from .config import load
from .core.heart import start_loop

load_dotenv(find_dotenv())


@click.command()
@click.option("--config", help="Config file", default="config.yaml")
@click.option("--noop/--op",
              help="'No operation' mode."
                   "Events will be processed, but not sent to Riemann",
              default=False)
def main(config, noop):
    cfg = load(config)
    start_loop(cfg, noop)


if __name__ == "__main__":
    main()
