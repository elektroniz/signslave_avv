
#!/usr/bin/env python
# WS server example
import lib_signslave
import asyncio
import websockets
import json
from concurrent.futures import TimeoutError as ConnectionTimeoutError

config = lib_signslave.load_config("config.ini")
HOST = config['CONNECTION']['ip']
TIMEOUT = 10
ENDPOINT = "ws://" + HOST + ":8760"

async def checkWebSocket():
    try:
        # make connection attempt
        connection = await asyncio.wait_for(websockets.connect(ENDPOINT), TIMEOUT)
        return {"method": "signslave", "status": "True"}
    except ConnectionTimeoutError as e:
        return {"method": "signslave", "status": "False"}


async def readUSBCert(path):
    uri = "ws://" + HOST + ":8760"
    # Check if machine is on the network
    try:
        # make connection attempt
        connection = await asyncio.wait_for(websockets.connect(uri), TIMEOUT)
        # If success
        async with websockets.connect(uri) as websocket:
            await websocket.send('{"method": "readUSBCert"}')
            # print(f"request to signslave > readUSBCert")
            signslaveresponse = await websocket.recv()
            # print(f"signslave response: < {signslaveresponse}")
            return signslaveresponse
    except ConnectionTimeoutError as e:
        return {"method": "readUSBCert", "status": "False"}


async def checkWebDisk():
    uri = "ws://" + HOST + ":8760"
    # Check if machine is on the network
    try:
        # make connection attempt
        connection = await asyncio.wait_for(websockets.connect(uri), TIMEOUT)
        # If success
        async with websockets.connect(uri) as websocket:
            await websocket.send('{"method": "checkWebDisk"}')
            # print(f"request to signslave > checkWebDisk")
            signslaveresponse = await websocket.recv()
            # print("ho ricevuto", signslaveresponse)
            # print(f"signslave response: < {signslaveresponse}")
            return signslaveresponse
    except ConnectionTimeoutError as e:
        return {"method": "Signslave non in ascolto", "status": "False"}
async def proxyclient(path):
    # print("Trying to connect with signslave...")
    uri = "ws://" + HOST + ":8760"
    # Check if machine is on the network
    try:
        # make connection attempt
        connection = await asyncio.wait_for(websockets.connect(uri), TIMEOUT)
        # If success
        async with websockets.connect(uri) as websocket:
            path = '{"method": "fileFirma", "message": "' + path + '"}'
            await websocket.send(path)
            # print(f"request to signslave > {path}")
            signslaveresponse = await websocket.recv()
            # print(f"signslave response: < {signslaveresponse}")
            return signslaveresponse
    except ConnectionTimeoutError as e:
        # print("Problemi durante la connessione")
        return {"method": "signslave", "status": "False"}

async def controller(websocket, path):
    # Await for the command from Javascript Side
    try:
        command = await websocket.recv()
    except:
        print("Errore durante la ricezione del messaggio")
    # Make String an JSON Object
    command = json.loads(command)
    command["methods"] = command['methods'].split(",")
    # Check if method in order to check if signslave is on
    responses = []
    for method in command["methods"]:
        if method == "checkSignSlave":
            # Check if signslave is alive!
            try:
                response = await checkWebSocket()
            except:
                response = {"method": "signslave", "status": "False"}
                return
            # print(f"> {response}")
            responses.append(response)
        if method == "checkWebDisk":
            # Check if signslave is alive!
            try:
              response = await checkWebDisk()
            except:
              response = {"method": "checkWebDisk", "status": "False"}
            # print(f"> {response}")
            responses.append(response)
        if method == "fileFirma":
            # Take the parameter from the object
            path = str(command["parameter"])
            # print(f"< Webapp sent this path: {path}")
            response = await proxyclient(path)
            # print(f"> {response}")
            responses.append(response)
        if method == "readUSBCert":
            # print("[*] Reading certificate from digital signed file [*]")
            # print(f"< Webapp requested readUSBCert: {path}")
            response = await readUSBCert(path)
            # print(f"> {response}")
            responses.append(response)
    responses = str(responses)
    # print(responses)
    responses = responses.replace('"', '')
    await websocket.send(str(responses))
    # websocket.close()

print("[*] Postazione Segreteria in esecuzione [*]")
start_server = websockets.serve(controller, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()