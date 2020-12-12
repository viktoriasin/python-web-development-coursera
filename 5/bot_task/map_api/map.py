import requests


def distance_matrix(client, origins, destinations=None, informat=None, outformat=None, callback=None,
                    body_param_alltoall=None, body_param_manytoone=None):
    # если destinations None то должен быть тип body_param_alltoall True или body_para_manytoone Ture
    if body_param_manytoone and body_param_alltoall:
        raise ValueError('ManyToOne body parameters and allToAll body parameter could not been set to True '
                         'simultaneously')
    if destinations is None and not body_param_alltoall:
        raise ValueError('If destination parametr of distance_matrix function is None'
                         'body_param_alltoall must be True')
    if destinations and body_param_alltoall:
        raise ValueError('If destination parametr of distance_matrix function is True'
                         'body_param_alltoall must not be True')
    if body_param_manytoone and destinations:
        if len(destinations) > 1:
            raise ValueError('Length of destinations must be one when body_param_manytoone is set')
    params = {}
    if informat:
        params['inFormat'] = informat

    if outformat:
        params['outFormat'] = outformat

    if callback:
        params['callback'] = callback

    body = {"locations": []}

    if destinations and body_param_manytoone:
        body['locations'].extend(destinations)
        body['locations'].extend(origins)
    elif destinations:
        body['locations'].extend(origins)
        body['locations'].extend(destinations)
    elif body_param_alltoall:
        body['locations'].extend(origins)
    extra_params = {}
    if body_param_alltoall is not None:
        extra_params['allToAll'] = body_param_alltoall
    if body_param_manytoone is not None:
        extra_params['manyToOne'] = body_param_manytoone
    if extra_params:
        body['options'] = extra_params
    return client._request('/directions/v2/routematrix', params=params,  post_json=body)

