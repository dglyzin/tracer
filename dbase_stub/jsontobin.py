import MySQLdb
import argparse
import os

def createRunFile(jobId, OutputRunFile, projFolder, solverExecutable, preprocessorFolder, runAtDebugPartition,
                       DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName):
    print "generating launcher script..."
    flag = 0
    if finishTimeProvided: flag+=1
    else: finishTime = -1.1
    if continueEnabled: flag +=2
    else: continueFileName = "n_a"
    #print OutputRunFile, DomFileName, finishTimeProvided, finishTime, continueEnabled, continueFileName
    
    runFile = open(OutputRunFile, "w")
    #conn = self.dmodel.connection
    videoGenerator = preprocessorFolder + "/createMovieOnCluster.py"
      
    partitionOption = " "
    if runAtDebugPartition:
        partitionOption = " -p debug "
      
    nodeCount = 2#self.dmodel.getNodeCount()
    runFile.write("echo Welcome to generated kernel launcher!\n")
    runFile.write("export LD_LIBRARY_PATH="+projFolder+":$LD_LIBRARY_PATH\n")
    runFile.write("srun -N "+str(nodeCount)+ partitionOption +solverExecutable+" "+str(jobId)+" "+DomFileName+" "+str(flag)+" "+str(finishTime)+" "+continueFileName+ "\n")
    runFile.close()


def createBinaries(jobId, inputFile, solverExecutable, preprocessorFolder, runAtDebugPartition, 
                   finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName):    

    db = MySQLdb.connect(host="127.0.0.1", # your host, usually localhost
                         user="cherry", # your username
                         passwd="sho0ro0p", # your password
                         db="cluster") # name of the data base
    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor() 
    #1. get task id
    #command = 'python '+connection.preprocessorFolder+'/jsontobin.py '+str(jobId)+' '   +projFolder+'/'+remoteProjectFileName + " " + 
    #                       connection.solverExecutable + " " + connection.preprocessorFolder
    #2. add task to db
    #3. generate launcher script

    # Use all the SQL you like
    cur.execute("DELETE FROM jobs WHERE id="+str(jobId) )
    cur.execute("INSERT INTO jobs (id, slurmid, starttime, finishtime, percentage, state) VALUES ("+str(jobId)+", 0, NOW(), NOW(), 0, 0)")
    db.commit()
    #cur.execute("SELECT * FROM tasks")

    # print all the first cell of all the rows
    #for row in cur.fetchall() :
    #    print row[0],":",row[1],":", row[2]


    projectDir = os.path.dirname(inputFile)
    projectName, _ = os.path.splitext(inputFile)   
    projectTitle = os.path.basename(projectName)
    if projectName == '':
        print "Bad file name"
        return

    OutputDataFile = projectName+".dom"
    OutputFuncFile = projectName+".cpp"
    OutputRunFile = projectName+".sh"
    
    createRunFile(jobId, OutputRunFile, projectDir, solverExecutable, preprocessorFolder, runAtDebugPartition, 
                     OutputDataFile, finishTimeProvided, finishTime, continueEnabled, continueFileName)





if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Processing json file on a remote cluster.', epilog = "Have fun!")
    #mandatory argument, unique job Id for identification in database
    parser.add_argument('jobId', type = int, help = "unique job ID")
    #mandatory argument, json filename
    parser.add_argument('fileName', type = str, help = "local json file to process")
    parser.add_argument('solverExecutable', type = str, help = "Solver executable")
    parser.add_argument('preprocessorFolder', type = str, help = "Preprocessor folder")
    #optional argument, exactly one float to override json finish time
    parser.add_argument('-finish', type=float, help = "new finish time to override json value")
    #optional argument with one or no argument, filename to continue computations from
    #if no filename is provided with this option, the last state is taken
    parser.add_argument('-cont', nargs='?', const="/", type=str, help = "add this flag if you want to continue existing solution.\n Provide specific remote filename or the last one will be used. ")
    parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
    args = parser.parse_args()
  
    inputFile = args.fileName
    finishTime = args.finish
    finishTimeProvided = not (finishTime is None)
    continueFileName = args.cont  
    continueEnabled = not (continueFileName is None)
    continueFnameProvided =  not (continueFileName == "/") if continueEnabled else False

    print "jsontobin input!", inputFile, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName
    createBinaries(args.jobId, inputFile, args.solverExecutable, args.preprocessorFolder, args.debug, finishTimeProvided, finishTime, continueEnabled, continueFnameProvided, continueFileName)
    