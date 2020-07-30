# QuorumCluster

**Network programming project SS20**

Welcome to my project, which implements a decentralized network of different Nodes.  
One of the Nodes has the role of a master and the Nodes will decide base on a  
quorum who will be selected as master especially in case of an shutdown of the  
current master.   

**Installation**

To clone the repository use following command:

`git clone https://gitlab.ub.uni-bielefeld.de/till.johanndeiter/quorumCluster.git`

(Optional) you could use a virtual enviroment. For this you have to create one and activate it:

`python3 -m venv env`

`pip install --upgrade pip`

`source env/bin/activate`


Then install requirements form your repository folder

`pip install -r requirements`


**Manual**

You can start one Node directly by using the node.py script.

`python node.py`

Optional you can 


If your port is already in use a free port will be searched and selected.


The first four are the address, port, broadcast address and broadcast port. As
an default the combination  
`'0.0.0.0' 8080 '255.255.255.255' 5595 `  
will be used. The broadcast port is used to make a handshake with existing nodes.

If you want, that instead of birthtime/time of initalization of one node the  
lowest port will be used for voting in quorum, you can add the 
`--use_port_instead_of_life_time` flag. If not first initalized node will be  
voted.

For testing issues you can pass with

`-m=i_am_master.py `

and for slave

`-s=i_am_slave.py`

a path to python scripts which are executed if the node change his role.

With `-d` you get a debug log with more information about e.g. who recieved  
a vote or number of connected notes.

```
Till want Till as new master
Till set Till as new master
Till add Kevin to connected by broadcast. Now are 0 nodes connected 
Till add Kevin to connected len of connected 1
Till want Kevin as new master
Till received vote for Kevin form Kevin
Till set Kevin as new master
```

For better readability. This name will also be used for reentering in current 
Network if a node dispatched and come back later.

If you want to dispatch your node enter `:q` in the command line. If you exit
by STRG + C then the node will be killed and marked as lost from existing Nodes

Example command:

`python node.py 0.0.0.0 6170 -d -m=i_am_master.py -s=i_am_slave.py -n=Till -d`


