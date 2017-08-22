Riemann
========
In short - Riemann is event router. It receives an event (log or metric) and decides where it should go.
Usual scenarios are Graphite, Logstash, or directly to your Email. Similar to StatsD.

It's power comes from ability to analyze raw events. 
It is possible (and quite easy) to alert on certain events. Watching single raw events is usually not enough,
but Riemann allows multiple options of aggregation and transformation of events - calculate percentiles, rates,
apdex etc...

At the moment, the best source of information can be found in this book: [ArtOfMonitoring(https://www.artofmonitoring.com/)

Fresh Config file
-----------------

