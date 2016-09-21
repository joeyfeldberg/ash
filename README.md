# sip

## not working yet!

## install

This project was built using python 3.5.2 and using pybuilder: http://pybuilder.github.io/

1. clone the repo
2. pip install pybuilder
3. pyb install_dependencies install

## quick start

###### to create a local ec2 inventory
    sip --refresh_inventory
###### to connect to a machine by the name tag
    sip <name-tag>
###### to install a cron job that refreshes the local ec2 inventory every 10 minutes
    sip --install_cron 10

## usage
```
usage: sip [-h] [--completions COMPLETIONS] [--refresh_inventory]
           [--install_cron minutes]
           [name]

positional arguments:
  name

optional arguments:
  -h, --help            show this help message and exit
  --completions COMPLETIONS
  --refresh_inventory
  --install_cron minutes
```
