import os
import unittest
from decouple import config
from app import app
import json
from flask_mysqldb import MySQL


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_hello_world(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_auth(self):
        response = self.app.post('/login', data=dict(
            username='test',
            password='test'
        ), follow_redirects=True)
        self.assertIn('access_token', json.loads(response.data))

    def test_create_user(self):
        response = self.app.post('/login', data=dict(
            username='test',
            password='test'
        ), follow_redirects=True)

        token = json.loads(response.data)['access_token']
        headers = {
            'Authorization': 'Bearer {}'.format(token)
        }

        response = self.app.post('/users',
            data=dict(
                username='new_user',
                password='no_secrets',
                admin='True',
                email='new_user@example.com'
            ),
            headers=headers,
            follow_redirects=True
        )

        self.assertTrue(response.status_code == 201)

        response = self.app.post('/users?username=new_user', follow_redirects=True)
        self.assertTrue(response.status_code == 200)

    def test_get_users(self):
        response = self.app.get('/users', follow_redirects=True)
        self.assertTrue(response.status_code == 200 or response.status_code == 404)

    def test_get_single_user(self):
        response = self.app.get('/users/1', follow_redirects=True)
        self.assertTrue(response.status_code == 200 or response.status_code == 404)


if __name__ == "__main__":
    unittest.main()

