Output Events
=============
Oshino works by pushing events to Riemann. Bellow are listed common events provided by Oshino. Altering and Monitoring can be based on these events.

By Oshino core
-------------
- `oshino.heartbeat` - event with ttl of 1.5x of interval. Monitor for `expired` event to know when Oshino is down
- `oshino.processing_time` - how long it takes to collect metrics. If it takes longer than interval - metric will come with state `error`
- `oshino.metrics_count` - sends count of collected metrics. Metrics which failed to send are summed up

By Oshino Http Agent
--------------------
- `<agent_name>.health` - returns result of http call. HTTP status maps into state: success codes into `success`, failure - `failure`. Metric - how long it took in miliseconds.

By Oshino Subprocess Agent
-------------------------
- `<agent_name>.shell` - returns result of defined shell command. `0` - is counted as sucess, all other codes marks failure and are added to `description` field
