import datetime

from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import Employee, Task


class EmployeeSerializer(ModelSerializer):
    """
    Сериализатор для модели Employee.
    Включает валидацию данных.
    """
    active_task_count = SerializerMethodField()

    def get_active_task_count(self, employee):
        return Task.objects.filter(assigned_to=employee, status__in=['new', 'in_progress']).count()

    def validate_first_name(self, value):
        if not value.isalpha():
            raise ValidationError("Имя должно содержать только буквы.")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise ValidationError("Фамилия должна содержать только буквы.")
        return value

    def validate_middle_name(self, value):
        if not value.isalpha():
            raise ValidationError("Отчество должно содержать только буквы.")
        return value

    def validate_hired_date(self, value):
        if value > datetime.date.today():
            raise ValidationError("Дата приема на работу не может быть в будущем.")
        return value

    class Meta:
        model = Employee
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'position', 'department',
                  'hired_date', 'active_task_count']


class TaskSummarySerializer(ModelSerializer):
    parent_task = SerializerMethodField()

    def get_parent_task(self, task):
        if task.parent_task:
            return {
                'id': task.parent_task.id,
                'name': task.parent_task.name,
                'due_date': task.parent_task.due_date
            }
        return None

    class Meta:
        model = Task
        fields = ['id', 'name', 'due_date', 'status', 'parent_task']


class BusyEmployeeSerializer(ModelSerializer):
    """
    Сериализатор для списка занятых сотрудников.
    Включает необходимые поля и список активных задач.
    """
    tasks = SerializerMethodField()
    active_task_count = SerializerMethodField()

    def get_tasks(self, employee):
        tasks = Task.objects.filter(assigned_to=employee, status__in=['new', 'in_progress'])
        return TaskSummarySerializer(tasks, many=True).data

    def get_active_task_count(self, employee):
        return Task.objects.filter(assigned_to=employee, status__in=['new', 'in_progress']).count()

    class Meta:
        model = Employee
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'position', 'hired_date', 'active_task_count',
                  'tasks']


class TaskSerializer(ModelSerializer):
    """
    Сериализатор для модели Task.
    Включает валидацию данных.
    """

    def validate_due_date(self, value):
        if value < datetime.date.today():
            raise ValidationError("Срок выполнения задачи не может быть в прошлом.")
        return value

    class Meta:
        model = Task
        fields = '__all__'


class ImportantTaskSerializer(ModelSerializer):
    """
    Сериализатор для отображения важных задач и сотрудников, которые могут их взять.
    Включает дополнительное поле для отображения потенциальных сотрудников.
    """
    potential_employees = SerializerMethodField()

    def get_potential_employees(self, task):
        """
        Возвращает список сотрудников, которые могут взять задачу.
        Сотрудники отбираются по критерию минимальной загруженности или выполнения родительской задачи.
        """
        employees = Employee.objects.all()
        if not employees:
            return []

        # Определяем минимальное количество задач у сотрудников
        min_task_count = None
        for employee in employees:
            task_count = Task.objects.filter(assigned_to=employee).count()
            if min_task_count is None or task_count < min_task_count:
                min_task_count = task_count

        suitable_employees = []

        # Отбираем сотрудников, которые могут взять задачу
        for employee in employees:
            task_count = Task.objects.filter(assigned_to=employee).count()
            parent_task_employee = Task.objects.filter(parent_task=task, assigned_to=employee).exists()

            # Если сотрудник имеет минимальную загруженность или выполняет родительскую задачу,
            # и у него не более чем на 2 задачи больше, чем у наименее загруженного сотрудника
            if task_count == min_task_count or (parent_task_employee and task_count <= min_task_count + 2):
                employee_name = (f"{employee.last_name} {employee.first_name}"
                                 f" {employee.middle_name or ''}. ID:{employee.id}").strip()
                if employee_name not in suitable_employees:
                    suitable_employees.append(employee_name)

        return suitable_employees

    class Meta:
        model = Task
        fields = ['id', 'name', 'due_date', 'potential_employees']
