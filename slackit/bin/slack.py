# send splunk results to slack

import prettytable
import ConfigParser
import requests
import json
import os
import sys

import splunk.Intersplunk as sis
(a, kwargs) = sis.getKeywordsAndOptions()
TRUE_VALUES = ['true', '1', 't', 'y', 'yes']

def get_pretty_table(results):
    if results:
        keys = results[0].keys()
    else:
        return ''
    x = prettytable.PrettyTable(keys, padding_width=4)
    for row in results:
        x.add_row([row[k] for k in keys])
    return "```" + x.get_string() + "```"


def main():
    # get config from config file
    config = ConfigParser.ConfigParser()
    
    if os.path.exists(os.path.join('..', 'local', 'slack.conf')):
        config.readfp(open(os.path.join('..', 'local', 'slack.conf')))
    else:
        config.readfp(open(os.path.join('..', 'default', 'slack.conf')))

    # username and icon can only be set by conf
    username = config.get('config', 'username')
    icon = config.get('config', 'icon')

    # update args if user speicify them in search
    channel = kwargs.get('channel', config.get('config', 'channel'))
    if not channel.startswith('#'): channel = '#' + channel
    if config.get('config', 'allow_user_set_slack_url').lower() in TRUE_VALUES:
        url = kwargs.get('url', config.get('config', 'url'))
    else:
        url = config.get('config', 'url')

    # no url specified, dont procceed.
    if not url:
        raise Exception("Not slack url specified!")

    # read search results
    results = sis.readResults(None, None, True)

    https_proxy = config.get('config', 'proxy')
    proxyDict = { 
                  "https" : https_proxy
                }

    # prepare data to be sent to slack
    data = {
        'text': get_pretty_table(results),
        'username': username,
        'channel': channel,
        'icon_url': icon,
        'mrkdwn': True,
    }

    if https_proxy != "":  
        # send data to slack.
        r = requests.post(url, data=json.dumps(data), proxies=proxyDict)
    else:
        r = requests.post(url, data=json.dumps(data))

    if r.status_code == 200:
        sis.outputResults(results)
    else:
        err_msg = ("Error sending results to slack, reason: {r}, {t}".format( 
                    r=r.reason, t=r.text))
        sis.generateErrorResults(err_msg)

try:
    main()
except Exception, e:
    import traceback
    stack =  traceback.format_exc()
    sis.generateErrorResults("Error '{e}'. {s}".format(e=e, s=stack))   
