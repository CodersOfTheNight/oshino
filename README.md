About
=====
Oshino - named after character Meme Oshino from anime called Bakemonogatari:
> Meme Oshino (忍野 メメ, Oshino Meme) is a middle-aged man who lives with the mysterious Shinobu Oshino in an abandoned cram school building in the town Koyomi Araragi resides in Bakemonogatari. An expert in the supernatural, he is the reason why Koyomi was able to return back to normal after being bitten by a vampire, and he becomes Koyomi's informant when it comes to oddities for some time.
[Source](https://myanimelist.net/character/22552/Meme_Oshino)

Just like anime character, this service likes to deal with supernatural - system availability.

Heavily inspired by [collectd](https://github.com/collectd/collectd) and
[riemann-tools](https://github.com/riemann/riemann-tools)

Alerting and Monitoring based on [Riemann](https://riemann.io)


[![Build Status](https://travis-ci.org/CodersOfTheNight/oshino.svg?branch=master)](https://travis-ci.org/CodersOfTheNight/oshino)

Output Events
=============
- `oshino.heartbeat` - event with ttl of 1.5x of interval. Monitor for `expired` event to know when Oshino is down
- `oshino.processing_time` - how long it takes to collect metrics. If it takes longer than interval - metric will come with state `error`
- `oshino.metrics_count` - sends count of collected metrics. Metrics which failed to send are summed up

Requirements
============
- Python 3.5+ version
- Have Riemann node running

How to install
==============
`pip install oshino`

Example config
==============
```yaml
---
interval: 10
riemann:
  host: localhost
  port: 5555
agents:
  - name: health-check
    module: oshino.agents.http_agent.HttpAgent
    url: http://python.org
    tag: healthcheck
```

Third party Agents
==================
Oshino agents can be added frome external sources.
You just need to install agent and set proper module config for it

Known agents:
- [oshino-consul](https://github.com/CodersOfTheNight/oshino-consul)
- [oshino-redis](https://github.com/CodersOfTheNight/oshino-redis)

Creating custom Agent
---------------------
It can be done by using our [Cookiecutter Template](https://github.com/CodersOfTheNight/oshino-cookiecutter)

