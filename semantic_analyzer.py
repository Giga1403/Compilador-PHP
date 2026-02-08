"""
Analisador Semântico para LALG-PHP

Realiza verificações semânticas na AST:
- Declaração e uso de variáveis
- Declaração e chamada de funções
- Verificação de escopos
- Validação de argumentos
"""

from ast_nodes import *
from tokens import TokenType


class SemanticError(Exception):

    def __init__(self, message, line=0, column=0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Erro semântico (linha {line}, coluna {column}): {message}")


class Symbol:
    """Representa um símbolo na tabela de símbolos"""

    def __init__(self, name, symbol_type, scope, line=0, column=0, params_count=0):
        self.name = name
        self.symbol_type = symbol_type
        self.scope = scope
        self.line = line
        self.column = column
        self.params_count = params_count

    def __repr__(self):
        if self.symbol_type == 'function':
            return f"Symbol({self.name}, {self.symbol_type}, {self.scope}, params={self.params_count})"
        return f"Symbol({self.name}, {self.symbol_type}, {self.scope})"


class SymbolTable:

    def __init__(self):
        self.scopes = [{}]
        self.scope_names = ['global']

    def enter_scope(self, scope_name):
        self.scopes.append({})
        self.scope_names.append(scope_name)

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_names.pop()

    def current_scope(self):
        return self.scope_names[-1]

    def declare(self, symbol):
        current = self.scopes[-1]

        if symbol.name in current:
            existing = current[symbol.name]
            raise SemanticError(
                f"'{symbol.name}' já foi declarado(a) anteriormente (linha {existing.line})",
                symbol.line,
                symbol.column
            )

        current[symbol.name] = symbol

    def lookup(self, name):
        """
        Busca um símbolo nos escopos (atual + global)
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        return None

    def lookup_current_scope(self, name):
        """
        Busca um símbolo apenas no escopo atual
        """
        return self.scopes[-1].get(name, None)

    def __repr__(self):
        result = "SymbolTable:\n"
        for i, (scope_name, scope) in enumerate(zip(self.scope_names, self.scopes)):
            result += f"  Escopo '{scope_name}':\n"
            for name, symbol in scope.items():
                result += f"    {symbol}\n"
        return result


class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []

    def analyze(self, ast):
        """
        Analisa a AST e verifica semântica
        """
        try:
            self.visit_program(ast)
            return True
        except SemanticError as e:
            raise

    def visit_program(self, node):
        for stmt in node.statements:
            if isinstance(stmt, FunctionDeclNode):
                self.declare_function(stmt)

        for stmt in node.statements:
            self.visit_statement(stmt)

    def declare_function(self, node):
        symbol = Symbol(
            name=node.name,
            symbol_type='function',
            scope='global',
            line=node.line,
            column=node.column,
            params_count=len(node.params)
        )
        self.symbol_table.declare(symbol)

    def visit_statement(self, node):
        if isinstance(node, FunctionDeclNode):
            self.visit_function_decl(node)
        elif isinstance(node, AssignmentNode):
            self.visit_assignment(node)
        elif isinstance(node, IfNode):
            self.visit_if(node)
        elif isinstance(node, WhileNode):
            self.visit_while(node)
        elif isinstance(node, EchoNode):
            self.visit_echo(node)
        elif isinstance(node, FunctionCallNode):
            self.visit_function_call(node)

    def visit_function_decl(self, node):
        self.symbol_table.enter_scope(node.name)

        for param in node.params:
            symbol = Symbol(
                name=param.name,
                symbol_type='parameter',
                scope=node.name,
                line=param.line,
                column=param.column
            )
            self.symbol_table.declare(symbol)

        for stmt in node.body:
            self.visit_statement(stmt)

        self.symbol_table.exit_scope()

    def visit_assignment(self, node):
        self.visit_expression(node.expression)

        existing = self.symbol_table.lookup_current_scope(node.variable.name)

        if existing is None:
            symbol = Symbol(
                name=node.variable.name,
                symbol_type='variable',
                scope=self.symbol_table.current_scope(),
                line=node.variable.line,
                column=node.variable.column
            )
            self.symbol_table.declare(symbol)

    def visit_if(self, node):
        self.visit_expression(node.condition)

        for stmt in node.then_body:
            self.visit_statement(stmt)

        if node.else_body:
            for stmt in node.else_body:
                self.visit_statement(stmt)

    def visit_while(self, node):
        self.visit_expression(node.condition)

        for stmt in node.body:
            self.visit_statement(stmt)

    def visit_echo(self, node):
        self.visit_expression(node.expression)

    def visit_function_call(self, node):
        symbol = self.symbol_table.lookup(node.name)

        if symbol is None:
            raise SemanticError(
                f"Função '{node.name}' não foi declarada",
                node.line,
                node.column
            )

        if symbol.symbol_type != 'function':
            raise SemanticError(
                f"'{node.name}' não é uma função",
                node.line,
                node.column
            )

        if len(node.arguments) != symbol.params_count:
            raise SemanticError(
                f"Função '{node.name}' espera {symbol.params_count} argumento(s), "
                f"mas recebeu {len(node.arguments)}",
                node.line,
                node.column
            )

        for arg in node.arguments:
            self.visit_expression(arg)

    def visit_expression(self, node):
        if isinstance(node, NumberNode):
            pass

        elif isinstance(node, VariableNode):
            self.visit_variable(node)

        elif isinstance(node, BinaryOpNode):
            self.visit_binary_op(node)

        elif isinstance(node, UnaryOpNode):
            self.visit_unary_op(node)

        elif isinstance(node, ConcatenationNode):
            self.visit_concatenation(node)

        elif isinstance(node, ReadlineNode):
            pass

        elif isinstance(node, PhpEolNode):
            pass

        elif isinstance(node, FunctionCallNode):
            self.visit_function_call(node)

    def visit_variable(self, node):
        symbol = self.symbol_table.lookup(node.name)

        if symbol is None:
            raise SemanticError(
                f"Variável '{node.name}' não foi declarada (não foi atribuída antes do uso)",
                node.line,
                node.column
            )

    def visit_binary_op(self, node):
        self.visit_expression(node.left)
        self.visit_expression(node.right)

    def visit_unary_op(self, node):
        self.visit_expression(node.operand)

    def visit_concatenation(self, node):
        self.visit_expression(node.left)
        self.visit_expression(node.right)
