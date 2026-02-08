"""
Analisador Léxico (Lexer) para LALG-PHP
Compilador LALG-PHP
"""

from tokens import Token, TokenType, is_keyword


class LexerError(Exception):
    pass


class Lexer:

    def __init__(self, source_code):

        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.current_char = self.source_code[0] if source_code else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        self.position += 1
        if self.position < len(self.source_code):
            self.current_char = self.source_code[self.position]
        else:
            self.current_char = None

    def peek(self, offset=1):
        peek_pos = self.position + offset
        if peek_pos < len(self.source_code):
            return self.source_code[peek_pos]
        return None

    def skip_whitespace(self):
        while self.current_char and self.current_char in ' \t\n\r':
            self.advance()

    def skip_comment(self): # This function handles block comments /* ... */
        self.advance() # Consume '/'
        self.advance() # Consume '*'

        while self.current_char:
            if self.current_char == '*' and self.peek() == '/':
                self.advance() # Consume '*'
                self.advance() # Consume '/'
                return
            self.advance()

        raise LexerError(f"Comentário não fechado na linha {self.line}")

    def skip_line_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()

    def read_number(self):
        num_str = ''
        has_dot = False

        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot:
                    raise LexerError(f"Número com múltiplos pontos na linha {self.line}, coluna {self.column}")
                has_dot = True
            num_str += self.current_char
            self.advance()

        return num_str

    def read_identifier(self):
        ident_str = ''

        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            ident_str += self.current_char
            self.advance()

        return ident_str

    def read_variable(self):
        var_str = '$'
        self.advance()

        if not self.current_char or not (self.current_char.isalpha() or self.current_char == '_'):
            raise LexerError(f"Variável inválida na linha {self.line}, coluna {self.column}")

        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            var_str += self.current_char
            self.advance()

        return var_str

    def get_next_token(self):
        while self.current_char:
            # Pula espaços em branco
            if self.current_char in ' \t\n\r':
                self.skip_whitespace()
                continue

            # Comentário de bloco /* ... */
            if self.current_char == '/' and self.peek() == '*':
                self.skip_comment()
                continue

            # Comentário de linha // ...
            if self.current_char == '/' and self.peek() == '/':
                self.skip_line_comment()
                continue

            token_line = self.line
            token_column = self.column

            # Números (inteiros e decimais)
            if self.current_char.isdigit():
                number = self.read_number()
                return Token(TokenType.NUMBER, float(number), self.line, self.column - len(number))

            # Variáveis $nome
            if self.current_char == '$':
                var = self.read_variable()
                return Token(TokenType.VARIABLE, var, self.line, self.column - len(var))

            # Identificadores e palavras-chave
            if self.current_char.isalpha() or self.current_char == '_':
                ident = self.read_identifier()

                keyword_type = is_keyword(ident)
                if keyword_type:
                    return Token(keyword_type, ident, self.line, self.column - len(ident))
                else:
                    return Token(TokenType.IDENTIFIER, ident, self.line, self.column - len(ident))

            # Tag de abertura <?php
            if self.current_char == '<':
                if self.peek() == '?':
                    if (self.peek(2) == 'p' and self.peek(3) == 'h' and
                        self.peek(4) == 'p' and
                        (self.peek(5) is None or not self.peek(5).isalnum())):
                        value = '<?php'
                        for _ in range(5):
                            self.advance()
                        return Token(TokenType.PHP_OPEN, value, token_line, token_column)
                # Operador menor ou igual <=
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', token_line, token_column)
                # Operador menor <
                char = self.current_char
                self.advance()
                return Token(TokenType.LESS, char, token_line, token_column)

            # Operador maior ou igual >=
            if self.current_char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', token_line, token_column)
                # Operador maior >
                char = self.current_char
                self.advance()
                return Token(TokenType.GREATER, char, token_line, token_column)

            # Operador de atribuição = ou Operador de igualdade ==
            if self.current_char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.EQUAL, '==', token_line, token_column)
                char = self.current_char
                self.advance()
                return Token(TokenType.ASSIGN, char, token_line, token_column)

            # Operador diferente !=
            if self.current_char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', token_line, token_column)
                raise LexerError(f"Caractere inesperado '!' na linha {self.line}, coluna {self.column}")

            # Tag de fechamento ?>
            if self.current_char == '?':
                if self.peek() == '>':
                    self.advance()
                    self.advance()
                    return Token(TokenType.PHP_CLOSE, '?>', self.line, self.column - 2)
                raise LexerError(f"Caractere inesperado '?' na linha {self.line}, coluna {self.column}")

            # Operador de adição +
            if self.current_char == '+':
                char = self.current_char
                self.advance()
                return Token(TokenType.PLUS, char, token_line, token_column)

            # Operador de subtração -
            if self.current_char == '-':
                char = self.current_char
                self.advance()
                return Token(TokenType.MINUS, char, token_line, token_column)

            # Operador de multiplicação *
            if self.current_char == '*':
                char = self.current_char
                self.advance()
                return Token(TokenType.MULTIPLY, char, token_line, token_column)

            # Operador de divisão /
            if self.current_char == '/':
                char = self.current_char
                self.advance()
                return Token(TokenType.DIVIDE, char, token_line, token_column)

            # Parêntese esquerdo (
            if self.current_char == '(':
                char = self.current_char
                self.advance()
                return Token(TokenType.LPAREN, char, token_line, token_column)

            # Parêntese direito )
            if self.current_char == ')':
                char = self.current_char
                self.advance()
                return Token(TokenType.RPAREN, char, token_line, token_column)

            # Chave esquerda {
            if self.current_char == '{':
                char = self.current_char
                self.advance()
                return Token(TokenType.LBRACE, char, token_line, token_column)

            # Chave direita }
            if self.current_char == '}':
                char = self.current_char
                self.advance()
                return Token(TokenType.RBRACE, char, token_line, token_column)

            # Ponto e vírgula ;
            if self.current_char == ';':
                char = self.current_char
                self.advance()
                return Token(TokenType.SEMICOLON, char, token_line, token_column)

            # Vírgula ,
            if self.current_char == ',':
                char = self.current_char
                self.advance()
                return Token(TokenType.COMMA, char, token_line, token_column)

            # Operador de concatenação .
            if self.current_char == '.':
                char = self.current_char
                self.advance()
                return Token(TokenType.DOT, char, token_line, token_column)

            raise LexerError(f"Caractere inválido '{self.current_char}' na linha {self.line}, coluna {self.column}")

        return Token(TokenType.EOF, '', self.line, self.column)

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
