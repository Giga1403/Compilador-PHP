"""
Compilador LALG-PHP - Programa Principal
"""

import sys
from lexer import Lexer
from parser import Parser
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_generator import CodeGenerator


def compile_file(input_file, output_file=None):
    if output_file is None:
        output_file = input_file.replace('.php', '.asm')

    print("=" * 70)
    print("COMPILADOR LALG-PHP")
    print("=" * 70)
    print(f"Arquivo de entrada: {input_file}")
    print(f"Arquivo de saída: {output_file}")
    print()

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()

        print("CÓDIGO FONTE:")
        print("-" * 70)
        print(code)
        print("-" * 70)
        print()

        print("Análise Léxica...", end=" ")
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print(f"({len(tokens)} tokens)")

        print("Análise Sintática...", end=" ")
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"({len(ast.statements)} declarações)")

        print("Análise Semântica...", end=" ")
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

        print("Geração de Código...", end=" ")
        generator = CodeGenerator()
        instructions = generator.generate(ast)
        print(f"({len(instructions)} instruções)")

        generator.save_to_file(output_file)

        print()
        print("=" * 70)
        print("COMPILAÇÃO BEM-SUCEDIDA!")
        print("=" * 70)
        print()
        print("CÓDIGO GERADO:")
        print("-" * 70)
        generator.print_code()
        print("-" * 70)
        print()
        print(f"Código salvo em: {output_file}")
        print()

        print("=" * 70)
        print("EXECUTANDO NA MÁQUINA VIRTUAL")
        print("=" * 70)
        print()

        try:
            from vm import VirtualMachine
            vm = VirtualMachine()
            vm.load_program(output_file)
            vm.execute()
        except Exception as e:
            print(f"Erro ao executar na VM: {e}")

        return True

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{input_file}' não encontrado")
        return False

    except SemanticError as e:
        print(f"ERRO SEMÂNTICO: {e}")
        return False

    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo.php> [arquivo.asm]")
        print()
        print("Exemplos:")
        print("python main.py programa.php")
        print("python main.py programa.php saida.asm")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = compile_file(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
