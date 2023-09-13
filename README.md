# aggro
A feed manipulator &amp; aggregator built with Python.

Aggro is a tool for creating, manipulating and serving syndicated feeds based on data from arbitrary web pages with a post-like structure. Aggro is capable of sourcing content by scraping HTML, using JSON APIs, using existing RSS/Atom feeds and reading Facebook posts. These content streams can be manipulated (filtered, mapped over, concatenated, digested) to create new, transformed feeds.

Aggro is based on a plugin system that is configured using a declarative JSON configuration file called Aggrofile. An Aggrofile defines the used plugin instances and a directed acyclic graph (DAG) between the plugins. Plugins are triggered either on a defined schedule or by propagating data through the DAG.

Aggro was born from a concrete need to aggregate post-like data from various websites, such as event venues in my city and artists on social media. The design of Aggro is very pragmatic: features are implemented if I need them for my personal use case. As such, Aggro is a very personal project. Aggro is not mature and probably never will be.

Aggro is free and open source, MIT licensed software.

## Installation and running

Aggro is intended to be run as a long-lived process on a server. I personally run it as a docker container on a DigitalOcean VPS, built with the Dockerfile in the repository root. See `docker-compose.yml` for a usage example. See the `Aggrofile` for a configuration example.

## Plugins

Plugin documentation is a work in progress. For now, check out the implementation (see `plugins -> *Plugin.py -> Plugin.__init__`) to figure out what parameters to give to each plugin.

## Author

Jan Tuomi <<jans.tuomi@gmail.com>>
