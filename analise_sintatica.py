import pandas as pd


def analise(tabela):
    global tokens, lexemas, numLinhas, tokens_lines, lexemas_lines, tabela_simbolos
    tokens = (tabela[tabela.columns[0:1:]]).values
    lexemas = (tabela[tabela.columns[1:2:]]).values
    numLinhas = (tabela[tabela.columns[2:3:]]).values

    tabela_simbolos = pd.DataFrame(
        columns=['Token', 'Lexema', 'Tipo', 'Linha', 'Valor',
                 'QntParametros', 'Variaveis', 'TiposVar', 'Escopo'])

    tokens_lines = create_line_tokens()
    lexemas_lines = create_line_lexemas()
    lista_escopo = []
    try:
        lista_escopo = verificar_escopo(tokens_lines)

        verificar_parentese()

        verificar_ponto_virgula(tokens_lines)

        loop_verificacao(lista_escopo)
    except Exception as e:
        print_error('Erro de sintaxe')

    return [tabela_simbolos, lista_escopo]


def determinar_linha_escopo(lista_escopo, linha):
    aux = ""
    # Verificar se está em uma condficional
    for escopo in lista_escopo:
        if linha >= escopo[2] and linha <= escopo[3]:
            if aux != "":
                if escopo[1] == "funcao" or escopo[1] == "procedimento":
                    lexemas_escopo = get_line_lexemas(escopo[2])
                    aux = lexemas_escopo[1] + "," + aux
                else:
                    aux = escopo[1] + "," + aux
            else:
                if escopo[1] == "funcao" or escopo[1] == "procedimento":
                    lexemas_escopo = get_line_lexemas(escopo[2])
                    aux = lexemas_escopo[1] + '[' + str(escopo[2]) + ',' + str(escopo[3]) + ']'
                else:
                    aux = escopo[1] + '[' + str(escopo[2]) + ',' + str(escopo[3]) + ']'

    if aux != "":
        return aux
    return "global"


def loop_verificacao(lista_escopo):
    for index, token in enumerate(tokens):
        verificar_identificador(token, numLinhas[index, 0])
        assinatura_if(token, numLinhas[index, 0], lexemas[index])
        assinatura_else(token, numLinhas[index, 0], lexemas[index])
        verificar_atribuicao(token, numLinhas[index, 0], index, lista_escopo)
        assinatura_procedimento_funcao(token, numLinhas[index, 0], index)
        assinatura_while(token, numLinhas[index, 0])
        assinatura_print(token, numLinhas[index, 0])


def print_error(mensagem, linha=None):
    if linha != None:
        print("Erro de Sintaxe:", mensagem, 'Linha:', linha)
    else:
        print("Erro de Sintaxe:", mensagem)
    exit()


def get_line_tokens(linha):
    try:
        return tokens_lines[linha].copy()
    except Exception as e:
        print('linha vazia ou não encontrada')


def verificar_atribuicao_expressao(lista_tokens, linha):
    if lista_tokens.pop() == 'ponto_virgula':
        expressao = []
        while (lista_tokens[-1] != 'operador_atribuicao'):
            try:
                valor_expressao = lista_tokens.pop()
                expressao.append(valor_expressao)
            except Exception as e:
                print_error('Erro na expressão', linha)
        if len(expressao) == 1 and expressao.pop() in ['booleano', 'numerico', 'identificador']:
            return True
        elif len(expressao) == 3:
            if expressao.pop() in ['numerico', 'identificador']:
                if expressao.pop() == 'operador_aritmetico':
                    if len(expressao) == 1 and expressao[0] in ['numerico', 'identificador']:
                        return True
        else:
            if expressao.pop() in ['numerico', 'identificador']:
                if verificar_multiplas_operacoes_expressao_numerica(expressao):
                    return True
        return False


def verificar_multiplas_operacoes_expressao_numerica(expressao):
    if len(expressao) == 0:
        return True
    elif len(expressao) >= 2 and expressao.pop() == 'operador_aritmetico':
        if expressao.pop() in ['numerico', 'identificador']:
            return verificar_multiplas_operacoes_expressao_numerica(expressao)


def verificar_atribuicao_funcao(lista_tokens, linha):
    virgula = True
    if lista_tokens.pop() == 'ponto_virgula':
        if lista_tokens.pop() == 'fecha_parentese':
            if lista_tokens.pop() in ['identificador', 'numerico']:

                while (lista_tokens[-1] != 'abre_parentese'):
                    token_vez = lista_tokens.pop()
                    try:
                        if token_vez == 'virgula' and virgula:
                            virgula = False
                        elif token_vez in ['identificador', 'numerico'] and virgula == False:
                            virgula = True
                        else:
                            return False

                    except Exception as e:
                        print_error('Erro na expressão', linha)
                if lista_tokens.pop() == 'abre_parentese':
                    if lista_tokens.pop() == 'identificador':
                        return True
    return False


def verificar_identificador(token, linha):
    if (token == 'identificador'):
        lista_tokens_linha = get_line_tokens(linha)
        if (lista_tokens_linha.pop() == 'ponto_virgula'):
            if (lista_tokens_linha.pop() == 'identificador'):
                try:
                    if (lista_tokens_linha.pop() == 'tipo'):
                        print_error('Identificador vazio não permitido!', linha)
                except:
                    print_error('Identificador vazio não permitido!', linha)


def verificar_atribuicao(token, linha, index, lista_escopo):
    valor = []
    if (token == 'operador_atribuicao'):
        lista_tokens_linha = get_line_tokens(linha)
        if verificar_atribuicao_expressao(lista_tokens_linha, linha):
            if lista_tokens_linha.pop() == 'operador_atribuicao':
                if lista_tokens_linha.pop() == 'identificador':
                    if lista_tokens_linha.pop() == 'tipo':
                        token_index = index
                        while (lexemas[token_index] != ';'):
                            token_index += 1
                            valor.append(lexemas[token_index][0])
                        tabela_simbolos.loc[len(tabela_simbolos)] = ['identificador', lexemas[index - 1][0],
                                                                     lexemas[index - 2][0],
                                                                     linha, ' '.join(valor[:-1]), "-",
                                                                     "-", "-",
                                                                     determinar_linha_escopo(lista_escopo, linha)]
                        return True
        else:
            lista_tokens_linha = get_line_tokens(linha)
            if verificar_atribuicao_funcao(lista_tokens_linha, linha):
                if lista_tokens_linha.pop() == 'operador_atribuicao':
                    if lista_tokens_linha.pop() == 'identificador':
                        if lista_tokens_linha.pop() == 'tipo':
                            token_index = index
                            while (lexemas[token_index] != ';'):
                                token_index += 1
                                valor.append(lexemas[token_index][0])
                            tabela_simbolos.loc[len(tabela_simbolos)] = ['identificador', lexemas[index - 1][0],
                                                                         lexemas[index - 2][0],
                                                                         linha, ''.join(valor[:-1]), "-",
                                                                         "-", "-",
                                                                         determinar_linha_escopo(lista_escopo, linha)]
                            return True
        print_error('Erro na atribuicao', linha)


def verificar_expressao_booleana(lista_tokens, linha):
    expressao = []
    while (lista_tokens[-1] != 'abre_parentese'):
        try:
            expressao.append(lista_tokens.pop())
        except Exception as e:
            print_error('Erro na expressão', linha)
    if (len(expressao) == 1):
        if (expressao.pop() in ['booleano', 'identificador']):
            return True
    elif expressao.pop() in ['booleano', 'numerico', 'identificador']:
        if expressao.pop() == 'operador_booleano':
            if len(expressao) == 1 and expressao[0] in ['booleano', 'numerico', 'identificador']:
                return True
    return False


def assinatura_while(token, linha):
    if (token == 'laco'):
        lista_tokens_linha = get_line_tokens(linha)
        if lista_tokens_linha.pop() == 'abre_chave':
            if lista_tokens_linha.pop() == 'fecha_parentese':
                if verificar_expressao_booleana(lista_tokens_linha, linha):
                    if lista_tokens_linha.pop() == 'abre_parentese':
                        if len(lista_tokens_linha) == 1 and lista_tokens_linha[0] == 'laco':
                            return True
        print_error('Erro na assinatura do While', linha)


def assinatura_if(token, linha, lexema):
    if (token == 'condicional' and lexema == 'if'):
        lista_tokens_linha = get_line_tokens(linha)
        if lista_tokens_linha.pop() == 'abre_chave':
            if lista_tokens_linha.pop() == 'fecha_parentese':
                if verificar_expressao_booleana(lista_tokens_linha, linha):
                    if lista_tokens_linha.pop() == 'abre_parentese':
                        if len(lista_tokens_linha) == 1 and lista_tokens_linha[0] == 'condicional':
                            return True
        print_error('Erro na assinatura do IF', linha)


def assinatura_print(token, linha):
    if (token == 'impressao'):
        lista_tokens_linha = get_line_tokens(linha)
        if lista_tokens_linha.pop() == 'ponto_virgula':
            if lista_tokens_linha.pop() == 'fecha_parentese':
                if lista_tokens_linha.pop() in ['numerico', 'identificador', 'booleano']:
                    if lista_tokens_linha.pop() == 'abre_parentese':
                        if len(lista_tokens_linha) == 1 and lista_tokens_linha[0] == 'impressao':
                            return True
        print_error('Erro na assinatura do PRINT', linha)


def assinatura_else(token, linha, lexema):
    if token == 'condicional' and lexema == 'else':
        lista_tokens_linha = get_line_tokens(linha)
        if len(lista_tokens_linha) == 3:
            if lista_tokens_linha.pop() == 'abre_chave':
                if lista_tokens_linha.pop() == 'condicional':
                    if lista_tokens_linha.pop() == 'fecha_chave':
                        if len(lista_tokens_linha) == 0:
                            return True
        print_error('Erro na assinatura do ELSE', linha)


def create_line_tokens():
    lista_tokens = {}
    tokens_line = []
    linha_aux = [1]
    last_position = -1
    for index, linha in enumerate(numLinhas):
        if (linha_aux == linha):
            tokens_line.append(tokens[index, 0])
        else:
            lista_tokens[linha_aux[0]] = tokens_line
            linha_aux = linha
            tokens_line = []
            tokens_line.append(tokens[index, 0])

    lista_tokens[numLinhas[last_position, 0]] = [tokens_line[last_position]]
    return lista_tokens


def create_line_lexemas():
    lista_lexemas = {}
    lexemas_line = []
    linha_aux = [1]
    last_position = -1
    for index, linha in enumerate(numLinhas):
        if (linha_aux == linha):
            lexemas_line.append(lexemas[index, 0])
        else:
            lista_lexemas[linha_aux[0]] = lexemas_line
            linha_aux = linha
            lexemas_line = []
            lexemas_line.append(lexemas[index, 0])

    lista_lexemas[numLinhas[last_position, 0]] = [lexemas_line[last_position]]
    return lista_lexemas


def get_line_lexemas(linha):
    try:
        return lexemas_lines[linha].copy()
    except Exception as e:
        print('linha vazia ou não encontrada')


def verifcar_abertura_chave(linha, posicao, tokens_validos, token, numero_linha):
    if token == 'abre_chave':
        if linha[0] not in tokens_validos and len(linha) > 1 and (
                linha[0] != 'fecha_chave' and linha[1] != 'condicional' and linha[2] != 'abre_chave'):
            print_error('Abertura de chave invalida.', numero_linha)
        if posicao != (len(linha) - 1):
            print_error('Abertura de chave invalida.', numero_linha)
        return True
    return False


def verifcar_fechamento_chave(token):
    if token == 'fecha_chave':
        return True
    return False


def verificar_escopo(tokens_lines):
    tokens_validos_inicio = ['condicional', 'funcao', 'procedimento', 'laco']
    chave_Count = []
    lista_escopo_fechado = []
    count_lexema = 0
    for numero_linha, linha in tokens_lines.items():
        for indice, token in enumerate(linha):
            # Verificar abertura de chave
            if verifcar_abertura_chave(linha, indice, tokens_validos_inicio, token, numero_linha):
                if linha[0] == "fecha_chave":
                    chave_Count.append([linha[-1], linha[1], numero_linha])
                else:
                    chave_Count.append([linha[-1], linha[0], numero_linha])

            # verificar fechamento de chave
            elif verifcar_fechamento_chave(token):
                try:
                    # Guardando valor do que foi retirado da pilha
                    aux = chave_Count.pop()
                    # Adicionar a linha de fechamento do escopo
                    aux.append(numero_linha)
                    # Adiciona o lexema
                    lista_escopo_fechado.append(aux)
                    # Verificando se o que foi retirado pertencia a assinatura de uma função, para então saber se ela tinha retorno
                    if aux[1] == 'funcao' and linha_anterior[0] != 'retorno':
                        print_error('A função necessita de um retorno.', aux[2])
                except Exception as e:
                    # Na erro ao retirar algo de uma pilha vazia, nos diz que temos mais fecha_chave do que abre_chave
                    print_error('A quantidade de fecha chave é superior ao de abre chave.', numero_linha)

            # Verificação de desvio incondicional
            elif token == 'desvio_incondicional':
                aux = 0
                for item in chave_Count:
                    if 'laco' in item:
                        aux += 1
                if aux == 0:
                    print_error('Desvios incondicionais devem estar presentes apenas em laços.', numero_linha)

            # Verificação de retorno
            elif token == 'retorno':
                aux = 0
                for item in chave_Count:
                    if 'funcao' in item:
                        aux += 1
                if aux == 0:
                    print_error('Retorno deve estar presente apenas em funções.', numero_linha)

            # Verificação de uso da condicional else
            elif token == 'condicional' and lexemas[count_lexema] == 'else':
                if len(lista_escopo_fechado) == 0 or lista_escopo_fechado[-1][1] != 'condicional':
                    print_error('Condicional ELSE deve ser aplicada somente após o IF.')

            count_lexema += 1

        # Guardando sempre a linha 'anterior' para validação do retorno da função
        linha_anterior = linha

    # Verificando se sobrou algum abre_chave na pilha
    if (len(chave_Count) > 0):
        aux = chave_Count.pop()
        print_error('A quantidade de abre chave é superior ao de fecha chave.', aux[2])

    return lista_escopo_fechado


def verificar_parentese():
    parenteseCount = []
    for index, token in enumerate(tokens):
        if token == 'abre_parentese':
            parenteseCount.append(['(', numLinhas[index]])
        elif token == 'fecha_parentese':
            try:
                parenteseCount.pop()
            except Exception as e:
                print_error('A quantidade de fecha parentese é superior ao de abre parentese.', numLinhas[index])
    if (len(parenteseCount) > 0):
        aux = parenteseCount.pop()
        print_error('A quantidade de abre parentese é superior ao de fecha parentese.', aux[1])


# Verificando se o ultimo token de cada linha é um token ponto_virgula, caso não seja, deve de forma obrigatória se iniciar a linha com [if,while,procedimento,funcao]
def verificar_ponto_virgula(tokens_lines):
    # Guardando os tokens que serão válidos para casos onde não se finaliza a linha com ponto_virgula
    tokens_validos_inicio = ['condicional', 'funcao', 'procedimento', 'laco']
    for numero_linha, linha in tokens_lines.items():
        if linha[-1] != 'ponto_virgula':
            if (linha[0] not in tokens_validos_inicio) and (len(linha) >= 1 and linha[0] != 'fecha_chave'):
                print_error('Finalização de expressão incorreta.', numero_linha)


def assinatura_procedimento_funcao(token, numero_linha, index):
    # Verificação do primeiro token, para saber se corresponde ao padrão dado a função/procedimento
    if (token == 'procedimento') or (token == 'funcao'):

        # Recuperação da linha, após verificação de existencia da funcao/procedimento
        linha = get_line_tokens(numero_linha)

        # Verificação se possui um identificador para essa função/procedimento
        if linha[1] != 'identificador':
            print_error('Incorreta a assinatura da funcao/procedimento.', numero_linha)

        # Verificação do conteudo presente entre o '(' (abre_parentese) e ')' (fecha_parentese)
        if (linha[2] != 'abre_parentese') and (linha[-2] != 'fecha_parentese'):
            print_error('Incorreta a assinatura da funcao/procedimento.', numero_linha)

        # Utilização de função auxiliar os argumentos presentes na função/procedimento
        verificao_argumento_procedimento_funcao(linha[3:-2], numero_linha, index)
        lista_lexemas = gerar_lista_lexemas_argumentos(linha[3:-2], index + 2)
        tipos_argumentos = [item[0] for item in lista_lexemas]
        identificadores_argumentos = [item[1] for item in lista_lexemas]

        # Adição na tabela de simbolos
        tabela_simbolos.loc[len(tabela_simbolos)] = \
            [token[0], lexemas[index + 1][0], '-', numero_linha, '-',
             len(lista_lexemas), identificadores_argumentos, tipos_argumentos, '-']


def verificao_argumento_procedimento_funcao(argumentos, linha, index):
    # Separação dos argumentos, separando a lista em sub-listas a partir do token 'virgula'
    lista_tokens = []
    sublista = []

    for token in argumentos:
        if token == 'virgula':
            lista_tokens.append(sublista)
            sublista = []
        else:
            sublista.append(token)

    lista_tokens.append(sublista)

    # Verificando se é respeitada a padronização de tokens na passagem dos argumentos
    for intervalo_tokens in lista_tokens:
        if len(intervalo_tokens) == 2:
            if intervalo_tokens[0] != 'tipo' or intervalo_tokens[1] != 'identificador':
                print_error('Incorreta a passagem dos argumentos.', linha)
        else:
            print_error('Incorreta a passagem dos argumentos.', linha)


def gerar_lista_lexemas_argumentos(argumentos, index):
    lista_lexemas = []
    sublista_lexemas = []
    cont = index

    for lexema in argumentos:
        cont += 1
        if lexema == 'virgula':
            lista_lexemas.append(sublista_lexemas)
            sublista_lexemas = []
        else:
            sublista_lexemas.append(lexemas[cont][0])
    lista_lexemas.append(sublista_lexemas)

    return lista_lexemas
