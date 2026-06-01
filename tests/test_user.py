from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]


def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@mail.com'})
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Test User',
        'email': 'test.user@mail.com'
    }
    
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    
    # API возвращает ID созданного пользователя
    created_user_id = response.json()
    assert isinstance(created_user_id, int)
    
    # Получаем созданного пользователя по email
    get_response = client.get("/api/v1/user", params={'email': new_user['email']})
    assert get_response.status_code == 200
    
    created_user = get_response.json()
    assert created_user['name'] == new_user['name']
    assert created_user['email'] == new_user['email']
    assert created_user['id'] == created_user_id


def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_user = {
        'name': 'Duplicate User',
        'email': users[0]['email']  # email Ивана Иванова
    }
    
    response = client.post("/api/v1/user", json=existing_user)
    # API возвращает 409 Conflict для дубликата email
    assert response.status_code == 409
    # Проверяем, что есть сообщение об ошибке
    assert 'detail' in response.json()


def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаём пользователя для удаления
    user_to_delete = {
        'name': 'To Delete',
        'email': 'todelete@mail.com'
    }
    
    create_response = client.post("/api/v1/user", json=user_to_delete)
    assert create_response.status_code == 201
    
    # Удаляем созданного пользователя
    delete_response = client.delete("/api/v1/user", params={'email': user_to_delete['email']})
    assert delete_response.status_code == 204
    
    # Проверяем, что пользователь действительно удалён
    get_response = client.get("/api/v1/user", params={'email': user_to_delete['email']})
    assert get_response.status_code == 404
