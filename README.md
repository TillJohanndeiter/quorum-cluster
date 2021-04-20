# Quorum Cluster

Implementation of a decentralized network of multiple Nodes. One of the nodes has the role of a master and the nodes will elect the current master automatically.

**Installation**

You could use a virtual environment to avoid dependency problems:

`python3 -m venv env`

`pip install --upgrade pip`

`source env/bin/activate`

Install requirements:

`pip install -r requirements`


**Manual**

You can start one Node directly by using the node.py script.

`python node.py`


The first four arguments are address, port, broadcast address and broadcast port.  
As a default the combination  

`'0.0.0.0' 8080 '255.255.255.255' 5595 `  

will be used. The broadcast is used to make a handshake with existing nodes.

If a port is already in use a free port will be selected.

If you want, that instead of birthtime/time of initalization of one node the lowest port will be used for voting in quorum, you can add the `--use_port_instead_of_life_time` flag.

For testing issues, you can pass with

`-m=i_am_master.py `

and for slave

`-s=i_am_slave.py`

a path to python scripts which are executed if the node change his role.

With `-d` you get a debug log with more information about e.g. who received    
a vote or number of connected notes.

```
A set A as new master
A add B to connected by handshake. Now are 1 nodes connected 
A set B as new master
```

For better readability of logs you can give the node a nickname by set  

`-n=Your_Node_Name`  

This name will also be used for re-entering if a node dispatched and come back 
later.

If you want to dispatch your node enter 'q` in the command line. If you exit  
by STRG + C then the node will be killed and marked as lost from existing Nodes

Example command:

`python node.py 0.0.0.0 6170 -d -m=i_am_master.py -s=i_am_slave.py -n=B -d`


**Quorum algorithm**

Each node calculates based on time or port metric his wanted master  
and send constantly information about his vote to other nodes.  
If a node detects changes (New Node or Lost/Dispatching Slave/Master)  
it will change his voted master and change his transmitted information per  
TCP socket. Also each Node constantly listen to incoming messages from other    
nodes and evaluate most voted master.

So you can imagine the network as a constant election.

Base on own and recieving votes the new master is constantly  
calculated by absolute majoritiy. If their is no absolute the largest part  
will surivive. Others will dispatch. If more nodes lost than connected the node  
will dispatch, because the network cannot build a majority any longer.  
                 


**Tests**

In test/ are unittest classes and integration_tests.py which contains  
bigger integrations test especially for determination of a master in different  
scenarios. More information about each case are in documentation.

```
pytest -v test/
pytest -v test/integration_tests.py
```


## License

[The Unlicense](https://choosealicense.com/licenses/unlicense/)


# Contact

If you have questions, issues or feedback: 

till.johanndeiter (at) web.de


