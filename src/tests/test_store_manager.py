"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app
from db import get_sqlalchemy_session
from orders.models.user import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    # Supprimez l'utilisateur de test s'il existe déjà (contrainte UNIQUE sur email)
    session = get_sqlalchemy_session()
    existing_user = session.query(User).filter_by(email='test@example.com').first()
    if existing_user:
        client.delete(f'/users/{existing_user.id}')
    session.close()

    # Créez un utilisateur nécessaire pour passer une commande
    user_response = client.post('/users',
                                data=json.dumps({'name': 'Test User', 'email': 'test@example.com'}),
                                content_type='application/json')
    assert user_response.status_code == 201
    user_id = user_response.get_json()['user_id']

    # 1. Créez un article (`POST /products`)
    product_data = {'name': 'Some Item', 'sku': '12345', 'price': 99.90}
    response = client.post('/products',
                          data=json.dumps(product_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert data['product_id'] > 0
    product_id = data['product_id']

    # 2. Ajoutez 5 unités au stock de cet article (`POST /stocks`)
    stock_response = client.post('/stocks',
                                 data=json.dumps({'product_id': product_id, 'quantity': 5}),
                                 content_type='application/json')
    assert stock_response.status_code == 201

    # 3. Vérifiez le stock, votre article devra avoir 5 unités dans le stock (`GET /stocks/:id`)
    get_stock_1 = client.get(f'/stocks/{product_id}')
    assert get_stock_1.status_code == 200
    assert get_stock_1.get_json()['quantity'] == 5

    # 4. Faites une commande de 2 unités de l'article que vous avez créé (`POST /orders`)
    order_response = client.post('/orders',
                                 data=json.dumps({'user_id': user_id, 'items': [{'product_id': product_id, 'quantity': 2}]}),
                                 content_type='application/json')
    assert order_response.status_code == 201
    order_id = order_response.get_json()['order_id']

    # 5. Vérifiez le stock encore une fois (`GET /stocks/:id`)
    get_stock_2 = client.get(f'/stocks/{product_id}')
    assert get_stock_2.status_code == 200
    assert get_stock_2.get_json()['quantity'] == 3  # 5 - 2 = 3

    # 6. Étape extra: supprimez la commande (`DELETE /orders/:id`) et vérifiez le stock de nouveau
    delete_response = client.delete(f'/orders/{order_id}')
    assert delete_response.status_code == 200
    assert delete_response.get_json()['deleted'] == True

    get_stock_3 = client.get(f'/stocks/{product_id}')
    assert get_stock_3.status_code == 200
    assert get_stock_3.get_json()['quantity'] == 5  # Le stock remonte à 5 après suppression de la commande