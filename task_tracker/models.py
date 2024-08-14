from django.db import models

NULLABLE = {'blank': True, 'null': True}


class Employee(models.Model):
    """
    Модель сотрудника.

    Атрибуты:

        first_name (CharField): Имя сотрудника.
        last_name (CharField): Фамилия сотрудника.
        middle_name (CharField): Отчество сотрудника.
        position (CharField): Должность сотрудника.
        department (CharField): Отдел, в котором работает сотрудник.
        hired_date (DateField): Дата приема на работу.
    """
    last_name = models.CharField(max_length=30, verbose_name="Фамилия", help_text="Укажите фамилию сотрудника")
    first_name = models.CharField(max_length=30, verbose_name="Имя", help_text="Укажите имя сотрудника")
    middle_name = models.CharField(max_length=30, **NULLABLE, verbose_name="Отчество",
                                   help_text="Укажите отчество сотрудника")
    position = models.CharField(max_length=100, verbose_name="Должность", help_text="Укажите должность сотрудника.")
    department = models.CharField(max_length=100, **NULLABLE, verbose_name="Отдел",
                                  help_text="Укажите отдел сотрудника.")
    hired_date = models.DateField(**NULLABLE, verbose_name="Дата приема на работу",
                                  help_text="Укажите дату приема на работу.")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''} - {self.position}"


class Task(models.Model):
    """
    Модель задачи.

    Атрибуты:
        name (CharField): Наименование задачи.
        description (TextField): Описание задачи.
        parent_task (ForeignKey): Ссылка на родительскую задачу.
        assigned_to (ForeignKey): Сотрудник, ответственный за выполнение задачи.
        due_date (DateField): Срок выполнения задачи.
        status (CharField): Статус задачи.
    """
    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('on_hold', 'На паузе'),
        ('canceled', 'Отменена'),
        ('overdue', 'Просрочена'),
    )

    name = models.CharField(max_length=200, verbose_name="Наименование задачи",
                            help_text="Введите наименование задачи.")
    description = models.TextField(**NULLABLE, verbose_name="Описание задачи", help_text="Введите описание задачи.")
    parent_task = models.ForeignKey('self', **NULLABLE, on_delete=models.SET_NULL, related_name='subtasks',
                                    verbose_name="Родительская задача",
                                    help_text="Выберите родительскую задачу, если задача является зависимой.")
    assigned_to = models.ForeignKey('Employee', **NULLABLE, on_delete=models.SET_NULL, related_name='tasks',
                                    verbose_name="Исполнитель",
                                    help_text="Укажите сотрудника, ответственного за выполнение задачи.")
    due_date = models.DateField(verbose_name="Срок выполнения", help_text="Укажите срок выполнения задачи.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус",
                              help_text="Выберите статус задачи.")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
