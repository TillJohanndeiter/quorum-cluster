import os
from observer import Observer
from src.vote_strategy import NEW_MASTER


class StatusHandler(Observer):

    def __init__(self, own_information, slave_script=None, master_script=None):
        super().__init__()
        self.own_information = own_information
        self.slave_script = slave_script
        self.master_script = master_script

    def update(self, new_value):
        new_value = new_value[0]
        event = new_value.name
        master = new_value.value
        if event == NEW_MASTER:
            if master == self.own_information:
                if self.master_script is not None:
                    os.system('python ' + self.master_script)
            else:
                if self.slave_script is not None:
                    os.system('python ' + self.slave_script)
