from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, ChoiceFilter, BooleanFilter, DateRangeFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from tasks.models import Task
from tasks.models import TaskHistory
from tasks.models import STATUS_CHOICES


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains')
    status = ChoiceFilter(choices=STATUS_CHOICES)
    completed = BooleanFilter()

class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'completed', 'user']

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskListApi(APIView):

    def get(self, request):
        tasks = Task.objects.filter(deleted=False)
        data = TaskSerializer(tasks, many=True).data
        return Response({'tasks': data})



class TaskHistorySerializer(ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskHistory
        fields = ['task', 'new_status', 'old_status', 'updated_date']

class TaskHistoryFilter(FilterSet):
    updated_date = DateRangeFilter(field_name='updated_date', lookup_expr='exact')
    new_status = ChoiceFilter(choices=STATUS_CHOICES)
    old_status = ChoiceFilter(choices=STATUS_CHOICES)


class TaskHistoryViewSet(ModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskHistoryFilter

    def get_queryset(self):
        task_id = self.kwargs['task_id']    
        return TaskHistory.objects.filter(task=task_id, user=self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        print(serializer.validated_data)
        return super().perform_update(serializer)