In This milestone, I'm extending the functionality of the project I worked in [Django ORM Task Manager](https://github.com/Ankur-9598/django_orm_task_manager)

The specification for this program is as follows,

## Specification

To implement the two new features to it.

1) A Filter to filter out completed tasks in the Tasks Listing API.
2) Creating a model to store the history of the tasks changes in status
    The model should store the old status and the new status it was updated to, it should also store the data and time of this change.
3) API to view all changes made to a task. This API should have filters based on the date and status.


## Extra Routes
1. ```api/v1/tasks``` :- Task ViewSet API endpoint

2. ```api/v1/task/<pk>/history``` :- Task History API endpoint

## Boilerplate code

Use the following repository as a starting point for this project: https://github.com/vigneshhari/GDC-Level-7-Milestone

to install the requirements for this project, run the following command in your terminal:

```bash
pip install -r requirements.txt
```