About
=====
Oshino - named after character Meme Oshino from anime called Bakemonogatari:
> Meme Oshino (忍野 メメ, Oshino Meme) is a middle-aged man who lives with the mysterious Shinobu Oshino in an abandoned cram school building in the town Koyomi Araragi resides in Bakemonogatari. An expert in the supernatural, he is the reason why Koyomi was able to return back to normal after being bitten by a vampire, and he becomes Koyomi's informant when it comes to oddities for some time.

Just like anime character, this service likes to deal with supernatural - system availability.

Heavily inspired by [collectd](https://github.com/collectd/collectd) and
[riemann-tools](https://github.com/riemann/riemann-tools)


[![Build Status](https://travis-ci.org/CodersOfTheNight/oshino.svg?branch=master)](https://travis-ci.org/CodersOfTheNight/oshino)
[![Coverage Status](https://coveralls.io/repos/github/CodersOfTheNight/oshino/badge.svg?branch=master)](https://coveralls.io/github/CodersOfTheNight/oshino?branch=master)

Requirements
============
Python 3.5+ version

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
  - name: consul
    module: oshino.agents.consul_agent.ConsulAgent
    tag: discovery
```
