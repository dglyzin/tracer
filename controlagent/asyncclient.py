import socket
import json
import base64
import struct
import asyncio 
 
def getData(title):
    #create data
    with open('image.jpg', 'rb') as f:
        data = f.read()

    #encode binary data into bytestring containing only "good" characters
    b64data = base64.b64encode(data)
    #make it real string to be json serializable
    #we pretend it is utf-8 encoded 
    #(every "good" character is just the same character in utf-8)
    stringData = b64data.decode('UTF-8')
    pic1 = {"title":title, "data":stringData}
    mydict = {"JobId":345, "State":"OK", "Results":[pic1]}
    djson = json.dumps(mydict)
    ssize = struct.pack("I",len(djson))
    message = ssize + djson.encode('UTF-8')
    return message


def getStopMessage():
    mydict = {"JobId":345, "State":"Stop"}
    djson = json.dumps(mydict)
    ssize = struct.pack("I", len(djson))
    message = ssize + djson.encode('UTF-8')
    return message


async def tcp_echo_client(loop):
    reader, writer = await asyncio.open_connection('192.168.10.100', 8888,
                                                        loop=loop)
    userStatus = "Continue"
    count = 555
    for idx in range(count):
        #print('Send: %r' % message)
        message = getData("uplot%d"%idx)

        writer.write(message)
        await writer.drain() 
        print("Message %d of %d sent!" % (idx, count))
        #data = await reader.read(100)
        #print('Received: %r' % data.decode())
        response = await reader.read(100)
        respdict = json.loads(response.decode())
        userStatus = respdict["UserStatus"] 
        if userStatus == "Terminate":
            break
        await asyncio.sleep(1)
    
    if userStatus == "Contunue":
        message = getStopMessage()
        writer.write(message)
    else:
        print ("User terminated the computations")

    print('Close the socket')    
    writer.close()


#async def 

#message = 'Hello World!'
loop = asyncio.get_event_loop()
loop.run_until_complete(tcp_echo_client( loop))
loop.close()

