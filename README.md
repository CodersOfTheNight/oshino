About
=====
Oshino - named after character Meme Oshino from anime called Bakemonogatari:
> Meme Oshino (忍野 メメ, Oshino Meme) is a middle-aged man who lives with the mysterious Shinobu Oshino in an abandoned cram school building in the town Koyomi Araragi resides in Bakemonogatari. An expert in the supernatural, he is the reason why Koyomi was able to return back to normal after being bitten by a vampire, and he becomes Koyomi's informant when it comes to oddities for some time.
[Source](https://myanimelist.net/character/22552/Meme_Oshino)

Just like anime character, this service likes to deal with supernatural - system availability.

Heavily inspired by [collectd](https://github.com/collectd/collectd) and
[riemann-tools](https://github.com/riemann/riemann-tools), and unintentionally similar to [python-diamond](https://github.com/python-diamond/Diamond)

Alerting and Monitoring based on [Riemann](https://riemann.io)


[![Build Status](https://travis-ci.org/CodersOfTheNight/oshino.svg?branch=master)](https://travis-ci.org/CodersOfTheNight/oshino)
[![Coverage Status](https://coveralls.io/repos/github/CodersOfTheNight/oshino/badge.svg?branch=master)](https://coveralls.io/github/CodersOfTheNight/oshino?branch=master)
[![Documentation Status](https://readthedocs.org/projects/oshino/badge/?version=latest)](http://oshino.readthedocs.io/projects/https://github.com/CodersOfTheNight/oshino-consul/en/latest/?badge=latest)


Requirements
============
- Python 3.5+ version
- Have Riemann node running

How to install
==============
`pip install oshino`

Quickstart
==========
It is highly recommended for new users to use [Quickstart Guide](quickstart.md)


Riemann. What? Why? How?
=========================
Riemann is a backbone of this system. It does alerting, it receives metrics, it aggregates metrics and it decides where to send them (eg.: Graphite, Logstash).
However, it is rather unknown to the most of people, and configuring can be not trivial at all. 

To mitigate this problem, documentation for setuping Riemann for this scenario has been made:
[riemann](docs/riemann.md)

Example config
--------------
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

Custom Agents
===============
Documentation about additional agents can be found [here](docs/thirdparty.md)

More documentation
==================
More documentation can be found under [docs](docs/index.md) directory

Contributing
============
Refer to [CONTRIBUTING.md](CONTRIBUTING.md)
