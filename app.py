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


def esl_event_handler(event):
    """
    Handle FreeSWITCH ESL events.
    """
    if not event:
        return

    event_name = event.getHeader("Event-Name")
    match event_name:
        case "CHANNEL_ANSWER":
            uuid = event.getHeader("Unique-ID")
            destination_number = event.getHeader("Caller-Destination-Number")
            if destination_number == config.get('NUMBER_TO_DIAL'):
                logger.info("Call %s answered", uuid)
        case "CUSTOM":
            event_subclass = event.getHeader("Event-Subclass")
            match event_subclass:
                case "avmd::beep":
                    uuid = event.getHeader("Unique-ID")
                    logger.info("Beep detected on call %s", uuid)
                case "avmd::start":
                    uuid = event.getHeader("Unique-ID")
                    logger.info("AVMD started on call %s", uuid)
                case _:
                    logger.info("Custom event: %s", event_subclass)
        case _:
            if event_name != "SERVER_DISCONNECTED":
                logger.debug("Received event: %s", event_name)


def avmd_start(esl_connection, uuid):
    """
    Start beep detection on channel using mod_avmd.
    """
    esl_connection.api(f"avmd {uuid} start")
    logger.info("AVMD started on call %s", uuid)


def originate_call(esl_connection, leg):
    """
    Initiates an outbound call from FreeSWITCH to a specified extension.

    This method uses an existing ESLconnection object to originate an outbound
    call to the specified extension on the FreeSWITCH server.

    Args:
        esl_connection (ESLconnection): An existing connection object to the FreeSWITCH server.
        leg (str): formatted extension.

    Returns:
        str or None: The UUID of the call if successfully originated, otherwise None.
    """
    response = esl_connection.api(
        "originate", f"{leg} &park()")
    if response:
        uuid = response.getBody().split()[1]
        logger.info('Call originated: %s', uuid)
        avmd_start(esl_connection, uuid)
        return uuid

    logger.error('Could not originate call')
    return None


def originate_call_to_sip_uri(esl_connection, sip_uri):
    """
    Initiates an outbound call from FreeSWITCH to a specified SIP URI.
    """
    originate_format = f"sofia/external/{sip_uri}"
    return originate_call(esl_connection, originate_format)


def originate_call_to_extension(esl_connection, extension):
    """
    Initiates an outbound call from FreeSWITCH to a local extension.
    """
    originate_format = f"sofia/internal/{extension}"
    return originate_call(esl_connection, originate_format)


def originate_call_to_dialplan_section(esl_connection, expression):
    """
    Initiates an outbound call from FreeSWITCH to a dialplan section.
    """
    originate_format = f"loopback/{expression}"
    return originate_call(esl_connection, originate_format)


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

    originate_call_to_sip_uri(esl_conn, config.get('SIP_ENDPOINT'))
    # originate_call_to_extension(esl_conn, config.get('EXTENSION_TO_CALL'))
    # originate_call_to_dialplan_section(
    #    esl_conn, config.get('DIALPLAN_EXPRESSIONs'))

    esl_conn.events("plain", "ALL")
    while True:
        event = esl_conn.recvEvent()
        esl_event_handler(event)


if __name__ == "__main__":
    main()
