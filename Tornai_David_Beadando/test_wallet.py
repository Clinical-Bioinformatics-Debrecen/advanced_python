import pytest
from app import app, db, Expense

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    app.config['WTF_CSRF_ENABLED'] = False 

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_index_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    # MÓDOSÍTÁS: Az új címet keressük
    assert 'Pénztárca (költés követő)'.encode('utf-8') in response.data

def test_add_valid_expense(client):
    response = client.post('/add', data={
        'title': 'Teszt Pizza',
        'amount': '2500',
        # MÓDOSÍTÁS: Új kategória név használata
        'category': 'Élelmiszer/Étkezés' 
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Teszt Pizza' in response.data
    assert b'Sikeres' in response.data

def test_add_negative_amount_error(client):
    response = client.post('/add', data={
        'title': 'Hibás tétel',
        'amount': '-500',
        'category': 'Egyéb'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Hiba' in response.data
    assert b'pozit' in response.data

def test_add_invalid_number_format(client):
    response = client.post('/add', data={
        'title': 'Hibás szám',
        'amount': 'kettőezer',
        'category': 'Egyéb'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Hiba' in response.data

def test_edit_expense_success(client):
    """Szerkesztés funkció tesztelése."""
    client.post('/add', data={'title': 'Régi', 'amount': '1000', 'category': 'Egyéb'})
    
    response = client.post('/edit/1', data={
        'title': 'Új Név',
        'amount': '2000',
        # MÓDOSÍTÁS: Új kategória név
        'category': 'Élelmiszer/Étkezés'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Sikeres' in response.data 
    assert b'2000 Ft' in response.data 
    assert 'Új Név'.encode('utf-8') in response.data

def test_edit_expense_invalid(client):
    client.post('/add', data={'title': 'Régi', 'amount': '1000', 'category': 'Egyéb'})
    
    response = client.post('/edit/1', data={
        'title': 'Új Név',
        'amount': '-500',
        # MÓDOSÍTÁS: Új kategória név
        'category': 'Élelmiszer/Étkezés'
    }, follow_redirects=True)
    
    assert b'Hiba' in response.data 
    assert b'pozit' in response.data

def test_delete_expense(client):
    client.post('/add', data={'title': 'Torlendo', 'amount': '100', 'category': 'Egyéb'})
    
    response = client.get('/delete/1', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Torlendo' not in response.data
    assert 'törölve'.encode('utf-8') in response.data