from airflow.decorators import dag, task_group
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from typing import Dict

default_args: Dict[str, str] = {
    "retries": 1,
    "retry_delay": timedelta(minutes = 5)
}


def good_morning(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good morning, today is {ds}"


def good_afternoon(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good afternoon, today is {ds}"


def good_night(ds, **kwargs) -> str:
    return f"Hi, {kwargs['user']}! Good night, today is {ds}"

@dag(
    dag_id = "dag_taskgroup",
    start_date = datetime(2023, 10, 1),
    schedule = "0 21 * * *",
    default_args = default_args,
    catchup = True,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["XCOM", "daily"]
)
def generate_dag():
    
    users = ["user_1", "user_2", "user_3", "user_4"]
    all_tasks = []
    for user in users:
        
        @task_group(group_id=user)
        def tasks():
            morning = PythonOperator(
                task_id=f"good_morning_to_{user}",
                python_callable=good_morning,
                provide_context=True,
                op_kwargs={"user": user, "dt_ref": "{{ ds }}"},
            )
            
            afternoon = PythonOperator(
                task_id=f"good_afternoon_to_{user}",
                python_callable=good_afternoon,
                provide_context=True,
                op_kwargs={"user": user, "dt_ref": "{{ ds }}"},
            )
            
            night = PythonOperator(
                task_id=f"good_night_to_{user}",
                python_callable=good_night,
                provide_context=True,
                op_kwargs={"user": user, "dt_ref": "{{ ds }}"},
            )
        
            morning >> afternoon >> night

        tasks()
    
    

 
generate_dag()