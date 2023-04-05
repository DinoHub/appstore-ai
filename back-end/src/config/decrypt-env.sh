#!/bin/sh
echo "Decrypting environment variables with passphrase"
gpg --quiet --batch --yes --decrypt --passphrase="$GPG_PASS" --output .env .env.gpg