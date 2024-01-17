import os
import random
import string
import xml.etree.ElementTree as et
from datetime import datetime, timedelta

import dateutil.parser

# from google.cloud import texttospeech
import pytz
from signxml import XMLSigner, methods

# Google Cloud TTS shit
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./data/app.json"
cert = open("cert.pem", "rb").read()
key = open("key.pem", "rb").read()
# UTC Offset
offset = datetime.now(pytz.timezone("America/Chicago")).strftime("%z")

# def TTS(input, uid):

#     client = texttospeech.TextToSpeechClient()
#     synthesis_input = texttospeech.SynthesisInput(text=input)
#     voParams = texttospeech.VoiceSelectionParams(language_code='en-US', name='en-US-Wavenet-D')
#     voConfig = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

#     request = client.synthesize_speech(input=synthesis_input, voice=voParams, audio_config=voConfig)

#     with open(f"media/{uid}.mp3", "wb") as output:
#         output.write(request.audio_content)


def prettify(element, indent="  "):
    queue = [(0, element)]  # (level, element)
    while queue:
        level, element = queue.pop(0)
        children = [(level + 1, child) for child in list(element)]
        if children:
            element.text = "\n" + indent * (level + 1)  # for child open
        if queue:
            element.tail = "\n" + indent * queue[0][0]  # for sibling open
        else:
            element.tail = "\n" + indent * (level - 1)  # for parent close
        queue[0:0] = children  # prepend so children come before siblings


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


def addToIPAWSFeed(eventCode, stateCode, id):
    et.register_namespace("", "http://www.w3.org/2005/Atom")

    feedFile = et.parse("api_feed.xml")
    feedRoot = feedFile.getroot()

    global time
    time = (
        str(dateutil.parser.parse(datetime.utcnow().isoformat()))[:-3].replace(" ", "T")
        + "Z"
    )

    # New entry contents
    thing = et.Element("entry")
    et.SubElement(thing, "title", type="text").text = eventCode
    et.SubElement(
        thing, "link", href=f"http://localhost:5000/IPAWSOPEN_EAS_SERVICE/rest/eas/{id}"
    )
    et.SubElement(
        thing, "id"
    ).text = f"http://localhost:5000/IPAWSOPEN_EAS_SERVICE/rest/eas/{id}"
    et.SubElement(thing, "updated").text = time
    for i in stateCode:
        et.SubElement(thing, "category", term=f"{i}", label="statefips")
    et.SubElement(thing, "category", term=f"{eventCode}", label="event")

    # Update this side of the feed.
    feedRoot.find("{http://www.w3.org/2005/Atom}updated").text = time

    feedRoot.append(thing)
    prettify(feedRoot)
    xml = et.ElementTree(feedRoot)
    xml.write("api_feed.xml", encoding="UTF-8", xml_declaration=False)


def updateIPAWSTimestamp():
    et.register_namespace("", "http://www.w3.org/2005/Atom")
    xml_root = et.Element("feed", xmlns="http://www.w3.org/2005/Atom")
    et.SubElement(
        xml_root, "title", type="text"
    ).text = "MISSINGTEXTURES SOFTWARE - CAP SERVER"
    et.SubElement(xml_root, "updated").text = time
    et.SubElement(
        xml_root, "id"
    ).text = "http://localhost:5000/IPAWSOPEN_EAS_SERVICE/rest/feed"

    # Make it purdy.
    prettify(xml_root)

    # Push to the web server
    xml = et.ElementTree(xml_root)
    xml.write("api_update.xml", encoding="UTF-8", xml_declaration=False)


def createCAPAlert(
    event: str,
    fips: str,
    description: str,
    duration: str,
    audio: bool = False,
    dev: bool = False,
    base64=None,
    pphrase: bytes = b"changeme",
):
    # Time shit
    sent = (
        str(datetime.now().replace(microsecond=0).isoformat())[0:23].replace(" ", "T")
        + offset[0:3]
        + ":"
        + offset[3:6]
    )

    # FIPS
    locs = fips.split()
    loc_States = []

    # Events interperetation shit
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

    event_code = event_dict.get(event)
    if event_code == None:
        event = list(event_dict.keys())[list(event_dict.values()).index(event)]
        event_code = event_dict.get(event)

    # CAP unique ID
    uid = "MSNGTXTRS-" + "".join(
        random.choices(string.ascii_uppercase + string.digits, k=8)
    )

    # Define the root element and sub-elements
    et.register_namespace("", "urn:oasis:names:tc:emergency:cap:1.2")
    et.register_namespace("ds", "http://www.w3.org/2000/09/xmldsig#")
    xml_root = et.Element("alert", xmlns="urn:oasis:names:tc:emergency:cap:1.2")
    et.SubElement(xml_root, "identifier").text = uid
    et.SubElement(xml_root, "sender").text = "admin@localhost"
    et.SubElement(xml_root, "sent").text = sent
    et.SubElement(xml_root, "status").text = "Actual"
    et.SubElement(xml_root, "msgType").text = "Alert"
    et.SubElement(xml_root, "source").text = "CAP SERVER JSON API"
    et.SubElement(xml_root, "scope").text = "Public"
    et.SubElement(xml_root, "code").text = "IPAWSv1.0"

    # Make the <info> section
    info = et.Element("info")
    et.SubElement(info, "language").text = "en-US"
    et.SubElement(info, "category").text = "Other"

    et.SubElement(info, "event").text = event
    et.SubElement(info, "urgency").text = "Unknown"
    et.SubElement(info, "severity").text = "Unknown"

    # Put the event code into the CAP alert.
    eventCode = et.SubElement(info, "eventCode")
    et.SubElement(eventCode, "valueName").text = "SAME"
    et.SubElement(eventCode, "value").text = event_code

    # Expiration
    et.SubElement(info, "expires").text = cap_create_expire(duration)
    et.SubElement(info, "description").text = description

    # Parameters
    parameter1 = et.SubElement(info, "parameter")
    et.SubElement(parameter1, "valueName").text = "EAS-ORG"
    et.SubElement(parameter1, "value").text = "EAS"
    parameter2 = et.SubElement(info, "parameter")
    et.SubElement(parameter2, "valueName").text = "timezone"
    et.SubElement(parameter2, "value").text = "CDT"

    # Resource
    if audio == True:
        resource = et.SubElement(info, "resource")
        et.SubElement(resource, "resourceDesc").text = "EAS Broadcast Content"
        et.SubElement(resource, "mimeType").text = "audio/x-ipaws-audio-mp3"
        et.SubElement(
            resource, "uri"
        ).text = f"https://s3.amazonaws.com/ipawstestbucket/MediaCloud/HSEMDemo.mp3"
    elif audio == False and base64 != None:
        resource = et.SubElement(info, "resource")
        et.SubElement(resource, "resourceDesc").text = "EAS Broadcast Content"
        et.SubElement(resource, "mimeType").text = "audio/x-ipaws-audio-mp3"
        et.SubElement(resource, "derefUri").text = base64

    xml_root.append(info)

    # Locations
    area = et.SubElement(info, "area")
    et.SubElement(area, "areaDesc").text = "FIPS"

    for fips in locs:
        loc_States.append(fips[1:3])
        geocode = et.SubElement(area, "geocode")
        et.SubElement(geocode, "valueName").text = "SAME"
        et.SubElement(geocode, "value").text = fips

    xml_root.append(
        et.fromstring(
            '<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#" Id="placeholder"></ds:Signature>'
        )
    )

    xml_root = XMLSigner(method=methods.enveloped).sign(
        xml_root,
        key=key,
        cert=cert,
        passphrase=pphrase,
    )
    # prettify(xml_root)

    # Push to the web server
    xml = et.ElementTree(xml_root)

    xml.write(f"api.xml", encoding="UTF-8", xml_declaration=True, default_namespace="")

    if dev == False:
        hrm = False
        while hrm == False:
            uid2 = "".join(random.choices(string.digits, k=7))
            if uid2 not in [
                f
                for f in os.listdir("Web/alerts/")
                if os.path.isfile(os.path.join("Web/alerts/", f))
            ]:
                hrm = True
        os.system(f"cp api.xml Web/alerts/{uid2}")
        addToIPAWSFeed(event_code, loc_States, uid2)
        updateIPAWSTimestamp()

    # TTS(description, uid)
    ## IF DOING TTS, COPY FILES TO PATH HERE
