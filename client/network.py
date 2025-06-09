import requests

BASE_URL = "https://levelking-web.onrender.com/api/"


class APIClient:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.username = ''

    def register_user(self, username: str, password: str) -> bool:
        url = BASE_URL + 'auth/register/'
        data = {
            'username': username,
            'password': password,
            'password2': password  # <- обов'язково!
        }
        response = requests.post(url, json=data)
        print('Register:', response.status_code, response.text)
        return response.status_code == 201

    def login(self, username: str, password: str) -> bool:
        """
        Авторизація користувача. Отримання токенів.
        """
        url = BASE_URL + 'auth/token/'
        data = {'username': username, 'password': password}
        response = requests.post(url, json=data)  # 👈 Тут теж краще json=
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens['access']
            self.refresh_token = tokens['refresh']
            self.username = username
            return True
        print('Login:', response.status_code, response.text)
        return False

    def _headers(self):
        """
        Заголовки з JWT токеном.
        """
        return {'Authorization': f'Bearer {self.access_token}'}

    def get_public_levels(self):
        """
        Отримати всі публічні рівні.
        """
        url = BASE_URL + 'levels/public/'
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        print('Public levels error:', response.status_code, response.text)
        return []

    def get_level_by_id(self, level_id: int):
        """
        Отримати рівень по ID.
        """
        url = BASE_URL + f'levels/{level_id}/'
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        print('Level by ID error:', response.status_code, response.text)
        return None

    def get_change_request_by_id(self, change_id):
        """
        Отримати конкретний запит на зміну за його ID.
        """
        url = BASE_URL + f'levels/changes/{change_id}/'
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        print('Change request error:', response.status_code, response.text)
        return None

    def upload_level(self, title, description, data, is_public=True):
        """
        Завантаження нового рівня на сервер.
        """
        url = BASE_URL + 'levels/upload/'
        payload = {
            'title': title,
            'description': description,
            'data': data,
            'is_public': is_public
        }
        response = requests.post(url, headers=self._headers(), json=payload)
        return response.status_code == 201

    def get_public_levels_by_author(self, username):
        """
        Отримати публічні рівні певного автора.
        """
        url = BASE_URL + f'levels/public/by-author/{username}/'
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        return []

    def propose_change(self, level_id, data, comment=""):
        """
        Надіслати пропозицію змін до чужого рівня.
        """
        url = BASE_URL + f'levels/{level_id}/propose-change/'
        payload = {
            'data': data,
            'comment': comment
        }
        response = requests.post(url, headers=self._headers(), json=payload)
        return response.status_code == 201

    def view_change_requests(self):
        """
        Отримати список усіх запитів на зміну до власних рівнів.
        """
        url = BASE_URL + 'levels/changes/'
        response = requests.get(url, headers=self._headers())
        if response.status_code == 200:
            return response.json()
        print('Change requests error:', response.status_code, response.text)
        return []

    def accept_change(self, level_id, change_id):
        """
        Схвалити зміну до рівня.
        """
        url = BASE_URL + f'levels/{level_id}/changes/{change_id}/accept/'
        response = requests.post(url, headers=self._headers())
        return response.status_code == 200

    def reject_change(self, level_id, change_id):
        """
        Відхилити зміну до рівня.
        """
        url = BASE_URL + f'levels/{level_id}/changes/{change_id}/reject/'
        response = requests.post(url, headers=self._headers())
        return response.status_code == 200

    def delete_level(self, level_id):
        """
        Видалити власний рівень.
        """
        url = BASE_URL + f'levels/{level_id}/delete/'
        response = requests.delete(url, headers=self._headers())
        return response.status_code == 204

    def edit_level(self, level_id, **kwargs):
        """
        Редагувати власний рівень. Можна передати:
        - title
        - description
        - data
        - is_public
        """
        url = BASE_URL + f'levels/{level_id}/edit/'
        response = requests.patch(url, headers=self._headers(), json=kwargs)
        return response.status_code == 200

    def delete_account(self) -> bool:
        """
        Видалення власного облікового запису користувачем.
        """
        url = BASE_URL + 'auth/delete/'
        response = requests.delete(url, headers=self._headers())
        print("Delete account:", response.status_code, response.text)
        return response.status_code == 204