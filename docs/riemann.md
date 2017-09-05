Riemann
========
In short - Riemann is event router. It receives an event (log or metric) and decides where it should go.
Usual scenarios are Graphite, Logstash, or directly to your Email. Similar to StatsD.

It's power comes from ability to analyze raw events. 
It is possible (and quite easy) to alert on certain events. Watching single raw events is usually not enough,
but Riemann allows multiple options of aggregation and transformation of events - calculate percentiles, rates,
apdex etc...

At the moment, the best source of information can be found in this book: [ArtOfMonitoring](https://www.artofmonitoring.com/)

Installing
-----------
Packages of Riemann can be found [here](https://github.com/riemann/riemann/releases), it has `.deb` and `.rpm` package versions which should cover most of the use cases.

Fresh Config file
-----------------
(`/etc/riemann/riemann.config`)
```clojure
(logging/init {:file "/var/log/riemann/riemann.log"})

(let [host "0.0.0.0"]
  (repl-server {:host "127.0.0.1"})
  (tcp-server {:host host})
  (udp-server {:host host})
  (ws-server  {:host host}))

(periodically-expire 10 {:keep-keys [:host :service :tags, :state, :description, :metric]})

(let [index (index)]]

  ; Inbound events will be passed to these streams:
  (streams
    (default :ttl 60
      ; Index all events immediately.
      index

      ; Send all events to the log file.
      #(info %)
    )))
```

Basic config file should look something like this. 
It can (and should) look confusing, but everything is not that hard after getting used to it.

### Basic syntax of Clojure
Usually code looks like this: `(<function> <arg1> <arg2> ... <argN>)`
So `(+ 1 2 3)` would translate into `1 + 2 + 3`
Nesting is allowed as well, so `(<function1> <arg1> (<function2> <arg2> <arg3>))` is OK.

Keyword `let` is used to define variables, so `(let [a 5 b 6] (+ a b))` says that `a = 5, b = 6` and I want to do `a + b` which is `11`

Colon is used to access certain key in Map, so eg. Event consists of these params: host, servie, tags, state, description, metric, ttl
By saying `(default :ttl 60 ...)` we take what is in `ttl` field, and if it's empty we say it is `60`. Same could be applied to any other field.

### Trying to understand what is happening in this config

First of all, keep in mind that these explanations bellow are not totally accurate. Most of the API in Riemann is made simple in surface,
but to make that happen, it is rather complex beneath. I'm trying to ignore what is actually happening and explain situation from user point of view. Most of explanations could be found [here](http://riemann.io/howto.html)


Lets start with `(let [index (index)])`. This one is kinda tricky. Basically `index` is a function which would normally require arguments and should be used something like this `(index event)`, but we're lazy and we prefer just to write `index` and forget about it. This definition is basically a macro which will expand into correct code when it is needed.

`(streams ...)` is the backbone of whole Riemann ecosystem. It provides constant stream of all events which came to Riemann, and we're free to manipulate them. Eg. if we would do something like this:
```clojure
(streams
    (where (tag "test")
        #(info "Our test event" %)
    )
)
```

Each event tagged "test" will be printed out with prefix "Our test event". You can look it as a "if" statement in usual programming.
Most likely 90% of your logic will look like this - you search for something and do something when you find it: send that event to Graphite, Logstash, database, Slack, or Email - you basically have limitless options at this point. And due to this mechanics, it's called event router - you're just routing events. And alerting seems to be same routing, just to different services.

`index` is used to register event in index table, and it's key is formed via `host` + `service` pair. If new event comes with same key, it overrides current one. In this configuration, everything is indexed. However it has it's cost, so usually you're filtering out relevant events and index just them.

Lastly, `#(info %)` is a shorthand function. There's no point to dwelve deep into it. Basically it takes N arguments and prints them out. `%` is a shorthand to push everything you got at this point. You can add any prefix easily by doing `#(info "A prefix " %)`, `%` usually consists of event, so it's good for debuging purposes.

Making Config relevant for Oshino
----------------------------------
### Creating Email notifier

Probably the most important part - notify you when something goes terribly wrong.

This process will involve creating module and importing it to Riemann's config.
Usual convention is: `<app_name>/<group>/<module>.clj`
For this example, we can do `app/notifiers/email.clj`

This file needs to be created under `/etc/riemann/` path. 
So, to be on the same page - lets create and open a file under `/etc/riemann/app/notifiers/email.clj`

First step is to define namespace: 
```clojure
(ns app.notifiers.email)
```

What goes further can be highly opionated, you can use any service you want, I just happened to be using MailGun for a while now, so it was natural to implement using it.

```clojure
(ns app.notifiers.email
    (:require [riemann.mailgun :refer :all])
)
```

So now we have a namespace and we say, that we will want to use MailGun utilities defined in Riemann's library.

Next, we create a function which will emails event to defined address:

```clojure
(def email(mailgun {:sandbox "<sandbox_key>.mailgun.org" :from "<notifier_name>@<our_domain>" :service-key "<service_key>"}))
```

So basically we use existing function `mailgun`, give it most of required params (which makes it a partial function).

Usage goes like this: 
```clojure
(email <email_i_want_to>@<notify>)
```

Which leaves a function with only one required param - event, which will be given implicitly.

Full module looks like this:

```clojure
(ns app.notifiers.email
    (:require [riemann.mailgun :refer :all])
)

(def email(mailgun {:sandbox "<sandbox_key>.mailgun.org" :from "<notifier_name>@<our_domain>" :service-key "<service_key>"}))
```

### Including our modules

Modules are included by using `require` function. It needs to go somewhere inside `riemann.config` file, and looks like this:
```clojure
(require '[app.notifiers.email :refer :all])
```

Syntax isn't as clear as many of us would want to, but the basic idea is that we are importing everything from `app.notifiers.email` module.

### Actual alering
```clojure
(require '[app.notifiers.email :refer :all])

(streams
    (where (tagged-all ["oshino", "heartbeat"])
       (changed :state
         (email "my@email.com")
       )
    )
)
```

Ok, this very important part and it might be a little bit confusing at start.
`(where (tagged-all ["oshino", "heartbeat"])` says that we should keep only events which has both of these tags inside them.

`(changed :state)` this is the tricky part, and genius of it lies inside design of Riemann.
Lets start with the concept of TimeToLive (TTL). Each unique event (defined by index, which is `host` + `service` concated strings) have certain time to live. If same event occurs, TTL counter resets. 
This cycle repeats on and on again. However, it timer exceeds the limit, new clone event comes into system, only difference is - it has state `expired`.
To summarize, Oshino is constantly sending heartbeat events. If any heartbeat misses - we get notify.
Note: `(changed :state)` will be triggered in both `ok -> expired` and `expired -> ok` state transitions. It means that you will know when system shutsoff as well as it recovers (Could be temporary network issue for example)

And, of course, `(email "my@email.com")` send us an email.
