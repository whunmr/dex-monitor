from chalice import Chalice, Rate
import requests
import json

################################################################################
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
################################################################################


app = Chalice(app_name='dex-monitor')
app.debug = True
query_server_url = "http://%s/blocks/latest" % QUERY_SERVER
query_signinfo_url = "http://%s/slashing/validators/%s/signing_info" % (QUERY_SERVER, VALIDATOR_CONSPK)


@app.schedule(Rate(240, unit=Rate.MINUTES))
def check_and_report_even_ok(event):
    return check_node_status(also_report_ok = True)


@app.schedule(Rate(10, unit=Rate.MINUTES))
def check_and_report(event):
    return check_node_status(also_report_ok = False)


def check_node_status(also_report_ok):
    r = get_latest_block()
    if r.status_code == 200:
        return check_and_notify(r, also_report_ok)
    else:
        return notify("fetch node status failed. %d" % r.status_code)


def get_latest_block():
    headers = {'accept': 'application/json'}
    return requests.get(query_server_url, headers=headers)


def check_and_notify(r, also_report_ok):
    block = json.loads(r.content)

    height_info = get_height_info(block)

    if is_node_participates_consensus(block, VALIDATOR_ADDR):
        if also_report_ok:
            return notify("Has precommits. %s" % height_info)
        else:
            return 200

    warning_msg = "WARNING: Do not has precommits of validator %s. %s" % (VALIDATOR_ADDR, height_info)
    return notify(warning_msg)


def get_height_info(block):
    chain_id = block['block']['header']['chain_id']
    height = block['block']['header']['height']
    height_info = "chain_id: %s, height: %s" % (chain_id, height)
    return height_info


def is_node_participates_consensus(block, vaddr):
    last_pre_commits = block['block']['last_commit']['precommits']
    for pre_commit in last_pre_commits:
        if pre_commit['validator_address'] == vaddr and pre_commit['type'] == 2:
            return True

    return False


def notify(msg):
    headers = {'Content-type': 'application/json'}
    payload = '{"text":"%s"}' % msg
    r = requests.post(SLACK_NOTIFY_URL, data=payload, headers=headers)
    return r.status_code
