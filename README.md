# dex-monitor
dex-monitor

# usage

## 0. clone code
```
https://github.com/whunmr/dex-monitor.git
```

## 1. config
- Fill config items in `dex-monitor/app.py`

```
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

```

## 2. config your aws access key
```
$ mkdir ~/.aws
$ cat >> ~/.aws/config
[default]
aws_access_key_id=YOUR_ACCESS_KEY_HERE
aws_secret_access_key=YOUR_SECRET_ACCESS_KEY
region=YOUR_REGION (such as us-west-2, us-west-1, etc)
```

## 3. deploy
```
$ python --version
Python 3.7.3
$ pip install chalice

$ chalice deploy
```

## references:
- https://github.com/aws/chalice

