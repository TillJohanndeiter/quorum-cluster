from observer import Observer
from src.node_manger import NodeManger


class CmdController(Observer):

    def __init__(self, node_manager: NodeManger):
        super().__init__()
        self.node_manger = node_manager

    def start_input_loop(self):
        running = True
        while running:
            pass