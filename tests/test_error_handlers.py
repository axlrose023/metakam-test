def test_not_found_error(client):
    response = client.get('/api/v1/cakes/9999')
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Resource not found'


def test_validation_error(client):
    data = {'name': '', 'price': 'not a number'}
    response = client.post('/api/v1/cakes', json=data)
    assert response.status_code == 422
    errors = response.get_json()
    assert 'flavor' in errors
    assert 'price' in errors


def test_internal_server_error(client):
    response = client.get('/api/v1/trigger-500')
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['error'] == 'An unexpected error occurred'
