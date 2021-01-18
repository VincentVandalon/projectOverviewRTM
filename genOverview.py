# Copyright 2012 Vincent Vandalon
# 
# This file is part of <++>. <++> is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# <++> is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of
# the GNU General Public License along with <++>. If not, see
# <http://www.gnu.org/licenses/>. "


import requests
import hashlib
import xml.etree.ElementTree as ET
import pickle
apiKey = '90e1ce22476d35f2d9ff3f6435b148e7'
sharedSecret = 'BANANAS'
sharedSecret = '7b62438b56355b78'
urlAPI = 'https://api.rememberthemilk.com/services/rest/'
authURL = 'https://api.rememberthemilk.com/services/auth/'

def composeURL(url, params):
    outURL = url
    isFirst = True

    # See RTM documentation
    # We have to sign each message
    def calcSig(params):
        sigString = sharedSecret
        for key in sorted(params.keys()):
            sigString += key + params[key]
        return hashlib.md5(sigString.encode('utf-8')).hexdigest()

    params['api_sig'] = calcSig(params)

    for (parKey,parValue) in params.items():
        if isFirst:
            outURL += '?'
            isFirst=False
        else:
            outURL += '&'
        outURL += parKey + '=' + parValue

    return outURL

##########################
# REAL CODE FROM HERE ON #
##########################
# testURLRTM = 'https://api.rememberthemilk.com/services/rest/'
# testParams ={ 'yxz':'foo', 'feg':'bar', 'abc':'baz' }
# r = requests.get(composeURL(testURLRTM,testParams))
# print(r.text)
#T his checks out

if False:
    frobParams={ 'method':'rtm.auth.getFrob', 'api_key':apiKey}
    r = requests.get(composeURL(urlAPI,frobParams))
    responseText = r.text
    root = ET.fromstring(responseText)
    print(responseText)
    frob = root.find('frob').text

    authParams={ 'perms':'read', 'api_key':apiKey, 'frob':frob}
    print(composeURL(authURL,authParams))
    pickle.dump(frob, open('frob.p','wb'))
elif False:
    frob = pickle.load(open('frob.p','rb'))
    print(frob)

    tokenParams={'method':'rtm.auth.getToken', 'api_key':apiKey, 'frob':frob}
    r = requests.get(composeURL(urlAPI,tokenParams))
    responseText = r.text
    root = ET.fromstring(responseText)
    print(">>" + responseText)
    try:
        authToken = root.find('auth').find('token').text
        pickle.dump(authToken, open('authToken.p','wb'))
    except:
        pass

else:
    authToken = pickle.load(open('authToken.p','rb'))
    frob = pickle.load(open('frob.p','rb'))

    listID = 36678032
    tokenParams={'method':'rtm.tasks.getList', 'api_key':apiKey, 'frob':frob, 'auth_token':authToken, 'list_id':str(listID),
            'filter':'status:incomplete'} 
    r = requests.get(composeURL(urlAPI,tokenParams))
    root = ET.fromstring(r.text)
    taskSeries = root[0][0]#.find('list'))#.find('taskseries'))
    htmlString = '<html><head><style>'
    htmlString += '*{font-family:sans-serif;}'
    htmlString += 'td, th{padding: .3em 2em .3em 2em;}'
    htmlString += 'table, td {border:solid 0px #CC0000;border-collapse:collapse}'
    htmlString += 'tr.taskRow:nth-child(odd) td {background-color:lightgray; color:black;}'
    htmlString += 'tr.taskRow:last-child td {border:solid #CC0000;border-width:0 0 2px 0 }'
    htmlString += 'th {background-color:#CC0000; color:white;}'
    #htmlString += '.subTaskRow {display:none};'
    htmlString += '</style></head><body><table><tr><th>Project description</th><th>Outcome / end game</th><th>Completion date</th></tr>'
    taskList = ({t.get('name'):t for t in taskSeries.findall('*')})
    print(taskList)
    for t in sorted(taskList.keys()):
        task = taskList[t]
        print(t,task)
        taskID = (task.find('task').get('id'))
        dueDate = task.find('task').get('due').split('T')[0]
        taskName = (task.get('name'))
        taskName = taskName.split('=>')
        if len(taskName)>1:
            print("%30s\t%60s\t%s"%(taskName[0],taskName[1],dueDate))
            urlTask = 'https://www.rememberthemilk.com/app/#list/%s/%s'%(listID, taskID)
            htmlString += ("<tr class='taskRow'><td><a href='%s'>%30s</a></td><td>%60s</td><td>%s</td></tr>"%(urlTask, taskName[0], taskName[1], dueDate))
            # htmlString += "<tr class='subTaskRow'><td>&nbsp;</td><td>Subtask</td><td>asdf</td></tr>"
    htmlString += '</table></body></html>'
    open('overview.html','w').write(htmlString)
