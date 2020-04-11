import logging

from .app import init_app


app = init_app()
log = logging.getLogger()
log.info("Lad CRM application started")
