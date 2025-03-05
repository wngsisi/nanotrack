import time
import socket


def initConnection(portNo, baudRate):
    try:
        scc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        scc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        scc.connect((portNo, baudRate))
        print("Device connected")
        return scc
    except:
        print("Not Connected")


def sendData(sock, data):
    try:
        if data[0] > 95 and data[1] > 92:                       
            if 1 < data[0] - data[1]:
                d = bytes.fromhex('FF 01 00 04 05 00 0A')       
                sock.send(d)
                
            elif 1 < data[1] - data[0]:
                d = bytes.fromhex('FF 01 00 08 00 05 0E')       
                sock.send(d)
           
            else:
                d = bytes.fromhex('FF 01 00 0C 05 05 17')       
                sock.send(d)
              
        elif 85 > data[0] and 88 < data[1] < 92:               
            d = bytes.fromhex('FF 01 00 02 05 00 08')
            print("1")
            sock.send(d)
            print("2")
        elif data[0] > 95 and data[1] < 92:                  
            if 1 < data[0] -90 - (90 - data[1]):
                d = bytes.fromhex('FF 01 00 04 05 00 0A')     
                sock.send(d)
            
            elif 1 < 90 - data[0] - (data[1] - 90):
                d = bytes.fromhex('FF 01 00 10 00 05 16')       
                sock.send(d)
          
            else:
                d = bytes.fromhex('FF 01 00 14 05 05 1F ')     
                sock.send(d)
        
        elif data[0] < 95 and data[1] > 92:                    
            time.sleep(0.1)
            if 1 < data[0] - 90 - (90 - data[1]):
                d = bytes.fromhex('FF 01 00 08 00 05 0E')      
                sock.send(d)
          
            elif 1 < 90 - data[0] - (data[1] - 90):
                d = bytes.fromhex('FF 01 00 02 05 00 08')  
                sock.send(d)
          
            else:
                d = bytes.fromhex('FF 01 00 0A 05 05 15')     
                sock.send(d)
       
        elif data[0] < 85 and data[1] < 88:               
            if 1 < data[0] - data[1]:
                d = bytes.fromhex('FF 01 00 10 00 05 16')    
                sock.send(d)
     
            elif 1 < data[1] - data[0]:
                d = bytes.fromhex('FF 01 00 02 05 00 08')     
                sock.send(d)
           
            else:
                d = bytes.fromhex('FF 01 00 12 05 05 1D')    
                sock.send(d)
          
        elif 85 <= data[0] <= 95 and 88 <= data[1] <= 92:      
            d = bytes.fromhex('FF 01 00 00 00 00 01')
            sock.send(d)
     
        elif 85 < data[0] < 95 and 88 > data[1]:                
            d = bytes.fromhex('FF 01 00 10 00 05 16')
            sock.send(d)
        elif 85 < data[0] < 95 and 92 < data[1]:               
            d = bytes.fromhex('FF 01 00 08 00 05 0E')
            sock.send(d)
        elif 95 < data[0] and 88 < data[1] < 92:               
            d = bytes.fromhex('FF 01 00 04 05 00 0A')
            sock.send(d)
        
        else:
            pass
    except:
         print("Data Transmission Failed ........")
         d = bytes.fromhex('FF 01 00 00 00 00 01')
         sock.send(d)
