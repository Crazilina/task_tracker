from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from task_tracker.models import Employee, Task
from users.models import User
from django.test import TestCase
from task_tracker.serializers import TaskSummarySerializer
import datetime


class EmployeeAPITestCase(APITestCase):
    """
    Тесты для проверки операций CRUD с моделью Employee.
    """

    def setUp(self):
        """
        Метод для подготовки тестовых данных. Создает тестового пользователя и аутентифицирует его.
        """
        # Создаем пользователя без поля username
        self.user = User.objects.create(email="test@test.com", password="password123")
        self.client.force_authenticate(user=self.user)

        # Создаем тестового сотрудника
        self.employee = Employee.objects.create(
            first_name="Алексей",
            last_name="Сидоров",
            middle_name="Игоревич",
            position="Менеджер",
            department="Маркетинг",
            hired_date="2022-02-01"
        )

    def test_employee_create(self):
        """
        Тест создания нового сотрудника.
        Проверяет, что сотрудник успешно создается и количество сотрудников увеличивается.
        """
        # URL для создания сотрудника
        url = reverse("task_tracker:employee-create")

        # Данные для создания нового сотрудника
        data = {
            "first_name": "Алексей",
            "last_name": "Сидоров",
            "middle_name": "Игоревич",
            "position": "Менеджер",
            "department": "Маркетинг",
            "hired_date": "2022-02-01"
        }

        # Отправляем POST-запрос для создания сотрудника
        response = self.client.post(url, data)

        # Проверяем, что запрос завершился успешно с кодом 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что количество сотрудников в базе данных увеличилось на 1
        self.assertEqual(Employee.objects.count(), 2)

    def test_employee_invalid_first_name(self):
        """
        Тест валидации: имя должно содержать только буквы.
        """
        url = reverse("task_tracker:employee-create")
        data = {
            "first_name": "1234",  # Невалидное имя
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "position": "Менеджер",
            "department": "Маркетинг",
            "hired_date": "2022-02-01"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Имя должно содержать только буквы.", response.json()['first_name'][0])

    def test_employee_invalid_last_name(self):
        """
        Тест валидации: фамилия должна содержать только буквы.
        """
        url = reverse("task_tracker:employee-create")
        data = {
            "first_name": "Иван",
            "last_name": "1234",  # Невалидная фамилия
            "middle_name": "Иванович",
            "position": "Менеджер",
            "department": "Маркетинг",
            "hired_date": "2022-02-01"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Фамилия должна содержать только буквы.", response.json()['last_name'][0])

    def test_employee_invalid_middle_name(self):
        """
        Тест валидации: отчество должно содержать только буквы.
        """
        url = reverse("task_tracker:employee-create")
        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "1234",  # Невалидное отчество
            "position": "Менеджер",
            "department": "Маркетинг",
            "hired_date": "2022-02-01"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Отчество должно содержать только буквы.", response.json()['middle_name'][0])

    def test_employee_invalid_hired_date(self):
        """
        Тест валидации: дата приема на работу не может быть в будущем.
        """
        url = reverse("task_tracker:employee-create")
        future_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "middle_name": "Иванович",
            "position": "Менеджер",
            "department": "Маркетинг",
            "hired_date": future_date  # Будущая дата
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Дата приема на работу не может быть в будущем.", response.json()['hired_date'][0])

    def test_employee_retrieve(self):
        """
        Тест получения информации о сотруднике по его ID.
        """
        # URL для получения сотрудника по ID
        url = reverse("task_tracker:employee-detail", args=(self.employee.pk,))

        # Отправляем GET-запрос для получения данных о сотруднике
        response = self.client.get(url)
        data = response.json()

        # Проверяем, что запрос завершился успешно с кодом 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что возвращенные данные совпадают с данными созданного сотрудника
        self.assertEqual(data.get("first_name"), self.employee.first_name)
        self.assertEqual(data.get("last_name"), self.employee.last_name)
        self.assertEqual(data.get("middle_name"), self.employee.middle_name)
        self.assertEqual(data.get("position"), self.employee.position)
        self.assertEqual(data.get("hired_date"), str(self.employee.hired_date))

    def test_employee_update(self):
        """
        Тест обновления информации о сотруднике.
        Обновляется отдел сотрудника.
        """
        url = reverse("task_tracker:employee-update", args=(self.employee.pk,))
        data = {
            "department": "Бухгалтерия"
        }
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            data.get("department"), "Бухгалтерия"
        )

    def test_employee_delete(self):
        """
        Тест удаления сотрудника.
        Проверяет, что сотрудник успешно удаляется и количество сотрудников уменьшается.
        """
        url = reverse("task_tracker:employee-delete", args=(self.employee.pk,))
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )
        self.assertEqual(
            Employee.objects.all().count(), 0
        )

    def test_employee_list(self):
        """
        Тест вывода списка сотрудников.
        Проверяет, что список сотрудников выводится корректно.
        """
        # Создаем еще одного сотрудника для проверки списка
        Employee.objects.create(
            first_name="Иван",
            last_name="Петров",
            middle_name="Иванович",
            position="Тестировщик",
            department="Тестирование",
            hired_date="2023-03-15"
        )

        url = reverse("task_tracker:employee-list")
        response = self.client.get(url)
        data = response.json()

        # Проверяем, что запрос завершился успешно с кодом 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что в списке сотрудников два элемента
        self.assertEqual(len(data), 2)

        # Проверяем, что данные первого сотрудника совпадают с ожидаемыми
        self.assertEqual(data[0]['first_name'], self.employee.first_name)
        self.assertEqual(data[0]['last_name'], self.employee.last_name)

        # Проверяем, что данные второго сотрудника совпадают с ожидаемыми
        self.assertEqual(data[1]['first_name'], "Иван")
        self.assertEqual(data[1]['last_name'], "Петров")


class BusyEmployeesListAPITestCase(APITestCase):
    """
    Тесты для проверки эндпоинта получения списка сотрудников,
    отсортированных по количеству активных задач и срокам выполнения.
    """

    def setUp(self):
        """
        Метод для подготовки тестовых данных. Создает тестового пользователя и несколько сотрудников.
        """
        self.user = User.objects.create(email="test@test.com", password="password123")
        self.client.force_authenticate(user=self.user)

        # Создаем нескольких сотрудников
        self.employee1 = Employee.objects.create(first_name="Иван", last_name="Иванов")
        self.employee2 = Employee.objects.create(first_name="Петр", last_name="Петров")
        self.employee3 = Employee.objects.create(first_name="Анна", last_name="Сидорова")

        # Создаем задачи для сотрудников с указанием due_date
        self.task1 = Task.objects.create(name="Задача 1", assigned_to=self.employee1, status='new',
                                         due_date="2024-09-01")
        self.task2 = Task.objects.create(name="Задача 2", assigned_to=self.employee1, status='in_progress',
                                         due_date="2024-09-10")
        self.task3 = Task.objects.create(name="Задача 3", assigned_to=self.employee2, status='new',
                                         due_date="2024-09-15")
        self.task4 = Task.objects.create(name="Задача 4", assigned_to=self.employee3, status='new',
                                         due_date="2024-08-01")
        self.task5 = Task.objects.create(name="Задача 5", assigned_to=self.employee3, status='in_progress',
                                         due_date="2024-08-15")

    def test_busy_employees_list(self):
        """
        Тест получения списка сотрудников, отсортированных по количеству активных задач
        и по срокам выполнения задач.
        """
        url = reverse("task_tracker:busy-employees")
        response = self.client.get(url)

        # Проверяем, что запрос завершился успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем правильность сортировки сотрудников по количеству активных задач и срокам выполнения
        data = response.json()
        self.assertEqual(len(data), 3)

        # Проверяем, что задачи включены в вывод для каждого сотрудника
        self.assertEqual(data[0]['first_name'], "Анна")  # У нее 2 задачи, earliest_due_date="2024-08-01"
        self.assertEqual(data[0]['active_task_count'], 2)
        self.assertEqual(len(data[0]['tasks']), 2)
        self.assertEqual(data[0]['tasks'][0]['name'], "Задача 4")
        self.assertEqual(data[0]['tasks'][1]['name'], "Задача 5")

        self.assertEqual(data[1]['first_name'], "Иван")  # У него 2 задачи, earliest_due_date="2024-09-01"
        self.assertEqual(data[1]['active_task_count'], 2)
        self.assertEqual(len(data[1]['tasks']), 2)
        self.assertEqual(data[1]['tasks'][0]['name'], "Задача 1")
        self.assertEqual(data[1]['tasks'][1]['name'], "Задача 2")

        self.assertEqual(data[2]['first_name'], "Петр")  # У него 1 задача, earliest_due_date="2024-09-15"
        self.assertEqual(data[2]['active_task_count'], 1)
        self.assertEqual(len(data[2]['tasks']), 1)
        self.assertEqual(data[2]['tasks'][0]['name'], "Задача 3")

    def test_no_active_tasks(self):
        """
        Тест, когда у сотрудников нет активных задач.
        """
        # Удаляем все задачи
        Task.objects.all().delete()

        url = reverse("task_tracker:busy-employees")
        response = self.client.get(url)

        # Проверяем, что запрос завершился успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Все сотрудники должны быть в списке, но без задач
        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['first_name'], "Иван")
        self.assertEqual(data[0]['active_task_count'], 0)
        self.assertEqual(len(data[0]['tasks']), 0)

        self.assertEqual(data[1]['first_name'], "Петр")
        self.assertEqual(data[1]['active_task_count'], 0)
        self.assertEqual(len(data[1]['tasks']), 0)

        self.assertEqual(data[2]['first_name'], "Анна")
        self.assertEqual(data[2]['active_task_count'], 0)
        self.assertEqual(len(data[2]['tasks']), 0)

    def test_employees_with_equal_tasks(self):
        """
        Тест, когда у сотрудников одинаковое количество активных задач.
        Проверяет, что сотрудники с одинаковым количеством активных задач сортируются по срокам выполнения.
        """
        # Удаляем все существующие задачи, чтобы тесты были изолированы
        Task.objects.all().delete()

        # Создаем задачи с одинаковым количеством активных задач, но с разными сроками выполнения
        Task.objects.create(name="Задача 1", assigned_to=self.employee1, status='new', due_date="2024-08-05")
        Task.objects.create(name="Задача 2", assigned_to=self.employee2, status='new', due_date="2024-08-10")
        Task.objects.create(name="Задача 3", assigned_to=self.employee3, status='new', due_date="2024-08-01")

        url = reverse("task_tracker:busy-employees")
        response = self.client.get(url)

        # Проверяем, что запрос завершился успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что все сотрудники возвращены и правильно отсортированы
        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['first_name'], "Анна")  # У нее earliest_due_date="2024-08-01"
        self.assertEqual(data[1]['first_name'], "Иван")  # У него earliest_due_date="2024-08-05"
        self.assertEqual(data[2]['first_name'], "Петр")  # У него earliest_due_date="2024-08-10"

        # Проверяем задачи для каждого сотрудника
        self.assertEqual(len(data[0]['tasks']), 1)
        self.assertEqual(data[0]['tasks'][0]['name'], "Задача 3")

        self.assertEqual(len(data[1]['tasks']), 1)
        self.assertEqual(data[1]['tasks'][0]['name'], "Задача 1")

        self.assertEqual(len(data[2]['tasks']), 1)
        self.assertEqual(data[2]['tasks'][0]['name'], "Задача 2")


class TaskAPITestCase(APITestCase):
    """
    Тесты для проверки операций CRUD с моделью Task.
    """

    def setUp(self):
        """
        Метод для подготовки тестовых данных. Создает тестового пользователя и сотрудника.
        """
        self.user = User.objects.create(email="test@test.com", password="password123")
        self.client.force_authenticate(user=self.user)

        # Создаем сотрудника, который будет выполнять задачи
        self.employee = Employee.objects.create(first_name="Иван", last_name="Иванов")

    def test_task_create(self):
        """
        Тест создания новой задачи.
        """
        url = reverse("task_tracker:task-create")
        data = {
            "name": "Тестовая задача",
            "description": "Описание задачи",
            "assigned_to": self.employee.id,
            "due_date": "2024-09-15",
            "status": "new",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.all().count(), 1)
        task = Task.objects.get()
        self.assertEqual(task.name, data['name'])
        self.assertEqual(task.description, data['description'])
        self.assertEqual(task.assigned_to, self.employee)
        self.assertEqual(str(task.due_date), data['due_date'])
        self.assertEqual(task.status, data['status'])

    def test_task_invalid_due_date(self):
        """
        Тест валидации: срок выполнения задачи не может быть в прошлом.
        """
        url = reverse("task_tracker:task-create")
        past_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        data = {
            "name": "Тестовая задача",
            "description": "Описание задачи",
            "assigned_to": self.employee.id,
            "due_date": past_date,  # Прошедшая дата
            "status": "new",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Срок выполнения задачи не может быть в прошлом.", response.json()['due_date'][0])

    def test_task_retrieve(self):
        """
        Тест получения информации о задаче по ее ID.
        """
        task = Task.objects.create(name="Задача 1", assigned_to=self.employee, due_date="2024-09-01", status="new")

        url = reverse("task_tracker:task-detail", args=(task.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['name'], task.name)
        self.assertEqual(data['assigned_to'], self.employee.id)
        self.assertEqual(data['status'], task.status)

    def test_task_update(self):
        """
        Тест обновления данных задачи.
        """
        # Создаем тестовую задачу
        task = Task.objects.create(name="Задача 1", assigned_to=self.employee, due_date="2024-09-01", status="new")

        # URL для обновления задачи
        url = reverse("task_tracker:task-update", args=(task.pk,))

        # Данные для обновления задачи
        data = {
            "name": "Обновленная задача",
            "status": "in_progress"
        }

        # Отправляем PATCH-запрос для обновления задачи
        response = self.client.patch(url, data)
        data = response.json()

        # Проверяем, что запрос завершился успешно с кодом 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что имя задачи обновилось
        self.assertEqual(data.get("name"), "Обновленная задача")

        # Проверяем, что статус задачи обновился
        self.assertEqual(data.get("status"), "in_progress")

    def test_task_delete(self):
        """
        Тест удаления задачи.
        """
        task = Task.objects.create(name="Задача 1", assigned_to=self.employee, due_date="2024-09-01", status="new")

        url = reverse("task_tracker:task-delete", args=(task.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.all().count(), 0)

    def test_task_list(self):
        """
        Тест получения списка задач.
        """
        Task.objects.create(name="Задача 1", assigned_to=self.employee, due_date="2024-09-01", status="new")
        Task.objects.create(name="Задача 2", assigned_to=self.employee, due_date="2024-09-15", status="in_progress")

        url = reverse("task_tracker:task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], "Задача 1")
        self.assertEqual(data[1]['name'], "Задача 2")

    def test_task_list_with_invalid_filter(self):
        """
        Тест фильтрации по недопустимому полю.
        """
        url = reverse("task_tracker:task-list")
        # Добавляем недопустимый параметр фильтрации `invalid_field`
        response = self.client.get(url, {'invalid_field': 'some_value'})

        # Ожидаем, что вернется ошибка 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Проверяем, что ответ представляет собой список с сообщением об ошибке
        error_message = response.json()
        self.assertIsInstance(error_message, list)
        self.assertTrue(any("Фильтрация по полю(-ям)" in msg for msg in error_message))

    def test_task_list_with_subtasks_filter_true(self):
        """
        Тест фильтрации задач, у которых есть подзадачи (subtasks=true).
        """
        # Создаем задачи для этого теста
        parent_task = Task.objects.create(
            name="Родительская задача",
            assigned_to=self.employee,
            due_date="2024-09-01",
            status="new"
        )
        subtask = Task.objects.create(
            name="Подзадача",
            parent_task=parent_task,
            assigned_to=self.employee,
            due_date="2024-09-02",
            status="new"
        )

        url = reverse("task_tracker:task-list")
        response = self.client.get(url, {'subtasks': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 1)  # Ожидаем, что будет возвращена только родительская задача
        self.assertEqual(data[0]['id'], parent_task.id)

    def test_task_list_with_subtasks_filter_false(self):
        """
        Тест фильтрации задач, у которых нет подзадач (subtasks=false).
        """
        task_without_subtasks = Task.objects.create(
            name="Задача без подзадач",
            assigned_to=self.employee,
            due_date="2024-09-05",
            status="new"
        )

        url = reverse("task_tracker:task-list")
        response = self.client.get(url, {'subtasks': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 1)  # Должны быть задачи без подзадач
        task_ids = [task['id'] for task in data]
        self.assertIn(task_without_subtasks.id, task_ids)

    def test_task_list_with_has_parent_filter_true(self):
        """
        Тест фильтрации задач, у которых есть родительская задача (has_parent=true).
        """
        parent_task = Task.objects.create(
            name="Родительская задача",
            assigned_to=self.employee,
            due_date="2024-09-01",
            status="new"
        )
        subtask = Task.objects.create(
            name="Подзадача",
            parent_task=parent_task,
            assigned_to=self.employee,
            due_date="2024-09-02",
            status="new"
        )

        url = reverse("task_tracker:task-list")
        response = self.client.get(url, {'has_parent': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 1)  # Ожидаем, что будет возвращена только подзадача
        self.assertEqual(data[0]['id'], subtask.id)

    def test_task_list_with_has_parent_filter_false(self):
        """
        Тест фильтрации задач, у которых нет родительской задачи (has_parent=false).
        """
        parent_task = Task.objects.create(
            name="Родительская задача",
            assigned_to=self.employee,
            due_date="2024-09-01",
            status="new"
        )
        task_without_subtasks = Task.objects.create(
            name="Задача без подзадач",
            assigned_to=self.employee,
            due_date="2024-09-05",
            status="new"
        )

        url = reverse("task_tracker:task-list")
        response = self.client.get(url, {'has_parent': 'false'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 2)  # Должны быть задачи без родительской задачи
        task_ids = [task['id'] for task in data]
        self.assertIn(parent_task.id, task_ids)
        self.assertIn(task_without_subtasks.id, task_ids)


class ImportantTasksListAPITestCase(APITestCase):
    """
    Тесты для проверки эндпоинта получения списка важных задач.
    """

    def setUp(self):
        """
        Метод для подготовки тестовых данных. Создает тестового пользователя, сотрудников и задачи.
        """
        self.user = User.objects.create(email="test@test.com", password="password123")
        self.client.force_authenticate(user=self.user)

        # Создаем сотрудника
        self.employee = Employee.objects.create(first_name="Иван", last_name="Иванов")

        # Создаем задачи
        self.parent_task_in_progress = Task.objects.create(
            name="Родительская задача в работе",
            assigned_to=self.employee,
            due_date="2024-09-01",
            status="in_progress"
        )
        self.important_task = Task.objects.create(
            name="Важная задача",
            parent_task=self.parent_task_in_progress,
            assigned_to=self.employee,
            due_date="2024-09-10",
            status="new"
        )
        self.unimportant_task = Task.objects.create(
            name="Неважная задача",
            assigned_to=self.employee,
            due_date="2024-09-15",
            status="new"
        )

    def test_important_tasks_list(self):
        """
        Тест получения списка важных задач.
        """
        url = reverse("task_tracker:important-tasks")
        response = self.client.get(url)

        # Проверяем, что запрос завершился успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что список задач содержит только важные задачи
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Важная задача")

    def test_no_important_tasks(self):
        """
        Тест, когда нет важных задач (все родительские задачи не в работе).
        """
        # Обновляем статус родительской задачи
        self.parent_task_in_progress.status = "completed"
        self.parent_task_in_progress.save()

        url = reverse("task_tracker:important-tasks")
        response = self.client.get(url)

        # Проверяем, что запрос завершился успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что список задач пуст
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_no_employees_available(self):
        """
        Тест, когда нет доступных сотрудников.
        """
        # Удаляем всех сотрудников из базы данных
        Employee.objects.all().delete()

        url = reverse("task_tracker:important-tasks")
        response = self.client.get(url)

        # Проверяем, что запрос завершился успешно
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что список задач пуст, так как некому их выполнять
        data = response.json()
        self.assertEqual(len(data[0]['potential_employees']), 0)


class EmployeeModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="Иван",
            last_name="Иванов",
            middle_name="Сидорович",
            position="Разработчик",
            department="IT"
        )

    def test_employee_str(self):
        """
        Тестирует строковое представление модели Employee.
        """
        expected_str = "Иванов Иван Сидорович - Разработчик"
        self.assertEqual(str(self.employee), expected_str)


class TaskModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="Петр",
            last_name="Петров",
            position="Менеджер"
        )
        self.task = Task.objects.create(
            name="Тестовая задача",
            assigned_to=self.employee,
            status="in_progress",
            due_date="2024-09-01")

    def test_task_str(self):
        """
        Тестирует строковое представление модели Task.
        """
        expected_str = "Тестовая задача - В работе"
        self.assertEqual(str(self.task), expected_str)


class TaskSummarySerializerTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            first_name="Иван",
            last_name="Петров",
            position="Разработчик"
        )

        # Создаем родительскую задачу
        self.parent_task = Task.objects.create(
            name="Родительская задача",
            assigned_to=self.employee,
            status="new",
            due_date="2024-09-01"
        )

        # Создаем задачу, у которой есть родительская задача
        self.task = Task.objects.create(
            name="Зависимая задача",
            parent_task=self.parent_task,
            assigned_to=self.employee,
            status="in_progress",
            due_date="2024-09-10"
        )

    def test_get_parent_task(self):
        serializer = TaskSummarySerializer(self.task)
        serialized_data = serializer.data

        # Проверяем, что родительская задача возвращается корректно
        self.assertEqual(serialized_data['parent_task']['id'], self.parent_task.id)
        self.assertEqual(serialized_data['parent_task']['name'], self.parent_task.name)
        self.assertEqual(serialized_data['parent_task']['due_date'], str(self.parent_task.due_date))
