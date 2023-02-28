# Airflow

According to Apache entrerprise, Apache Airflow is a plataform created by the community to progammatically author schedule and monitor **batch-oriented** workflows. It's main principles are scalability dynamism, extensibility and elegance. It's features are pure Python, useful UI, robust integrations, easy to use and open source.

The main characteristic of Airflow is **Workflows as code**, because the workflows are defined in Python code and serves several purposes: dynamic, extensible and flexible.

**Airflow is not a streaming solution**

## Core concepts (DAGs, DAG Runs, Tasks, Operators)

A **DAG** (Directed Acyclic Graph) is a core concept of Airflow, collectiong Tasks together, organized with dependencias and relationships to say how they should run.

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

A **Task** is a basic unit of execution in Airflow. Task are arranged into DAG's, and then have upstream and downstream dependencies set between them into order to express. There are tree basic kinds of tasks: operatos, sensors and taskflow.

An **Operator** is a conceptually a template for a predefined Task, that you can just define declaratively inside your DAG. There are a very extensive set of operators available, some popular operators from core include: BashOperator, PythonOperator and EmailOperator.

A **Sensor** is a special subclass of operators witch are entirely about waiting for an external event to happen. Have two differents modes of running:

- **poke**: the sensor takes up a worker slot for its entire runtime.
- **reschedule**: the sensor takes up a worker slot only when it is checking, and sleeps for a set duration between checks.

A **TaskFlow** will make it much easier to author clean DAGs without extra boilerplate, all using @task decorator.

A DAG is created with for a set of tasks, so it has dependencies on tasks (upstream and downstream of it)

```python
first_taks >> [second_task, third_task]
third_task << fourth_task


fist_task.set_downstream(second_task, third_task)
third_task.set_upstream(fourth_task)
```

## DAG / Task scheduling process

An instance of a Task is a specific run of that task for a given DAG. They are also the representation of a Task that has statem representing what stage of the lifecycle it is in. The possible states for a Task Instance are:

- **none**: the task has'nt yet benn queued for execution.
- **scheduled**: the scheduler has determined the task dependencies are met and it should run.
- **queud**:the task has been assigned to an Executor ans is awaiting a worker.
- **running**: the task is running on a worker.
- **success**: the task finished running withour errors.
- **shutdown**: the task was externally requested to shut down when it was running.
- **restarting**: the task was externally requested to restard when it was running.
- **failed**: the task had an error during execution and failed to run.
- **skipped**: the task was skipped due to branching, LastestOnly, or similar.
- **upstream_failed**: an upstream task failed and the trigger rule says we needed it.
- **up_for_retry**: the task failed, but has retry attempts left and will be rescheduled.
- **up_for_reschedule**: the task is a sensor thar is in reschedule mode.
- **deferred**: the task has been deferred to a trigger.
- **removed**: the task has vanished from the DAG since the run started.

## Backfill / Catchup

## DAG skeleton

## Architecture components (Web Server, Scheduler, Metadata DB, Executor, Worker)



## What Airflow is and what Airflow is not




## Variables

## Pools

## Trigger Rules

## DAG Dependencies

## Idempotency

## Dynamic DAGs

## Templanting

## TaskFlow API

## XCOMs

## SubDAGs

# Branching

## SLAs