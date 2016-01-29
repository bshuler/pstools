
# About
This is a splunk addon that enables users to easily send search results to Slack


# Usages
## Install the app:
Untar this app or clone from [github](https://github.com/billcchung/splunk_slack) into your $SPLUNK_HOME/etc/apps folder


## Set config
You'll want to set the slack.conf in default folder:

    [config]
    url=
    username=splunk
    channel=#general
    icon=https://www.splunk.com/content/dam/splunk2/images/icons/favicons/mstile-150x150.png
    allow_user_set_slack_url=0

1. `url`:  the url of your slack team, e.g.:
`https://hooks.slack.com/services/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`
2. `username`: the username that appears in slack.
3. `channel`: the channel that will receive the search results, channel can be specified by slackit search arg
4. `icon`: the icon that appears in slack.
5. `allow_user_set_slack_url`: enable this option if you're allowing the users send results to different slack teams.


## Using it
After installing and restarting splunk, yo can now use the `slackit` search command anywhere inside splunk, e.g.:
`index=_internal source=*metrics.log kbps=* | stats avg(eps) | slackit`
then the report should be seen in slack: 

![splunk_slack](https://s3.amazonaws.com/slackit/splunk_slackit.png)
### Arguments for search
You can specifiy `url` and `channel` slackit arguments, e.g.:

1. `index=_internal source=*metrics.log kbps=* | stats avg(eps) | slackit channel=#devops`
2. `index=_internal source=*metrics.log kbps=* | stats avg(eps) | slackit url=https://hooks.slack.com/services/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` (You need to set `allow_user_set_slack_url`=1 to enable url overwriting.)


# Notes
1. The main purpose of this addon is to send report to slack. Raw events contain many fields, if you send them slack channel, it'll be hard to read.


# Questions and suggestions:
If you have any questions and suggestions, please feel free to contact me: `billcchung@gmail.com`