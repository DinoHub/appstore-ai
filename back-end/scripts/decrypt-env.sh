#!/bin/sh
# This script is used in CICD to decrypt the .env file
# unlike the other decrypt script, the passphrase is passed
# as an environment variable
gpg --quiet --batch --yes --decrypt --passphrase="$GPG_PASSPHRASE" \
--output src/config/.env src/config/.env.gpg
