"""
Nós da Árvore Sintática Abstrata (AST) para LALG-PHP
Compilador LALG-PHP
"""


class ASTNode:
    """Classe base para todos os nós da AST"""

    def __init__(self, line=0, column=0):
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.__class__.__name__}()"



class ProgramNode(ASTNode):
    """Nó raiz do programa: <?php ... ?>"""

    def __init__(self, statements, line=0, column=0):
        super().__init__(line, column)
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode(statements={len(self.statements)})"



class FunctionDeclNode(ASTNode):
    """Declaração de função: function nome(params) { body }"""

    def __init__(self, name, params, body, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"FunctionDeclNode(name='{self.name}', params={len(self.params)}, body={len(self.body)})"


class VariableNode(ASTNode):
    """Variável: $nome"""

    def __init__(self, name, line=0, column=0):
        super().__init__(line, column)
        self.name = name

    def __repr__(self):
        return f"VariableNode(name='{self.name}')"



class AssignmentNode(ASTNode):
    """Atribuição: $var = expr;"""

    def __init__(self, variable, expression, line=0, column=0):
        super().__init__(line, column)
        self.variable = variable
        self.expression = expression

    def __repr__(self):
        return f"AssignmentNode(variable={self.variable}, expression={self.expression})"


class IfNode(ASTNode):
    """Comando if: if (condition) { then_body } else { else_body }"""

    def __init__(self, condition, then_body, else_body=None, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    def __repr__(self):
        return f"IfNode(condition={self.condition}, then={len(self.then_body)}, else={len(self.else_body) if self.else_body else 0})"


class WhileNode(ASTNode):
    """Comando while: while (condition) { body }"""

    def __init__(self, condition, body, line=0, column=0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={len(self.body)})"


class EchoNode(ASTNode):
    """Comando echo: echo expr;"""

    def __init__(self, expression, line=0, column=0):
        super().__init__(line, column)
        self.expression = expression

    def __repr__(self):
        return f"EchoNode(expression={self.expression})"


class FunctionCallNode(ASTNode):
    """Chamada de função: nome(args)"""

    def __init__(self, name, arguments, line=0, column=0):
        super().__init__(line, column)
        self.name = name
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCallNode(name='{self.name}', args={len(self.arguments)})"



class BinaryOpNode(ASTNode):
    """Operação binária: left op right"""

    def __init__(self, operator, left, right, line=0, column=0):
        super().__init__(line, column)
        self.operator = operator
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinaryOpNode(op={self.operator.name}, left={self.left}, right={self.right})"


class UnaryOpNode(ASTNode):
    """Operação unária: op expr"""

    def __init__(self, operator, operand, line=0, column=0):
        super().__init__(line, column)
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOpNode(op={self.operator.name}, operand={self.operand})"


class NumberNode(ASTNode):
    """Literal numérico: 3.14"""

    def __init__(self, value, line=0, column=0):
        super().__init__(line, column)
        self.value = float(value)

    def __repr__(self):
        return f"NumberNode(value={self.value})"


class ReadlineNode(ASTNode):
    """Leitura de entrada: floatval(readline())"""

    def __init__(self, line=0, column=0):
        super().__init__(line, column)

    def __repr__(self):
        return "ReadlineNode()"


class PhpEolNode(ASTNode):
    """Constante PHP_EOL"""

    def __init__(self, line=0, column=0):
        super().__init__(line, column)

    def __repr__(self):
        return "PhpEolNode()"


class ConcatenationNode(ASTNode):
    """Concatenação: expr . expr"""

    def __init__(self, left, right, line=0, column=0):
        super().__init__(line, column)
        self.left = left
        self.right = right

    def __repr__(self):
        return f"ConcatenationNode(left={self.left}, right={self.right})"


