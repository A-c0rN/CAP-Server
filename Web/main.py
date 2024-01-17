import os

from flask import (
    Blueprint,
    Response,
    abort,
    make_response,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import redirect

from . import xml_feed_handler as XFH

cogs = []  # Provide example "COG-IDs" here
pins = []  # Provide PINS here.
main = Blueprint("main", __name__)


@main.route("/favicon.ico")
def layout():
    try:
        return send_from_directory(
            directory="static", path="favicon.ico", mimetype="image/x-icon"
        )
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/", methods=["GET"])
def redToCap():
    try:
        return redirect(url_for("main.CAPSERV"), code=302)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/media/<path:filename>", methods=["GET"])
def download(filename):
    try:
        return send_from_directory(directory="media", path=filename)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/IPAWSOPEN_EAS_SERVICE/rest/eas/<path:filename>", methods=["GET"])
def download2(filename):
    try:
        if request.args.get("pin") != None:
            if request.args.get("pin") in pins:
                with open(f"Web/alerts/{filename}") as f:
                    x = f.read()
                return Response(x, mimetype="application/xml")
            else:
                return make_response("Invalid PIN", 403)
        else:
            return make_response("Required String parameter 'pin' is not present", 400)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/IPAWSOPEN_EAS_SERVICE/rest/feed", methods=["GET"])
def IPAWSFEED():
    try:
        if request.args.get("pin") != None:
            if request.args.get("pin") in pins:
                with open("api_feed.xml") as f:
                    x = f.read()
                return Response(x, mimetype="application/xml")
            else:
                return make_response("Invalid PIN", 403)
        else:
            return make_response("Required String parameter 'pin' is not present", 400)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/IPAWSOPEN_EAS_SERVICE/rest/update", methods=["GET"])
def IPAWSUPDATE():
    try:
        if request.args.get("pin") != None:
            if request.args.get("pin") in pins:
                with open("api_update.xml") as f:
                    x = f.read()
                    return Response(x, mimetype="application/xml")
            else:
                return make_response("Invalid PIN", 403)
        else:
            return make_response("Required String parameter 'pin' is not present", 400)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/CAP", methods=["GET"])
def CAPSERV():
    env = request.args.get("env")
    try:
        if env == "dev":
            with open("CAP/dev/alerts.xml", "r") as f:
                resp = f.read()
                return Response(resp, mimetype="text/xml")
        else:
            with open("CAP/alerts.xml", "r") as f:
                resp = f.read()
                return Response(resp, mimetype="text/xml")
    except FileNotFoundError:
        return abort(404)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)


@main.route("/POST/new", methods=["POST"])
def CAPAPI():
    try:
        if request.headers["CogID"] in cogs:
            event = request.json["event"]

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

            if not event and not event_code:
                return make_response(
                    f"Event Code is Invalid. Valid event codes are {', '.join(list(event_dict.keys())[:-1])}, and {list(event_dict.keys())[-1:][0]}",
                    422,
                )
            else:
                env = request.json["env"]

                try:
                    if request.json["audio"] == "True":
                        audio_exists = True
                    elif request.json["audio"] == "False":
                        audio_exists = False
                except KeyError:
                    audio_exists = False

                try:
                    if request.json["base64"] != None:
                        b64Aud = request.json["base64"]
                    else:
                        b64Aud = None
                except KeyError:
                    b64Aud = None

                try:
                    if request.json["description"] != None:
                        description = request.json["description"]
                    else:
                        description = "None"
                except:
                    description = None

                area = request.json["area"]
                duration = request.json["duration"]

                if "dev" in env and not "live" in env:
                    XFH.createCAPAlert(
                        event,
                        area,
                        description,
                        duration,
                        audio=audio_exists,
                        dev=True,
                        base64=b64Aud,
                    )
                else:
                    XFH.createCAPAlert(
                        event,
                        area,
                        description,
                        duration,
                        audio=audio_exists,
                        dev=False,
                        base64=b64Aud,
                    )

                if "live" in env and not "dev" in env:
                    with open("api.xml", "r") as f:
                        resp = f.read()
                        os.system("cp api.xml CAP/alerts.xml")
                        return Response(resp, mimetype="text/xml")
                elif "live" in env and "dev" in env:
                    with open("api.xml", "r") as f:
                        resp = f.read()
                        os.system("cp api.xml CAP/alerts.xml")
                        os.system("cp api.xml CAP/dev/alerts.xml")
                        return Response(resp, mimetype="text/xml")
                elif "live" not in env and "dev" in env:
                    with open("api.xml", "r") as f:
                        resp = f.read()
                        os.system("cp api.xml CAP/dev/alerts.xml")
                        return Response(resp, mimetype="text/xml")
                else:
                    return make_response(
                        "Environment not specified, please use 'live', 'dev', or both.",
                        400,
                    )
        else:
            return make_response("Invalid KEY", 403)
    except Exception as E:
        return make_response(f"System Errror: {str(E)}", 500)
