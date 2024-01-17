from datetime import datetime, timedelta

import dateutil.parser
import pytz

offset = datetime.now(pytz.timezone("America/Chicago")).strftime("%z")


event_dict = {
    "Adminstrative Message": "ADR",
    "Avalanche Watch": "AVA",
    "Avalanche Warning": "AVW",
    "Blue Alert": "BLU",
    "Child Abduction Emergency": "CAE",
    "Civil Danger Warning": "CDW",
    "Civil Emergency Message": "CEM",
    "Practice/Demo Warning": "DMO",
    "Earthquake Warning": "EQW",
    "Immediate Evacuation": "EVI",
    "Fire Warning": "FRW",
    "Hazardous Materials Warning": "HMW",
    "Local Area Emergency": "LAE",
    "Law Enforcement Warning": "LEW",
    "Nuclear Power Plant Warning": "NUW",
    "Radiological Hazard Warning": "RHW",
    "Required Monthly Test": "RMT",
    "Required Weekly Test": "RWT",
    "Shelter in Place Warning": "SPW",
    "911 Telephone Outage Emergency": "TOE",
    "Volcano Warning": "VOW",
}

event = "DMO"
event_code = event_dict.get(event)
if event_code == None:
    event = list(event_dict.keys())[list(event_dict.values()).index(event)]
    event_code = event_dict.get(event)
print(event_code, event)


def cap_create_expire(duration):
    if len(duration) > 4:
        duration = "0015"
    H, M = int(duration[:-2]), int(duration[2:])
    if H > 0:
        if M >= 30:
            M = 30
        else:
            M = 0
    print(f"Hours: {H}, Minutes: {M}")
    now = datetime.now().replace(microsecond=0).isoformat()
    time_parsed = dateutil.parser.parse(now)
    final = time_parsed + timedelta(hours=H, minutes=M)
    return str(final).replace(" ", "T") + offset[0:3] + ":" + offset[3:6]


dur = "99999"
print(cap_create_expire(dur))
