#!/bin/sh
kubectl -n kubernetes-dashboard create token admin-user --duration=488h > token.txt
