from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.forms import ModelForm, ValidationError
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from tasks.api_views import TaskUtilityFunctions
from tasks.models import Task


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


class GenericTaskCreateView(LoginRequiredMixin, CreateView, TaskUtilityFunctions):
    form_class = TaskCreateForm
    template_name = 'task_create.html'
    extra_context = {'title': 'Create Todo'}
    success_url = '/tasks'

    def form_valid(self, form):
        # Apply priority cascading logic
        self.priority_cascading_logic(form.cleaned_data['priority'])
        
        # Save the task model
        self.object = form.save()
        self.object.user = self.request.user 
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class GenericTaskDetailView(AuthorisedTaskManager, DetailView):
    model = Task
    template_name = 'task_details.html'
    extra_context = {'title': 'Task Details'}


class GenericTaskUpdateView(AuthorisedTaskManager, UpdateView, TaskUtilityFunctions):
    model = Task
    form_class = TaskCreateForm
    template_name = 'task_update.html'
    extra_context = {'title': 'Update Todo'}
    success_url = '/tasks'

    def form_valid(self, form):
        # Get the current active task instance
        task = self.get_object()

        # Apply priority cascading logic
        self.priority_cascading_logic(form.cleaned_data['priority'], task.id)

        old_status = task.status
        new_status = form.cleaned_data['status']

        # Check for the status changes
        if old_status != new_status:
            self.create_task_history(task, old_status, new_status)
        
        return super().form_valid(form)


class GenericTaskDeleteView(AuthorisedTaskManager, DeleteView, TaskUtilityFunctions):
    model = Task
    template_name = 'task_delete.html'
    success_url = '/tasks'

    def form_valid(self, form):
        task = self.get_object()
        old_status = task.status
        new_status = 'CANCELLED'

        if old_status != new_status:
            self.create_task_history(task, old_status, new_status)

        Task.objects.filter(pk=task.id, user=self.request.user).update(deleted=True)

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
        context['completed_tasks_len'] = Task.objects.filter(completed=True, deleted=False, user=self.request.user).count()
        return context


class GenericPendingTaskView(GenericTaskView):
    template_name = 'pending_tasks.html'
    context_object_name = 'pending_tasks'

    def get_queryset(self):
        return Task.objects.filter(completed=False, deleted=False, user=self.request.user).order_by('priority')


def home_view(request):
    return HttpResponseRedirect('/tasks')
