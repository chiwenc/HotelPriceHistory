from airflow import DAG
from airflow.decorators import dag, task
from airflow.models import XCom
from airflow.operators.python import PythonOperator
from datetime import datetime
from google_travel import get_tracking_request, crawl_single_hotel, insert_single_history_to_db


# 定义默认参数
default_args = {
    'owner': 'your_name',
    'start_date': datetime(2023, 9, 22),
    'retries': 1,
}

# 创建DAG对象
# dag = DAG('web_scraping_dag', 
#           default_args=default_args, 
#           schedule_interval=None,
#           on_success_callback=cleanup_xcom
#           )
# @dag(schedule="@daily", default_args=default_args, catchup=False, schedule_interval=None,)

def query_tracking_request(ti):
    ti.xcom_push(key="tracking_request", value=get_tracking_request())

def get_single_hotel_crawling_result(ti):
    requests = ti.xcom_pull(task_ids='query_request')
    for request in requests:
        ti.xcom_push(key="single_crawlingresult", value=crawl_single_hotel(*request))
    
def insert_single_hotel_crawling_to_db(ti):
    value = ti.xcom_pull(task_ids='crawl_data')
    insert_single_history_to_db(value)

with DAG(
    "xcom_dag",
    start_date=datetime(2023, 9, 22),
    # max_active_runs=2,
    schedule="@daily",
    default_args=default_args,
    catchup=False,
) as dag:
    query_request = PythonOperator(
        task_id="query_request", python_callable=query_tracking_request
    )
    
    crawl_single_data = PythonOperator(
        task_id="crawl_data", python_callable=get_single_hotel_crawling_result
    )

    insert_crawling_data_to_db = PythonOperator(
        task_id="insert_data", python_callable=insert_single_hotel_crawling_to_db
    )

    query_request >> crawl_single_data >> insert_crawling_data_to_db





# @task(task_id="scrape_data")
# def run_spider():
#     crawl_single_hotel(hotel_name, checkin_date, checkout_date)  # 调用爬虫脚本

# crawl_single_hotel_task = PythonOperator(
#     task_id='scrape_data',
#     python_callable=crawl_single_hotel,
#     op_args=[(hotel_name, checkin_date, checkout_date)]
#     dag=dag,
# )


# @task(task_id="insert_task")
# def insert_to_db():
#     insert_single_history_to_db  # 调用插入数据到数据库的脚本



# # 定义任务的顺序
# scrape_task >> insert_task
