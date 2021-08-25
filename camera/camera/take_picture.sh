cd /var/www/html/pictures

FILE=water_$(date +%Y-%m-%d-%H%M%S).jpg

echo $FILE

raspistill  -o $FILE
#convert -pointsize 40 -fill yellow -draw "text 15,50 '$(date)'" water_raw.jpg water.jpg


