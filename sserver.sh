#!/bin/bash

export DOCUMENT_SERVER_PRIVATE_URL=http://localhost:8000
export DOCUMENT_SERVER_PUBLIC_URL=http://10.4.8.109:80
export EXAMPLE_URL=http://localhost:8000
export JWT_SECRET="$(cat .secret)"


python3 manage.py runserver
