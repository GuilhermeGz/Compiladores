def gerar(tabela_lexica, tabela_sintatica):
    global tokens, lexemas, numLinhas, tokens_lines, lexemas_lines, tabela_simbolos, arquivo, lexemas_funcoes;
    # Limpar arquivo
    arquivo = open("CodigoIntermediario.txt", "w")
    arquivo.write("")
    arquivo.close
    arquivo = open("CodigoIntermediario.txt", "a")

    tokens = (tabela_lexica[tabela_lexica.columns[0:1:]]).values
    lexemas = (tabela_lexica[tabela_lexica.columns[1:2:]]).values
    numLinhas = (tabela_lexica[tabela_lexica.columns[2:3:]]).values

    indices_funcoes = tabela_sintatica.loc[tabela_sintatica['Token'] == "funcao"].index.to_numpy()
    lexemas_funcoes = tabela_sintatica.loc[indices_funcoes, 'Lexema'].values

    tokens_lines = create_line_tokens()
    lexemas_lines = create_line_lexemas()

    loop_geracao(tabela_lexica)


def loop_geracao(tabela):
    adicionar_identificador_arquivo(tabela)


def adicionar_identificador_arquivo(tabela):
    aux = 0
    for index, linha in tabela.iterrows():
        lista_lexemas = get_line_lexemas(linha['linha'])
        lista_tokens = get_line_tokens(linha['linha'])
        if (linha['Token'] == 'identificador' and aux == 1 and lista_tokens[0] == 'tipo'):
            if(lista_lexemas[3] not in lexemas_funcoes):
                linha_lexemas = ' '.join(lista_lexemas)
                arquivo.write(linha_lexemas + '\n')
        aux += 1
        if (linha['Token'] == 'ponto_virgula' or linha['Token'] == 'abre_chave' or linha['Token'] == 'fecha_chave'):
            aux = 0


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


def get_line_tokens(linha):
    return tokens_lines[linha].copy()
