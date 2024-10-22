import pytest
from app.models import Bakery

def test_get_bakeries(client):
    response = client.get('/api/v1/bakeries')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_create_bakery(client, db):
    data = {
        'name': 'Downtown Bakery',
        'location': '123 Baker St',
        'rating': 5
    }
    response = client.post('/api/v1/bakeries', json=data)
    assert response.status_code == 201
    bakery = response.get_json()
    assert bakery['name'] == data['name']
    assert bakery['location'] == data['location']
    assert bakery['rating'] == data['rating']

def test_get_bakery(client, db):
    bakery = Bakery(name='Uptown Bakery', location='456 Baker St', rating=4)
    db.session.add(bakery)
    db.session.commit()
    response = client.get(f'/api/v1/bakeries/{bakery.id}')
    assert response.status_code == 200
    bakery_data = response.get_json()
    assert bakery_data['name'] == 'Uptown Bakery'
    assert bakery_data['location'] == '456 Baker St'

def test_update_bakery(client, db):
    bakery = Bakery(name='Midtown Bakery', location='789 Baker St', rating=3)
    db.session.add(bakery)
    db.session.commit()
    update_data = {'rating': 5}
    response = client.put(f'/api/v1/bakeries/{bakery.id}', json=update_data)
    assert response.status_code == 200
    updated_bakery = response.get_json()
    assert updated_bakery['rating'] == 5

def test_delete_bakery(client, db):
    bakery = Bakery(name='Oldtown Bakery', location='111 Old St', rating=2)
    db.session.add(bakery)
    db.session.commit()
    response = client.delete(f'/api/v1/bakeries/{bakery.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Bakery deleted successfully'
    # Verify deletion
    response = client.get(f'/api/v1/bakeries/{bakery.id}')
    assert response.status_code == 404

def test_create_bakery_no_data(client):
    response = client.post('/api/v1/bakeries', content_type='application/json')
    assert response.status_code == 400  # Expecting a 400 Bad Request due to missing data

def test_create_bakery_invalid_rating(client):
    data = {
        'name': 'Invalid Rating Bakery',
        'location': '999 Baker St',
        'rating': 6  # Invalid rating, should be between 1 and 5
    }
    response = client.post('/api/v1/bakeries', json=data)
    assert response.status_code == 422
    errors = response.get_json()
    assert 'rating' in errors
    assert errors['rating'][0] == 'Rating must be between 1 and 5.'

def test_create_bakery_missing_fields(client):
    data = {'name': 'Incomplete Bakery'}
    response = client.post('/api/v1/bakeries', json=data)
    assert response.status_code == 422
    errors = response.get_json()
    assert 'location' in errors
    assert 'rating' in errors
