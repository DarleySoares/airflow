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

def good_morning(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good morning, today is {ds}"

dag = DAG(
    dag_id="dag_1",
    start_date=datetime(2023, 10, 1),
    schedule="0 9 * * *",
    default_args=default_args,
    catchup=True,
    tags=["good_morning", "daily"]
)

task_1 = BashOperator(
    task_id="task_1",
    bash_command="echo 1",
    dag=dag
)

task_2 = PythonOperator(
    task_id="task_2",
    python_callable=hello_world, 
    dag=dag
)

task_3 = PythonOperator(
    task_id="task_3",
    python_callable=good_morning,
    provide_context=True,
    op_kwargs={"user": "Rodolfo"},
    dag=dag
)
    
task_1 >> task_2 >> task_3