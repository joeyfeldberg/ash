from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.filters.cli import HasFocus
from prompt_toolkit.filters import Condition
from prompt_toolkit.document import Document
from prompt_toolkit.keys import Keys
from prompt_toolkit.selection import SelectionState, SelectionType
from prompt_toolkit.buffer import Buffer


class KeyBindings():
    def __init__(self, ash_cli):
        self.selection_mode = False
        self.ash_cli = ash_cli
        self.inventory = ash_cli.inventory

        manager = KeyBindingManager(
            enable_extra_page_navigation=True)
        handle = manager.registry.add_binding
        self.add_bindings(handle)
        self.registry = manager.registry
        self.settings = ash_cli.settings

    def add_bindings(self, handle):
        search_empty = Condition(lambda cli: len(cli.buffers["SEARCH_BUFFER"].text) <= 0 )
        shift_down = Condition(lambda cli: self.selection_mode )

        @handle(Keys.Escape, eager=True)
        @handle(Keys.ControlC, eager=True)
        @handle(Keys.ControlD, eager=True)
        @handle(Keys.ControlQ, eager=True)
        def _(event):
            event.cli.set_return_value(None)
        @handle(Keys.Backspace, filter=HasFocus("RESOURCES_BUFFER") & ~search_empty)
        @handle(Keys.Any, filter=HasFocus("RESOURCES_BUFFER"))
        def _(event):
            resouces_buffer = event.cli.current_buffer
            event.cli.push_focus("SEARCH_BUFFER")
            if event.key_sequence[0].key == Keys.Backspace:
                event.cli.current_buffer.delete_before_cursor(1)
            else:
                event.cli.current_buffer.insert_text(event.data)

        @handle(Keys.Backspace, filter=HasFocus("SEARCH_BUFFER") & search_empty)
        @handle(Keys.Down, filter=HasFocus("SEARCH_BUFFER"))
        @handle(Keys.Up, filter=HasFocus("SEARCH_BUFFER"))
        @handle(Keys.Enter, filter=HasFocus("SEARCH_BUFFER"))
        def _(event):
            event.cli.pop_focus()

        @handle(Keys.F9)
        def _(event):
            def done():
                self.ash_cli.window.refresh_resource_buffer()
                self.ash_cli.cli.request_redraw()
            self.ash_cli.cli.buffers["RESOURCES_BUFFER"].reset()
            self.ash_cli.inventory.refresh(done)

        @handle(Keys.F2)
        def _(event):
            self.selection_mode = True
            buf = event.cli.buffers["RESOURCES_BUFFER"]
            buf.cursor_position = 0
            
            pos = buf.document.get_end_of_document_position()
            buf.selection_state = SelectionState(
                original_cursor_position=0,
                type=SelectionType.LINES
            )

            buf.cursor_position = pos

        @handle(Keys.Any, filter=shift_down)
        @handle(Keys.Up, filter=shift_down)
        @handle(Keys.Down, filter=shift_down)
        def _(event):
            self.selection_mode = False
            buf = event.cli.buffers["RESOURCES_BUFFER"]
            buf.selection_state = None
            if event.key_sequence[0].key == Keys.Down:
                buf.auto_down()
            elif event.key_sequence[0].key == Keys.Up:
                buf.auto_up()

        @handle(Keys.ShiftDown)
        @handle(Keys.ShiftUp)
        def _(event):
            self.selection_mode = True
            buf = event.cli.buffers["RESOURCES_BUFFER"]
            if buf.selection_state == None:
                buf.selection_state = SelectionState(
                    original_cursor_position=buf.cursor_position,
                    type=SelectionType.LINES
                )

            if event.key_sequence[0].key == Keys.ShiftDown:
                buf.auto_down()
            else:
                buf.auto_up()

        @handle(Keys.Enter, filter=HasFocus("SEARCH_BUFFER"))
        def _(event):
            buf = event.cli.buffers["RESOURCES_BUFFER"]
            buf.accept_action.validate_and_handle(event.cli, buf)
