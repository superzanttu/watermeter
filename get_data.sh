export RSYNC_PASSWORD="xxx"
rsync -avzh --delete pi@192.168.0.22:/var/www/html ./html
rsync -avzh --delete pi@192.168.0.22:/home/pi/camera ./camera
