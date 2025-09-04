date >> ~/log/cron_main.log
echo "start speecher data maker"
/home/ubuntu/.local/bin/pipenv run python3 main.py >> ~/log/cron_main.log
#echo "start backup"
#date >> ~/log/cron_backup.log
#/home/ubuntu/.local/bin/pipenv run python3 backup.py >> ~/log/cron_backup.log