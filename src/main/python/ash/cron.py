from crontab import CronTab


def install_cron(minutes):
    cron = CronTab(user=True)
    cron.remove_all(command='refresh_inventory')
    job = cron.new(command="/bin/bash -l -c 'ash --refresh_inventory'")
    job.minute.every(minutes)
    cron.write()
