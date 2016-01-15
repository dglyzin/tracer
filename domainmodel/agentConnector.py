'''
Created on Nov 10, 2015

@author: dglyzin
'''

import socket
 
 
def fromClient():
    import socket
    import json
    import base64
    import struct
    
    TCP_IP = '192.168.10.100'
    TCP_PORT = 8888
    BUFFER_SIZE = 1024
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    
    with open('image.jpg', 'rb') as f:
        data = f.read()
    
    pic1 = {"title":"uplot", "data":base64.b64encode(data)}
    mydict = {"Results":[pic1]}
    djson = json.dumps(mydict)
    ssize = struct.pack("I",len(djson))
    
    MESSAGE = ssize + djson
    
    s.send(MESSAGE)
    s.close()






def getDbConn(jobId):
    TCP_IP = '192.168.10.100'
    TCP_PORT = 8888
    BUFFER_SIZE = 1024
    MESSAGE = "Hello, World!"     
    cur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cur.connect((TCP_IP, TCP_PORT))
    
    
    #cur.execute("DELETE FROM task_results WHERE task_id="+str(jobId) )
        
    return 0, cur

def freeDbConn(db, cur):
    # close the cursor object
    cur.close ()
    

def setDbJobState(db, cur, jobId, state):   
  
    cur.execute("UPDATE tasks SET state="+str(state)+" WHERE id="+str(jobId) )    
    db.commit()

def setDbSlurmId(db, cur, jobId, slurmId):    
    cur.execute("UPDATE tasks SET slurm_job="+str(slurmId)+" WHERE id="+str(jobId) )    
    db.commit()

def setDbJobPercentage(db, cur, jobId, percentage):    
    cur.execute("UPDATE tasks SET readiness="+str(percentage)+" WHERE id="+str(jobId) )    
    db.commit()

def setDbJobStartTime(db, cur, jobId):    
    cur.execute("UPDATE tasks SET date_start=NOW()  WHERE id="+str(jobId) )    
    db.commit()


def setDbJobFinishTime(db, cur, jobId):    
    cur.execute("UPDATE tasks SET date_end=NOW()  WHERE id="+str(jobId) )    
    db.commit()

def clearDbJobFinishTime(db, cur, jobId):    
    cur.execute("UPDATE tasks SET date_end=NULL  WHERE id="+str(jobId) )    
    db.commit()

    
def getDbUserStatus(cur, jobId):
    cur.execute("SELECT is_running FROM tasks WHERE id="+str(jobId))
    data = cur.fetchone()
    #returns LONG somehow, so int it    
    return data[0]

def setDbUserStatus(db, cur, jobId, status):
    sql = "UPDATE tasks SET is_running=%d WHERE id=%d"
    cur.execute(sql % (jobId, status))
    db.commit()



def addDbTaskResFile(db, cur, jobId, fileName, probTime ):
    #cur.execute("SELECT COUNT(task_id) AS NumberOfFiles FROM task_results WHERE task_id="+str(jobId) );
    #num = cur.fetchone()[0]
    #cur.execute("INSERT INTO task_results (num, filename, task_id) VALUES ("+str(picIdx)+", '"+ fileName+"', "+ str(jobId)+")")  
    isFinal = 0
    picData = open(fileName, 'rb').read()
    sql = "INSERT INTO task_results (is_final, task_id, prob_time, picture) VALUES (%d, %d, %s, '%s')"
    cur.execute(sql % (isFinal, jobId, str(probTime), MySQLdb.escape_string(picData)  ) )        
    db.commit()

