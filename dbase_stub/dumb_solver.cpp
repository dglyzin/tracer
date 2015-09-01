/* Standard C++ includes */
#include <stdlib.h>
#include <iostream>
#include <unistd.h>

/*
  Include directly the different
  headers from cppconn/ and mysql_driver.h + mysql_util.h
  (and mysql_connection.h). This will reduce your build time!
*/
#include "mysql_connection.h"

#include <cppconn/driver.h>
#include <cppconn/exception.h>
#include <cppconn/resultset.h>
#include <cppconn/statement.h>

#include <mpi.h>

using namespace std;

int main(int argc, char * argv[])
{
  
MPI_Init(NULL, NULL);

/*
 * Для каждого потока получаем его номер и общее количество потоков.
 */
int world_size, world_rank;
MPI_Comm_size(MPI_COMM_WORLD, &world_size);
MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);


cout << endl;
cout << "Hello World from"<< world_rank  << endl;

if (world_rank==0)
{
int jobId = atoi(argv[1]);

try {
  sql::Driver *driver;
  sql::Connection *con;
  sql::Statement *stmt;
  sql::ResultSet *res;

  /* Create a connection */
  driver = get_driver_instance();
  con = driver->connect("192.168.10.100", "cherry", "sho0ro0p");
  /* Connect to the MySQL test database */
  con->setSchema("cluster");

  
  char stmtstring[256];
  //change state to computing
  sprintf(stmtstring, "UPDATE jobs SET state=1 WHERE id=%d", jobId);
  stmt = con->createStatement();
  stmt->execute(stmtstring);
  //stmt->execute("INSERT INTO tasks (id, user, taskname) VALUES (NULL, 'dgl', 'oloolo')"); 
  delete stmt;

  
  for (int idx = 0; idx<100; idx++){
      sleep(1);
      sprintf(stmtstring, "UPDATE jobs SET percentage=%d WHERE id=%d", idx, jobId);
      stmt = con->createStatement();
      stmt->execute(stmtstring);     
      cout<< "completed " << idx<<endl;
      delete stmt;  
  }
  
  
  //change state to finished  
  sprintf(stmtstring, "UPDATE jobs SET percentage=100, state=2 WHERE id=%d", jobId);
  stmt = con->createStatement();
  stmt->execute(stmtstring);  
  delete stmt;

  

  stmt = con->createStatement();
  //res = stmt->executeQuery("SELECT 'Hello World!' AS _message");
  res = stmt->executeQuery("SELECT * FROM jobs");
  while (res->next()) {
    cout << "\t... MySQL replies: ";
    /* Access column data by alias or column name */
    //cout << res->getString("_message") << endl;
    //cout << "\t... MySQL says it again: ";
    /* Access column fata by numeric offset, 1 is the first column */
    cout << res->getString(1) <<":"<<res->getString(2)<<":"<< res->getString(3) << endl;
  }
  delete res;
  delete stmt;
  delete con;



} catch (sql::SQLException &e) {
  cout << "# ERR: SQLException in " << __FILE__;
  cout << "(" << __FUNCTION__ << ") on line "   << __LINE__ << endl;
  cout << "# ERR: " << e.what();
  cout << " (MySQL error code: " << e.getErrorCode();
  cout << ", SQLState: " << e.getSQLState() << " )" << endl;
}

cout << endl;
}

MPI_Finalize();

return EXIT_SUCCESS;
}
