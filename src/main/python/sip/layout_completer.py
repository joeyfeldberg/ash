from prompt_toolkit.layout.containers import ConditionalContainer, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, TokenListControl
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.layout.containers import Float
from prompt_toolkit.filters.cli import HasFocus
from pygments.token import Token

def completion_bar():
    return Float(
        bottom=1,
        left=3,
        content=ConditionalContainer(
            VSplit([
                Window(
                    content=TokenListControl(get_tokens=lambda _: [(Token.Toolbar.Search, "Filter: ")])
                ),
                Window(
                    content=BufferControl(
                        buffer_name='SEARCH_BUFFER'
                    ),
                    width=LayoutDimension(min=30),
                    height=LayoutDimension.exact(1),
                    dont_extend_width=True,
                )
            ]),
            filter=HasFocus('SEARCH_BUFFER')
        )
    )
