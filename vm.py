class VirtualMachine:
    
    def __init__(self):
        self.stack = []
        self.memory = [0.0] * 100
        self.pc = 0
        self.instructions = []
        self.call_stack = []
        self.running = True
        self.memory_pointer = 0  # Rastreia o próximo endereço de memória disponível
        
    def load_program(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue

                if '#' in line:
                    line = line.split('#')[0].strip()
                    
                if line:
                    self.instructions.append(line)
        
        print(f"Programa carregado: {len(self.instructions)} instruções")

    def execute(self):
        print("\nIniciando execução\n")
        
        while self.running and self.pc < len(self.instructions):
            instruction = self.instructions[self.pc]
            self.execute_instruction(instruction)
            self.pc += 1
        
        print("\nExecução finalizada")

    def execute_instruction(self, instruction):
        parts = instruction.split()
        opcode = parts[0]
        
        # INPP - Inicializar Programa
        if opcode == 'INPP':
            pass
        
        # ALME - Alocar Memória (e desempilhar parâmetros se houver)
        elif opcode == 'ALME':
            n = int(parts[1])
            # Cada ALME é executado separadamente para cada parâmetro
            # Precisamos desempilhar na ordem FIFO (primeiro a entrar, primeiro a sair)
            # porque os argumentos foram empilhados na ordem: arg1, arg2, arg3, arg4
            for i in range(n):
                if self.stack:
                    value = self.stack.pop(0)  # FIFO - remove do início
                    self.memory[self.memory_pointer] = value
                self.memory_pointer += 1
        
        # CRCT - Carregar Constante
        elif opcode == 'CRCT':
            value = float(parts[1])
            self.stack.append(value)
        
        # CRVL - Carregar Valor de Variável
        elif opcode == 'CRVL':
            address = int(parts[1])
            value = self.memory[address]
            self.stack.append(value)
        
        # ARMZ - Armazenar em Memória
        elif opcode == 'ARMZ':
            address = int(parts[1])
            value = self.stack.pop()
            self.memory[address] = value

        # SOMA - Adição
        elif opcode == 'SOMA':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        
        # SUBT - Subtração
        elif opcode == 'SUBT':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        
        # MULT - Multiplicação
        elif opcode == 'MULT':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        
        # DIVI - Divisão
        elif opcode == 'DIVI':
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a / b)
        
        # LEIT - Ler entrada do usuário
        elif opcode == 'LEIT':
            value = float(input("Digite um valor: "))
            self.stack.append(value)
        
        # IMPR - Imprimir valor
        elif opcode == 'IMPR':
            value = self.stack.pop()
            print(value)
        
        # DSVI - Desvio Incondicional
        elif opcode == 'DSVI':
            line = int(parts[1])
            self.pc = line - 2
        
        # DSVF - Desvio se Falso
        elif opcode == 'DSVF':
            line = int(parts[1])
            condition = self.stack.pop()
            if condition == 0:
                self.pc = line - 2
        
        # CMAI - Comparar Maior ou Igual (>=)
        elif opcode == 'CMAI':
            b = self.stack.pop()
            a = self.stack.pop()
            result = 1 if a >= b else 0
            self.stack.append(result)
        
        # CPMI - Comparar Menor ou Igual (<=)
        elif opcode == 'CPMI':
            b = self.stack.pop()
            a = self.stack.pop()
            result = 1 if a <= b else 0
            self.stack.append(result)
        
        # PUSHER - Empilhar Endereço de Retorno
        elif opcode == 'PUSHER':
            if len(parts) > 1 and parts[1].isdigit():
                return_address = int(parts[1])
            else:
                return_address = self.pc + 1
            self.call_stack.append(return_address)
        
        # PARAM - Passar Parâmetro
        elif opcode == 'PARAM':
            address = int(parts[1])
            value = self.memory[address]
            self.stack.append(value)
        
        # CHPR - Chamar Procedimento
        elif opcode == 'CHPR':
            line = int(parts[1])
            self.memory_pointer = 8  # Reset para início das variáveis locais
            self.pc = line - 2
        
        # RTPR - Retornar de Procedimento
        elif opcode == 'RTPR':
            if self.call_stack:
                return_address = self.call_stack.pop()
                self.pc = return_address - 1
            else:
                self.running = False
        
        # DESM - Desempilhar (limpa n valores da pilha)
        elif opcode == 'DESM':
            n = int(parts[1])
            for _ in range(n):
                if self.stack:
                    self.stack.pop()
        
        # PARA - Parar Execução
        elif opcode == 'PARA':
            self.running = False
        
        else:
            print(f"Instrução não implementada: {opcode}")
