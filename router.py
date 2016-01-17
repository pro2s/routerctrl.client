#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json
import transmissionrpc
import os
import ConfigParser

def readconfig(section = "Default"):
    config = ConfigParser.RawConfigParser()
    config.read('settings.ini')
    return dict(config.items(section))
    
def send_api(url,data,name,service,value):
    if 'id' in data:
        data['value']  = value
        data.pop("updated", None)
        id = str(data['id'])
        data = json.dumps(data)
        r = requests.put(url + id, data)
        print "%s(%s) - %d" % (service, name, r.status_code)
    else:
        r = requests.post(url,json.dumps({"value":value,"name":name,"service":service}))
        print "%s(%s) - %d" % (service, name, r.status_code)
    return 0

def router_data():
    def_cfg = readconfig()
    tm_cfg =  readconfig("Transmission")

    url = def_cfg ["api_url"] + "api/router/"
    data = {}
    r = requests.get(url)

    if r.status_code == 200:
        data = r.json()

    openwrt = {}
    transmission = {}

    for item in data:
        if item['service'] == 'openwrt':
            if  item['name'] == 'state':
                openwrt['state'] = item
            if  item['name'] == 'traffic':
                openwrt['traffic'] = item    
        if item['service'] == 'transmission' and item['name'] == 'state':
            transmission['state'] = item
            
    stream = os.popen("uptime")
    uptime = stream.read()
    send_api(url,openwrt['state'],'state','openwrt',uptime)

    tc = transmissionrpc.Client(user = tm_cfg["user"], password = tm_cfg["password"])
    s = tc.get_session()
    send_api(url,transmission['state'],'state','transmission',s.version)
   
    os.system("vnstat -u -i %s" % def_cfg["vnstat_interface"])
    os.system("vnstati -vs -i %s -o /www/http/vnstat.png" % def_cfg["vnstat_interface"])
    with open("/www/http/vnstat.png", "rb") as f:
        data = f.read()
    value =  data.encode("base64")
    send_api(url,openwrt.get('traffic',{}),'traffic','openwrt',value)
    
    
    
def transmission_data():
    tm_cfg =  readconfig("Transmission")
    tc = transmissionrpc.Client(user = tm_cfg["user"], password = tm_cfg["password"])
    # get commands 
    data = {}
    url = tm_cfg["api_url"] + "api/cmds/" 
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
    
    for item in data:
        if item['service'] == 'transmission':
            if item['name'] == 'add' and item['value'] == 'file' and item['file'] != None:
                fh = open("/tmp/%d.torrent" % item['id'], "wb")
                fh.write(item['file'].decode('base64'))
                fh.close()
                t = tc.add_torrent("/tmp/%d.torrent" % item['id'])
                t.start()
                r = requests.delete(url+str(item['id']))
                
    
    # get torrents
    url = tm_cfg["api_url"] + "api/torrents/"
    ts = tc.get_torrents()	
    r_t = {}
    data = {}

    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()

    for item in data:
        r_t[item["hashString"]] = item["id"]

    for t in ts:
        data = {
        "name":t.name,
        "hashString":t.hashString,
        "status":t.status,
        "totalSize":t.totalSize,
        "progress":t.progress,
        }
        if t.hashString in r_t:
            id = str(r_t[t.hashString])
            r = requests.put(url+id,json.dumps(data))
            r_t.pop(t.hashString, None)
        else:    
            r = requests.post(url,json.dumps(data))
        print "%s(%s) - %d" % ("transmission", t.name.encode("utf-8"), r.status_code)

    for key, id in r_t.iteritems():
        id = str(id)
        r = requests.delete(url+id)
        print "%s(%s) - %d" % ("transmission-delete", id, r.status_code)

router_data()
transmission_data()
