"""
Analisador Sintático (Parser) ASCENDENTE para LALG-PHP
Compilador LALG-PHP

Algoritmo:
1. SHIFT: Empilha próximo token da entrada
2. REDUCE: Aplica regra de produção quando encontra padrão na pilha
3. ACCEPT: Programa analisado com sucesso
4. ERROR: Erro sintático detectado

"""

from tokens import Token, TokenType
from ast_nodes import *


class ParserError(Exception):
    pass


class ShiftReduceParser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.stack = []

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def shift(self):
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.stack.append(token)
            self.position += 1
            return True
        return False

    def peek_stack(self, count):
        """
        Olha os últimos N elementos da pilha sem removê-los
        """
        if len(self.stack) < count:
            return None
        return self.stack[-count:]

    def reduce(self, count, node):
        """
        REDUCE: Remove N elementos da pilha e empilha um nó AST
        """
        for _ in range(count):
            self.stack.pop()
        self.stack.append(node)

    def try_reduce(self):
        """
        Tenta aplicar uma regra de redução
        Verifica padrões na pilha e aplica a regra correspondente.
        """

        # Regra: NUMBER -> NumberNode
        if len(self.stack) >= 1:
            top = self.stack[-1]
            if isinstance(top, Token) and top.type == TokenType.NUMBER:
                node = NumberNode(top.value, top.line, top.column)
                self.reduce(1, node)
                return True

        # Regra: VARIABLE -> VariableNode
        if len(self.stack) >= 1:
            top = self.stack[-1]
            if isinstance(top, Token) and top.type == TokenType.VARIABLE:
                node = VariableNode(top.value, top.line, top.column)
                self.reduce(1, node)
                return True

        # Regra: PHP_EOL -> PhpEolNode
        if len(self.stack) >= 1:
            top = self.stack[-1]
            if isinstance(top, Token) and top.type == TokenType.PHP_EOL:
                node = PhpEolNode(top.line, top.column)
                self.reduce(1, node)
                return True

        # Regra: floatval(readline()) -> ReadlineNode
        if len(self.stack) >= 6:
            pattern = self.peek_stack(6)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.FLOATVAL and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.LPAREN and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.READLINE and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.LPAREN and
                isinstance(pattern[4], Token) and pattern[4].type == TokenType.RPAREN and
                isinstance(pattern[5], Token) and pattern[5].type == TokenType.RPAREN):
                node = ReadlineNode(pattern[0].line, pattern[0].column)
                self.reduce(6, node)
                return True


        # Regra: if (expr) { stmts } else { stmts } -> IfNode
        if len(self.stack) >= 11:
            pattern = self.peek_stack(11)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.IF and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.LPAREN and
                self._is_expression(pattern[2]) and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.RPAREN and
                isinstance(pattern[4], Token) and pattern[4].type == TokenType.LBRACE and
                isinstance(pattern[5], list) and
                isinstance(pattern[6], Token) and pattern[6].type == TokenType.RBRACE and
                isinstance(pattern[7], Token) and pattern[7].type == TokenType.ELSE and
                isinstance(pattern[8], Token) and pattern[8].type == TokenType.LBRACE and
                isinstance(pattern[9], list) and
                isinstance(pattern[10], Token) and pattern[10].type == TokenType.RBRACE):
                node = IfNode(pattern[2], pattern[5], pattern[9], pattern[0].line, pattern[0].column)
                self.reduce(11, node)
                return True


        # Regra: if (expr) { stmts } -> IfNode (sem else)
        if len(self.stack) >= 7:
            pattern = self.peek_stack(7)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.IF and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.LPAREN and
                self._is_expression(pattern[2]) and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.RPAREN and
                isinstance(pattern[4], Token) and pattern[4].type == TokenType.LBRACE and
                isinstance(pattern[5], list) and
                isinstance(pattern[6], Token) and pattern[6].type == TokenType.RBRACE):
                next_token = self.current_token()
                if not (next_token and next_token.type == TokenType.ELSE):
                    node = IfNode(pattern[2], pattern[5], None, pattern[0].line, pattern[0].column)
                    self.reduce(7, node)
                    return True

        # Regra: while (expr) { stmts } -> WhileNode
        if len(self.stack) >= 7:
            pattern = self.peek_stack(7)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.WHILE and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.LPAREN and
                self._is_expression(pattern[2]) and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.RPAREN and
                isinstance(pattern[4], Token) and pattern[4].type == TokenType.LBRACE and
                isinstance(pattern[5], list) and
                isinstance(pattern[6], Token) and pattern[6].type == TokenType.RBRACE):
                node = WhileNode(pattern[2], pattern[5], pattern[0].line, pattern[0].column)
                self.reduce(7, node)
                return True

        # Regra: (expr) -> expr (remove parênteses desnecessários)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.LPAREN and
                self._is_expression(pattern[1]) and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.RPAREN):
                if len(self.stack) < 4 or not (isinstance(self.stack[-4], Token) and
                                               self.stack[-4].type in (TokenType.IF, TokenType.WHILE)):
                    expr = pattern[1]
                    self.reduce(3, expr)
                    return True

        # Regra: - expr -> UnaryOpNode (negação unária)
        if len(self.stack) >= 2:
            pattern = self.peek_stack(2)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.MINUS and
                self._is_expression(pattern[1])):
                if len(self.stack) < 3 or not self._is_expression(self.stack[-3]):
                    node = UnaryOpNode(TokenType.MINUS, pattern[1], pattern[0].line, pattern[0].column)
                    self.reduce(2, node)
                    return True

        # Regra: function nome(params) { stmts } -> FunctionDeclNode
        if len(self.stack) >= 8:
            pattern = self.peek_stack(8)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.FUNCTION and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.IDENTIFIER and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.LPAREN and
                isinstance(pattern[4], Token) and pattern[4].type == TokenType.RPAREN and
                isinstance(pattern[5], Token) and pattern[5].type == TokenType.LBRACE and
                isinstance(pattern[6], list) and
                isinstance(pattern[7], Token) and pattern[7].type == TokenType.RBRACE):
                params = pattern[3] if isinstance(pattern[3], list) else []
                node = FunctionDeclNode(pattern[1].value, params, pattern[6], pattern[0].line, pattern[0].column)
                self.reduce(8, node)
                return True

        # Regra: function nome() { stmts } -> FunctionDeclNode (sem parâmetros)
        if len(self.stack) >= 7:
            pattern = self.peek_stack(7)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.FUNCTION and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.IDENTIFIER and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.LPAREN and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.RPAREN and
                isinstance(pattern[4], Token) and pattern[4].type == TokenType.LBRACE and
                isinstance(pattern[5], list) and
                isinstance(pattern[6], Token) and pattern[6].type == TokenType.RBRACE):
                node = FunctionDeclNode(pattern[1].value, [], pattern[5], pattern[0].line, pattern[0].column)
                self.reduce(7, node)
                return True

        # Regra: nome(args) -> FunctionCallNode (com argumentos)
        if len(self.stack) >= 4:
            pattern = self.peek_stack(4)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.IDENTIFIER and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.LPAREN and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.RPAREN):
                if len(self.stack) < 5 or not (isinstance(self.stack[-5], Token) and self.stack[-5].type == TokenType.FUNCTION):
                    if isinstance(pattern[2], list):
                        node = FunctionCallNode(pattern[0].value, pattern[2], pattern[0].line, pattern[0].column)
                        self.reduce(4, node)
                        return True

        # Regra: nome() -> FunctionCallNode (sem argumentos)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.IDENTIFIER and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.LPAREN and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.RPAREN):
                if len(self.stack) < 4 or not (isinstance(self.stack[-4], Token) and self.stack[-4].type == TokenType.FUNCTION):
                    node = FunctionCallNode(pattern[0].value, [], pattern[0].line, pattern[0].column)
                    self.reduce(3, node)
                    return True

        # Regra: expr -> [expr] (cria lista de argumentos)
        if len(self.stack) >= 1:
            top = self.stack[-1]
            next_token = self.current_token()
            if self._is_expression(top) and next_token:
                if next_token.type in (TokenType.COMMA, TokenType.RPAREN):
                    if not isinstance(top, list):
                        if len(self.stack) >= 3:
                            if (isinstance(self.stack[-3], Token) and
                                self.stack[-3].type == TokenType.IDENTIFIER and
                                isinstance(self.stack[-2], Token) and
                                self.stack[-2].type == TokenType.LPAREN):
                                args_list = [top]
                                self.reduce(1, args_list)
                                return True

        # Regra: [args], expr -> [args, expr] (adiciona argumento à lista)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], list) and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.COMMA and
                self._is_expression(pattern[2])):
                new_args = pattern[0] + [pattern[2]]
                self.reduce(3, new_args)
                return True

        # Regra: expr . expr -> ConcatenationNode (concatenação de strings)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (self._is_expression(pattern[0]) and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.DOT and
                self._is_expression(pattern[2])):
                node = ConcatenationNode(pattern[0], pattern[2], pattern[1].line, pattern[1].column)
                self.reduce(3, node)
                return True

        # Regra: expr OP expr -> BinaryOpNode (comparações: ==, !=, >, <, >=, <=)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (self._is_expression(pattern[0]) and
                isinstance(pattern[1], Token) and
                pattern[1].type in (TokenType.EQUAL, TokenType.NOT_EQUAL, TokenType.GREATER,
                                   TokenType.LESS, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL) and
                self._is_expression(pattern[2])):
                node = BinaryOpNode(pattern[1].type, pattern[0], pattern[2], pattern[1].line, pattern[1].column)
                self.reduce(3, node)
                return True


        # Regra: expr * expr | expr / expr -> BinaryOpNode (multiplicação e divisão)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (self._is_expression(pattern[0]) and
                isinstance(pattern[1], Token) and pattern[1].type in (TokenType.MULTIPLY, TokenType.DIVIDE) and
                self._is_expression(pattern[2])):
                node = BinaryOpNode(pattern[1].type, pattern[0], pattern[2], pattern[1].line, pattern[1].column)
                self.reduce(3, node)
                return True

        # Regra: expr + expr | expr - expr -> BinaryOpNode (adição e subtração)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (self._is_expression(pattern[0]) and
                isinstance(pattern[1], Token) and pattern[1].type in (TokenType.PLUS, TokenType.MINUS) and
                self._is_expression(pattern[2])):

                if len(self.stack) >= 4:
                    next_token = self.peek_stack(4)[3] if len(self.stack) > 3 else None
                    if isinstance(next_token, Token) and next_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
                        return False

                node = BinaryOpNode(pattern[1].type, pattern[0], pattern[2], pattern[1].line, pattern[1].column)
                self.reduce(3, node)
                return True


        # Regra: funcao(); -> FunctionCallNode (chamada como statement)
        if len(self.stack) >= 2:
            pattern = self.peek_stack(2)
            if (isinstance(pattern[0], FunctionCallNode) and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.SEMICOLON):
                self.reduce(2, pattern[0])
                return True

        # Regra: $var = expr; -> AssignmentNode
        if len(self.stack) >= 4:
            pattern = self.peek_stack(4)
            if (isinstance(pattern[0], VariableNode) and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.ASSIGN and
                self._is_expression(pattern[2]) and
                isinstance(pattern[3], Token) and pattern[3].type == TokenType.SEMICOLON):
                node = AssignmentNode(pattern[0], pattern[2], pattern[0].line, pattern[0].column)
                self.reduce(4, node)
                return True

        # Regra: echo expr; -> EchoNode
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.ECHO and
                self._is_expression(pattern[1]) and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.SEMICOLON):
                node = EchoNode(pattern[1], pattern[0].line, pattern[0].column)
                self.reduce(3, node)
                return True


        # Regra: { stmt -> [stmt] (inicia lista de comandos)
        if len(self.stack) >= 2:
            pattern = self.peek_stack(2)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.LBRACE and
                self._is_command(pattern[1])):
                commands_list = [pattern[1]]
                self.reduce(1, commands_list)
                return True

        # Regra: { [stmts] stmt -> { [stmts, stmt] (adiciona comando à lista)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.LBRACE and
                isinstance(pattern[1], list) and
                self._is_command(pattern[2])):
                if pattern[1] and self._is_command(pattern[1][0]):
                    new_commands = pattern[1] + [pattern[2]]
                    self.reduce(2, new_commands)
                    return True

        # Regra: { [stmts] ; -> { [stmts] (remove ponto e vírgula extra)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.LBRACE and
                isinstance(pattern[1], list) and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.SEMICOLON):
                if pattern[1] and self._is_command(pattern[1][0]):
                    self.stack.pop()
                    return True

        # Regra: <?php [decls] -> [decls] (remove <?php no início)
        if len(self.stack) >= 2:
            pattern = self.peek_stack(2)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.PHP_OPEN and
                isinstance(pattern[1], (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode))):
                next_token = self.current_token()
                if not (next_token and next_token.type == TokenType.SEMICOLON):
                    decls_list = [pattern[1]]
                    self.reduce(1, decls_list)
                    return True

        # Regra: <?php [decls] ; -> [decls] (remove <?php e ponto e vírgula extra)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.PHP_OPEN and
                isinstance(pattern[1], list) and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.SEMICOLON):
                if pattern[1] and isinstance(pattern[1][0], (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode)):
                    self.reduce(2, pattern[1])
                    return True

        # Regra: <?php [decls] stmt -> [decls, stmt] (adiciona declaração à lista)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.PHP_OPEN and
                isinstance(pattern[1], list) and
                isinstance(pattern[2], (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode))):
                if pattern[1] and isinstance(pattern[1][0], (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode)):
                    new_decls = pattern[1] + [pattern[2]]
                    self.reduce(2, new_decls)
                    return True

        # Regra: $var -> VariableNode (variável como expressão)
        if len(self.stack) >= 1:
            top = self.stack[-1]
            if isinstance(top, VariableNode):
                next_token = self.current_token()
                if next_token and next_token.type in (TokenType.COMMA, TokenType.RPAREN):
                    if len(self.stack) >= 2:
                        prev = self.stack[-2]
                        if isinstance(prev, Token) and prev.type == TokenType.LPAREN:
                            params_list = [top]
                            self.reduce(1, params_list)
                            return True

        # Regra: [params] , $var -> [params, $var] (adiciona parâmetro à lista)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], list) and
                isinstance(pattern[1], Token) and pattern[1].type == TokenType.COMMA and
                isinstance(pattern[2], VariableNode)):
                new_params = pattern[0] + [pattern[2]]
                self.reduce(3, new_params)
                return True

        # Regra: [decls] ?> -> [decls] (remove ?> no final)
        if len(self.stack) >= 1:
            top = self.stack[-1]
            if isinstance(top, (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode)):
                next_token = self.current_token()
                if next_token and next_token.type == TokenType.PHP_CLOSE:
                    if not isinstance(top, list):
                        decls_list = [top]
                        self.reduce(1, decls_list)
                        return True

        # Regra: [decls] stmt -> [decls, stmt] (adiciona declaração à lista)
        if len(self.stack) >= 2:
            pattern = self.peek_stack(2)
            if isinstance(pattern[0], list) and isinstance(pattern[1], (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode)):
                new_decls = pattern[0] + [pattern[1]]
                self.reduce(2, new_decls)
                return True

        # Regra: <?php [decls] ?> -> ProgramNode (programa completo)
        if len(self.stack) >= 3:
            pattern = self.peek_stack(3)
            if (isinstance(pattern[0], Token) and pattern[0].type == TokenType.PHP_OPEN and
                isinstance(pattern[1], list) and
                isinstance(pattern[2], Token) and pattern[2].type == TokenType.PHP_CLOSE):
                node = ProgramNode(pattern[1], pattern[0].line, pattern[0].column)
                self.reduce(3, node)
                return True

        return False

    def _is_expression(self, item):
        return isinstance(item, (NumberNode, VariableNode, BinaryOpNode, UnaryOpNode,
                                ConcatenationNode, ReadlineNode, PhpEolNode, FunctionCallNode))

    def _is_command(self, item):
        return isinstance(item, (AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode))

    def _next_is_command_start(self):
        next_token = self.current_token()
        if not next_token:
            return False
        return next_token.type in (TokenType.VARIABLE, TokenType.IF, TokenType.WHILE,
                                   TokenType.ECHO, TokenType.IDENTIFIER, TokenType.FUNCTION)

    def parse(self):
        if self.tokens and self.tokens[-1].type == TokenType.EOF:
            self.tokens = self.tokens[:-1]

        while True:
            reduced = True
            while reduced:
                reduced = self.try_reduce()

            if self.position >= len(self.tokens):
                if len(self.stack) == 1 and isinstance(self.stack[0], ProgramNode):
                    return self.stack[0]

                if len(self.stack) > 0:
                    if all(isinstance(item, (FunctionDeclNode, AssignmentNode, IfNode, WhileNode, EchoNode, FunctionCallNode)) for item in self.stack):
                        decls_list = list(self.stack)
                        self.stack = [decls_list]
                        if self.try_reduce():
                            continue

                    if len(self.stack) >= 2:
                        if isinstance(self.stack[0], Token) and self.stack[0].type == TokenType.PHP_OPEN:
                            if isinstance(self.stack[1], list):
                                raise ParserError("Erro sintático: esperado '?>' no final do programa")

                raise ParserError(f"Erro sintático: pilha final inválida com {len(self.stack)} elementos")

            if not self.shift():
                raise ParserError("Erro sintático: não foi possível fazer shift")

class Parser(ShiftReduceParser):
    pass
