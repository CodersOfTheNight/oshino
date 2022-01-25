import logging

from argparse import ArgumentParser

from dotenv import load_dotenv, find_dotenv
from .config import load
from .core.heart import start_loop

logger = logging.getLogger(__name__)


try:
    load_dotenv(find_dotenv())
except Exception as ex:
    logger.error("Error while loading .env: '{}'. Ignoring.".format(ex))


def main(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = load(args.config)
    start_loop(cfg, args.noop)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config", help="Config file", default="config.yaml")
    parser.add_argument("--noop", action="store_true", default=False, help="Events will be processed, but not sent to Riemann")
    parser.add_argument("--debug", action="store_true", default=False, help="Debug mode")
    main(parser.parse_args())
