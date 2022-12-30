#!/bin/sh
echo "Decrypting environment variables with passphrase"
gpg --quiet --batch --yes --decrypt --passphrase="$1" --output .env .env.gpg