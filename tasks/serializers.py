from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from tasks.models import Task, TaskHistory


# User serializer
class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['username']
    
# Task serializer
class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'completed', 'status', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['pretty_date'] = instance.pretty_date()
        return data

# Task History serializer 
class TaskHistorySerializer(ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TaskHistory
        fields = ['task', 'new_status', 'old_status', 'updated_date', 'id']
