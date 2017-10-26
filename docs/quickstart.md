Preparing Environment
======================
You will need Python version 3.5+ and `pip` installed.
In the most cases `pip` should come bundled, if building from source, you will need to have `openssl` development package installed, otherwise it will skip.

If for some reason you don't have it and cannot build with `openssl`, there's always:

`wget https://bootstrap.pypa.io/get-pip.py | python`

Virtualenv
----------
It is optional, but highly recommended. 
Can be installed via `pip install virtualenv`

To create actual virtualenv, do:
`virtualenv venv`
Or if you have multiple versions of python (usually 2.7 and 3.****), 
failproof approach would be:
`python3 -m virtualenv venv`

This will create virtual environment inside folder

Depending on OS, activating environment may slightly differ.
Linux/MacOS/*BSD it is `source venv/bin/activate`
Windows: `venv\Scripts\activate`

Installing Oshino
-----------------
When everything is prepared, installing is as easy as:
`pip install oshino`


Launching Oshino
================
First create config. Easy way to do that is by using `oshino-admin`

`oshino-admin config init config.yaml`

And now you can actually start it:
`oshino --config=config.yaml`

Running as daemon
------------------
To start as a daemon, we need to use `oshino-admin`
`oshino-admin start --config=config.yaml`

If you're running on your local machine or not as root, it's possible to get error like:
`Unable to create the pidfile.`
By default it writes PID (Process ID) file to `/var/run/oshino.pid` and permissions are not always sufficient to do that.
Issue can be easily mitigated by providing custom path:
`oshino-admin start --config=config.yaml --pid=oshino.pid`

To check if it's running:
`oshino-admin status`

To stop it:
`oshino-admin stop`

Main caveat in using custom pid path, you need to provide it for `status` and `stop` commands as well:

`oshino-admin status --pid=oshino.pid`
`oshino-admin stop --pid=oshino.pid`


Installing plugins
==================

In the most cases, these plugins are for agents. Agent in Oshino context is metrics collector.
So for example, if our service is using [Prometheus](https://prometheus.io/) and we want to collect metrics from it, 
plugin needs to be installed:

`oshino-admin plugin install oshino_prometheus`

To list available plugins:
`oshino-admin plugin list`

Plugin can be removed via `uninstall` command:

`oshino-admin plugin uninstall oshino_statsd`

Making sense of Config
=======================
Generated config should look like this:

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

It says, that `interval` at which metrics will be pushed is 10 seconds,
it is expecting Riemann at `localhost:5555`
And currently has one Agent called `health-check` which uses included `HttpAgent`
to do a healthcheck on `http://python.org`. Resulting metrics are tagged `healthcheck`

More info can be found on: [Config](config.md) section.

In general, a proper Riemann's address needs to be providen and array of agents extended
with agents you require
