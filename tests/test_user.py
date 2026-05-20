from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи (из базы данных)
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
    response = client.get("/api/v1/user", params={'email': 'nonexistent@example.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_email = "newuser@example.com"
    response = client.post("/api/v1/user", json={"name": "New User", "email": new_email})
    assert response.status_code == 201
    user_id = response.json()
    assert isinstance(user_id, int)
    
    # Проверяем, что пользователя можно получить
    get_response = client.get("/api/v1/user", params={'email': new_email})
    assert get_response.status_code == 200
    assert get_response.json()['name'] == "New User"
    assert get_response.json()['email'] == new_email

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_email = users[0]['email']
    response = client.post("/api/v1/user", json={"name": "Duplicate", "email": existing_email})
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
    # Создаём пользователя для удаления
    email_to_delete = "todelete@example.com"
    create_response = client.post("/api/v1/user", json={"name": "To Delete", "email": email_to_delete})
    assert create_response.status_code == 201
    
    # Удаляем
    delete_response = client.delete("/api/v1/user", params={'email': email_to_delete})
    assert delete_response.status_code == 204
    
    # Проверяем, что после удаления получить пользователя нельзя
    get_response = client.get("/api/v1/user", params={'email': email_to_delete})
    assert get_response.status_code == 404
