def send_heartbeat(event_fn, logger, ttl):
    logger.debug("Sending heartbeat")
    event_fn(metric_f=1.0,
             service="oshino.heartbeat",
             tags=["oshino", "heartbeat"],
             ttl=ttl)


def send_timedelta(event_fn, logger, td, interval):
    logger.debug("Oshino took: {0}ms to collect metrics"
                 .format(int(td * 1000)))
    if td > interval:
        state = "error"
    else:
        state = "ok"

    event_fn(metric_f=td,
             state=state,
             service="oshino.processing_time",
             tags=["oshino", "instrumentation"])


def send_metrics_count(event_fn, logger, count):
    logger.debug("Oshino collected {0} metrics".format(count))
    event_fn(metric_f=count,
             service="oshino.metrics_count",
             tags=["oshino", "instrumentation"])
