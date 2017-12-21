# -*- coding: utf-8 -*-
'''
Created on Mar 3, 2017

@author: hustcc
'''
from functools import wraps
from threading import Thread
import json
import click
import datetime
import copy
import os
from webhookit import app
import base64

the_unicode = str  # noqa


def standard_response(success, data):
    '''standard response
    '''
    rst = {}
    rst['success'] = success
    rst['data'] = data
    return json.dumps(rst)


def async(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.setDaemon(True)
        thr.start()
    return wrapper


# log
def log(t):
    msg = '%s: %s' % (current_date(), t)
    app.WSHandler.push_msg({'type': 'log', 'msg': msg})
    click.echo(msg)


def current_date():
    return datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S.%f")


def filter_server(server):
    server = copy.deepcopy(server)
    if is_remote_server(server):
        server['HOST'] = '***.**.**.**'
        server['PORT'] = '****'
        server['USER'] = '*******'
        server['PWD'] = '*******'
    return server


# 过滤服务器配置信息的敏感信息
def filter_sensitive(config):
    fconfig = {}
    for k, v in config.items():
        fconfig[k] = []
        for server in v:
            fconfig[k].append(filter_server(server))
    return fconfig


# if host port user pwd all is not empty, then it is a remote server.
def is_remote_server(s):
    # all is not empty or zero, then remote server
    return all([s.get('HOST', None),
                s.get('PORT', None),
                s.get('USER', None),
                s.get('PWD', None)])


# ssh to exec cmd
def do_ssh_cmd(ip, port, account, pkey, shell, push_data='', timeout=300):
    #os.system()

    return ("EMPTY_BY_HONZA", "EMPTY_BY_HONZA")


# 使用线程来异步执行
@async
def do_webhook_shell(server, data):
    log('Start to process server: %s' % json.dumps(filter_server(server)))
    script = server.get('SCRIPT', '')
    if script:
        if is_remote_server(server):
            # ip, port, account, pkey, shell, push_data='', timeout=300
            log('Start to execute remote SSH command. %s' % script)
            (success, msg) = do_ssh_cmd(server.get('HOST', None),
                                        server.get('PORT', 0),
                                        server.get('USER', None),
                                        server.get('PWD', None),
                                        server.get('SCRIPT', ''),
                                        data)
        else:
            log('Start to execute local command. %s' % script)
            msg = ""
            #import commands
            # local
            #(success, msg) = commands.getstatusoutput(server.get('SCRIPT', ''))
            tmpdata = json.dumps(data).encode()
            log(tmpdata)
            data = base64.standard_b64encode(tmpdata)
            
            os.system("python " + server.get('SCRIPT') + " %s" % data.decode("UTF-8"))

            success = True
    else:
        success = False
        msg = 'There is no SCRIPT configured.'
    # end exec, log data
    msg = str(msg)
    msg = msg.strip()
    msg = msg.replace('\n', ' ')
    log('Completed execute: (%s, %s)' % (success, msg))
    return True
