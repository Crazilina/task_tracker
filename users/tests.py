from django.test import TestCase
from users.models import User
from users.serializers import UserSerializer


class UserModelTest(TestCase):
    """
    Тесты для проверки модели User.
    """

    def test_user_str(self):
        """
        Тестирует строковое представление модели User.
        """
        # Создаем тестового пользователя
        user = User.objects.create(email="test@example.com")

        # Проверяем, что строковое представление возвращает email пользователя
        self.assertEqual(str(user), "test@example.com")


class UserSerializerTest(TestCase):
    """
    Тесты для проверки сериализатора UserSerializer.
    """

    def setUp(self):
        """
        Метод для подготовки тестовых данных. Создаем тестового пользователя.
        """
        self.user = User.objects.create(
            email="test@example.com",
            first_name="Иван",
            last_name="Иванов"
        )

    def test_user_serialization(self):
        """
        Тест сериализации данных пользователя.
        Проверяет, что данные пользователя корректно преобразуются в JSON.
        """
        serializer = UserSerializer(self.user)
        data = serializer.data

        # Проверяем корректность данных после сериализации
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)

    def test_user_deserialization(self):
        """
        Тест десериализации данных пользователя.
        Проверяет, что данные корректно преобразуются из JSON в модель.
        """
        data = {
            'email': 'new@example.com',
            'first_name': 'Алексей',
            'last_name': 'Алексеев'
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Проверяем корректность данных после десериализации
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])

    def test_user_validation(self):
        """
        Тест валидации данных пользователя.
        Проверяет, что сериализатор правильно валидирует данные.
        """
        invalid_data = {
            'email': '',  # Поле email пустое, что вызовет ошибку
            'first_name': '',
            'last_name': ''
        }

        serializer = UserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        # Поскольку поля first_name и last_name не обязательные, проверяем только email
