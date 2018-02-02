def get_logger():
    import logging

    logger = logging.getLogger('debug')             # create logger
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('debug.log', mode='w') # create file handler which logs even debug messages
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()                        # create console handler and set level to debug
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')# create formatter and add it to the handlers
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)                               # add the handlers to the logger
    logger.addHandler(ch)

    return logger