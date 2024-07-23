#/bin/bash
sudo cp -p SkiTunes/skitunes/log/skimoviesongs.log ./skimoviesongs.log.`date -I`
sudo rm -R SkiTunes/
git clone https://github.com/Gin-G/SkiTunes.git
cd SkiTunes/skitunes
sudo pkill gunicorn
gunicorn --daemon --bind 0.0.0.0:8000 wsgi:app