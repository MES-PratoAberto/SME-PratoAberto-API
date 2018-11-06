

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
