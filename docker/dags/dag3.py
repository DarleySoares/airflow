from airflow.decorators import dag
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

def good_night(**kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good night, today is {kwargs['dt_ref']}"

@dag(
    dag_id = "dag_3",
    start_date = datetime(2023, 1, 1),
    schedule = "0 21 * * *",
    default_args = default_args,
    catchup = False,
    tags=["good_nigth", "daily"]
)
def generate_dag():
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
        python_callable=good_night,
        provide_context=True,
        op_kwargs={"user": "Rodolfo", "dt_ref": "{{ ds }}"}
    )
    
    task_1 >> task_2 >> task_3

 
generate_dag()