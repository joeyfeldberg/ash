# ash

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

###### For multiple ssh sessions ash uses cssh, tmux-cssh or i2cssh and it defaults to cssh

###### If you're using iTerm

this will integrate with iTerm's split panel ability to open several ssh sessions

``gem install i2cssh``

If you're on a mac and not using iTerm you can install tmux-cssh with ``` brew install tmux-cssh ```

###### Now just run ```ash```


## Usage
```
usage: ash [-h] [--completions COMPLETIONS] [--refresh_inventory]
           [--install_cron minutes]
           [name]

positional arguments:
  name

optional arguments:
  -h, --help            show this help message and exit
  --refresh_inventory
  --install_cron minutes
```

###### To create a local ec2 inventory
    ash --refresh_inventory
###### To install a cron job that refreshes the local ec2 inventory every 10 minutes
    ash --install_cron 10

###### It has some settings saved as an ini file in ``~/.ashconfig`` and it looks like this:

```ini
[SSH]
ssh_username = ubuntu
ssh_mux = tmux-cssh
```

it supports:
```
ssh_username - default username to use
ssh_mux - one of cssh/tmux-cssh/i2cssh
ssh_identity_file - default identity file to use (I suggest using ssh-agent though)
```
