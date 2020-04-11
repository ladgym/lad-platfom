FROM python:3.6

WORKDIR /app

ENV FLASK_ENV "production"

COPY lad-common /app/lad-common
COPY lad-crm /app/lad-crm

# CIRCLE_BUILD_NUM required before pip install of backend-common,
# because the base image doesn't have git.
# it is quicker to install the requirements than install git from apt.
ARG CIRCLE_BUILD_URL=""
ARG CIRCLE_BUILD_NUM=""

ENV CIRCLE_BUILD_URL=$CIRCLE_BRANCH
ENV CIRCLE_BUILD_NUM=$CIRCLE_BUILD_NUM

RUN cd lad-crm && pip --no-cache-dir install -r requirements/production.txt

WORKDIR /app/lad-crm

STOPSIGNAL SIGINT
#ENTRYPOINT ["lad-crm/scripts/run_uwsgi.sh"]




