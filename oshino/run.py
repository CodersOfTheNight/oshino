import click
from dotenv import load_dotenv, find_dotenv
from logbook import Logger
from .config import load
from .core.heart import start_loop


logger = Logger("Runner")

try:
    load_dotenv(find_dotenv())
except Exception as ex:
    logger.error("Error while loading .env: '{}'. Ignoring.".format(ex))


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
