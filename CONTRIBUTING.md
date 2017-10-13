New agents
==========
Most natural way of contributing to this project is creating new agents.
What is agent? It is basically a metrics collector for specific service, 
eg. `oshino-redis` is an agent which runs `info` command as a Redis client,
parses received metrics and gives them to `oshino` as events.

To make life easier, there's a `cookiecutter` template (oshino-cookiecutter)[https://github.com/CodersOfTheNight/oshino-cookiecutter]
which generates all boilerplate code, you just need to modify it.

Already existing custom agents are mostly listed here: (Third party Agents)[https://github.com/CodersOfTheNight/oshino/blob/master/docs/thirdparty.md]

Contributing to the Core
========================
It should mostly consist of reporting/solving issues. 

General Guidelines
===================
- Code must pass `flake8` (PEP8) coding style test
- All code (with few exceptions) must be non-blocking - asyncio compatible
- New parameters should be covered in documentation section
