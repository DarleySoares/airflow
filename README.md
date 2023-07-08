<h1 align="center">
    <a><img src = "img/airflow.png" width="100px"></a>
</h1>

<h1 align="center">
    Airflow
</h1>

According to Apache entrerprise, Apache Airflow is a plataform created by the community to progammatically author schedule and monitor **batch-oriented** workflows. It's main principles are scalability dynamism, extensibility and elegance. It's features are pure Python, useful UI, robust integrations, easy to use and open source.

The main characteristic of Airflow is **Workflows as a code**, because the workflows are defined in Python code and serves several purposes: dynamic, extensible and flexible.


<strong style="color:#EB360F">
    Airflow is not a streaming solution.
</strong>

<br/><br/>

## Core concepts (DAGs, DAG Runs, Tasks, Operators)

A **DAG** (Directed Acyclic Graph) is a core concept of Airflow, collecting Tasks together, organized with dependencies and relationships to say how they should run.

```python
from airflow import DAG
from datetime import datetime

with DAG(
    "dag_name",
    start_date = datetime(2023,2,23),
    schedule = "* * * * *",
    catchup= False
) as dag:
    ...
```

A DAG Run status is determined when the execution of the DAG is finished, like **sucess**, **failed** or **skipped**.

A **Task** is a basic unit of execution in Airflow. Task are arranged into DAG's, and then have upstream and downstream dependencies set between them into order to express. There're tree basic kinds of tasks: operatos, sensors and taskflow.

An **Operator** is a conceptually a template for a predefined Task, that you can just define declaratively inside your DAG. There're a very extensive set of operators available, some popular operators from core include: BashOperator, PythonOperator and EmailOperator.

A **Sensor** is a special subclass of operators witch are entirely about waiting for an external event to happen. Have two differents modes of running:

- **poke**: the sensor takes up a worker slot for it's entire runtime.
- **reschedule**: the sensor takes up a worker slot only when it's checking, and sleeps for a set duration between checks.

A **TaskFlow** will make it much easier to author clean DAGs without extra boilerplate, all using <bold style="color:#EB360F">@task</bold> decorator.

A DAG is created with for a set of tasks, so it has dependencies on tasks (upstream and downstream of it)

```python
first_taks >> [second_task, third_task]
third_task << fourth_task


fist_task.set_downstream(second_task, third_task)
third_task.set_upstream(fourth_task)
```

## DAG / Task scheduling process

An instance of a Task is a specific run of that task for a given DAG. They're also the representation of a Task that has state representing what stage of the lifecycle it's in. The possible states for a Task Instance are:

- **none**: the task has'nt yet been queued for execution.
- **scheduled**: the scheduler has determined the task dependencies are met and it should run.
- **queud**: the task has been assigned to an Executor and is awaiting a worker.
- **running**: the task is running on a worker.
- **success**: the task finished running without errors.
- **shutdown**: the task was externally requested to shutdown when it was running.
- **restarting**: the task was externally requested to restard when it was running.
- **failed**: the task had an error during execution and failed to run.
- **skipped**: the task was skipped due to branching, LastestOnly or similar.
- **upstream_failed**: an upstream task failed and the trigger rule says we needed it.
- **up_for_retry**: the task failed, but has retry attempts left and will be rescheduled.
- **up_for_reschedule**: the task is a sensor that is in reschedule mode.
- **deferred**: the task has been deferred to a trigger.
- **removed**: the task has vanished from the DAG since the run started.

## Backfill / Catchup

The Catchup will kick off a DAG Run for any data interval that has not been run since the last data interval (or has been cleared). When catchup turned off, the scheduller creates a DAG Run only for the latest interval.

The Backfill is used when you may want run the DAG for a specified historical period. You may want to backfill the data even in the cases when catchup is disable.

## Architecture components (Web Server, Scheduler, Metadata DB, Executor, Worker)

The **Workers** execute the assigned tasks.

The **Scheduler** is responsible for adding the neceasary tasks to the queue.

The **Web Server** is the HTTP Server provides access to DAG/task status information.

The **Database** contains information about the status of tasks, DAGs, Variables, connections, etc.

The **Executors** are the mechanism by with task instance get run. They have a common API and are "pluggable", meaning you can swap executors based on your installation needs. There are two types of executor: locally and remotely.

## Variables

Variables are runtime configurationm concept, a general key/value store that is global and can be queried from your tasks. To use

```python
from airflow.models import Variable

value = Variable.get("variable_name")

value = "{{ var.value.variable_name }}"
```

**PS:** if there is **_secret** in the variable name, the value is hidden.

The template engine is powerfull because the connection with database is fetched only once the DAG is running, but using a Variable the connection is created every 30 seconds.

To create environment variables in Airflow it's needed add in dockerfile

```dockerfile
AIRFLOW_VAR_VARIABLE_NAME="variable_value"
```

## Templating

Variables, macros and filters can be used in templates.

```python

{{ ds }}: str # the DAG run's logical date as YYYY-MM-DD
{{ data_interval_start}}: pendulum.DateTime # start of the data interval
{{ data_interval_end}}: pendulum.DateTime # end of the data interval 
```

## XCOMs

XComs (cross communications) are a mechanism that allows tasks talk to each other, as by default tasks are entirely isolated an may be running on entirely different machines.
XComs are explicity (pushed and pulled to/from) with **xcom_push** and **xcom_pull** methods.

```python
# XCom pull
value = task_intance.xcom_pull(task_ids="pushing_task")

SELECT * FROM {{ task_instance.xcom_pull(task_ids="foo", key="table_name")}}
```

With SQLite are limited to 2GB for a given XCom, Postgres are limited 1GB and MySQL are limited to 64kB.

## TaskFlow API

The TaskFlow API is a new Airflow feature that allows you to explicity declare message passing while implicity declaring task dependencies. For that, XCom Args was abstracted and inferred as result of the Python function invocation,  task decorators that automatically creates PythonOperator tasks and handles variable passing were implemented and supports for custom Xcom backends.

**Decorators**: help you in order to create dags in an easier and faster way.

```python
# Without decorator
from airflow.operator.python import PythonOperator

def process(ti):
    return 'end'

process = PythonOperator(task_id="process", python_callable=process)

process

# With decorator
from airflow.decorators import task

@task.python
def process():
    return 'end'

process

```

## SubDAGs

SubDAGs are a legacy Airflow feature that allowed the creation of reusable task patterns in DAGs and are deprecated in Airflow 2.0. It's recommended you don't use SubDAGs, use the following alternatives: task groups or cross-dag-dependencies.

## Task Groups

Task Groups are used to organize tasks in the Airflow UI DAG graph view.

```python
# Without decorator
from airflow.utils.task_group import TaskGroup

initial_task = extract()

with TaskGroup(group_id="process_tasks") as process_tasks:
    process_a()
    process_b()
    process_c()

initial_task >> process_tasks

# With decorator
from airflow.decorators import task, task_group

@task_group(group_id="process_tasks")
def process_tasks()
    process_a()
    process_b()
    process_c()

initial_task >> process_tasks
```

## Dynamic DAGs

It's possible create many DAG's automatically using Dynamic DAGs context. For that, it's common use dictonary to help.

```python
partners = {
    "A": {"name": "partner_a"},
    "B": {"name": "partner_b"},
    "C": {"name": "partner_c"},
}

@task_group(group_id="process_tasks", add_suffix_on_collision=True)
def process_tasks()
    process_a()
    process_b()
    process_c()

for partner, details in partnes.items():

    @task.python(task_id=f"extract_{partner}", do_xcom_push=False, multiple_outputs=True)
    def extract(partner)
        return partner   

    process_tasks(extract(details["name"]))
```

## Branching

When designing your data pipelines, you may encounter use cases that require more complex task flows. For example, you may havea use case where you need to decide between multiple tasks to execute based on the results of an upstream taks, for that has multiple options for building conditional logic or branching, with: BranchPythonOperator and ShortCircuitOperator.

```python
from airflow.operators.python import BranchPythonOperator

def _choosing_partner(execution_date):
    day = execution_date.day_of_week

    if day == 1:
        return  "extract_partner_A"
    if day == 2:
        return  "extract_partner_B"
    else
        return  "extract_partner_C "

choosing_partner = BranchPythonOperator(
    task_id="choosing_partner",
    python_callable=_choosing_partner
)

choosing_partner >> process_tasks
```

## Trigger Rules

Trigger Rules determine whn a task will be executed.

- **all_sucess**: task gets triggered when all upstream tasks have succeeded.
- **all_failed**: task gets triggered when all upstream tasks have failed.
- **all_done**: task gets triggered once all upstream tasks ared done with their execution whatever their state.
- **one_failed**: task gets triggered as soon as one of the upstream tasks fails.
- **one_sucess**: taks gets triggered as soon as one of the upstream tasks succeeds.
- **none_failed**: task gets triggered if all upstream tasks have succeeded or been skipped.
- **none_failed_min_one_sucess | none_failed_or_skipped**: tasks gets triggered if all upstream tasks haven't failed and at least one has succeeded.
- **none_skipped**: tasks gets triggered if no upstream tasks are skipped.
