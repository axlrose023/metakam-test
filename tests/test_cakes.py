import pytest
from app.models import Cake, Bakery


def test_get_cakes(client):
    response = client.get('/api/v1/cakes')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_cake(client, db):
    data = {
        'name': 'Red Velvet Cake',
        'flavor': 'Red Velvet',
        'price': 25.00,
        'available': True
    }
    response = client.post('/api/v1/cakes', json=data)
    assert response.status_code == 201
    cake = response.get_json()
    assert cake['name'] == data['name']
    assert cake['flavor'] == data['flavor']
    assert cake['price'] == data['price']
    assert cake['available'] == data['available']


def test_get_cake(client, db):
    cake = Cake(name='Chocolate Cake', flavor='Chocolate', price=20.0)
    db.session.add(cake)
    db.session.commit()
    response = client.get(f'/api/v1/cakes/{cake.id}')
    assert response.status_code == 200
    cake_data = response.get_json()
    assert cake_data['name'] == 'Chocolate Cake'
    assert cake_data['flavor'] == 'Chocolate'


def test_update_cake(client, db):
    cake = Cake(name='Vanilla Cake', flavor='Vanilla', price=15.0)
    db.session.add(cake)
    db.session.commit()
    update_data = {'price': 18.0}
    response = client.put(f'/api/v1/cakes/{cake.id}', json=update_data)
    assert response.status_code == 200
    updated_cake = response.get_json()
    assert updated_cake['price'] == 18.0


def test_delete_cake(client, db):
    cake = Cake(name='Strawberry Cake', flavor='Strawberry', price=22.0)
    db.session.add(cake)
    db.session.commit()
    response = client.delete(f'/api/v1/cakes/{cake.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Cake deleted successfully'
    response = client.get(f'/api/v1/cakes/{cake.id}')
    assert response.status_code == 404


def test_create_cake_no_data(client):
    response = client.post('/api/v1/cakes', content_type='application/json')
    assert response.status_code == 400


def test_create_cake_invalid_price(client):
    data = {
        'name': 'Negative Price Cake',
        'flavor': 'Lemon',
        'price': -5.0,
        'available': True
    }
    response = client.post('/api/v1/cakes', json=data)
    assert response.status_code == 422
    errors = response.get_json()
    assert 'price' in errors
    assert errors['price'][0] == 'Price must be a positive number.'


def test_create_cake_missing_fields(client):
    data = {'name': 'Incomplete Cake'}
    response = client.post('/api/v1/cakes', json=data)
    assert response.status_code == 422
    errors = response.get_json()
    assert 'flavor' in errors
    assert 'price' in errors


def test_get_cakes_with_pagination(client, db):
    for i in range(15):
        cake = Cake(name=f'Cake {i}', flavor='Vanilla', price=10.0 + i)
        db.session.add(cake)
    db.session.commit()

    response = client.get('/api/v1/cakes?page=1&limit=10')
    assert response.status_code == 200
    result = response.get_json()
    assert len(result['cakes']) == 10
    assert result['total_pages'] == 2
    assert result['current_page'] == 1
    assert result['total_items'] == 18

    response = client.get('/api/v1/cakes?page=2&limit=10')
    assert response.status_code == 200
    result = response.get_json()
    assert len(result['cakes']) == 8
    assert result['total_pages'] == 2
    assert result['current_page'] == 2


def test_get_cakes_with_flavor_filter(client, db):
    cake1 = Cake(name='Chocolate Cake', flavor='Mango-Chocolate', price=20.0)
    cake2 = Cake(name='Vanilla Cake', flavor='Vanilla', price=15.0)
    db.session.add(cake1)
    db.session.add(cake2)
    db.session.commit()

    response = client.get('/api/v1/cakes?flavor=Mango-Chocolate')
    assert response.status_code == 200
    result = response.get_json()
    assert len(result) == 1
    assert result[0]['flavor'] == 'Mango-Chocolate'


def test_get_cakes_with_price_filter(client, db):
    cake1 = Cake(name='Expensive Cake', flavor='Chocolate', price=1.0)
    cake2 = Cake(name='Affordable Cake', flavor='Vanilla', price=2.25)
    db.session.add(cake1)
    db.session.add(cake2)
    db.session.commit()

    response = client.get('/api/v1/cakes?max_price=2.0')
    assert response.status_code == 200
    result = response.get_json()
    assert len(result) == 1
    assert result[0]['price'] == 1.0
