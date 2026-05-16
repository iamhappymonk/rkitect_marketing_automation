import httpx
print(httpx.post('https://api.bufferapp.com/1/updates/create.json', headers={'Authorization': 'Bearer WsaN6pD6roKFLYXbK0Djdw1aeqXksGeFHVCYwg_0UUw'}, data={'profile_ids[]': '6a020514090476fb990aeaf3', 'text': 'test'}).text)
