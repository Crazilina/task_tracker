from django.urls import path
from rest_framework.routers import SimpleRouter

from task_tracker.apps import TaskTrackerConfig
from task_tracker.views import (
    EmployeeCreateAPIView, EmployeeListAPIView, EmployeeRetrieveAPIView, EmployeeUpdateAPIView, EmployeeDestroyAPIView,
    BusyEmployeesListAPIView, TaskCreateAPIView, TaskListAPIView, TaskRetrieveAPIView, TaskUpdateAPIView,
    TaskDestroyAPIView, ImportantTasksListAPIView
)

app_name = TaskTrackerConfig.name

router = SimpleRouter()

urlpatterns = [
    # Маршруты для сотрудников
    path('employees/', EmployeeListAPIView.as_view(), name='employee-list'),
    path('employees/create/', EmployeeCreateAPIView.as_view(), name='employee-create'),
    path('employees/<int:pk>/', EmployeeRetrieveAPIView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/update/', EmployeeUpdateAPIView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', EmployeeDestroyAPIView.as_view(), name='employee-delete'),

    # Эндпоинт для занятых сотрудников
    path('employees/busy/', BusyEmployeesListAPIView.as_view(), name='busy-employees'),


    # Маршруты для задач
    path('tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('tasks/create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskRetrieveAPIView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/update/', TaskUpdateAPIView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDestroyAPIView.as_view(), name='task-delete'),

    # Эндпоинт для важных задач
    path('tasks/important/', ImportantTasksListAPIView.as_view(), name='important-tasks'),

] + router.urls
