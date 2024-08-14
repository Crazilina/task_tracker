from django.contrib import admin
from task_tracker.models import Task, Employee


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'assigned_to', 'status', 'due_date')
    search_fields = ('name',)
    list_filter = ('status', 'due_date')
    ordering = ('due_date',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'position', 'department', 'hired_date')
    search_fields = ('last_name', 'first_name', 'middle_name', 'position')
    list_filter = ('department', 'position', 'hired_date')
    ordering = ('last_name', 'first_name', 'hired_date')
