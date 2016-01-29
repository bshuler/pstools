import sys, json
import urllib2
import os


def get_pretty_table(results):
    if results:
        keys = results[0].keys()
    else:
        return ''
    x = prettytable.PrettyTable(keys, padding_width=4)
    for row in results:
        x.add_row([row[k] for k in keys])
    return "```" + x.get_string() + "```"

def send_slack_message(settings, results_link, search_name):

    attachment = dict()
    attachment['pretext'] = "Splunk search '" + search_name + "' triggered an alert."
    attachment['title'] = "New Splunk alert results"
    attachment['title_link'] = results_link
    attachment['color'] = "#7CD197"
    attachments = [attachment]

    params = dict()
    params['text'] = "New message from Splunk: " + settings.get('message')
    params['username'] = settings.get('from_user', 'Splunk')
    params['icon_url'] = settings.get('from_user_icon')
    params['mrkdwn'] = True
    params['attachments'] = attachments
    #params['text'] = pretty_text

    channel = settings.get('channel')
    if channel:
        params['channel'] = channel
    else:
        print >> sys.stderr, "WARN No channel supplied, using default for webhook"
    url = settings.get('webhook_url')
    my_proxy = settings.get('webhook_proxy')
    body = json.dumps(params)
    print >> sys.stderr, 'DEBUG Calling url="%s" with body=%s' % (url, body)



    req = urllib2.Request(url, body, {"Content-Type": "application/json"})
    try:

        if my_proxy != "":
            os.environ['http_proxy'] = my_proxy
            os.environ['https_proxy'] = my_proxy

        res = urllib2.urlopen(req)
        body = res.read()
        print >> sys.stderr, "INFO Slack API responded with HTTP status=%d" % res.code
        print >> sys.stderr, "DEBUG Slack API response: %s" % json.dumps(body)
        return 200 <= res.code < 300
    except urllib2.HTTPError, e:
        print >> sys.stderr, "ERROR Error sending message: %s" % e
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        my_in = sys.stdin.read()
        #print >> sys.stderr, "ERROR my_in: " + my_in
        payload = json.loads(my_in)

        config = payload.get('configuration')
        results_link = payload.get('results_link')
        search_name = payload.get('search_name')
        if not send_slack_message(config, results_link, search_name):
            print >> sys.stderr, "FATAL Sending the slack message failed"
