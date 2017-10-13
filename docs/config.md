Base Config
-----------
- `interval` - how often to send metrics (in seconds)
- `riemann.host` - riemann hostname (default: localhost)
- `riemann.port` - riemann port (default: 5555)
- `riemann.transport` - set transport protocol for riemann (default: TCPTransport)
- `loglevel` - level of logging (default: INFO)
- `sentry-dsn` - sentry address for error reporting (default: `None`)
- `executor` - allows to define executor class, default one is `concurrent.futures.ThreadPoolExecutor`
- `executors-count` - set worker count for executor, default: 10

General Config for Agents
------------------------
- `tag` - adds this tag to all metrics related to this agent

Http Agent Config
----------------
- `url` - which url to call

Subprocess Agent Config
-----------------------
- `script` - what shell script to execute


Suggested Riemann config
-------------------------
```clojure
 (where (tagged-all ["oshino", "heartbeat"])
       (changed :state
         (email "something@something.com")
       )
    )
```

If Oshino goes down, or encounters some performance hickups - you'll be notified
