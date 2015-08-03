import socket
import select
import threading
import json
from pymongo import MongoClient

############################################
### Main Classes for API access ###
############################################

class SigmaClient:

    def __init__(self):
        self.sigmaSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sigmaSocket.connect(("169.254.11.141", 8784))
        self.sigmaSocket.setblocking(0)

    def request(self, jsonStr, timeout = 20):
        try:
            msgToSend = jsonStr.encode(encoding = "utf-8");
            bytesSent = 0
            while bytesSent < len(msgToSend):
                bytesSent += self.sigmaSocket.send(msgToSend[bytesSent:])

            recvMessage = ""
            while True:
                ready = select.select([self.sigmaSocket], [], [], timeout)
                if ready[0]:
                    recvMessage += self.sigmaSocket.recv(1024 * 1024).decode(encoding = "utf-8")
                    if "\n" in recvMessage: #Complete message ends with \n
                        break
                else:
                    #timeout...
                    break
                
        except Exception as e:
            print(e)
            #handle exceptions...

        if not "\n" in recvMessage:
            print("Server: Empty or partial message received")
            return None
        else:
            print("Server: Complete message received") 
            return recvMessage

    def close(self):
        self.sigmaSocket.close()

    def getMasterIP(self):
        response = self.request('{"command": "getIpConfig"}')
        JSON_response = json.loads(response)
        return JSON_response["ip"]

    def getMasterID(self):
        response = self.request('{"command": "version"}')
        JSON_response = json.loads(response)
        return JSON_response["id"]

    def distanceToMaster(self):
        ID = self.getMasterID()
        command = '{"command": "getDist", "id": ' + '"' + str(ID) + '"' + '}'
        response = self.request(command)
        JSON_response = json.loads(response)
        return JSON_response

    def listAnchors(self):
        response = self.request('{"command": "listAnchors"}')
        JSON_response = json.loads(response)
        anchors = []
        for anchor in JSON_response['anchors']:
            anchors.append({"id": anchor['id'], "x": anchor['coordinates']['x'], 
                            "y": anchor['coordinates']['y'], 
                            "z": anchor['coordinates']['z']
                            })
        return anchors

    def listTags(self):
        response = self.request('{"command": "listTags"}')
        JSON_response = json.loads(response)
        tags = []
        for tag in JSON_response['tags']:
            tags.append({"id": tag['id'], "x": tag['coordinates']['x'],
                        "y": tag['coordinates']['y'], "z": tag['coordinates']['z'],
                        "heading": tag['coordinates']['heading']})
        return tags

    def getTagPosition(self, tagID):
        tags = self.listTags()
        target_tag = [tag for tag in tags if tag['id'] == tagID]
        if not target_tag:
            return {"error": "tag ID not found"}
        coordinates = [{"x": target_tag[0]['x-coordinate'], "y": target_tag[0]['y-coordinate'],
                       "z": target_tag[0]['z-coordinate'], "heading": target_tag[0]['heading']}]
        return coordinates

class ActiveClients:

    def __init__(self):
        self.clients = {}

    def newClient(self, username, app_type):
        if app_type == 'realtime':
            realtime_client = SigmaClient()
            self.clients[username] = realtime_client
        elif app_type == 'database':
            database_client = MongoClient()
            self.clients[username] = database_client

    def endSession(self, username, app_type):
        if app_type == 'realtime':
            self.clients[username].close()
            self.clients.pop(username, None)
        elif app_type == 'database':
            self.clients[username].close()
            self.clients.pop(username, None)

    def viewActive(self):
        return self.clients
