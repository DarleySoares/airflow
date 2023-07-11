from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from typing import Dict

default_args: Dict[str, str] = {
    "retries": 1,
    "retry_delay": timedelta(minutes = 5)
}

def hello_word() -> str:
    return "Hello World!"

with DAG(
    dag_id = "dag",
    start_date = datetime(2023, 1, 1),
    schedule = "* 9 * * *",
    default_args = default_args,
    catchup = False
):
    
    hello_word_task = PythonOperator(
        task_id = "hello_world_task",
        python_callable = hello_word, 
    )
    
hello_word_task