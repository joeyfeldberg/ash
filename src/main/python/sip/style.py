from pygments.token import Token, Keyword, Name, Comment, String, Operator, Number
from pygments.styles import get_style_by_name, get_all_styles
from prompt_toolkit.styles import DEFAULT_STYLE_EXTENSIONS, style_from_dict
from prompt_toolkit.utils import is_windows, is_conemu_ansi


style = {
        # Classic prompt.
        Token.Prompt:                                 'bold',
        Token.Prompt.Dots:                            'noinherit',

        # Separator between windows. (Used above docstring.)
        Token.Separator:                              '#bbbbbb',

        # Search toolbar.
        Token.Toolbar.Search:                         '#22aaaa noinherit',
        Token.Toolbar.Search.Text:                    'noinherit',

        # System toolbar
        Token.Toolbar.System:                         '#22aaaa noinherit',

        # Status toolbar.
        Token.Toolbar.Status:                         'bg:#222222 #aaaaaa',
        Token.Toolbar.Status.Title:                   '#FFB269 underline',
        Token.Toolbar.Status.Key:                     'bg:#000000 #888888',

        Token.Resouce.Border:                         '#ABB2BF',
        Token.Resouce.Title:                          '#FFB269',
        Token.Resouce.Running:                        '#98C379',
        Token.Resouce.Stopped:                        '#E06C75',
}
