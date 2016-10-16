from prompt_toolkit.layout.controls import UIControl, UIContent, _ProcessedLine
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.layout.processors import Processor
from prompt_toolkit.layout.lexers import Lexer
from prompt_toolkit.layout.screen import Char, Point
from prompt_toolkit.filters import to_cli_filter
from prompt_toolkit.cache import SimpleCache


class TableControl(UIControl):
    """
    Control for visualising the content of a Table.

    :param input_processors: list of :class:`~prompt_toolkit.layout.processors.Processor`.
    :param lexer: :class:`~prompt_toolkit.layout.lexers.Lexer` instance for syntax highlighting.
    :param buffer_name: String representing the name of the buffer to display.
    :param default_char: :class:`.Char` instance to use to fill the background. This is
        transparent by default.
    :param focus_on_click: Focus this buffer when it's click, but not yet focussed.
    """
    def __init__(self,
                 buffer_name=DEFAULT_BUFFER,
                 input_processors=None,
                 lexer=None,
                 default_char=None,
                 focus_on_click=False):
        assert input_processors is None or all(isinstance(i, Processor) for i in input_processors)
        assert lexer is None or isinstance(lexer, Lexer)
        assert default_char is None or isinstance(default_char, Char)

        self.focus_on_click = to_cli_filter(focus_on_click)

        self.input_processors = input_processors or []
        self.buffer_name = buffer_name
        self.lexer = lexer or SimpleLexer()
        self.default_char = default_char or Char(token=Token.Transparent)

        #: Cache for the lexer.
        #: Often, due to cursor movement, undo/redo and window resizing
        #: operations, it happens that a short time, the same document has to be
        #: lexed. This is a faily easy way to cache such an expensive operation.
        self._token_cache = SimpleCache(maxsize=8)

        self._xy_to_cursor_position = None
        self._last_click_timestamp = None
        self._last_get_processed_line = None

    def _buffer(self, cli):
        """
        The buffer object that contains the 'main' content.
        """
        return cli.buffers[self.buffer_name]

    def has_focus(self, cli):
        # This control gets the focussed if the actual `Buffer` instance has the
        # focus or when any of the `InputProcessor` classes tells us that it
        # wants the focus. (E.g. in case of a reverse-search, where the actual
        # search buffer may not be displayed, but the "reverse-i-search" text
        # should get the focus.)
        return cli.current_buffer_name == self.buffer_name or \
            any(i.has_focus(cli) for i in self.input_processors)

    def preferred_width(self, cli, max_available_width):
        """
        This should return the preferred width.

        Note: We don't specify a preferred width according to the content,
              because it would be too expensive. Calculating the preferred
              width can be done by calculating the longest line, but this would
              require applying all the processors to each line. This is
              unfeasible for a larger document, and doing it for small
              documents only would result in inconsistent behaviour.
        """
        return None

    def preferred_height(self, cli, width, max_available_height, wrap_lines):
        # Calculate the content height, if it was drawn on a screen with the
        # given width.
        height = 0
        content = self.create_content(cli, width, None)

        # When line wrapping is off, the height should be equal to the amount
        # of lines.
        if not wrap_lines:
            return content.line_count

        # When the number of lines exceeds the max_available_height, just
        # return max_available_height. No need to calculate anything.
        if content.line_count >= max_available_height:
            return max_available_height

        for i in range(content.line_count):
            height += content.get_height_for_line(i, width)

            if height >= max_available_height:
                return max_available_height

        return height

    def _get_tokens_for_line_func(self, cli, document):
        """
        Create a function that returns the tokens for a given line.
        """
        # Cache using `document.text`.
        def get_tokens_for_line():
            return self.lexer.lex_document(cli, document)

        return self._token_cache.get(document.text, get_tokens_for_line)

    def _create_get_processed_line_func(self, cli, document):
        """
        Create a function that takes a line number of the current document and
        returns a _ProcessedLine(processed_tokens, source_to_display, display_to_source)
        tuple.
        """
        def transform(lineno, tokens):
            " Transform the tokens for a given line number. "
            source_to_display_functions = []
            display_to_source_functions = []

            # Get cursor position at this line.
            if document.cursor_position_row == lineno:
                cursor_column = document.cursor_position_col
            else:
                cursor_column = None

            def source_to_display(i):
                """ Translate x position from the buffer to the x position in the
                processed token list. """
                for f in source_to_display_functions:
                    i = f(i)
                return i

            # Apply each processor.
            for p in self.input_processors:
                transformation = p.apply_transformation(
                    cli, document, lineno, source_to_display, tokens)
                tokens = transformation.tokens

                if cursor_column:
                    cursor_column = transformation.source_to_display(cursor_column)

                display_to_source_functions.append(transformation.display_to_source)
                source_to_display_functions.append(transformation.source_to_display)

            def display_to_source(i):
                for f in reversed(display_to_source_functions):
                    i = f(i)
                return i

            return _ProcessedLine(tokens, source_to_display, display_to_source)

        def create_func():
            get_line = self._get_tokens_for_line_func(cli, document)
            cache = {}

            def get_processed_line(i):
                try:
                    return cache[i]
                except KeyError:
                    processed_line = transform(i, get_line(i))
                    cache[i] = processed_line
                    return processed_line
            return get_processed_line

        return create_func()

    def create_content(self, cli, width, height):
        """
        Create a UIContent.
        """
        buffer = self._buffer(cli)
        document = buffer.document

        get_processed_line = self._create_get_processed_line_func(cli, document)
        self._last_get_processed_line = get_processed_line

        def translate_rowcol(row, col):
            " Return the content column for this coordinate. "
            return Point(y=row, x=get_processed_line(row).source_to_display(col))

        def get_line(i):
            " Return the tokens for a given line number. "
            tokens = get_processed_line(i).tokens

            # Add a space at the end, because that is a possible cursor
            # position. (When inserting after the input.) We should do this on
            # all the lines, not just the line containing the cursor. (Because
            # otherwise, line wrapping/scrolling could change when moving the
            # cursor around.)
            tokens = tokens + [(self.default_char.token, ' ')]
            return tokens

        content = UIContent(
            get_line=get_line,
            line_count=document.line_count,
            cursor_position=translate_rowcol(document.cursor_position_row,
                                             document.cursor_position_col),
            default_char=self.default_char)

        return content

    def mouse_handler(self, cli, mouse_event):
        """
        Mouse handler for this control.
        """
        buffer = self._buffer(cli)
        position = mouse_event.position

        # Focus buffer when clicked.
        if self.has_focus(cli):
            if self._last_get_processed_line:
                processed_line = self._last_get_processed_line(position.y)

                # Translate coordinates back to the cursor position of the
                # original input.
                xpos = processed_line.display_to_source(position.x)
                index = buffer.document.translate_row_col_to_index(position.y, xpos)

                # Set the cursor position.
                if mouse_event.event_type == MouseEventType.MOUSE_DOWN:
                    buffer.exit_selection()
                    buffer.cursor_position = index

                elif mouse_event.event_type == MouseEventType.MOUSE_UP:
                    # When the cursor was moved to another place, select the text.
                    # (The >1 is actually a small but acceptable workaround for
                    # selecting text in Vi navigation mode. In navigation mode,
                    # the cursor can never be after the text, so the cursor
                    # will be repositioned automatically.)
                    if abs(buffer.cursor_position - index) > 1:
                        buffer.start_selection(selection_type=SelectionType.CHARACTERS)
                        buffer.cursor_position = index

                    # Select word around cursor on double click.
                    # Two MOUSE_UP events in a short timespan are considered a double click.
                    double_click = self._last_click_timestamp and time.time() - self._last_click_timestamp < .3
                    self._last_click_timestamp = time.time()

                    if double_click:
                        start, end = buffer.document.find_boundaries_of_current_word()
                        buffer.cursor_position += start
                        buffer.start_selection(selection_type=SelectionType.CHARACTERS)
                        buffer.cursor_position += end - start
                else:
                    # Don't handle scroll events here.
                    return NotImplemented

        # Not focussed, but focussing on click events.
        else:
            if self.focus_on_click(cli) and mouse_event.event_type == MouseEventType.MOUSE_UP:
                # Focus happens on mouseup. (If we did this on mousedown, the
                # up event will be received at the point where this widget is
                # focussed and be handled anyway.)
                cli.focus(self.buffer_name)
            else:
                return NotImplemented

    def move_cursor_down(self, cli):
        b = self._buffer(cli)
        b.cursor_position += b.document.get_cursor_down_position()

    def move_cursor_up(self, cli):
        b = self._buffer(cli)
        b.cursor_position += b.document.get_cursor_up_position()
