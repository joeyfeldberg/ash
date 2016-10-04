from pygments.lexer import RegexLexer
from pygments.token import Token

class EC2Lexer(RegexLexer):
    name = 'EC2'
    T = Token.Resouce

    tokens = {
        'root': [
            (r'running', T.Running),
            (r'stopped', T.Stopped)
        ]
    }
