# twstock

## Requirements

sudo apt install apache2
sudo a2enmod cgid

<Directory /var/www/>
        Options +ExecCGI
        AddHandler cgi-script .py
</Directory>
