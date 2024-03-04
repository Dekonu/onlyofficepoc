#!/bin/bash

export DOCUMENT_SERVER_PRIVATE_URL='http://localhost:80'
export DOCUMENT_SERVER_PUBLIC_URL='http://localhost:80'
export EXAMPLE_URL='http://host.docker.internal:8000'

python3  manage.py run-server
