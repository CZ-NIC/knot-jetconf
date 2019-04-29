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

### Allow running knot systemd command without sudo password
Create a new group, for example `knotcontrol`
```bash
$ sudo groupadd knotcontrol
```
Add `jetconf` user or user who is running knot to this group.
```bash
$ usermod -a -G knotcontrol jetconf
```
Create the new sudoers configuration file in `sudoers.d` directory
```bash
$ sudo nano /etc/sudoers.d/knotcontrol
```
Add these rules to this file 
```bash
Cmnd_Alias KNOT_CMDS = /bin/systemctl start knot, /bin/systemctl stop knot, /bin/systemctl reload knot, /bin/systemctl restart knot
%knotcontrol ALL=(ALL) NOPASSWD: KNOT_CMDS
```
Now every user, which is member of `knotcontrol` group cal execute `systemctl` commands for `knot` with `sudo` and sudo password is not needed.


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
