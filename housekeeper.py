import time
from config import Config
from alert_analyzer import check_tracked_time, delete_non_tracked
from configurator import get_conf

def run_periodic_checks(period, time_window):
    time.sleep(30)
    while True:
        check_tracked_time(int(time_window)*86400)
        delete_non_tracked()
        time.sleep(int(period))

if __name__ == "__main__":
    run_periodic_checks(get_conf('check_period'), get_conf('track_time'))