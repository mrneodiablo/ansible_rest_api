#!/usr/bin/env bash
PROJECT_DIR="/mto_automation"
cd ${PROJECT_DIR}
celery multi start worker -A polemarch.wapp:app  -B -f /var/log/polemarch/worker.log -l WARNING --pidfile=/var/run/polemarch/worker.pid --schedule=/var/run/polemarch/beat-schedule