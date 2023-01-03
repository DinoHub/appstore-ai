#!/bin/sh
echo "Encrypting environment variables with passphrase"
gpg --symmetric --cipher-algo AES256 --batch --passphrase "$1" --output .env.gpg .env
