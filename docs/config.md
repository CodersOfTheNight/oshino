Base Config
============
- `interval` - how often to send metrics (in seconds)
- `riemann.host` - riemann hostname (default: localhost)
- `riemann.port` - riemann port (default: 5555)
- `riemann.transport` - set transport protocol for riemann (default: TCPTransport)
- `loglevel` - level of logging (default: INFO)
- `sentry-dsn` - sentry address for error reporting (default: `None`)
- `executor` - allows to define executor class, default one is `concurrent.futures.ThreadPoolExecutor`
- `executors-count` - set worker count for executor, default: 10
- `agents` - an array of agent configs used in this setup
- `augments` - an array of augment configs used in this setup

Agents
=======

General Config for Agents
------------------------
- `name`- give name for agent
- `tag` - adds this tag to all metrics related to this agent
- `module` - path to module from which actual agent should be loaded. In most cases this path should be declared in actor's README

Http Agent Config
----------------
Agent used to produce HTTP calls to specific website
module: `oshino.agents.http_agent.HttpAgent`

- `url` - which url to call

Subprocess Agent Config
-----------------------
Agent used to execute CLI scripts
module: `oshino.agents.subprocess_agent.SubprocessAgent`

- `script` - what shell script to execute


Augments
========

General config for Augments
---------------------------
- `name`- give name for augment
- `key` - defines a metric key to listen to
- `tag` - adds this tag to all metrics related to this augment
- `module` - path to module from which actual augment should be loaded. In most cases this path should be declared in augment's README


Moving Average
--------------
Reads metrics and produces moving average
module: `oshino.augments.stats.MovingAverage`

- `step` - how much metrics it should inhale before it can produce average
