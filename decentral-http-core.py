# project url: https://www.github.com/tomzcn/http-p2p

import aiohttp
import asyncio
from aiohttp import web
import shelve

def db_init(filename):
    with shelve.open(filename) as db:
        if 'server_db' not in db:
            db['server_db']={}
            
db_init('./server.db')
db_init('./s1.db')
db_init('./s2.db')

async def say(url,message,myfile):
    if await exist(url):
        async with aiohttp.ClientSession() as session:
            async with session.post(url,json=message) as resp:
                print(resp.status)
                data= await resp.json()
        return data
    else:
        file_del_server(myfile,url)
        return {'message':'Url does not exist.'}

async def file_del_server(myfile,server_url):
    with shelve.open(myfile) as db:
        db2=db['server_db']
        del db2[server_url]
        db['server_db']=db2
        return True
    return False

async def file_add_server(myfile,server_url):
    with shelve.open(myfile) as db:
        db2=db['server_db']
        db2[server_url]=1
        db['server_db']=db2
        return True
    return False

async def exist(url):
    message={'message':'ping'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url,json=message) as resp:
            print(resp.status)
            if resp.status == 200:
                return True
    return False

async def server_post_template(request,myurl,myfile):
    req_json=await request.json()
    data={'message':'ok'}
    if req_json['message']=='ping':
        data={'message':'pong'}
    if req_json['message']=='add_server':
        print('=============add_server========================')
        print(myurl)
        server_url=req_json['server_url']
        exist_resp=await exist(server_url)
        print(exist_resp)
        if not exist_resp:
            raise()
        with shelve.open(myfile) as db:
            db1=db['server_db'].copy()
        if server_url not in db1 and exist_resp:
            # Record the server locally
            print('4')
            await file_add_server(myfile,server_url)
            # Tell all servers to add this server
            print('2')
            for i in db1.keys():
                message={'message':'broadcast_add_server','server_url':server_url}
                print(i)
                await say(i,message,myfile)
            # Tell all servers to the new server
            print('1')
            for i in db1.keys():
                message={'message':'broadcast_add_server','server_url':i}
                await say(server_url,message,myfile)
            # Tell the new server to record this server
            print('3')
            message={'message':'broadcast_add_server','server_url':myurl}
            await say(server_url,message,myfile)
    if req_json['message']=='broadcast_add_server':
        print('=============broadcast_add_server==================')
        print(myurl)
        server_url=req_json['server_url']
        with shelve.open(myfile) as db:
            db1=db['server_db'].copy()
            print(myfile)
            print(db1,'db1')
        if server_url not in db1:
            # Record the server locally
            print('4')
            await file_add_server(myfile,server_url)
    return data 

routes = web.RouteTableDef()

@routes.post('/server/post') 
async def server_post(request):
    print('server')
    data=await server_post_template(request,'http://s1:8881/server/post','/my/aiohttp/server.db')
    return web.json_response(data)

@routes.post('/s1/post') 
async def s1_post(request):
    print('s1')
    data=await server_post_template(request,'http://s1:8881/s1/post','/my/aiohttp/s1.db')
    return web.json_response(data)

@routes.post('/s2/post') 
async def s1_post(request):
    print('s2')
    data=await server_post_template(request,'http://s1:8881/s2/post','/my/aiohttp/s2.db')
    return web.json_response(data)
    
app = web.Application()
app.add_routes(routes)
web.run_app(app,port='8881',host='0.0.0.0')

