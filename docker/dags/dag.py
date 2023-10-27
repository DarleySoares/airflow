
from airflow.decorators import dag
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime, timedelta
from typing import Dict


def day_of_week(ti, ds):
    
    ti.xcom_push(
        key="day_of_week",
        value=datetime.strptime(ds, "%Y-%M-%d").weekday()
    )
    return datetime.strptime(ds, "%Y-%M-%d").weekday()


def branching(**kwargs):
    
    day_of_week = int(kwargs["day_of_week"])

    if day_of_week in [0, 4]:
        return "training_model"
    else:
        return "predict_without_training"
    

def training(ti):
    
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split, cross_val_score
    import numpy as np
    import pickle
    
    iris = load_iris()
    
    X = iris.data
    y = iris.target
    
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    model = LogisticRegression()

    model.fit(x_train, y_train)
    accuracy=model.score(x_test, y_test)
    print('Accuracy:', accuracy)

    score = cross_val_score(model, X, y, cv=5)
    print('CV Score:', np.mean(score))
    
    if accuracy >= 0.95:
        print("Saving model")
        pickle.dump(model, open("./model.sav", 'wb'))
    
    ti.xcom_push(key="accuracy", value=accuracy)
    return accuracy


def predict(**kwargs):
    
    import pickle
    
    model = pickle.load(open("./model.sav", 'rb'))
    results = model.predict(kwargs["samples"])
    print(results)
    

default_args: Dict[str, str] = {
    "retries": 1,
    "retry_delay": timedelta(minutes=2)
}

@dag(
    dag_id="dag_machine_learning",
    start_date=datetime(2023, 10, 1),
    schedule="0 9 * * *",
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["ML", "machine_learning", "sklearn"]
)
def generate_dag():
    
    check_day_of_week = PythonOperator(
        task_id="check_day_of_week",
        python_callable=day_of_week,
        provide_context=True
    )
    
    branching_ = BranchPythonOperator(
        task_id="branching",
        python_callable=branching,
        provide_context=True,
        op_kwargs={
            "day_of_week": "{{ ti.xcom_pull(task_ids=['check_day_of_week'], key='day_of_week')[0] }}"
        }
    )
    
    training_model = PythonOperator(
        task_id="training_model",
        python_callable=training
    )
    
    predicts = PythonOperator(
        task_id="predict_without_training",
        python_callable=predict,
        provide_context=True,
        op_kwargs= {
            "samples": [[5, 3.6, 0.2, 0.1], [2, 1.6, 0.3, 0.1], [4, 2.6, 0.5, 0.1]]
        }
    )
    
    predicts_ = PythonOperator(
        task_id="predict_with_training",
        python_callable=predict,
        provide_context=True,
        op_kwargs={
            "samples": [[5, 3.6, 0.2, 0.1], [2, 1.6, 0.3, 0.1], [4, 2.6, 0.5, 0.1]]
        }
    )
    
    check_day_of_week >> branching_ >> [training_model, predicts]
    training_model >> predicts_

generate_dag()
