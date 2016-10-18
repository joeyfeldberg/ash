from prompt_toolkit.layout.controls import UIControl, UIContent, _ProcessedLine
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.layout.processors import Processor
from prompt_toolkit.layout.lexers import Lexer
from prompt_toolkit.layout.screen import Char, Point
from prompt_toolkit.layout.utils import split_lines
from prompt_toolkit.filters import to_cli_filter
from prompt_toolkit.cache import SimpleCache
from pygments.token import Token


class TableControl(UIControl):
    """
    :param get_table_tokens: Callable that takes a `CommandLineInterface` instance
        and returns the dict where keys are titles and values are lists of (Token, text)
        tuples to be displayed right now.
    :param default_char: default :class:`.Char` (character and Token) to use
        for the background when there is more space available than `get_table_tokens`
        returns.
    :param get_default_char: Like `default_char`, but this is a callable that
        takes a :class:`prompt_toolkit.interface.CommandLineInterface` and
        returns a :class:`.Char` instance.
    :param has_focus: `bool` or `CLIFilter`, when this evaluates to `True`,
        this UI control will take the focus. The cursor will be shown in the
        upper left corner of this control, unless `get_token` returns a
        ``Token.SetCursorPosition`` token somewhere in the token list, then the
        cursor will be shown there.
    """
    def __init__(self, get_table_tokens, default_char=None, get_default_char=None,
                 align_right=False, align_center=False, has_focus=False):
        assert callable(get_table_tokens)
        assert default_char is None or isinstance(default_char, Char)
        assert get_default_char is None or callable(get_default_char)
        assert not (default_char and get_default_char)

        self.align_right = to_cli_filter(align_right)
        self.align_center = to_cli_filter(align_center)
        self._has_focus_filter = to_cli_filter(has_focus)

        self.get_table_tokens = get_table_tokens

        # Construct `get_default_char` callable.
        if default_char:
            get_default_char = lambda _: default_char
        elif not get_default_char:
            get_default_char = lambda _: Char(' ', Token.Transparent)

        self.get_default_char = get_default_char

        #: Cache for the content.
        self._content_cache = SimpleCache(maxsize=18)
        self._token_cache = SimpleCache(maxsize=1)
            # Only cache one token list. We don't need the previous item.

        # Render info for the mouse support.
        self._tokens = None

    def reset(self):
        self._tokens = None

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.get_table_tokens)

    def _get_table_tokens_cached(self, cli):
        """
        Get tokens, but only retrieve tokens once during one render run.
        (This function is called several times during one rendering, because
        we also need those for calculating the dimensions.)
        """
        return self._token_cache.get(
            cli.render_counter, lambda: self.get_table_tokens(cli))

    def has_focus(self, cli):
        return self._has_focus_filter(cli)

    def preferred_width(self, cli, max_available_width):
        """
        Return the preferred width for this control.
        That is the width of the longest line.
        """
        text = token_list_to_text(self._get_table_tokens_cached(cli))
        line_lengths = [get_cwidth(l) for l in text.split('\n')]
        return max(line_lengths)

    def preferred_height(self, cli, width, max_available_height, wrap_lines):
        content = self.create_content(cli, width, None)
        return content.line_count

    def create_content(self, cli, width, height):
        # Get tokens
        tokens_with_mouse_handlers = self._get_table_tokens_cached(cli)

        default_char = self.get_default_char(cli)

        # Wrap/align right/center parameters.
        right = self.align_right(cli)
        center = self.align_center(cli)

        def process_line(line):
            " Center or right align a single line. "
            used_width = token_list_width(line)
            padding = width - used_width
            if center:
                padding = int(padding / 2)
            return [(default_char.token, default_char.char * padding)] + line

        if right or center:
            token_lines_with_mouse_handlers = []

            for line in split_lines(tokens_with_mouse_handlers):
                token_lines_with_mouse_handlers.append(process_line(line))
        else:
            token_lines_with_mouse_handlers = list(split_lines(tokens_with_mouse_handlers))

        # Strip mouse handlers from tokens.
        token_lines = [
            [tuple(item[:2]) for item in line] for line in token_lines_with_mouse_handlers
        ]

        # Keep track of the tokens with mouse handler, for later use in
        # `mouse_handler`.
        self._tokens = tokens_with_mouse_handlers

        # If there is a `Token.SetCursorPosition` in the token list, set the
        # cursor position here.
        def get_cursor_position():
            SetCursorPosition = Token.SetCursorPosition

            for y, line in enumerate(token_lines):
                x = 0
                for token, text in line:
                    if token == SetCursorPosition:
                        return Point(x=x, y=y)
                    x += len(text)
            return None

        # Create content, or take it from the cache.
        key = (default_char.char, default_char.token,
                tuple(tokens_with_mouse_handlers), width, right, center)

        def get_content():
            return UIContent(get_line=lambda i: token_lines[i],
                             line_count=len(token_lines),
                             default_char=default_char,
                             cursor_position=get_cursor_position())

        return self._content_cache.get(key, get_content)

    @classmethod
    def static(cls, tokens):
        def get_static_tokens(cli):
            return tokens
        return cls(get_static_tokens)

    def mouse_handler(self, cli, mouse_event):
        """
        Handle mouse events.

        (When the token list contained mouse handlers and the user clicked on
        on any of these, the matching handler is called. This handler can still
        return `NotImplemented` in case we want the `Window` to handle this
        particular event.)
        """
        if self._tokens:
            # Read the generator.
            tokens_for_line = list(split_lines(self._tokens))

            try:
                tokens = tokens_for_line[mouse_event.position.y]
            except IndexError:
                return NotImplemented
            else:
                # Find position in the token list.
                xpos = mouse_event.position.x

                # Find mouse handler for this character.
                count = 0
                for item in tokens:
                    count += len(item[1])
                    if count >= xpos:
                        if len(item) >= 3:
                            # Handler found. Call it.
                            # (Handler can return NotImplemented, so return
                            # that result.)
                            handler = item[2]
                            return handler(cli, mouse_event)
                        else:
                            break

        # Otherwise, don't handle here.
        return NotImplemented
