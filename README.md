# Compilador LALG-PHP

Este e um compilador completo para a linguagem LALG-PHP, desenvolvido em Python. O compilador transforma codigo fonte em PHP para instrucoes de uma maquina virtual customizada, permitindo a execucao completa do programa.

## O Que Este Projeto Faz

O compilador le um arquivo PHP simplificado e realiza as seguintes etapas:

1. Le o codigo fonte e identifica cada elemento (tokens)
2. Organiza os tokens em uma estrutura hierarquica (arvore sintatica)
3. Verifica se o codigo faz sentido (analise semantica)
4. Gera instrucoes de baixo nivel para a maquina virtual
5. Executa as instrucoes e mostra o resultado

## Como Usar

### Requisitos

- Python 3.6 ou superior instalado no computador

### Executando o Compilador

Abra o terminal na pasta src do projeto e execute:

```powershell
python main.py caminho/para/seu/arquivo.php
```

Por exemplo, para compilar o arquivo de exemplo:

```powershell
python main.py exemplos/correto.php
```

O compilador ira mostrar cada fase da compilacao e, ao final, executar o programa na maquina virtual.

### Saida do Compilador

Quando voce executa o compilador, ele mostra:

- O codigo fonte original
- Quantos tokens foram identificados
- Quantas declaracoes foram encontradas
- Quantas instrucoes foram geradas
- O codigo assembly gerado (numerado linha por linha)
- O resultado da execucao na maquina virtual

## Estrutura do Projeto

O projeto esta organizado da seguinte forma:

```
compilador-php/
    src/
        main.py               Programa principal que coordena tudo
        tokens.py             Define os tipos de tokens da linguagem
        lexer.py              Analisador lexico - identifica tokens
        parser.py             Analisador sintatico - gera arvore
        ast_nodes.py          Define os tipos de nos da arvore
        semantic_analyzer.py  Verifica erros semanticos
        code_generator.py     Gera codigo para a maquina virtual
        vm.py                 Maquina virtual que executa o codigo
        test_all.py           Testes automatizados
    exemplos/
        correto.php           Exemplo completo de programa
    testes/
        codigo.objeto.txt     Exemplo de codigo assembly esperado
    docs/
        README.md             Esta documentacao
```

## Como Funciona Cada Parte

### Analisador Lexico (lexer.py)

O analisador lexico le o codigo fonte caractere por caractere e agrupa em tokens. Por exemplo, a linha:

```php
$x = 10 + 5;
```

Gera os seguintes tokens:
- VARIABLE ($x)
- ASSIGN (=)
- NUMBER (10)
- PLUS (+)
- NUMBER (5)
- SEMICOLON (;)

### Analisador Sintatico (parser.py)

O parser usa o algoritmo shift-reduce para construir uma arvore sintatica abstrata (AST). Esse algoritmo funciona de baixo para cima, empilhando tokens e reduzindo quando encontra padroes que correspondem a regras da gramatica.

Por exemplo, a expressao $x = 10 + 5 gera uma arvore onde:
- A raiz e um no de atribuicao
- O lado esquerdo e a variavel $x
- O lado direito e uma operacao de soma entre 10 e 5

### Correcao de Precedencia (ast_nodes.py)

O parser shift-reduce tem uma limitacao: ele nao respeita automaticamente a precedencia de operadores. Por exemplo, em 2 + 3 * 4, a multiplicacao deve ser feita primeiro.

Para resolver isso, existe uma etapa de pos-processamento que reorganiza a arvore para garantir que multiplicacao e divisao tenham prioridade sobre soma e subtracao.

### Analisador Semantico (semantic_analyzer.py)

Esta etapa verifica se o codigo faz sentido semanticamente:
- Variaveis sao declaradas antes de usar
- Funcoes sao chamadas com o numero correto de parametros
- Nao existem variaveis duplicadas no mesmo escopo

### Gerador de Codigo (code_generator.py)

O gerador percorre a arvore sintatica e emite instrucoes para a maquina virtual. Cada tipo de construcao na linguagem gera um padrao especifico de instrucoes.

Por exemplo, um comando if-else gera:
1. Codigo para avaliar a condicao
2. DSVF para pular o bloco then se falso
3. Codigo do bloco then
4. DSVI para pular o bloco else
5. Codigo do bloco else

### Maquina Virtual (vm.py)

A maquina virtual e baseada em pilha. Ela tem:
- Uma pilha para operacoes aritmeticas e chamadas de funcao
- Uma area de memoria para variaveis
- Um contador de programa que indica a proxima instrucao

## Linguagem LALG-PHP

### Variaveis

Todas as variaveis comecam com $ e devem ser inicializadas:

```php
$numero = 0.0;
$contador = 10;
$valor = 3.14;
```

### Funcoes

Funcoes sao declaradas com a palavra function e podem ter parametros:

```php
function calcular($a, $b, $c) {
    $resultado = $a + $b * $c;
    echo $resultado . PHP_EOL;
}
```

Para chamar a funcao:

```php
calcular($x, $y, $z);
```

### Estrutura If-Else

Condicoes sao escritas com if e else:

```php
if ($valor >= 10) {
    echo $valor . PHP_EOL;
} else {
    echo 0 . PHP_EOL;
}
```

### Estrutura While

Lacos de repeticao usam while:

```php
$i = 1;
while ($i <= 10) {
    echo $i . PHP_EOL;
    $i = $i + 1;
}
```

### Entrada de Dados

Para ler valores do usuario:

```php
$entrada = floatval(readline());
```

### Saida de Dados

Para mostrar valores na tela:

```php
echo $valor . PHP_EOL;
```

### Operadores Disponiveis

Aritmeticos:
- Soma: +
- Subtracao: -
- Multiplicacao: *
- Divisao: /

Comparacao:
- Maior ou igual: >=
- Menor ou igual: <=
- Maior: >
- Menor: <
- Igual: ==
- Diferente: !=

## Instrucoes da Maquina Virtual

### Controle do Programa

- INPP: Inicia o programa
- PARA: Termina a execucao
- ALME n: Aloca espaco na memoria para uma variavel

### Manipulacao de Dados

- CRCT n: Coloca uma constante na pilha
- CRVL n: Coloca o valor da variavel n na pilha
- ARMZ n: Remove o topo da pilha e armazena na variavel n

### Operacoes Aritmeticas

- SOMA: Remove dois valores da pilha, soma e empilha o resultado
- SUBT: Remove dois valores da pilha, subtrai e empilha o resultado
- MULT: Remove dois valores da pilha, multiplica e empilha o resultado
- DIVI: Remove dois valores da pilha, divide e empilha o resultado

### Desvios

- DSVI n: Desvia incondicionalmente para a linha n
- DSVF n: Desvia para a linha n se o topo da pilha for falso (zero)

### Comparacoes

Todas removem dois valores da pilha e empilham 1 (verdadeiro) ou 0 (falso):
- CMAI: Compara se o segundo valor e maior ou igual ao primeiro
- CPMI: Compara se o segundo valor e menor ou igual ao primeiro
- CMAG: Compara se o segundo valor e maior que o primeiro
- CPME: Compara se o segundo valor e menor que o primeiro
- CMIG: Compara se os valores sao iguais
- CMDG: Compara se os valores sao diferentes

### Entrada e Saida

- LEIT: Le um valor do teclado e empilha
- IMPR: Remove o topo da pilha e mostra na tela

### Chamadas de Funcao

- PUSHER n: Empilha o endereco de retorno n
- PARAM n: Passa o valor da variavel n como parametro
- CHPR n: Chama o procedimento na linha n
- RTPR: Retorna do procedimento
- DESM n: Desaloca n variaveis locais

## Exemplo Completo

Este e um programa que demonstra as principais funcionalidades:

```php
<?php
$a = 0.0;
$b = 0.0;

function somar($x, $y) {
    $resultado = $x + $y;
    echo $resultado . PHP_EOL;
}

$a = floatval(readline());
$b = floatval(readline());

if ($a >= $b) {
    somar($a, $b);
} else {
    echo $b . PHP_EOL;
}
?>
```

Ao executar este programa e digitar 10 e 5, a saida sera 15.0.

## Testando o Compilador

Para executar todos os testes automatizados:

```powershell
cd src
python test_all.py
```

Os testes verificam se cada parte do compilador esta funcionando corretamente.

## Limitacoes Conhecidas

- Apenas um tipo de dado (numeros de ponto flutuante)
- Funcoes nao retornam valores, apenas imprimem
- Nao suporta strings alem de PHP_EOL
- Nao suporta arrays ou estruturas de dados complexas

## Sobre o Desenvolvimento

Este compilador foi desenvolvido como projeto academico para a disciplina de compiladores. Ele demonstra os conceitos fundamentais de:

- Analise lexica e tokenizacao
- Analise sintatica com parser shift-reduce
- Geracao de codigo intermediario
- Execucao em maquina virtual baseada em pilha

O codigo esta escrito em Python puro, sem dependencias externas, para facilitar o entendimento e a portabilidade.
