import logging

logging.basicConfig(format='[Log] Process ID: %(process)d, levelname: %(levelname)s, message: %(message)s', level=logging.DEBUG)

def info(msg):
    logging.info(msg)

def error(msg):
    logging.error(msg)

def warning(msg):
    logging.warning(msg)

def debug(msg):
    logging.debug(msg)