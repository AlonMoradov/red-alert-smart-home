mkdir $HOME/red_alert_hue_lights
cd $HOME/red_alert_hue_lights

git init
git pull https://github.com/AlonMoradov/red_alert_smart_home.git

chmod +x $HOME/red_alert_hue_lights/red_alert.sh
chmod +x $HOME/red_alert_hue_lights/red_alert_watchdog.sh

python3 -m venv $HOME/red_alert_hue_lights/venv
source $HOME/red_alert_hue_lights/venv/bin/activate
pip install -r $HOME/red_alert_hue_lights/requirements.txt


(crontab -l 2>/dev/null; echo "@reboot nohup $HOME/red_alert_hue_lights/red_alert.sh > $HOME/red_alert.log 2>&1 &") | crontab -
(crontab -l 2>/dev/null; echo "@reboot nohup $HOME/red_alert_hue_lights/red_alert_watchdog.sh > $HOME/red_alert_watchdog.log 2>&1 &") | crontab -
(crontab -l 2>/dev/null; echo "@reboot nohup $HOME/red_alert_hue_lights/venv/bin/python3 $HOME/red_alert_hue_lights/api.py > $HOME/api.log 2>&1 &") | crontab -
(crontab -l 2>/dev/null; echo "@reboot sudo nohup $HOME/red_alert_hue_lights/venv/bin/python3 -m http.server 80 --directory $HOME/red_alert_hue_lights/web > $HOME/http_server.log 2>&1 &") | crontab -


nohup $HOME/red_alert_hue_lights/red_alert.sh > $HOME/red_alert.log 2>&1 &
nohup $HOME/red_alert_hue_lights/red_alert_watchdog.sh > $HOME/red_alert_watchdog.log 2>&1 &
nohup $HOME/red_alert_hue_lights/venv/bin/python3 $HOME/red_alert_hue_lights/api.py > $HOME/api.log 2>&1 &
sudo nohup $HOME/red_alert_hue_lights/venv/bin/python3 -m http.server 80 --directory $HOME/red_alert_hue_lights/web > $HOME/http_server.log 2>&1 &
