import os
from observer import Observer
from src.vote_strategy import NEW_MASTER


class StatusHandler(Observer):

    def __init__(self, own_information, normal_script=None, master_script=None):
        super().__init__()
        self.own_information = own_information
        self.normal_script = normal_script
        self.master_script = master_script

    def update(self, new_state):
        new_value = new_state[0]
        event = new_value.name
        if event == NEW_MASTER:
            if new_value == self.own_information:
                if self.master_script is not None:
                    os.system(self.master_script + "1")
            else:
                if self.normal_script is not None:
                    os.system(self.normal_script + "1")
