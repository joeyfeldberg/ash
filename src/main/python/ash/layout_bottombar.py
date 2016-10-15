from prompt_toolkit.layout.toolbars import TokenListToolbar
from prompt_toolkit.layout.screen import Char
from pygments.token import Token


def bottombar(inventory):
    TB = Token.Toolbar.Status

    def get_tokens(cli):

        tokens = [
            (TB.Key, '[Esc]'),
            (TB, ' Exit '),
            (TB.Key, '[Enter]'),
            (TB, ' SSH '),
            (TB.Key, '[F2]'),
            (TB, ' Select All '),
            (TB.Key, '[F9]'),
        ]

        if inventory.status == "refreshing":
            tokens.append((TB, ' Refreshing.. '))
        else:
            tokens.append((TB, ' Refresh '))

        return tokens

    return TokenListToolbar(
        get_tokens=get_tokens,
        default_char=Char(token=TB)
    )
