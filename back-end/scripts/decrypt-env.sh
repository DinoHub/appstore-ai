#!/bin/sh
gpg --quiet --batch --yes --decrypt --passphrase="$GPG_PASSPHRASE" \
--output src/config/.env src/config/.env.gpg
