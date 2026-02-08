"""
Gerador de Código VM
"""

from ast_nodes import *
from tokens import TokenType


class VMCodeGenerator:

    def __init__(self):
        self.code = []
        self.var_map = {}
        self.next_addr = 0
        self.func_lines = {}
        self.func_names = []
        self.line = 1
        self.in_function = False
        self.current_func = None

    def emit(self, instr):
        self.code.append(instr)
        self.line += 1
        return self.line - 1

    def allocate_var(self, var_name):
        if var_name not in self.var_map:
            self.var_map[var_name] = self.next_addr
            self.next_addr += 1
        return self.var_map[var_name]

    def generate(self, ast):
        self.emit("INPP")

        # Aloca variáveis globais
        global_vars = []
        for stmt in ast.statements:
            if isinstance(stmt, AssignmentNode) and not self.in_function:
                var_name = stmt.variable.name
                if var_name not in global_vars:
                    global_vars.append(var_name)
                    self.allocate_var(var_name)
                    self.emit("ALME 1")

        # Coleta nomes das funções
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDeclNode):
                self.func_names.append(stmt.name)

        # DSVI para pular funções (com comentário da primeira função)
        dsvi_idx = len(self.code)
        first_func = self.func_names[0] if self.func_names else ""
        self.emit(f"DSVI ??? #funcao {first_func}")

        # Gera funções
        func_count = 0
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDeclNode):
                self.generate_function(stmt)
                func_count += 1
                # Adiciona DSVI após cada função (exceto a última)
                if func_count < len(self.func_names):
                    next_func = self.func_names[func_count] if func_count < len(self.func_names) else ""
                    self.emit(f"DSVI ??? #funcao {next_func}")

        main_line = self.line
        # Atualiza todos os DSVIs para apontar para main
        for i, instr in enumerate(self.code):
            if instr.startswith("DSVI ???"):
                comment = instr.replace("DSVI ???", "").strip()
                self.code[i] = f"DSVI {main_line} {comment}"

        # Gera código principal
        for stmt in ast.statements:
            if not isinstance(stmt, FunctionDeclNode):
                self.generate_stmt(stmt)

        self.emit("PARA")

        return self.code

    def generate_function(self, node):
        self.in_function = True
        self.current_func = node.name
        self.func_lines[node.name] = self.line

        saved_vars = dict(self.var_map)
        saved_addr = self.next_addr

        self.next_addr = 8
        self.var_map = {}

        # Aloca parâmetros
        for param in node.params:
            self.allocate_var(param.name)
            self.emit("ALME 1")

        # Coleta variáveis locais
        local_vars = []
        for stmt in node.body:
            if isinstance(stmt, AssignmentNode):
                var_name = stmt.variable.name
                if var_name not in self.var_map and var_name not in local_vars:
                    local_vars.append(var_name)
                    self.allocate_var(var_name)

        # Gera corpo
        for stmt in node.body:
            self.generate_stmt(stmt)

        # DESM para desalocar variáveis
        num_locals = self.next_addr - 8
        if num_locals > 0:
            self.emit(f"DESM {num_locals}")

        self.emit("RTPR")

        self.var_map = saved_vars
        self.next_addr = saved_addr
        self.in_function = False
        self.current_func = None

    def generate_stmt(self, stmt):
        if isinstance(stmt, AssignmentNode):
            self.generate_assignment(stmt)
        elif isinstance(stmt, IfNode):
            self.generate_if(stmt)
        elif isinstance(stmt, WhileNode):
            self.generate_while(stmt)
        elif isinstance(stmt, EchoNode):
            self.generate_echo(stmt)
        elif isinstance(stmt, FunctionCallNode):
            self.generate_call(stmt)

    def generate_assignment(self, stmt):
        # Pula inicializações com zero
        if isinstance(stmt.expression, NumberNode):
            if stmt.expression.value == 0 or stmt.expression.value == 0.0:
                return

        if isinstance(stmt.expression, ReadlineNode):
            self.emit("LEIT")
        else:
            self.generate_expr(stmt.expression)

        addr = self.allocate_var(stmt.variable.name)
        self.emit(f"ARMZ {addr}")

    def generate_if(self, stmt):
        self.generate_cond(stmt.condition)

        dsvf_idx = len(self.code)
        self.emit("DSVF ???")

        for s in stmt.then_body:
            self.generate_stmt(s)

        if stmt.else_body:
            dsvi_idx = len(self.code)
            self.emit("DSVI ???")

            else_line = self.line
            self.code[dsvf_idx] = f"DSVF {else_line}"

            for s in stmt.else_body:
                self.generate_stmt(s)

            end_line = self.line
            self.code[dsvi_idx] = f"DSVI {end_line}"
        else:
            end_line = self.line
            self.code[dsvf_idx] = f"DSVF {end_line}"

    def generate_while(self, stmt):
        start = self.line

        self.generate_cond(stmt.condition)

        dsvf_idx = len(self.code)
        self.emit("DSVF ???")

        for s in stmt.body:
            self.generate_stmt(s)

        self.emit(f"DSVI {start}")

        end_line = self.line
        self.code[dsvf_idx] = f"DSVF {end_line}"

    def generate_echo(self, stmt):
        if isinstance(stmt.expression, ConcatenationNode):
            self.generate_expr(stmt.expression.left)
        else:
            self.generate_expr(stmt.expression)
        self.emit("IMPR")

    def generate_call(self, stmt):
        ret_line = self.line + 1 + len(stmt.arguments) + 1

        if ret_line < 100:
            self.emit(f"PUSHER {ret_line}")
        else:
            self.emit("PUSHER DEPOIS")

        # Empilhar os valores dos argumentos na pilha
        for arg in stmt.arguments:
            self.generate_expr(arg)

        func_line = self.func_lines.get(stmt.name, 0)
        self.emit(f"CHPR {func_line}")

    def generate_cond(self, node):
        if isinstance(node, BinaryOpNode):
            # Ordem: left primeiro, depois right (para comparação correta)
            self.generate_expr(node.left)
            self.generate_expr(node.right)

            if node.operator == TokenType.GREATER_EQUAL:
                self.emit("CMAI")
            elif node.operator == TokenType.LESS_EQUAL:
                self.emit("CPMI")
            elif node.operator == TokenType.GREATER:
                self.emit("CMAG")
            elif node.operator == TokenType.LESS:
                self.emit("CPME")
            elif node.operator == TokenType.EQUAL:
                self.emit("CMIG")
            elif node.operator == TokenType.NOT_EQUAL:
                self.emit("CMDG")

    def generate_expr(self, node):
        if isinstance(node, NumberNode):
            val = int(node.value) if node.value == int(node.value) else node.value
            self.emit(f"CRCT {val}")

        elif isinstance(node, VariableNode):
            addr = self.var_map.get(node.name, 0)
            self.emit(f"CRVL {addr}")

        elif isinstance(node, BinaryOpNode):
            # Para +/- gera right primeiro (subexpressão), depois left
            # Para */÷ gera left primeiro, depois right
            if node.operator in [TokenType.PLUS, TokenType.MINUS]:
                self.generate_expr(node.right)
                self.generate_expr(node.left)
            else:
                self.generate_expr(node.left)
                self.generate_expr(node.right)

            if node.operator == TokenType.PLUS:
                self.emit("SOMA")
            elif node.operator == TokenType.MINUS:
                self.emit("SUBT")
            elif node.operator == TokenType.MULTIPLY:
                self.emit("MULT")
            elif node.operator == TokenType.DIVIDE:
                self.emit("DIVI")

        elif isinstance(node, ReadlineNode):
            self.emit("LEIT")

        elif isinstance(node, ConcatenationNode):
            self.generate_expr(node.left)

    def save_to_file(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            for instr in self.code:
                f.write(instr + '\n')

    def print_code(self):
        for i, instr in enumerate(self.code, 1):
            print(f"{i:3d}: {instr}")


CodeGenerator = VMCodeGenerator
