from airflow.decorators import dag
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta
from typing import Dict

default_args: Dict[str, str] = {
    "retries": 1,
    "retry_delay": timedelta(minutes = 5)
}

def random_hour(ti) -> int:
    from random import randint
    hour = randint(0, 24)
    ti.xcom_push(key="hour", value = hour)
    return hour

def show_hour(ts, **kwargs) -> str:
    return f"SYSTEM HOUR: {ts} | RANDOM HOUR: {kwargs['hour']}"


def branching(**kwargs):
    hour = int(kwargs["hour"])
    
    if hour >= 0 and hour < 12:
        return "good_morning"
    elif hour >= 12 and hour < 18:
        return "good_afternoon"
    elif hour >= 18:
        return "good_night"
    

def good_morning(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good morning, today is {ds}"


def good_afternoon(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good afternoon, today is {ds}"


def good_night(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good night, today is {ds}"

@dag(
    dag_id = "dag_xcom",
    start_date = datetime(2023, 10, 1),
    schedule = "0 21 * * *",
    default_args = default_args,
    catchup = True,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["XCOM", "daily"]
)
def generate_dag():
    
    
    task_1 = PythonOperator(
        task_id="random_hour",
        python_callable=random_hour,
        provide_context=True,
    )
    
    task_2 = PythonOperator(
        task_id="show_hour",
        python_callable=show_hour,
        provide_context=True,
        op_kwargs={"hour": "{{ ti.xcom_pull(task_ids=['random_hour'], key='hour')[0] }}"}
    )
    
    task_3 = BranchPythonOperator(
        task_id="branching",
        python_callable=branching,
        provide_context=True,
        op_kwargs={"hour": "{{ ti.xcom_pull(task_ids=['random_hour'], key='hour')[0] }}"}
    )
    
    option_1 = PythonOperator(
        task_id="good_morning",
        python_callable=good_morning,
        provide_context=True,
        op_kwargs={"user": "Rodolfo", "dt_ref": "{{ ds }}"}
    )
    
    option_2 = PythonOperator(
        task_id="good_afternoon",
        python_callable=good_afternoon,
        provide_context=True,
        op_kwargs={"user": "Rodolfo", "dt_ref": "{{ ds }}"}
    )
    
    option_3 = PythonOperator(
        task_id="good_night",
        python_callable=good_night,
        provide_context=True,
        op_kwargs={"user": "Rodolfo", "dt_ref": "{{ ds }}"}
    )
    
    task_1 >> task_2 >> task_3 >> [option_1, option_2, option_3]

 
generate_dag()