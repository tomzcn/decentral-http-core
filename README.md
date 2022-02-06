Parent Project: https://github.com/tomzcn/decentral-http

Run server:

```
python decentral-http-core.py
```

Test:

```
curl -X POST http://217.0.0.1:8881/server/post -H 'Content-Type: application/json'  -d '{"message":"add_server","server_url":"http://127.0.0.1:8881/s1/post"}'
```
