#!/bin/sh
echo "Encrypting environment variables with passphrase"
gpg --symmetric --cipher-algo AES256 --batch --passphrase "$GPG_PASS" --output .env.gpg .env