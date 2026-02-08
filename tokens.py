"""
Tokens para o Analisador Léxico
"""

from enum import Enum, auto


class TokenType(Enum):

    PHP_OPEN = auto()
    PHP_CLOSE = auto()
    FUNCTION = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    ECHO = auto()
    FLOATVAL = auto()
    READLINE = auto()
    PHP_EOL = auto()

    IDENTIFIER = auto()
    VARIABLE = auto()
    NUMBER = auto()

    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()

    EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    LESS = auto()

    ASSIGN = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    DOLLAR = auto()

    EOF = auto()
    ERROR = auto()


class Token:
    """Representa um token identificado pelo analisador léxico"""
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"

    def __str__(self):
        return f"{self.type.name:20} | {str(self.value):15} | Linha {self.line:3} | Coluna {self.column:3}"


KEYWORDS = {
    'function': TokenType.FUNCTION,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'echo': TokenType.ECHO,
    'floatval': TokenType.FLOATVAL,
    'readline': TokenType.READLINE,
    'PHP_EOL': TokenType.PHP_EOL,
}


def is_keyword(identifier):
    """
    Verifica se um identificador é uma palavra-chave
    """
    return KEYWORDS.get(identifier, None)
