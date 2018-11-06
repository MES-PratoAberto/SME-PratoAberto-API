def update_data(data, request):
    if request.args.get('data_inicial'):
        data.update({'$gte': request.args['data_inicial']})
    if request.args.get('data_final'):
        data.update({'$lte': request.args['data_final']})
    return data

def fill_data_query(query, data, request):
    if data:
        query['data'] = str(data)
    else:
        data = {}
        data = update_data(data, request)
        if data:
            query['data'] = data
    return query

def cardapios_from_db(cardapios, request):
    limit = int(request.args.get('limit', 0))
    page = int(request.args.get('page', 0))

    if page and limit:
        cardapios = cardapios.skip(limit*(page-1)).limit(limit)
    elif limit:
        cardapios = cardapios.limit(limit)
    return cardapios

def define_query_from_request(query, request, ind_idade_reversed):
    if request.args.get('agrupamento'):
        query['agrupamento'] = request.args['agrupamento']
    if request.args.get('tipo_atendimento'):
        query['tipo_atendimento'] = request.args['tipo_atendimento']
    if request.args.get('tipo_unidade'):
        query['tipo_unidade'] = request.args['tipo_unidade']
    if request.args.get('idade'):
        if ind_idade_reversed:
            query['idade'] = idades_reversed.get(request.args['idade'])
        else :
            query['idade'] = request.args['idade']

    return query
