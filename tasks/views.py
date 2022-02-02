from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from tasks.apiviews import TaskHistorySerializer

from tasks.models import Task, TaskHistory
from django.db.models import F


class AuthorisedTaskManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)

class TaskCreateForm(ModelForm):

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 10:
            raise ValidationError('Title must be at least 10 characters long')
        return title.upper()

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'status', 'completed']


class GenericTaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskCreateForm
    template_name = 'task_create.html'
    extra_context = {'title': 'Create Todo'}
    success_url = '/tasks'

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()

        priority = self.object.priority

        updated_tasks = []
        tasks = Task.objects.filter(deleted=False, user=self.request.user).select_for_update()
        task_to_update = tasks.filter(priority=priority).exclude(pk=self.object.id)

        while task_to_update.exists():
            excluded_task_id = task_to_update[0].id

            curr_task = tasks.get(id=excluded_task_id)
            curr_task.priority = priority + 1
            updated_tasks.append(curr_task)

            priority += 1
            task_to_update = tasks.filter(priority=priority).exclude(pk=excluded_task_id)

        Task.objects.bulk_update(updated_tasks, ['priority'])
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = 'task_details.html'
    extra_context = {'title': 'Task Details'}


class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = 'task_update.html'
    extra_context = {'title': 'Update Todo'}
    success_url = '/tasks'

    def form_valid(self, form):
        old_status = Task.objects.get(pk=self.object.id).status
        self.object = form.save()
        self.object.save()
        new_status = self.object.status
        if self.object.completed:
            new_status = 'COMPLETED'
        task_history = TaskHistory(task=self.object, old_status=old_status, new_status=new_status, user=self.request.user)
        task_history.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskDeleteView(AuthorisedTaskManager, DeleteView):
    model = Task
    template_name = 'task_delete.html'
    success_url = '/tasks'

    def form_valid(self, form):
        task_id = self.object.id
        Task.objects.filter(pk=task_id).update(deleted=True)
        old_status = Task.objects.get(pk=task_id).status
        new_status = 'CANCELLED'
        task_history = TaskHistory(task=self.object, old_status=old_status, new_status=new_status, user=self.request.user)
        task_history.save()

        return HttpResponseRedirect(self.get_success_url())


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    extra_context = { 'title': 'Task Manager' }

class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    extra_context = { 'title': 'Task Manager' }
    success_url = "/tasks"


class GenericTaskView(LoginRequiredMixin, ListView):
    template_name = 'tasks.html'
    context_object_name = 'tasks'
    paginate_by = 3

    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user).order_by('priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_tasks_len'] = Task.objects.filter(completed=True, deleted=False, user=self.request.user).count()
        context['total_tasks_len'] = Task.objects.filter(deleted=False, user=self.request.user).count()
        return context


class GenericCompleteTaskView(LoginRequiredMixin, ListView):
    template_name = 'completed_tasks.html'
    context_object_name = 'completed_tasks'
    paginate_by = 3

    def get_queryset(self):
        return Task.objects.filter(completed=True, deleted=False, user=self.request.user).order_by('priority')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_tasks_len'] = Task.objects.filter(deleted=False, user=self.request.user).count()
        return context


class GenericPendingTaskView(GenericTaskView):
    template_name = 'pending_tasks.html'
    context_object_name = 'pending_tasks'

    def get_queryset(self):
        return Task.objects.filter(completed=False, deleted=False, user=self.request.user).order_by('priority')


def home_view(request):
    return HttpResponseRedirect('/tasks')
