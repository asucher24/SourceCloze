declare myproject='sourcecloze'
declare projectpath=$( pwd )
declare apacheFile='/etc/apache2/sites-available/000-default-le-ssl.conf'
declare apacheServiceFile='/etc/systemd/system/apache2.service.d/override.conf'

patch_file () {
    declare file="$1"
    declare regex="$2"
    declare addBeforeRegex="$3"
    declare file_content=$( cat "${file}" )
    if grep -q "$regex" "$file";
        then
            echo ""
            echo "##### $file already contains: \"$regex\""
        else
            echo ""
            echo "##### $file does not contain: \"$regex\" ... adding ..."

	        if [[ "$4" == "withoutTab"  ]]; 
	        then
		    	sed -i "s/$addBeforeRegex/$regex\n$addBeforeRegex/g" ${file}
	        else
		    	sed -i "s|$addBeforeRegex|\t$regex\n$addBeforeRegex|g" ${file}
	        fi

    fi
}


echo "# Automatic installation of $myproject"
echo "# For complete installation take a look into:"
echo "# https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-apache-and-mod_wsgi-on-ubuntu-14-04"
cd ..
chmod 771 SourceCloze
cd -


echo "########################### Installing dependencies throught 'apt' ###########################"
apt-get install python3 python3-pip apache2 libapache2-mod-wsgi-py3 -y
apt-get install certbot  python-certbot-apache -y

echo "#### Install compilers for syntax check in application"
apt-get install default-jdk -y
apt-get install gcc -y 
apt-get install nodejs -y
echo "#### Install docker"
apt-get install apt-transport-https ca-certificates curl software-properties-common gnupg2 -y
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
apt-get update
apt-get install docker-ce -y
usermod -aG docker www-data
echo ""
echo ""
echo ""
echo "########################### Upgrading pip ###########################"
python3 -m pip install --upgrade pip

echo "########################### Installing virtualenv ###########################"
rm -r "${projectpath}/${myproject}env"
python3 -m pip install virtualenv
# python3 -m pip install python3-venv

echo ""
echo ""
echo ""
echo "########################### Creating VirtualEnv ###########################"
virtualenv "${myproject}env"
echo ""
echo ""
echo ""
source "./${myproject}env/bin/activate"
mkdir "./${myproject}env/compiler"
echo "./${myproject}env/bin/activate"
echo $VIRTUAL_ENV
echo "########################### Installing requirements inside virtualenv ###########################"
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip freeze
which cpp
echo ""
echo ""
echo ""
echo "########################### Create Certificate with Lets Encrypt ###########################"
declare fqn=$(host -TtA $(hostname -s)|grep "has address"|awk '{print $1}') ;
if [[ "${fqn}" == "" ]] ; then fqn=$(hostname -s) ; fi ;
declare file1="${projectpath}/config/.env"
echo "${fqn}"
declare fqn="${fqn,,}"
echo "${fqn}"
declare regex1="URL=\"https:\/\/${fqn}\""
echo "${regex1}"
declare addBefore="DEBUG"
certbot --apache -n -d "${fqn}" 

echo ""
echo ""
echo ""
echo "########################### Preparing Django ###########################"
#URL = "<souceclozeurl>" # will be changed automaticly
patch_file "$file1" "$regex1" "$addBefore" "withoutTab"

echo "#### Run Django commands"
python3 manage.py makemigrations
python3 manage.py migrate  --run-syncdb
python3 manage.py collectstatic --no-input
# echo ""
# echo ""
# echo ""
# echo "#### Please create your django (super-)user "
# echo "#### Or cancel this command with Control+C"
# python3 manage.py createsuperuser
#python3 manage.py runserver


# echo ""
# echo ""
# echo ""
# echo "########################### Creating Documentation ###########################"
# cd assets/docs
# make html
# cd -

# echo "########################## Create Documentation ###########################"
# # with Pycco
# pycco pages/*.py -p -d assets/doc
# pycco poll_api/*.py -p -d assets/doc
# pycco utils/*.py -p -d assets/doc
# pycco authentication/*.py -p -d assets/doc

echo ""
echo ""
echo ""
echo "########################### Deactivate VirtualEnv ###########################"
deactivate

echo ""
echo ""
echo ""
echo "########################### Apache2 Configuration ###########################"



declare addBeforeRegex1="</VirtualHost>"
declare file1="$apacheFile"
declare regex1="Include conf-available/sourcecloze.conf"
patch_file "$file1" "$regex1" "$addBeforeRegex1" "addBefore"

declare file1="/etc/apache2/sites-available/000-default.conf"
declare regex1='RewriteEngine On'
patch_file "$file1" "$regex1" "$addBeforeRegex1" "addBefore"

# declare file1="/etc/apache2/sites-available/000-default.conf"
declare regex1='RewriteCond %{SERVER_PORT} !^443\$'
patch_file "$file1" "$regex1" "$addBeforeRegex1" "addBefore"

# declare file1="/etc/apache2/sites-available/000-default.conf"
declare regex1='RewriteRule ^(.*)\$ https://%{HTTP_HOST}\$1 \[R=301,L\]'
patch_file "$file1" "$regex1" "$addBeforeRegex1" "addBefore"


declare regex="PATH${myproject}PATH"
sed "s|PATH${myproject}PATH|$projectpath|g" apache.${myproject}.conf > .apache.${myproject}.conf
cp .apache.${myproject}.conf /etc/apache2/conf-available/sourcecloze.conf
rm .apache.${myproject}.conf


echo "########################### Preparing apache ###########################"
# sed -i "s|PrivateTmp=true|PrivateTmp=false|g" "${apacheServiceFile}"
echo "PrivateTmp=false" > "${apacheServiceFile}"
systemctl daemon-reload

mkdir /builds/shared/SourceCloze
chown -R www-data /builds/shared/SourceCloze
echo ""
echo ""
echo ""
echo "########################### Preparing files ###########################"
chmod 664 ${projectpath}/.db.sqlite3
chown :www-data ${projectpath}/.db.sqlite3
chown :www-data ${projectpath}
chown :www-data "${projectpath}/${myproject}env"
echo ""
echo ""
echo ""
echo "########################## Configure services ###########################"
a2ensite default-ssl
a2enmod ssl
a2enmod rewrite
service apache2 restart
