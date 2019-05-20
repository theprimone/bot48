import os

from apscheduler.schedulers.blocking import BlockingScheduler
from start import start


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(start, 'cron', hour='7-23, 0-2')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
