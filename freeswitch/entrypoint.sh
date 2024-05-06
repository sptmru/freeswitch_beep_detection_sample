#!/bin/bash

sed -i '/<X-PRE-PROCESS cmd="set" data="default_password=[^"]*"\/>/c\<X-PRE-PROCESS cmd="set" data="default_password='"${EXTENSION_PASSWORD:-extensionpassword}"'"\/>' /usr/local/freeswitch/conf/vars.xml

sed -i '/<context name="default">/a \
<extension name="play_beep_tone">\n\
      <condition field="destination_number" expression="^74331$">\n\
        <action application="avmd_start" data="inbound_channel=1,outbound_channel=1,debug=0,report_status=1,fast_math=1,require_continuous_streak=0,require_continuous_streak_amp=0,simplified_estimation=1,detection_mode=1"/>\n\
        <action application="answer"/>\n\
        <action application="playback" data="tone_stream://L=3;%(500,6850,850)"/>\n\
        <action application="avmd_stop"/>\n\
        <action application="hangup"/>\n\
      </condition>\n\
    </extension>' /usr/local/freeswitch/conf/dialplan/default.xml

/usr/local/freeswitch/bin/freeswitch -nonat -nf -nc