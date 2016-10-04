# sip

## Install

This project was built using python 3.5.2 and using pybuilder: http://pybuilder.github.io/

1. clone the repo
2. pip install pybuilder
3. pyb install_dependencies install

## Quick start

###### Make sure you have aws credentials set in the usual way, for example
in ``~/.aws/credentials`` put:

    [default]
    aws_access_key_id = YOUR_KEY
    aws_secret_access_key = YOUR_SECRET

and in ``~/.aws/config`` put:

    [default]
    region=us-east-1

###### If your're using iTerm

this will integrate with iTerm's split panel ability to open several ssh sessions

``gem install i2cssh``


## Usage
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

###### To create a local ec2 inventory
    sip --refresh_inventory
###### To install a cron job that refreshes the local ec2 inventory every 10 minutes
    sip --install_cron 10
