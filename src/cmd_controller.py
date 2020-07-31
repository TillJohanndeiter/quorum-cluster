"""
Provides cmd controller class which prints debug information and can handle
user input.
"""
from threading import Thread
from observer import Observer

from src.beans import node_information_from_json
from src.node_manger import NodeManger
from src.handshake import NEW_ENTERING_NODE
from src.vote_strategy import VOTE_FOR, NEW_MASTER, NO_MAJORITY_SHUTDOWN
from src.pinger import CONNECTION_LOST, INCOMING_MESSAGE
from src.message_dict import DEFAULT_MESSAGE, DISPATCH_MESSAGE, \
    JSON_SEPARATOR, HANDSHAKE_MESSAGE, MESSAGE_SEPARATOR


# TODO: Implement dispatching by enter :q

class CmdController(Observer):
    """
    Class which prints debug information and can handle user input.
    """

    def __init__(self, node_manager: NodeManger, debug: bool):
        super().__init__()
        self.node_manger = node_manager
        self.own_information = node_manager.own_information
        self.debug = debug

    def start_input_loop(self):
        """
        Start input and evaluate user input.
        :return: None
        """
        Thread(target=self.input_loop).start()
        print('Start input loop')

    def input_loop(self):
        running = True
        while running:
            name = input()
            if name == 'q':
                self.node_manger.dispatch()
                running = False

    def update(self, update_value):
        """
        React to notification from observer and print debug information
        :param update_value: notification from observed instance
        :return: None
        """
        if self.debug:
            update_value = update_value[0]
            event = update_value.name

            if event == VOTE_FOR:
                voted_for = update_value.value
                print('{} want {} as new master'.format(self.own_information.name, voted_for.name))
            elif event == NEW_ENTERING_NODE:
                node_info = update_value.value
                if node_info != self.own_information:
                    print('{} add {} to connected by broadcast. Now are {} nodes connected '.format(
                        self.own_information.name, node_info.name, len(self.node_manger.connected)))
            elif event == CONNECTION_LOST:
                lost_node = update_value.value
                print('{} lost connection from {}'.format(self.own_information.name, lost_node.name))
            elif event == NEW_MASTER:
                new_master = update_value.value
                print('{} set {} as new master'.format(self.own_information.name, new_master.name))

            elif event == NO_MAJORITY_SHUTDOWN:
                print('{} dispatching their is not majority'.format(self.own_information.name))
            elif event == INCOMING_MESSAGE:
                messages = str(update_value.value).split(MESSAGE_SEPARATOR)
                messages.sort(key=lambda x: x.startswith(HANDSHAKE_MESSAGE))
                for message in messages:
                    subject = message.split(JSON_SEPARATOR)[0]
                    if subject == DEFAULT_MESSAGE:
                        return

                    json = message.split(JSON_SEPARATOR)[1]
                    node_info = node_information_from_json(json)
                    if subject == DISPATCH_MESSAGE:
                        print('{} Dispatched from {}'.format(node_info.name, self.own_information.name))
                    elif subject == HANDSHAKE_MESSAGE:
                        if node_info != self.own_information:
                            print('{} add {} to connected by broadcast. '
                                  'Now are {} nodes connected '.format(self.own_information.name,
                                                                       node_info.name,
                                                                       len(self.node_manger.connected)))

