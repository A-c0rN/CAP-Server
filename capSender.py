import base64

import requests

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
payload2 = {}


def isInt(number):
    try:
        int(number)
    except ValueError:
        return False
    else:
        return True


def envDef():
    env_inp = input("Environment? (L/D/B): ")
    if env_inp.lower == "l":
        env = ["live"]
    elif env_inp.lower == "d":
        env = ["dev"]
    elif env_inp.lower() == "b":
        env = ["live", "dev"]
    else:
        return None
    return env


def evntDef():
    evnt_inp = input("Event? (IPAWS Only): ")
    try:
        event_code = event_dict.get(evnt_inp)
        if event_code == None:
            event = list(event_dict.keys())[list(event_dict.values()).index(evnt_inp)]
            event_code = event_dict.get(event)
    except KeyError:
        print("Invalid Event.")
        return None
    except ValueError:
        print("Invalid Event.")
        return None
    return event_code


def durDef():
    dur_inp = input("Duration? (HHMM): ")
    if isInt(dur_inp) and len(dur_inp) == 4:
        duration = dur_inp
    else:
        return None
    return duration


def descDef():
    desc_inp = input("Alert Text?: ")
    if len(desc_inp) > 0:
        description = desc_inp
    else:
        oof = input("Empty Alert Desc? [Y/n]: ")
        if oof.lower() in ["y", "yes"]:
            return "None"
        else:
            return None
    return description


def areaDef():
    area = ""
    while True:
        area_inp = ""
        area_inp_2 = ""
        area_inp = input("FIPS Codes?: ")
        if isInt(area_inp) and len(area_inp) == 6:
            if area == "":
                area += area_inp
            if not area_inp in area:
                area += " " + area_inp
        else:
            return None
        area_inp_2 = input("Add Another? [Y/n]: ")
        if area_inp_2.lower() in ["y", "yes"]:
            pass
        else:
            break
    return area


def audDef():
    aud_inp = input("Audio File? [Y/n]: ")
    if aud_inp.lower() in ["y", "yes"]:
        while True:
            try:
                aud_inp_file = input("Audio File Path (MP3 Only): ")
                if aud_inp_file == "":
                    return False
                if not aud_inp_file.endswith(".mp3"):
                    print("Not an MP3 File.")
                else:
                    aud = base64.b64encode(open(aud_inp_file, "rb").read())
                    break
            except FileNotFoundError:
                print("File Does Not Exist.")
    else:
        return False
    return aud


def genPayload():
    env = ""
    evnt = ""
    dur = ""
    desc = ""
    area = ""
    aud = ""
    while True:
        if not env:
            env = envDef()
        elif not evnt:
            evnt = evntDef()
        elif not dur:
            dur = durDef()
        elif not desc:
            desc = descDef()
        elif not area:
            area = areaDef()
        elif not aud:
            aud = audDef()
            if aud == False and not aud == None:
                break
        else:
            break
    payload = {
        "env": env,
        "event": evnt,
        "duration": dur,
        "description": desc,
        "area": area,
    }
    if aud:
        payload["base64"] = aud
    return payload


def sendPayload(payload):
    cogID = input("Please enter COG-ID: ")
    headers = {"CogID": cogID}
    r = requests.post("http://localhost:5000/POST/new", json=payload, headers=headers)
    print(r.status_code, r.content)


pl = genPayload()
print(pl)
sendPayload(pl)
