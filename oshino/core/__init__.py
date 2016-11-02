def send_heartbeat(event_fn, logger, ttl):
    logger.debug("Sending heartbeat")
    event_fn(metric_f=1.0,
             service="oshino.heartbeat",
             tags=["oshino", "heartbeat"],
             ttl=ttl)
