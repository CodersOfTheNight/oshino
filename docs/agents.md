What is "Agent"?
-----------------
In this context, we call a worker which collects specific type of metrics, an agent.

How to use them
--------------
To be able to use any of agents, first you must import them.
Importing is done via config, by adding them under `agents` section


An example config could look like this:
```yaml
---
interval: 10
loglevel: DEBUG
riemann:
  host: localhost
  port: 5555
  transport: BlankTransport
agents:
  - name: echo
    module: oshino.agents.subprocess_agent.SubprocessAgent
    script: "echo 'Hello world!'"
    tag: "bash"
```

More configuration info can be found under [Config](config.md)

As you can see, there's one agent in agents array, which is called `echo`
and uses internal `SubprocessAgent` class. 
This type of agent is able to execute command in command line
and return it's result as a metric.

Internal agents also includes `HttpAgent` which is able to do HTTP calls,
and returns response and time it took to execute as metrics.

Usual source of agents is [Third Party agent section](thirdparty.md)
They can be installed via `pip` command, or using `oshino-admin`. 
For more information on `oshino-admin` usage, do `oshino-admin --help`.


Creating custom Agent
---------------------
It can be done by using our [Cookiecutter Template](https://github.com/CodersOfTheNight/oshino-cookiecutter)
