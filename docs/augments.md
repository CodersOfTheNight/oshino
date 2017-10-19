What is "Augment"?
------------------
In this context, we a process which reads specific metrics and produces new ones, we call an augment.
Augment's job is to produce additional insights from metrics we already have.

How to use them?
----------------
You need to include specific augment inside config under augments array, very similar to [Agents](agents.md).

An example config could look like this:
```yaml
---
interval: 10
loglevel: DEBUG
riemann:
  host: localhost
  port: 5555
  transport: BlankTransport
augments:
  - name: moving average
    key: cpu 
    module: oshino.augments.stats.SimpleMovingAverage
    step: 5
    tag: "sma"
```

More configuration info can be found under [Config](config.md)
