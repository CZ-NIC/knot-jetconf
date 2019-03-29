# KnotDNS JetConf backend

JetConf backend for the KnotDNS authoritative server 

## Development
[Information](https://gitlab.labs.nic.cz/labs/jetconf/wikis/development) for developers

## Prerequisites

[Python](https://www.python.org/) 3.6 or newer is required and [KnotDNS](https://gitlab.labs.nic.cz/knot/knot-dns) should be installed

These requirements should be installed by just running installation or by using `pip install -r requirements.txt` command.

* [jetconf](https://gitlab.labs.nic.cz/labs/jetconf)
* [libknot](https://gitlab.labs.nic.cz/knot/knot-dns/tree/master/src/libknot)


## Installation

```bash
$ python setup.py install
```

## Running with JetConf
Start KnotDNS
```bash
$ systemctl start knot.service
```

Example YAML configuration file, certificates and json-data are located in `conf` folder. 
More on [ JetConf wiki](https://gitlab.labs.nic.cz/labs/jetconf/wikis/home).
```bash
$ jetconf -c config-example.yaml
```

Server should be accessible on `https://localhost:8443`.

## JetConf Clients 
* [curl](https://curl.haxx.se/) - A Swiss-knife tool for HTTP/2, [installation](curl-installation)
* [jetscreen](https://gitlab.labs.nic.cz/jetconf/jetscreen) - Interactive graphical JetConf client written in Angular 2
