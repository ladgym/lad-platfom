#!/bin/bash

export NUM_UWSGI_PROCS=${LAD_CRM_UWSGI_NUM_PROCS:-1}
export NUM_UWSGI_THREADS=${LAD_CRM_UWSGI_NUM_THREADS:-8}

UWSGI_OPTS=""
if [ "${FLASK_ENV}" = "production" ]; then
    UWSGI_OPTS+="--ini conf/uwsgi.ini:production"
else
    UWSGI_OPTS+="--ini conf/uwsgi.ini:default"
fi

uwsgi ${UWSGI_OPTS}