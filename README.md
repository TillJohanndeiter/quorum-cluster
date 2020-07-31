# QuorumCluster

**Network programming project SS20**

Welcome to my project, which implements a decentralized network of different Nodes.  
One of the nodes has the role of a master and the nodes will decide base on a  
quorum who will be selected as master especially in case of unexpected shutdown
of the current master.

**Installation**

To clone the repository use following command:

`git clone https://gitlab.ub.uni-bielefeld.de/till.johanndeiter/quorumCluster.git`

(Optional) you could use a virtual enviroment to avoid dependecy problems. 
For this you have to create one and activate it:

`python3 -m venv env`

`pip install --upgrade pip`

`source env/bin/activate`

Then install requirements from your repository folder

`pip install -r requirements`


**Manual**

You can start one Node directly by using the node.py script.

`python node.py`


The first four arguments are address, port, broadcast address and broadcast port.  
As an default the combination  

`'0.0.0.0' 8080 '255.255.255.255' 5595 `  

will be used. The broadcast is used to make a handshake with existing nodes.

If default or passed port is already in use a free port will be searched 
and selected.

If you want, that instead of birthtime/time of initalization of one node the  
lowest port will be used for voting in quorum, you can add the 
`--use_port_instead_of_life_time` flag.

For testing issues you can pass with

`-m=i_am_master.py `

and for slave

`-s=i_am_slave.py`

a path to python scripts which are executed if the node change his role.

With `-d` you get a debug log with more information about e.g. who recieved  
a vote or number of connected notes.

```
Doof set Doof as new master
Doof add Dick to connected by handshake. Now are 1 nodes connected 
Doof set Dick as new master
```

For better readability of logs you can give the node a nickname by set  
`-n=Your_Node_Name`  
This name will also be used for reentering in current Network if a node  
dispatched and reentering later.

If you want to dispatch your node enter 'q` in the command line. If you exit  
by STRG + C then the node will be killed and marked as lost from existing Nodes

Example command:

`python node.py 0.0.0.0 6170 -d -m=i_am_master.py -s=i_am_slave.py -n=Till -d`


**Quorum algorithm**

Each node calculate based on time or port metric his wanted master 
and send constantly information about his vote to other nodes. 
If a node detect changes (New Node or Lost/Dispatching Slave/Master)
it will change his voted master and change his send information per TCP socker. 
Also each Node constantly listen to incoming messages from other nodes and 
evaluate most voted master.

So you can imagine the network as a constant election.

Base on own and recieving votes the new master is constaly 
calculated by absolute majoritiy. If their is no absolute the largest part 
will surivive. Others will dispatch. If more nodes lost than connect the node 
will dispatch, becausethe network cannot build a majority any longer. 

    select_self_as_master
    
    if network changes (Master or Slave dispatching, killed or enter network):  

        if PortStrategy:  
            select connected node with lowest port  
        if TimeStrategy:  
            select connected node furthest back initialisation time  

        send_vote_to_other_node_on_ping  
 
        for every incoming_ping:
        
            if more_lost_than_connected:  
                dispatch  
        
            add_vote_to_voting_dict  
            set_net_master

            if all_connected_nodes_voted:  
                calc_most_voted_note  
            
                if no_abs_majority:
                    largest_network_subpart_will_survive_rest_dispatch  
                 


**Tests**

In test/ are unittest classes and integration_tests.py which contains 
bigger integrations test especially for determination of a master in different
scenarios.

```
pytest -v test/
pytest -v test/integration_tests.py
```


**License**

I'm a big fan of open source software, so i decided to use 'The Unlicense' to  
allow maximal freedom of reusing.



