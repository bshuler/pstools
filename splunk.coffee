# Description
#   A Hubot script that interfaces with Splunk
#
# Configuration:
#   Set the splunk server URL, username, and password to use for searching
#
# Commands:
#   hubot splunk <your splunk search here>
#   hubot splunk help
#   hubot splunk configure
#
# Author:
#   Bert Shuler <bshuler@splunk.com>
#
# CONFIGURATION
#
# If you do not want to use hubot-auth,  define your admin.
# splunk_admin = 'admin'
#
#
# We recommend you change this secret, so that your passwords will be encrypted more securely
splunk_secret = 'CHANGEME'


QS = require 'querystring'

crypto = require("crypto")


encrypt = (key, data) ->
        cipher = crypto.createCipher('aes-256-cbc', key)
        crypted = cipher.update(data, 'utf-8', 'binary')
        crypted += cipher.final('binary')

        return crypted

decrypt = (key, data) ->
        decipher = crypto.createDecipher('aes-256-cbc', key)
        decrypted = decipher.update(data, 'binary', 'utf-8')
        decrypted += decipher.final('utf-8')

        return decrypted

is_userid = (robot, msg, splunk_user_id) ->
  for k of (robot.brain.data.users or { })
    if splunk_user_id == k
      return true
  robot.send {room: msg.message.user.name},  "Invalid user id " + splunk_user_id +". Try 'splunk list_users' to find valid user id."
  return false


is_admin = (msg, robot) ->
  if (typeof splunk_admin != 'undefined')
    debug(robot,msg,'splunk_admin: ', splunk_admin)
    if (msg.message.user.name.toString() == splunk_admin || msg.message.user.id.toString() == splunk_admin)
      return true
    else
      msg.reply "Sorry, you are not defined as the splunk_admin."
      return false
  else
    if robot.auth
      debug(robot,msg,'hubot-auth user id: ', msg.message.user.id.toString())
      if (robot.auth.hasRole(msg.envelope.user, 'splunk_admin'))
        return true
      else
        msg.reply "Sorry, you don't have 'splunk_admin' role"
        if robot.auth.hasRole(msg.envelope.user, 'admin')
          msg.reply "Because you are a HUBOT_AUTH_ADMIN, you can type '" + robot.name + " "  + msg.message.user.name + " has splunk_admin role'"
        return false
    else
      msg.reply "Sorry, you have neither defined the splunk_admin, or installed hubot-auth. You must complete one or the other."

debug = (robot, msg, tag, log) ->
  splunk_debug = robot.brain.get('splunk_debug')
  if splunk_debug == 1
    robot.send {room: msg.message.user.name}, 'DEBUG ' + tag + ': ' + log


splunkSearch = (robot, msg, search) ->
  splunk_job_link = robot.brain.get('splunk_job_link')
  splunk_uri = robot.brain.get('splunk_uri')
  splunk_user = robot.brain.get('splunk_user')
  splunk_password = robot.brain.get('splunk_password')
  splunk_personal_password = robot.brain.get("splunk_personal_password_"+msg.message.user.id.toString())
  if splunk_personal_password
    splunk_password  = splunk_personal_password
  splunk_personal_username = robot.brain.get("splunk_personal_username_"+msg.message.user.id.toString())
  if splunk_personal_username
    splunk_user  = splunk_personal_username
  if splunk_password
    decrypted_password  = decrypt(splunk_secret, splunk_password)
  splunk_url = robot.brain.get('splunk_url')
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_uri to get splunk data: " + splunk_uri if not splunk_uri
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_user to get splunk data: " +  splunk_user if not splunk_user
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_password (encrypted) to get splunk data: " +  splunk_password if not splunk_password
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_url to get splunk data: " +  splunk_url if not splunk_url


  data = QS.stringify({'search': search }) 


  process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  auth = 'Basic ' + new Buffer(splunk_user+":"+decrypted_password).toString('base64');
  url = splunk_uri + "services/search/jobs?output_mode=json"
  debug(robot,msg,'url', url)
  msg.http(url).header('Authorization', auth).post(data) (err, res, body) ->
    debug(robot,msg,'splunkSearch body', body)
    json_body = JSON.parse body
    
    if json_body.messages
      if json_body.messages.length
          for m, mi in json_body.messages
            msg.send '*Message Type:* ' + m.type + '\n*Message Text:* ' + m.text
    if json_body.sid
      if splunk_job_link == 1
        msg.send "View your splunk job status here: "+ splunk_uri + "services/search/jobs/" + json_body.sid
      else
        msg.send "Your SID is: " + json_body.sid
      splunkJobStatus(robot, msg, json_body.sid)
    

splunkJobStatus = (robot, msg, sid) ->
  splunk_uri = robot.brain.get('splunk_uri')
  splunk_user = robot.brain.get('splunk_user')
  splunk_password = robot.brain.get('splunk_password')
  splunk_personal_password = robot.brain.get("splunk_personal_password_"+msg.message.user.id.toString())
  if splunk_personal_password
    splunk_password  = splunk_personal_password
  splunk_personal_username = robot.brain.get("splunk_personal_username_"+msg.message.user.id.toString())
  if splunk_personal_username
    splunk_user  = splunk_personal_username
  if splunk_password
    decrypted_password  = decrypt(splunk_secret, splunk_password)
  splunk_url = robot.brain.get('splunk_url')

  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_uri to get splunk data: " + splunk_uri if not splunk_uri
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_user to get splunk data: " +  splunk_user if not splunk_user
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_password (encrypted) to get splunk data: " +  splunk_password if not splunk_password
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_url to get splunk data: " +  splunk_url if not splunk_url

  process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  auth = 'Basic ' + new Buffer(splunk_user+":"+decrypted_password).toString('base64');
  url = splunk_uri + "services/search/jobs/"+sid+"?output_mode=json"
  msg.http(url).header('Authorization', auth).get() (err, res, body) ->
        debug(robot,msg,'splunkJobStatus body', body)
        json_body = JSON.parse body
        if json_body.messages
          if json_body.messages.length
            for m, mi in json_body.messages
              msg.send '*Message Type:* ' + m.type + '\n*Message Text:* ' + m.text

        if not json_body.entry[0].content.isDone
            splunk_wait_seconds = robot.brain.get('splunk_wait_seconds')
            if Number(splunk_wait_seconds) > 1
              splunk_wait_seconds = Number(splunk_wait_seconds)
            else
              splunk_wait_seconds = 5
            msg.send "Waiting " + splunk_wait_seconds + " seconds for result"
            this.updateId = setTimeout () ->     
                splunkJobStatus(robot, msg, sid)
            , splunk_wait_seconds*1000
        else
            msg.send "Search is complete. Total results: " + json_body.entry[0].content.resultCount
            splunkJobResults(robot, msg, sid)


splunkJobResults = (robot, msg, sid) ->
  splunk_download_link = robot.brain.get('splunk_download_link')
  splunk_open_link = robot.brain.get('splunk_open_link')
  splunk_uri = robot.brain.get('splunk_uri')
  splunk_user = robot.brain.get('splunk_user')
  splunk_password = robot.brain.get('splunk_password')
  splunk_personal_password = robot.brain.get("splunk_personal_password_"+msg.message.user.id.toString())
  if splunk_personal_password
    splunk_password  = splunk_personal_password
  splunk_personal_username = robot.brain.get("splunk_personal_username_"+msg.message.user.id.toString())
  if splunk_personal_username
    splunk_user  = splunk_personal_username
  if splunk_password
    decrypted_password  = decrypt(splunk_secret, splunk_password)
  splunk_url = robot.brain.get('splunk_url')
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_uri to get splunk data: " + splunk_uri if not splunk_uri
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_user to get splunk data: " +  splunk_user if not splunk_user
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_password (encrypted) to get splunk data: " +  splunk_password if not splunk_password
  return msg.send "Type: " + robot.name + " splunk configure\nYou need to set splunk_url to get splunk data: " +  splunk_url if not splunk_url

  process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  auth = 'Basic ' + new Buffer(splunk_user+":"+decrypted_password).toString('base64');
  url = splunk_uri + "services/search/jobs/"+sid+"/results?output_mode=json"
  msg.http(url).header('Authorization', auth).get() (err, res, body) ->
    return msg.send 'Could not contact splunk at URI ' + url ' Error: ' + err if err
    debug(robot,msg,'splunkJobResults body', body)
    try
        json_body = JSON.parse body
    catch err
      return msg.send 'splunkJobResults: Unable to parse splunk data: ' + body

    if json_body.messages.length
      for m, mi in json_body.messages
        msg.send '*Message Type:* ' + m.type + '\n*Message Text:* ' + m.text
    
    if json_body.results
      if not json_body.results.length
        msg.send "No results were returned from that search."
      else
        # Find max lengths of the columns
        for r, ri in json_body.results
            for f, fi in json_body.fields
              name_length = f.name.length
              if not name_length
                name_length = 0
              if r[f.name]
                value_length = r[f.name].length
                if not value_length
                  value_length = 0
              else
                value_length = 0
              if typeof json_body.fields[fi].max_len == "undefined"
                if name_length > value_length
                    json_body.fields[fi].max_len = name_length
                else
                    json_body.fields[fi].max_len = value_length
              else
                if json_body.fields[fi].max_len < value_length
                    json_body.fields[fi].max_len = value_length
        head_line = ""
        star_line = ""
        for f, fi in json_body.fields
            name_length = f.name.length
            if not name_length
              name_length = 0
            if head_line!=""
                head_line = head_line + " | "
            if star_line!=""
                star_line = star_line + "***"
            head_line=head_line + f.name
            spaces = f.max_len-name_length-1
            debug(robot,msg,'add_name_spaces', "max_len: "+f.max_len+" length: "+name_length+" spaces:"+spaces)
            if spaces>1
              for i in [spaces..0]
                  head_line=head_line + " "
            spaces = f.max_len-1
            if spaces>1
              for i in [spaces..0]
                  star_line=star_line + "*"

        finaltext = "```" + star_line + "\n"
        finaltext = finaltext + head_line + "\n"
        finaltext = finaltext + star_line + "\n"



        for r, ri in json_body.results
            my_line=""
            my_value=""
            for f, fi in json_body.fields
                if r[f.name]
                  value_length = r[f.name].length
                  my_value = r[f.name]
                  if not value_length
                    value_length = 0
                else
                  value_length = 0
                  my_value = ""
                if my_line!=""
                    my_line = my_line + " | "
                spaces = f.max_len-value_length-1
                debug(robot,msg,'add_value_spaces', "max_len: "+f.max_len+" length: "+value_length+" spaces:"+spaces)
                my_spaces=""
                if spaces>0
                  for i in [spaces..0]
                      my_spaces=my_spaces + " "
                my_line=my_line+my_value+my_spaces
            finaltext = finaltext + my_line + "\n"
        finaltext = finaltext + star_line + "```"
        msg.send finaltext
        msg.send "Number of results returned: " + json_body.results.length
        if splunk_download_link == 1
          msg.send "Download your splunk results here: "+ splunk_uri + "services/search/jobs/" + sid + "/results?output_mode=csv"
        if splunk_open_link == 1
          msg.send "Open your results in splunk here: "+ splunk_url + "app/search/search?sid=" + sid 


module.exports = (robot) ->
  robot.respond /splunk (search .*)/i, (msg) ->
    search = msg.match[1]
    splunkSearch(robot, msg, search)
  robot.respond /splunk job_status (\d+\.\d+)/i, (msg) ->
    sid = msg.match[1]
    splunkJobStatus(robot, msg, sid)
  robot.respond /splunk job_results (\d+\.\d+)/i, (msg) ->
    sid = msg.match[1]
    splunkJobResults(robot, msg, sid)
  robot.respond /splunk help/i, (msg) ->
    msg.send robot.name+" splunk search [your_search]"
    msg.send robot.name+" splunk job_status [your_sid]"
    msg.send robot.name+" splunk job_results [your_sid]"


  ## Admin Functions
  robot.respond /splunk config_uri (.+)/i, (msg) ->
    if is_admin(msg, robot)
      uri = msg.match[1]
      previous_uri = robot.brain.get('splunk_uri')
      if previous_uri
        robot.send {room: msg.message.user.name},  "Previous URI was: " + previous_uri
      robot.brain.set 'splunk_uri', uri
      robot.send {room: msg.message.user.name},  "New URI is: " + uri

  robot.respond /splunk config_url (.+)/i, (msg) ->
    if is_admin(msg, robot)
      url = msg.match[1]
      previous_url = robot.brain.get('splunk_url')
      if previous_url
        robot.send {room: msg.message.user.name},  "Previous URL was: " + previous_url
      robot.brain.set 'splunk_url', url
      robot.send {room: msg.message.user.name},  "New URl is: " + url

  robot.respond /splunk config_user (.+)/i, (msg) ->
    if is_admin(msg, robot)
      user = msg.match[1]
      previous_user = robot.brain.get('splunk_user')
      if previous_user
        robot.send {room: msg.message.user.name},  "Previous user was: " + previous_user
      robot.brain.set 'splunk_user', user
      robot.send {room: msg.message.user.name},  "New user is: " + user

  robot.respond /splunk config_password (.+)/i, (msg) ->
    if is_admin(msg, robot)
      password = msg.match[1]
      previous_password = robot.brain.get('splunk_password')
      if previous_password
        robot.send {room: msg.message.user.name},  "Previous password (encrypted) was: "+previous_password
      encrypted_password  = encrypt(splunk_secret, password)
      robot.brain.set 'splunk_password', encrypted_password
      robot.send {room: msg.message.user.name},  "New password (encrypted) is: " + encrypted_password

  robot.respond /splunk debug (.+)/i, (msg) ->
    if is_admin(msg, robot)
      my_debug = msg.match[1]
      if Number(my_debug) == 1
        my_debug = Number(my_debug)
      else
        my_debug = 0
      previous_debug = robot.brain.get('splunk_debug')
      if previous_debug
        robot.send {room: msg.message.user.name},  "Previous debug was: " + previous_debug
      robot.brain.set 'splunk_debug', my_debug
      robot.send {room: msg.message.user.name},  "New debug is: " + my_debug

  
  robot.respond /splunk job_link (.+)/i, (msg) ->
    if is_admin(msg, robot)
      my_job_link = msg.match[1]
      if Number(my_job_link) == 1
        my_job_link = Number(my_job_link)
      else
        my_job_link = 0
      previous_job_link = robot.brain.get('splunk_job_link')
      if previous_job_link
        robot.send {room: msg.message.user.name},  "Previous job_link was: " + previous_job_link
      robot.brain.set 'splunk_job_link', my_job_link
      robot.send {room: msg.message.user.name},  "New job_link is: " + my_job_link

  robot.respond /splunk download_link (.+)/i, (msg) ->
    if is_admin(msg, robot)
      my_download_link = msg.match[1]
      if Number(my_download_link) == 1
        my_download_link = Number(my_download_link)
      else
        my_download_link = 0
      previous_download_link = robot.brain.get('splunk_download_link')
      if previous_download_link
        robot.send {room: msg.message.user.name},  "Previous download_link was: " + previous_download_link
      robot.brain.set 'splunk_download_link', my_download_link
      robot.send {room: msg.message.user.name},  "New download_link is: " + my_download_link

  robot.respond /splunk open_link (.+)/i, (msg) ->
    if is_admin(msg, robot)
      my_open_link = msg.match[1]
      if Number(my_open_link) == 1
        my_open_link = Number(my_open_link)
      else
        my_open_link = 0
      previous_open_link = robot.brain.get('splunk_open_link')
      if previous_open_link
        robot.send {room: msg.message.user.name},  "Previous open_link was: " + previous_open_link
      robot.brain.set 'splunk_open_link', my_open_link
      robot.send {room: msg.message.user.name},  "New open_link is: " + my_open_link

  robot.respond /splunk wait_seconds (.+)/i, (msg) ->
    if is_admin(msg, robot)
      my_wait_seconds = msg.match[1]
      if Number(my_wait_seconds) > 1
        my_wait_seconds = Number(my_wait_seconds)
      else
        my_wait_seconds = 5
      previous_wait_seconds = robot.brain.get('splunk_wait_seconds')
      if previous_wait_seconds
        robot.send {room: msg.message.user.name},  "Previous wait_seconds was: " + previous_wait_seconds
      robot.brain.set 'splunk_wait_seconds', my_wait_seconds
      robot.send {room: msg.message.user.name},  "New wait_seconds is: " + my_wait_seconds




  robot.respond /splunk configure/i, (msg) ->
    if is_admin(msg, robot)
      robot.send {room: msg.message.user.name}, "There are 4 parameters that need to be set to configure splunk."
      robot.send {room: msg.message.user.name}, "Please, only send these commands in this private chat with me("+robot.name+")"
      robot.send {room: msg.message.user.name}, 'splunk config_uri https://localhost:8089/'
      robot.send {room: msg.message.user.name}, 'splunk config_url  http://localhost:8000/'
      robot.send {room: msg.message.user.name}, 'splunk config_user admin'
      robot.send {room: msg.message.user.name}, 'splunk config_password changeme'
      robot.send {room: msg.message.user.name}, 'Optional Configuration:'
      robot.send {room: msg.message.user.name}, 'splunk job_link 0'
      robot.send {room: msg.message.user.name}, 'splunk download_link 0'
      robot.send {room: msg.message.user.name}, 'splunk open_link 1'
      robot.send {room: msg.message.user.name}, 'splunk wait_seconds 5'
      robot.send {room: msg.message.user.name}, 'splunk store_personal_username admin'
      robot.send {room: msg.message.user.name}, 'splunk store_personal_password changeme'
      robot.send {room: msg.message.user.name}, 'splunk clear_personal_credentials'
      robot.send {room: msg.message.user.name}, 'splunk list_users'
      robot.send {room: msg.message.user.name}, 'splunk store_personal_username <userid> admin'
      robot.send {room: msg.message.user.name}, 'splunk store_personal_password <userid> changeme'
      robot.send {room: msg.message.user.name}, 'splunk clear_personal_credentials <userid>'

    
  robot.respond /splunk whoami/i, (msg) ->
    robot.send {room: msg.message.user.name}, "Your id is: " + msg.message.user.id.toString()
    robot.send {room: msg.message.user.name}, "Your name is: " + msg.message.user.name.toString()

  robot.respond /splunk store_personal_username (\w+)$/i, (msg) ->
    my_personal_username = msg.match[1]
    previous_personal_username = robot.brain.get("splunk_personal_username_"+msg.message.user.id.toString())
    if previous_personal_username
      robot.send {room: msg.message.user.name},  "Previous personal_username was: " + previous_personal_username
    robot.brain.set "splunk_personal_username_"+msg.message.user.id.toString(), my_personal_username
    robot.send {room: msg.message.user.name},  "New personal_username is: " + my_personal_username

  robot.respond /splunk store_personal_password (\w+)$/i, (msg) ->
    my_personal_password = msg.match[1]
    previous_personal_password = robot.brain.get("splunk_personal_password_"+msg.message.user.id.toString())
    if previous_personal_password
      robot.send {room: msg.message.user.name},  "Previous personal_password (encrypted) was: " + previous_personal_password
    encrypted_personal_password  = encrypt(splunk_secret, my_personal_password)
    robot.brain.set "splunk_personal_password_"+msg.message.user.id.toString(), encrypted_personal_password
    robot.send {room: msg.message.user.name},  "New personal_password (encrypted) is: " + encrypted_personal_password

  robot.respond /splunk clear_personal_credentials$/i, (msg) ->
    previous_personal_username = robot.brain.get("splunk_personal_username_"+msg.message.user.id.toString())
    if previous_personal_username
      robot.send {room: msg.message.user.name},  "Previous personal_username was: " + previous_personal_username
    previous_personal_password = robot.brain.get("splunk_personal_password_"+msg.message.user.id.toString())
    if previous_personal_password
      robot.send {room: msg.message.user.name},  "Previous personal_password (encrypted) was: " + previous_personal_password
    robot.brain.set "splunk_personal_username_"+msg.message.user.id.toString(), null
    robot.send {room: msg.message.user.name},  "New personal_username is: " + null
    robot.brain.set "splunk_personal_password_"+msg.message.user.id.toString(), null
    robot.send {room: msg.message.user.name},  "New personal_password (encrypted) is: " + null
  
  robot.respond /splunk list_users/i, (msg) ->
    for k of (robot.brain.data.users or { })
      msg.send "*id* : " + k + "   *name* : " + robot.brain.data.users[k].name

  robot.respond /splunk store_personal_username (\w+) (\w+)$/i, (msg) ->
    if is_admin(msg, robot)
      my_user_id = msg.match[1]
      my_personal_username = msg.match[2]
      if is_userid(robot, msg, my_user_id) 
        previous_personal_username = robot.brain.get("splunk_personal_username_"+my_user_id)
        if previous_personal_username
          robot.send {room: msg.message.user.name},  "Previous personal_username for " + my_user_id + " was: " + previous_personal_username
        robot.brain.set "splunk_personal_username_"+my_user_id, my_personal_username
        robot.send {room: msg.message.user.name},  "New personal_username for " + my_user_id + " is: " + my_personal_username

  robot.respond /splunk store_personal_password (\w+) (\w+)$/i, (msg) ->
    if is_admin(msg, robot)
      my_personal_password = msg.match[2]
      my_user_id = msg.match[1]
      if is_userid(robot, msg, my_user_id)
        previous_personal_password = robot.brain.get("splunk_personal_password_"+my_user_id)
        if previous_personal_password
          robot.send {room: msg.message.user.name},  "Previous personal_password (encrypted) for " + my_user_id + " was: " + previous_personal_password
        encrypted_personal_password  = encrypt(splunk_secret, my_personal_password)
        robot.brain.set "splunk_personal_password_"+my_user_id, encrypted_personal_password
        robot.send {room: msg.message.user.name},  "New personal_password (encrypted) for " + my_user_id + " is: " + encrypted_personal_password

  robot.respond /splunk clear_personal_credentials (\w+)$/i, (msg) ->
    if is_admin(msg, robot)
      my_user_id = msg.match[1]
      if is_userid(robot, msg, my_user_id)
        previous_personal_username = robot.brain.get("splunk_personal_username_"+my_user_id)
        if previous_personal_username
          robot.send {room: msg.message.user.name},  "Previous personal_username for " + my_user_id + " was: " + previous_personal_username
        previous_personal_password = robot.brain.get("splunk_personal_password_"+my_user_id)
        if previous_personal_password
          robot.send {room: msg.message.user.name},  "Previous personal_password (encrypted) for " + my_user_id + " was: " + previous_personal_password
        robot.brain.set "splunk_personal_username_"+my_user_id, null
        robot.send {room: msg.message.user.name},  "New personal_username for " + my_user_id + " is: " + null
        robot.brain.set "splunk_personal_password_"+my_user_id, null
        robot.send {room: msg.message.user.name},  "New personal_password (encrypted) for " + my_user_id + " is: " + null






