
from django.contrib import admin
from django.urls import path

from tasks.views import (GenericCompleteTaskView, GenericPendingTaskView, GenericTaskCreateView, 
    GenericTaskDeleteView, GenericTaskDetailView, GenericTaskUpdateView, 
    GenericTaskView, UserCreateView, UserLoginView, home_view)

from django.contrib.auth.views import LogoutView

from rest_framework.routers import SimpleRouter
from tasks.apiviews import TaskListApi, TaskViewSet, TaskHistoryViewSet

router = SimpleRouter()

router.register(r'api/task', TaskViewSet)
router.register(r'api/task-history/(?P<task_id>\d+)', TaskHistoryViewSet)

urlpatterns = [
    path("", home_view, name="home"),
    path("taskapi", TaskListApi.as_view(), name="taskapi"),
    path("admin/", admin.site.urls),
    path("user/signup", UserCreateView.as_view(), name="create_user"),
    path("user/login", UserLoginView.as_view(), name="login_user"),
    path("tasks", GenericTaskView.as_view(), name="tasks"),
    path("user/logout", LogoutView.as_view(), name="logout_user"),
    path("create-task", GenericTaskCreateView.as_view(), name="create_task"),
    path("update-task/<pk>", GenericTaskUpdateView.as_view(), name="update_task"),
    path("detail-task/<pk>", GenericTaskDetailView.as_view(), name="detail_task"),
    path("delete-task/<pk>", GenericTaskDeleteView.as_view(), name="delete_task"),
    path("completed-tasks", GenericCompleteTaskView.as_view(), name="completed_tasks"),
    path("pending-tasks", GenericPendingTaskView.as_view(), name="pending_tasks"),
] + router.urls

