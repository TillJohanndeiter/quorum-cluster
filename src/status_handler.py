"""
Provides and observer that will execute specific python scripts if node changes status.
"""
import os
from observer import Observer
from src.vote_strategy import NEW_MASTER
from src.node_manger import NodeManger


class StatusHandler(Observer):
    """
    Observer that will make an terminal call to start python scripts if node
    changes wish_master or slave status.
    """

    def __init__(self, own_information, node_manger: NodeManger, slave_script=None, master_script=None):
        super().__init__()
        self.own_information = own_information
        self.slave_script = slave_script
        self.master_script = master_script
        self.node_manger = node_manger

    def update(self, new_value):
        new_value = new_value[0]
        event = new_value.name
        if event == NEW_MASTER:
            old_master, new_master = new_value.value
            if old_master != new_master:
                if new_master == self.own_information:
                    if self.master_script is not None:
                        os.system('python ' + self.master_script)
                else:
                    if self.slave_script is not None:
                        os.system('python ' + self.slave_script)
