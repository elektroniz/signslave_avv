import lib_signslave
import websockets
import asyncio
import json
import sys
from time import sleep

config = lib_signslave.load_config("config.ini")
PORT = config["CONNECTION"]["port"]

def checkWebDisk(path):
    if(lib_signslave.check_webdisk(path)):
        return str({"method": "checkWebDisk", "status": "True"})
    return str({"method": "checkWebDisk", "status": "False"})


def readUSBCert(cert):
    cert = lib_signslave.loadCert()
    certName = lib_signslave.readUSBCert(cert)
    return str({"method": "readUSBCert", "status": "True", "name": certName})


def signDocument(crypt, inputFile, outputFile):
    if(lib_signslave.signdocument(crypt, inputFile, outputFile)):
        return str({"method": "firmaFile", "status": "True"})
    return str({"method": "firmaFile", "status": "False"})
    

def func2(parametro):
    return str({"method": "chiamata2", "status": parametro})
    

async def wb_send(websocket, msg):
    try:
        await websocket.send(msg)
    except:
        return


async def websocket_controller(websocket, path):
    """
    Websocket controller is a method used to handle and sort request
    from a client to the selected method.

    Arguments:
    websocket - object to work with websocket protocol.
    """
    # Receive message from server.
    try:
        msg = await websocket.recv()
    except ValueError:
        lib_signslave.error_box("Error", "Fatal Error: websocket can't receive data...")
    # Trying to loads json, if the message is not a JSON
    # returns an error to client.
    try:
        msg_jsonObj = json.loads(msg)
    except ValueError:
        await wb_send(websocket, "Invalid JSON Message")
        return
    # Check in JSON there are these 2 parameters to work on.
    if not 'method' in msg_jsonObj:
        # If not, return an error to client.
        await wb_send(websocket, "Invalid JSON Message, requested keys not found")
        return
    # If all goes correctly, call the user selected method.
    for method in methods:
        if msg_jsonObj["method"] == method[0]:
            # If match call function from list as callback function
            # Some of methods are syncronous from lib_signslave.py.

            if("message" in msg_jsonObj):
                sign_jsonObj = json.loads(msg_jsonObj["message"].replace('\'', '"'))
                
                inputfile = config["PATHs"]["webdiskpath"] + \
                sign_jsonObj["source"] + sign_jsonObj["file"]

                outputfile = config["PATHs"]["webdiskpath"] + \
                sign_jsonObj["destination"] + sign_jsonObj["file"]
                response = method[1](method[2][0], inputfile, outputfile)

            else:
                response = method[1](method[2]) 
            # Take result and send to client
            await wb_send(websocket, response)
            return
    # If not any method is matched, return to client
    await wb_send(websocket, "Nonexistent method")
    return



if __name__ == '__main__':
    crypt = lib_signslave.loadChilkat2()
    cert = lib_signslave.loadCert()

    listParameters = [crypt]

    methods = [ ("checkWebDisk", checkWebDisk, config["PATHs"]["webdiskpath"]),
                ("readUSBCert", readUSBCert, cert),
                ("fileFirma", signDocument, listParameters) ]
    # Check if websocket can listen on that IP and PORT.
    try:
        start_server = websockets.serve(websocket_controller, "0.0.0.0", PORT)
    except:
        lib_signslave.error_box("Error", "Check connection parameters, maybe port is busy")
        sys.exit(0)

    print("[+] Servizio Server Di Firma In Ascolto [+]")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()