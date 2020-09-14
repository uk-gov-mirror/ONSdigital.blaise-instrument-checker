import os
import sys
import logging
from flask import Flask, jsonify, request
import pyblaise

app = Flask(__name__)

app.logger.setLevel(os.getenv("LOG_LEVEL", "WARN"))
handler = logging.StreamHandler(sys.stdout)
# handler.setLevel(os.getenv("LOG_LEVEL", "WARN"))
app.logger.addHandler(handler)

PROTOCOL = os.getenv("PROTOCOL", None)
BLAISE_USERNAME = os.getenv("BLAISE_USERNAME", None)
BLAISE_PASSWORD = os.getenv("BLAISE_PASSWORD", None)


@app.route('/')
def health_check():
    app.logger.debug(f"health_check from {request.remote_addr}")
    return ":)", 200


@app.route('/instrument')
def check_instrument_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")
    app.logger.info(f"Instrument to check : {instrument_check}")
    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        status, instruments = pyblaise.get_list_of_instruments(PROTOCOL, host, 8031, token)
        app.logger.info(f"get_list_of_instruments status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get list of instruments from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    for instrument in instruments:
        if instrument['name'] == instrument_check:
            app.logger.info(f"Found {instrument_check}")
            return jsonify(instrument)

    return jsonify("Not found"), 404


@app.route('/instruments')
def get_all_instruments_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    # instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")

    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        status, instruments = pyblaise.get_list_of_instruments(PROTOCOL, host, 8031, token)
        app.logger.info(f"get_list_of_instruments status: {status}")
        return jsonify(instruments), 200
    except Exception as e:
        app.logger.exception(f"could not get list of instruments from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500


@app.route('/users')
def get_all_users_on_blaise():
    host = request.args.get('vm_name', None, type=str)
    # instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")

    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        status, instruments = pyblaise.get_all_users(PROTOCOL, host, 8031, token)
        app.logger.info(f"get_all_users_on_blaise status: {status}")
        return jsonify(instruments), 200
    except Exception as e:
        app.logger.exception(f"could not get list of users from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500



@app.route('/upload_survey', methods=["POST"])
def upload_survey_blaise():
    yeah = request.files['OPN200T.zip']
    host = request.args.get('vm_name', None, type=str)
    instrument_check = request.args.get('instrument', None, type=str)

    app.logger.info(f"Host : {host}")

    app.logger.info(f"PROTOCOL : {PROTOCOL}")
    app.logger.info(f"BLAISE_USERNAME : {BLAISE_USERNAME}")

    try:
        status, token = pyblaise.get_auth_token(PROTOCOL, host, 8031, BLAISE_USERNAME, BLAISE_PASSWORD)
        app.logger.debug(f"get_auth_token Status: {status}")
    except Exception as e:
        app.logger.exception(f"could not get authentication token from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500

    try:
        new_survey_filename, survey_id = pyblaise.create_survey_from_existing(yeah, instrument_check)
        status = pyblaise.upload_survey(PROTOCOL, host, 8031, token, new_survey_filename)
        app.logger.info(f"get_all_users_on_blaise status: {status}")
        return jsonify(status), 200
    except Exception as e:
        app.logger.exception(f"could not get list of users from blaise on '{PROTOCOL}://{host}' as '{BLAISE_USERNAME}'")
        return jsonify("false"), 500
