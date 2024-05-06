# FreeSWITCH mod_avmd beep detection sample

## Description

This is a simple Python ESL script which initiates a call to a SIP endpoint and tries to detect beep with `mod_avmd`.

## Usage

Default configuration values are ready to use — you will only need to update `SIP_ENDPOINT` variable in `docker-compose.yml`. Then  you can just start everything using Docker Compose: `docker compose up -d --build`. Once it's started, you can authorize on the FreeSWITCH server with any SIP client. Login credentials would be:

- SIP server: `localhost`
- Username: anything in range from 1000 to 1019
- Password: `extensionpassword` (could be changed in `docker-compose.yml`, variable `EXTENSION_PASSWORD`, service `freeswitch`, section `environment`)

Once ESL app is started, it would originate a call to `SIP_ENDPOINT` and start AVMD. You'll see beep detection in the logs.
You can also change the call logic — there is a method to call a local extension, and you can bridge it with a call to `SIP_ENDPOINT` to hear everything. Feel free to play around!

