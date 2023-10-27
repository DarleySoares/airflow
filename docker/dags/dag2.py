from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from typing import Dict

default_args: Dict[str, str] = {
    "retries": 1,
    "retry_delay": timedelta(minutes = 5)
}

def hello_world() -> str:
    return "Hello World!"

def good_afternoon(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good afternoon, today is {ds}"

with DAG(
    dag_id = "dag_2",
    start_date = datetime(2023, 1, 1),
    end_date= datetime(2023, 1, 25),
    schedule = "0 13 * * *",
    default_args = default_args,
    catchup = True,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["good_afternoon", "daily"]
):
    task_1 = BashOperator(
        task_id="task_1",
        bash_command="echo 1"
    )
    
    task_2 = PythonOperator(
        task_id = "task_2",
        python_callable = hello_world, 
    )
    
    task_3 = PythonOperator(
        task_id="task_3",
        python_callable=good_afternoon,
        provide_context=True,
        op_kwargs={"user": "Rodolfo"}
    )
    
task_1 >> task_2 >> task_3