from riemann_client.client import QueuedClient


class QClient(QueuedClient):
    pass


def flush(client, transport, logger):
    try:
        transport.connect()
        client.flush()
        transport.disconnect()
    except ConnectionRefusedError as ce:
        logger.warn(ce)
