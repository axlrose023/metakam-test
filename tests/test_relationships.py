import pytest
from app.models import Cake, Bakery


def test_add_bakery_to_cake(client, db):
    cake = Cake(name='Carrot Cake', flavor='Carrot', price=18.0)
    bakery = Bakery(name='Health Bakery', location='123 Healthy St', rating=5)
    db.session.add(cake)
    db.session.add(bakery)
    db.session.commit()

    response = client.post(f'/api/v1/cakes/{cake.id}/bakeries/{bakery.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Bakery added to cake'

    updated_cake = db.session.get(Cake, cake.id)
    assert bakery in updated_cake.bakeries


def test_remove_bakery_from_cake(client, db):
    cake = Cake(name='Fruit Cake', flavor='Mixed Fruit', price=19.0)
    bakery = Bakery(name='Fruit Bakery', location='456 Fruit St', rating=4)
    cake.bakeries.append(bakery)
    db.session.add(cake)
    db.session.commit()

    response = client.delete(f'/api/v1/cakes/{cake.id}/bakeries/{bakery.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Bakery removed from cake'

    updated_cake = Cake.query.get(cake.id)
    assert bakery not in updated_cake.bakeries


def test_add_existing_bakery_to_cake(client, db):
    cake = Cake(name='Cheesecake', flavor='Cheese', price=21.0)
    bakery = Bakery(name='Cheese Bakery', location='789 Cheese St', rating=5)
    cake.bakeries.append(bakery)
    db.session.add(cake)
    db.session.commit()

    response = client.post(f'/api/v1/cakes/{cake.id}/bakeries/{bakery.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Bakery added to cake'

    updated_cake = Cake.query.get(cake.id)
    assert updated_cake.bakeries.count(bakery) == 1


def test_remove_nonexistent_bakery_from_cake(client, db):
    cake = Cake(name='Banana Cake', flavor='Banana', price=17.0)
    bakery = Bakery(name='Banana Bakery', location='101 Banana St', rating=3)
    db.session.add(cake)
    db.session.add(bakery)
    db.session.commit()

    response = client.delete(f'/api/v1/cakes/{cake.id}/bakeries/{bakery.id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Bakery removed from cake'

    updated_cake = Cake.query.get(cake.id)
    assert bakery not in updated_cake.bakeries
