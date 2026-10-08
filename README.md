# twstock

## Requirements

sudo apt install apache2
sudo a2enmod cgid

<Directory /var/www/html/twstock>
        Options +ExecCGI
        AddHandler cgi-script .py
</Directory>

# fonts

cp -rf fonts ~/.fonts
rm ~/.cache/matplotlib

# /etc/apache2/envvars
export APACHE_RUN_USER=www-data
export APACHE_RUN_GROUP=www-data
