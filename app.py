import time
from datetime import datetime

import dateutil
import dateutil.parser
from chalice import Chalice, Rate
import requests
import json

################################################################################
# how to start rest-server?
# ./cetcli rest-server --chain-id=coinexdex --laddr=tcp://0.0.0.0:1317 --node tcp://localhost:26657 --trust-node=true --swagger-host=3.105.193.191:1317 --default-http > cli.log
#
# REST API server to query chain states
# e.g.: QUERY_SERVER = "18.190.80.148:1317"
QUERY_SERVER = "TODO_FILL_REST_SERVER_TO_QUERY:1317"

# SLACK Incoming Webhook URL
# https://api.slack.com/messaging/webhooks
# e.g.: https://hooks.slack.com/services/TP6B13U/BPS4J4Q/6PRwelc9CJnHDuONdEzw

SLACK_NOTIFY_URL = "https://hooks.slack.com/services/TODO__FILL_YOUR_SLACK_INCOMING_WEBHOOK_URL"

# grep address ~/.cetd/config/priv_validator_key.json
# e.g.: VALIDATOR_ADDR = "2716C82E471084F0D0C232565670CDB9BD990328"
VALIDATOR_ADDR = "TODO___FILL_YOUR_VALIDATOR_ADDR"

# ./cetd tendermint show-validator
# e.g.: VALIDATOR_CONSPK = "cettestvalconspub1zcjduepqmt3aqqy3hcvm0wv8t3540cvdpy7h2258xamj7zscm3u875pgtg5qg2cpvv"
VALIDATOR_CONSPK = "TODO__FILL_YOUR_VALIDATOR_CONSENSUS_PUBLIB_KEY_HERE"

# warning when highest block is too old from now
LATEST_BLOCK_TOO_OLD_WARNING_THRESHOLD_SECONDS = 120
################################################################################


app = Chalice(app_name='dex-monitor')
app.debug = True
query_server_url = "http://%s/blocks/latest" % QUERY_SERVER
query_signinfo_url = "http://%s/slashing/validators/%s/signing_info" % (QUERY_SERVER, VALIDATOR_CONSPK)


@app.schedule(Rate(60, unit=Rate.MINUTES))
def check_and_report_even_ok(event):
#@app.route("/")
#def check_and_report_even_ok():
    return check_node_status(also_report_ok = True, missing_block_threshold = 0)


@app.schedule(Rate(10, unit=Rate.MINUTES))
def check_and_report(event):
    return check_node_status(also_report_ok = False, missing_block_threshold = 1200)


def check_node_status(also_report_ok, missing_block_threshold):
    r = get_latest_block()
    if r.status_code == 200:
        return check_and_notify(r, also_report_ok, missing_block_threshold)
    else:
        return notify("fetch node status failed. %d" % r.status_code)


def get_latest_block():
    headers = {'accept': 'application/json'}
    return requests.get(query_server_url, headers=headers)


def check_and_notify(r, also_report_ok, missing_block_threshold):
    msg = ""
    block = json.loads(r.content)

    height_info = get_height_info(block)

    msg += check_block_time_far_from_now(block)

    if is_node_participates_consensus(block, VALIDATOR_ADDR):
        if also_report_ok:
            msg += "`Precommits OK:` %s is participating consensus.\n" % VALIDATOR_ADDR
    else:
        msg += "`WARNING:` miss precommits of validator %s.\n" % VALIDATOR_ADDR

    msg += check_missed_blocks(missing_block_threshold)

    if msg != "":
        notify(height_info + "\n" + msg)


def check_missed_blocks(missing_block_threshold):
    headers = {'accept': 'application/json'}
    r = requests.get(query_signinfo_url, headers=headers)
    if r.status_code == 200:
        info = json.loads(r.content)
        missed_count = int(info['result']['missed_blocks_counter'])

        if missed_count > missing_block_threshold:
            return "`WARNING`: missing %d blocks" % missed_count
        else:
            return ""
    else:
        return "fetch node signing_info failed. %d\n" % r.status_code


def check_block_time_far_from_now(block):
    block_time = block['block']['header']['time']
    block_tval = time.mktime(dateutil.parser.parse(block_time).timetuple())

    now_tval = time.mktime(datetime.utcnow().timetuple())
    delay = now_tval - block_tval

    if delay > LATEST_BLOCK_TOO_OLD_WARNING_THRESHOLD_SECONDS:
        return "`ERROR:` highest block time:%s too far from now, %d seconds late.\n" % (block_time, delay)

    return ""


def get_height_info(block):
    chain_id = block['block']['header']['chain_id']
    height = block['block']['header']['height']
    height_info = "[chain_id: %s, height: %s]" % (chain_id, height)
    return height_info


def is_node_participates_consensus(block, vaddr):
    last_pre_commits = block['block']['last_commit']['precommits']
    for pre_commit in last_pre_commits:
         if pre_commit is not None and pre_commit['validator_address'] == vaddr and pre_commit['type'] == 2:
             return True

    return False


def notify(msg):
    headers = {'Content-type': 'application/json'}
    payload = '{"text":"%s"}' % msg
    r = requests.post(SLACK_NOTIFY_URL, data=payload, headers=headers)
    return r.status_code
