import asyncio
import logging

import settings
import base64
import json
import struct


logger = logging.getLogger("controle_node.request")


async def handle(reader, writer):
    addr = writer.get_extra_info('peername')
    logger.debug("From {0}".format(addr))
    
    status = "OK"
    messrecvd = 0
    while status == "OK":
        rawsize = await reader.read(4)
        print("got %d bytes from reader"%len(rawsize))
        #rawsize = rawdata[:4]
        size, = struct.unpack("I", rawsize)
        message = await reader.read(size)
        messrecvd = messrecvd + 1
        print("dumped json size = {}".format(size))
        #message = rawdata[4:].decode()
        jdict = json.loads(message.decode())
        print("Processing message for jobId %d", jdict["JobId"])
        status = jdict["State"]
        if status == "OK": 

            for pic in jdict["Results"]:
                fname = pic["title"]+".jpg"
                print("saving to {}\n".format(fname))
                data = base64.b64decode(pic["data"].encode("UTF-8"))
                with open(fname, "wb") as f:
                   f.write(data)
            #writer.write("Server confirmed receiving {}!".format(fname).encode())
            #await writer.drain()
        else:
            print ("client disconnected")
        if messrecvd>10:
            print ("I'm tired, go away, %d"% jdict["JobId"])
            status = "TOOMANY"
            response = json.dumps({"UserStatus":"Terminate"})
            writer.write(response.encode())
        else:
            response = json.dumps({"UserStatus":"Continue"})
            writer.write(response.encode())


loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle, loop=loop, **settings.SERVER)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
