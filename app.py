"""FreeSWITCH ESL mod_avmd beep detection sample"""

import logging
import sys
import time
from ESL import ESLconnection
from dotenv import dotenv_values

log_level_mapping = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

config = dotenv_values('.env')

log_level = config.get('LOG_LEVEL', 'INFO')
log_level = log_level_mapping.get(log_level.upper(), logging.INFO)

logger = logging.getLogger('freeswitch_audio_stream_poc')
logging.basicConfig(level=log_level)

log_console_handler = logging.StreamHandler(sys.stdout)
log_console_handler.setLevel(log_level)
log_console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(log_console_handler)

if config.get('LOG_TO_FILE', 'True'):
    log_file = config.get('LOG_FILE', 'fs_esl.log')
    log_file_handler = logging.FileHandler(log_file)
    log_file_handler.setLevel(log_level)
    log_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_file_handler)


def connect_to_freeswitch():
    """
    Connects to a FreeSWITCH server using ESL (Event Socket Library).

    This function establishes a connection to a FreeSWITCH server using ESL
    (Event Socket Library) and returns the connection object if successful.

    Returns:
        ESLconnection or None: The ESLconnection object if connection is successful,
        otherwise None.
    """
    con = ESLconnection(config.get('FS_HOST'), config.get(
        'FS_ESL_PORT'), config.get('FS_ESL_PASSWORD'))
    if con.connected():
        logger.info('Connected to FreeSWITCH')
        return con

    logger.error('Could not connect to FreeSWITCH!')
    return None


def originate_call(esl_connection, sip_endpoint):
    """
    Initiates an outbound call from FreeSWITCH to a specified extension.

    This method uses an existing ESLconnection object to originate an outbound
    call to the specified extension on the FreeSWITCH server.

    Args:
        esl_connection (ESLconnection): An existing connection object to the FreeSWITCH server.
        sip_endpoint (str): The SIP endpoint to call.

    Returns:
        str or None: The UUID of the call if successfully originated, otherwise None.
    """
    response = esl_connection.api(
        "originate", f"sofia/external/{sip_endpoint} &park()")
    if response:
        # uuid = response.getBody().decode().split(' ')[1]
        uuid = response.getBody().split()[1]
        logger.info('Call originated: %s', uuid)
        return uuid

    logger.error('Could not originate call')
    return None


def originate_call_to_extension(esl_connection, extension):
    """
    Initiates an outbound call from FreeSWITCH to a specified extension.

    This method uses an existing ESLconnection object to originate an outbound
    call to the specified extension on the FreeSWITCH server.

    Args:
        esl_connection (ESLconnection): An existing connection object to the FreeSWITCH server.
        extension (str): The SIP extension to call.

    Returns:
        str or None: The UUID of the call if successfully originated, otherwise None.
    """
    # response = esl_connection.api(
    #    f"originate {{ignore_early_media=true}}user/{extension} &park()")
    response = esl_connection.api(
        "originate", f"user/1010 {extension}")
    if response:
        # uuid = response.getBody().decode().split(' ')[1]
        uuid = response.getBody().split()[1]
        logger.info('Call originated: %s', uuid)
        return uuid

    logger.error('Could not originate call')
    return None


def play_beep(esl_connection, uuid):
    """
    Plag a beep sound (via tone_stream) on the call.

    Args:
        esl_connection (ESLconnection): An existing connection object to the FreeSWITCH server.
        uuid (str): Call UUID.

    Returns:
        None
    """

    esl_connection.api(
        f"uuid_broadcast {uuid} tone_stream://L=3;%(1000,0,350,440)")
    logger.info("Playing tone stream: %s", uuid)

    time.sleep(4)
    response = esl_connection.api(f"uuid_getvar {uuid} avmd_detect")
    logger.info("BEEP DETECTION STATUS: %s", response.getBody())


def main():
    """
    Main function
    """
    esl_conn = connect_to_freeswitch()
    if esl_conn is None:
        logger.error('Exiting...')
        sys.exit(1)

    esl_conn.events("plain", "ALL")

    # uuid = originate_call(esl_conn, config.get('SIP_ENDPOINT'))
    uuid = originate_call_to_extension(esl_conn, '74344')

    while True:
        event = esl_conn.recvEvent()
        if event:
            event_name = event.getHeader("Event-Name")
            logger.info("Event received: %s", event_name)
            logger.debug("Event data: %s", event.serialize())
            uuid = event.getHeader("Unique-ID")
            if event_name == "CHANNEL_ANSWER":
                logger.info("Call answered: %s", uuid)
                esl_conn.api(f"avmd {uuid} start")
                logger.info("Beep detection started: %s", uuid)
            if event_name == "CUSTOM":
                event_subclass = event.getHeader("Event-Subclass")
                if event_subclass.startswith("avmd"):
                    if event_subclass == "avmd::beep":
                        logger.info("Beep detected: %s", uuid)
                    else:
                        logger.info("Custom AVMD event: %s", event_subclass)
                        if event_subclass == "avmd::start":
                            logger.info("Got avmd::start event: %s", uuid)
                            # play_beep(esl_conn, uuid)


if __name__ == "__main__":
    main()
