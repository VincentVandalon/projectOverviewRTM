#tasi Copyright 2012 Vincent Vandalon
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
from datetime import datetime
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
htmlHeader = '''
    <html><head><style>
    *{font-family:sans-serif;}
    td, th{padding: .3em 2em .3em 2em;}
    table, td {border:solid 0px #CC0000;border-collapse:collapse}
    tr:nth-child(odd) td {background-color:lightgray; color:black;}
    tr:last-child td {border:solid #CC0000;border-width:0 0 2px 0 }
    th {background-color:#CC0000; color:white;}
    .subTaskRow {display:none};
    </style></head><body><table><tr><th>Project description</th><th>Outcome / end game</th><th>Log</th>
    <th>Tags</th><th>Completion date</th></tr>
'''

def queryData(authToken,frob):
    listID = 36678032
    tokenParams={'method':'rtm.tasks.getList', 'api_key':apiKey, 'frob':frob, 'auth_token':authToken, #'list_id':str(listID),
            'filter':'list:workProjects-TUe AND status:incomplete'} 
    r = requests.get(composeURL(urlAPI,tokenParams))
    root = ET.fromstring(r.text)
    #print(ET.tostring(root))
    taskSeries = root[0][0]#.find('list'))#.find('taskseries'))
    htmlString = htmlHeader

    def taskToHTML(task):
        #print(task)
        taskID = (task.find('task').get('id'))
        dueDate = task.find('task').get('due').split('T')[0]
        tags = task.find('tags')
        tagsString = ''
        for tag in tags.findall('*'):
            if tag.text != 'work':
                tagsString += '<p style="background-color:#CC0000;color:white;padding:0 1px 0 1px;margin:0 3px 0 3px;">' + tag.text + '</p>'
        taskName = (task.get('name'))
        taskURL = (task.get('url'))
        taskURLDesc = 'Logging'
        if len(taskURL) < 6:
            taskURLDesc ='-'
        def parseDataFromTaskName(n):
            if '{' in n:
                name, data = n.split('{')
                data = data.split('}')[0]
                # You could turn this into a map using {a[0]:a{1} from...}
                data = data.split(':')[1]
            else:
                name = n
                data =''
            return (name, data)
        taskName = parseDataFromTaskName(taskName)
        htmlString = ''
        if len(taskName)>1:
            #print("%30s\t%60s\t%s"%(taskName[0],taskName[1],dueDate))
            urlTask = 'https://www.rememberthemilk.com/app/#list/%s/%s'%(listID, taskID)
            htmlString = "<tr class='taskRow'><td><a href='%s' target='_new'>%30s</a></td>"%(urlTask, taskName[0],)
            htmlString += "<td>%60s</td><td><a href='%s' target='_new'>%s</a></td><td>%s</td><td>%s</td></tr>"%(taskName[1], taskURL, taskURLDesc, tagsString, dueDate)

        return htmlString


    taskList = ({t.find('task').get('due') + t.get('name'):t for t in taskSeries.findall('*')})
    #print(taskList)
    for t in sorted(taskList.keys()):
        task = taskList[t]
        htmlString +=  taskToHTML(task)
    htmlString += '</table>'
    htmlString += '<p>Updated at: ' + (datetime.now()).isoformat(sep=' ',timespec='seconds') +'</p>'
    htmlString += '</body></html>'
    open('overview.html','w').write(htmlString)

    print('Updated at: ' + (datetime.now()).isoformat(sep=' ',timespec='seconds'))


try:
    authToken = pickle.load(open('authToken.p','rb'))
    frob = pickle.load(open('frob.p','rb'))
    queryData(authToken, frob)

except:
    frobParams={ 'method':'rtm.auth.getFrob', 'api_key':apiKey}
    r = requests.get(composeURL(urlAPI,frobParams))
    responseText = r.text
    root = ET.fromstring(responseText)
    frob = root.find('frob').text

    authParams={ 'perms':'read', 'api_key':apiKey, 'frob':frob}
    print(composeURL(authURL,authParams))
    pickle.dump(frob, open('frob.p','wb'))
    print('Goto URL above and press enter when done')
    input()
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
        queryData(authToken, frob)
    except Exception as e:
        print(e)
        print('Something went wrong, clear p files')
