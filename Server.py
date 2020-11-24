import random
import socket
import time
from _thread import *
import threading
from datetime import datetime
import json
import urllib
import urllib.parse
import urllib.request
import random

playerInQueue=[]


def connectionLoop(sock):
   while True:
      data, addr = sock.recvfrom(1024)
      res=json.loads(data.decode())
      res['WaitTime']="0"
      res['Addr']=addr
      print("Got this: "+str(res)+" From: "+str(addr))
      playerInQueue.append(res)
      
def getGameEvent():
   res = urllib.request.urlopen("https://uzusl5kue1.execute-api.us-east-1.amazonaws.com/default/GameEvent").read().decode("utf-8")
   res=json.loads(res)
   if res:
      maxGameId=int(res[0]['GameID'])
      for item in res:
         if int(item['GameID'])>maxGameId:
            maxGameId=int(item['GameID'])
      return maxGameId
      
def updateGameEvent(GameEvent):
   GameID=GameEvent['GameID']
   AverageMMR=GameEvent['AverageMMR']
   P1=GameEvent['P1']
   P2=GameEvent['P2']
   P3=GameEvent['P3']
   TimeStamp=GameEvent['TimeStamp']
   Winner=GameEvent['Winner']
   item={
      "GameID":GameID,
      "AverageMMR":AverageMMR,
      "P1":P1,
      "P2":P2,
      "P3":P3,
      "TimeStamp":TimeStamp,
      "Winner":Winner
   }
   data = bytes(json.dumps(item),'utf8')
   headers = {"Content-Type": "application/json"}
   req = urllib.request.Request("https://uzusl5kue1.execute-api.us-east-1.amazonaws.com/default/GameEvent", data=data, headers=headers)
   res = urllib.request.urlopen(req)
   print(res.read().decode("utf-8")) 
         
def matchMakingServer(sock):
   playerInGame=[]
   while True:
      for player in playerInQueue:
         player['WaitTime']=int(player['WaitTime'])+1

      if len(playerInQueue)>=3 or playerInGame:
         
         
         if not playerInGame:
            playerInGame.append(playerInQueue[0])
            p1Max=int(playerInGame[0]['MMR'])+int(playerInGame[0]['WaitTime'])*1
            p1Min=int(playerInGame[0]['MMR'])-int(playerInGame[0]['WaitTime'])*1
            del playerInQueue[0]

         else:
            for player in playerInQueue:
               p2Max=int(playerInGame[0]['MMR'])+int(playerInGame[0]['WaitTime'])*1
               p2Min=int(playerInGame[0]['MMR'])-int(playerInGame[0]['WaitTime'])*1
               if p1Max>=p2Min or p1Min<=p2Max:
                  playerInGame.append(player)
                  playerInQueue.remove(player)
                  if len(playerInGame)==3:
                     simulateMatch(playerInGame[0],playerInGame[1],playerInGame[2],sock)
                     playerInGame=[]
                     break
               
            
      time.sleep(1)

      
def simulateMatch(player1,player2,player3,sock):
   print("MatchFound!\n"+str(player1)+str(player2)+str(player3))
   temp=random.randint(1,3)
   if temp==1:
      player1['Win']=str(int(player1['Win'])+1)
      player2['Lose']=str(int(player2['Lose'])+1)
      player3['Lose']=str(int(player3['Lose'])+1)
      winner=player1['UserName']
      player1['MMR']=str(int(player1['MMR'])+2)
      player2['MMR']=str(int(player2['MMR'])-1)
      player3['MMR']=str(int(player3['MMR'])-1)
   elif temp==2:
      player2['Win']=str(int(player2['Win'])+1)
      player1['Lose']=str(int(player1['Lose'])+1)
      player3['Lose']=str(int(player3['Lose'])+1)
      winner=player2['UserName']
      player1['MMR']=str(int(player1['MMR'])-1)
      player2['MMR']=str(int(player2['MMR'])+2)
      player3['MMR']=str(int(player3['MMR'])-1)
   elif temp==3:
      player3['Win']=str(int(player3['Win'])+1)
      player2['Lose']=str(int(player2['Lose'])+1)
      player1['Lose']=str(int(player1['Lose'])+1)
      winner=player3['UserName']
      player1['MMR']=str(int(player1['MMR'])-1)
      player2['MMR']=str(int(player2['MMR'])-1)
      player3['MMR']=str(int(player3['MMR'])+2)
      
   if int(player1['MMR'])<0:
      player1['MMR']='0'
      
   if int(player2['MMR'])<0:
      player2['MMR']='0'
      
   if int(player3['MMR'])<0:
      player3['MMR']='0'
      
      
      
   player1['Kill']=str(int(player1['Kill'])+random.randint(0,5))
   player1['Death']=str(int(player1['Death'])+random.randint(0,5))
   player1['Level']=str(int(player1['Level'])+1)
   
   player2['Kill']=str(int(player2['Kill'])+random.randint(0,5))
   player2['Death']=str(int(player2['Death'])+random.randint(0,5))
   player2['Level']=str(int(player2['Level'])+1)
   player3['Kill']=str(int(player3['Kill'])+random.randint(0,5))
   player3['Death']=str(int(player3['Death'])+random.randint(0,5))
   player3['Level']=str(int(player3['Level'])+1)
   
   temp_total=int(player1['MMR'])+int(player2['MMR'])+int(player3['MMR'])
   gameId=getGameEvent()+1
   GameEvent={"GameID":str(gameId),"AverageMMR":str(temp_total/3),"P1":player1['UserName'],"P2":player2['UserName'],"P3":player3['UserName'],"TimeStamp":str(time.time()),"Winner":winner}
   updateGameEvent(GameEvent)
    
      
   sock.sendto(json.dumps(player1).encode(), player1['Addr'])
   sock.sendto(json.dumps(player2).encode(), player2['Addr'])
   sock.sendto(json.dumps(player3).encode(), player3['Addr'])

def UpdatePlayer(player):
   UserName=player['UserName']
   Win=player['Win']
   Lose=player['Lose']
   MMR=player['MMR']
   Kill=player['Kill']
   Death=player['Death']
   Level=player['Level']
   item={
      "UserName":UserName,
      "Win":Win,
      "Lose":Lose,
      "MMR":MMR,
      "Kill":Kill,
      "Death":Death,
      "Level":Level
   }
   data = bytes(json.dumps(item),'utf8')
   headers = {"Content-Type": "application/json"}
   req = urllib.request.Request("https://uzusl5kue1.execute-api.us-east-1.amazonaws.com/default/GameEvent", data=data, headers=headers)
   res = urllib.request.urlopen(req)
   print(res.read().decode("utf-8")) 
   
   
def main():
   port = 12345
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.bind(('', port))
   start_new_thread(connectionLoop, (s,))
   start_new_thread(matchMakingServer, (s,))
   while True:
      time.sleep(1)

if __name__ == '__main__':
   main()