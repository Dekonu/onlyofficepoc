#!/bin/bash
sudo docker run -i -t -d -p 80:80 --restart=always \
-v $pwd/app/onlyoffice/documentserver/data:/var/www/onlyoffice/Data \
-e ALLOW_META_IP_ADDRESS=true \
-e ALLOW_PRIVATE_IP_ADDRERSS=true \
-e WOPI_ENABLED=true \
onlyoffice/documentserver-de
