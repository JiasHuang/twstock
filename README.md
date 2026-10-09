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

