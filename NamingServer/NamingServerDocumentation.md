# Named Server Documentation

## Using NamedServer

In order to use the NamedServer, run NamedServer.py before starting the dependent services.
Use the MessageProc class in the NamingServer folder to give and receive messages.

 - Use *give_to_name_server* method to give messages to the name server
   - Use label *register* with a name and pid to register with the server
   - Use label *deregister* with a name to remove registration from the server
   - Use label *get_service* with a name to get the name and pid of a service back (will block if no matching registered service)
   - Use label *stop* to shutdown the server
 - Receive and Give are used as normal, with the pid of the process to talk to

## Running examples

Two examples have been created:
 - *name_server_test.py*
 - *named_service_one.py* with *named_service_two.py*

Run test by starting the *name_server.py* file in one terminal and the *name_server_test.py* file in another.  
The test file will register and get services from the server, echoed by print statements.

Run the named services by starting the *name_server.py* file, then the *named_service_one.py* followed by *named_service_two.py*.  
The services will register themselves, get each others services, and talk to each other, echoed by print statements.

