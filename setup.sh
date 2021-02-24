sudo pip3 install -r requirements.txt
sudo cp eduprojects.conf /etc/supervisor/conf.d/
sudo cp eduprojects_nginx.conf /etc/nginx/sites-enabled/
sudo supervisorctl update
sudo systemctl restart nginx
sudo certbot --nginx -d eduprojects.telepat.online