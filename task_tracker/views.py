from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, ImportantTaskSerializer, BusyEmployeeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class EmployeeCreateAPIView(CreateAPIView):
    """
    Контроллер создания нового сотрудника.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


class EmployeeListAPIView(ListAPIView):
    """
    Контроллер для получения списка всех сотрудников.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'department', 'hired_date']


class EmployeeRetrieveAPIView(RetrieveAPIView):
    """
    Контроллер для получения одного сотрудника по указанному id.
    """
    queryset = Employee.objects.all()
    serializer_class = BusyEmployeeSerializer
    permission_classes = [IsAuthenticated]


class EmployeeUpdateAPIView(UpdateAPIView):
    """
    Контроллер для обновления данных одного сотрудника по указанному id.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


class EmployeeDestroyAPIView(DestroyAPIView):
    """
    Контроллер для удаления одного сотрудника по указанному id.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


class BusyEmployeesListAPIView(ListAPIView):
    """
    Эндпоинт для получения списка сотрудников, отсортированных по количеству активных задач
    и по срокам выполнения задач.
    """
    serializer_class = BusyEmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список сотрудников с их задачами, отсортированных по количеству активных задач.
        Активные задачи — это задачи со статусом 'new' или 'in_progress'.
        """
        employees = Employee.objects.all()

        employee_task_data = []
        for employee in employees:
            active_tasks = Task.objects.filter(assigned_to=employee, status__in=['new', 'in_progress'])
            active_task_count = active_tasks.count()

            # Находим самую раннюю дату выполнения задач
            earliest_due_date = None
            for task in active_tasks:
                if earliest_due_date is None or task.due_date < earliest_due_date:
                    earliest_due_date = task.due_date

            # Добавляем данные в список
            employee_task_data.append({
                'employee': employee,
                'tasks': active_tasks,
                'active_task_count': active_task_count,
                'earliest_due_date': earliest_due_date,
            })

        # Сортируем сотрудников сначала по количеству задач, затем по самой ранней дате выполнения задач
        sorted_employee_data = sorted(
            employee_task_data,
            key=lambda x: (-x['active_task_count'], x['earliest_due_date'] or '9999-12-31')
        )

        # Возвращаем отсортированный список сотрудников
        return [data['employee'] for data in sorted_employee_data]


class TaskCreateAPIView(CreateAPIView):
    """
    Контроллер создания новой задачи.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class TaskListAPIView(ListAPIView):
    """
    Контроллер для получения списка всех задач.
    """
    queryset = Task.objects.all().order_by('id')
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assigned_to', 'status', 'parent_task', 'due_date']

    @swagger_auto_schema(
        operation_description="Получение списка задач с возможностью фильтрации по параметрам",
        manual_parameters=[
            openapi.Parameter('assigned_to', openapi.IN_QUERY, description="ID сотрудника", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="Статус задачи", type=openapi.TYPE_STRING),
            openapi.Parameter('parent_task', openapi.IN_QUERY, description="ID родительской задачи",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('due_date', openapi.IN_QUERY, description="Дата выполнения задачи",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('subtasks', openapi.IN_QUERY, description="Фильтрация задач по наличию подзадач",
                              type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('has_parent', openapi.IN_QUERY,
                              description="Фильтрация задач по наличию родительской задачи",
                              type=openapi.TYPE_BOOLEAN),
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        # Проверка на допустимость фильтров
        allowed_filters = set(self.filterset_fields)
        requested_filters = set(self.request.query_params.keys()) - {'subtasks', 'has_parent'}
        invalid_filters = requested_filters - allowed_filters

        if invalid_filters:
            raise ValidationError(f"Фильтрация по полю(-ям) {', '.join(invalid_filters)} невозможна. "
                                  f"Доступные поля для фильтрации: {', '.join(allowed_filters)}")

        # Фильтрация по наличию подзадач
        subtasks_param = self.request.query_params.get('subtasks')
        if subtasks_param is not None:
            if subtasks_param.lower() in ('true', '1'):
                queryset = queryset.filter(subtasks__isnull=False).distinct()
            elif subtasks_param.lower() in ('false', '0'):
                queryset = queryset.filter(subtasks__isnull=True).distinct()

        # Фильтрация по наличию родительской задачи
        has_parent_param = self.request.query_params.get('has_parent')
        if has_parent_param is not None:
            if has_parent_param.lower() in ('true', '1'):
                queryset = queryset.filter(parent_task__isnull=False)
            elif has_parent_param.lower() in ('false', '0'):
                queryset = queryset.filter(parent_task__isnull=True)

        return queryset


class TaskRetrieveAPIView(RetrieveAPIView):
    """
    Контроллер для получения одной задачи по указанному id.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class TaskUpdateAPIView(UpdateAPIView):
    """
    Контроллер для обновления данных одной задачи по указанному id.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class TaskDestroyAPIView(DestroyAPIView):
    """
    Контроллер для удаления одной задачи по указанному id.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


class ImportantTasksListAPIView(ListAPIView):
    """
    Эндпоинт для получения списка важных задач, которые не взяты в работу,
    но от которых зависят другие задачи, находящиеся в работе.
    """
    serializer_class = ImportantTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список задач, которые не взяты в работу (статус 'new'),
        но от которых зависят другие задачи, находящиеся в работе.
        """
        important_tasks = Task.objects.filter(
            status='new',
            parent_task__status='in_progress'
        )

        return important_tasks
