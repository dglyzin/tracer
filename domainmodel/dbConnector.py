'''
Created on Sep 30, 2015

@author: dglyzin
'''


import MySQLdb

def getDbConn(jobId):
    db = MySQLdb.connect(host="127.0.0.1", # your host, usually localhost
                         user="cherry", # your username
                         passwd="sho0ro0p", # your password
                         db="cluster") # name of the data base
    cur = db.cursor()
    cur.execute("DELETE FROM task_results WHERE task_id="+str(jobId) )
    db.commit()    
    return db, cur

def setDbJobState(db, cur, jobId, state):    
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
     
    #1. get task id
    #command = 'python '+connection.preprocessorFolder+'/jsontobin.py '+str(jobId)+' '   +projFolder+'/'+remoteProjectFileName + " " + 
    #                       connection.solverExecutable + " " + connection.preprocessorFolder
    #2. add task to db
    #3. generate launcher script

    # Use all the SQL you like   
        
    #now record is created form web ui
    #cur.execute("DELETE FROM jobs WHERE id="+str(jobId) )
    #cur.execute("INSERT INTO jobs (id, slurmid, starttime, finishtime, percentage, state, userstatus) VALUES ("+str(jobId)+", 0, NOW(), NOW(), 0, "+str(JS_PREPROCESSING)+", "+str(USER_STATUS_START)+")")
    #cur.execute("UPDATE tasks SET  state=17 WHERE id=2")    
    cur.execute("UPDATE tasks SET  state="+str(state)+" WHERE id="+str(jobId) )    
    db.commit()
    
def getDbUserStatus(cur, jobId):
    cur.execute("SELECT userstatus FROM tasks WHERE id="+str(jobId))
    data = cur.fetchone()    
    return data[0]
