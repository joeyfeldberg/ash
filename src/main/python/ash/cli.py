from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.buffer_mapping import BufferMapping
from prompt_toolkit.application import Application
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.buffer import AcceptAction

from ash.style import style
from ash.inventory import Inventory
from ash.ec2_providor import EC2Providor
from ash.key_bindings import KeyBindings
from ash.layout import ResourceWindow


class ashCLI():
    def __init__(self, settings, eventloop):
        self.eventloop = eventloop
        self.inventory = Inventory(EC2Providor(), self)
        self.settings = settings
        self.bindings = KeyBindings(self)

    def create_application(self):
        self.window = ResourceWindow(self)
        application = Application(
            key_bindings_registry=self.bindings.registry,
            layout=self.window.get_layout(),
            style=style_from_dict(style),
            use_alternate_screen=True,
            buffers=BufferMapping(
                self._create_buffers(),
                initial="RESOURCES_BUFFER"
            )
        )

        self.cli = CommandLineInterface(application=application, eventloop=self.eventloop)
        self.window.refresh_resource_buffer()
        return self.cli

    def _create_buffers(self):

        resouces_buffer = Buffer(
            accept_action=AcceptAction(lambda cli, buffer: cli.set_return_value(buffer))
        )

        search_buffer = Buffer(
            on_text_changed=lambda b: self.window.refresh_resource_buffer(b.text)
        )

        return {"RESOURCES_BUFFER": resouces_buffer,
                "SEARCH_BUFFER": search_buffer}
