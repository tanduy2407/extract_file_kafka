from kafka import KafkaProducer
import json
from config import config
import sqlalchemy
import pandas as pd
import time
import logging
from typing import List, Union, Dict

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')


def get_database_engine(config: Dict):
    """
    Establishes a connection to the database based on the provided configuration.

    Args:
        config (dict): Dictionary containing database connection details.

    Returns:
        sqlalchemy.engine.Engine: Database engine object for executing SQL queries.
    """
    engine = None
    if config['system'] == 'mssql':
        engine = sqlalchemy.create_engine(
            'mssql+pymssql://{0}:{1}@{2}:{3}/{4}?charset=utf8'.format(
                config['user'], config['password'],
                config['server'], config['port'],
                config['database']))

    if config['system'] == 'mysql':
        engine = sqlalchemy.create_engine(
            'mysql+pymysql://{0}:{1}@{2}/{3}'.format(
                config['user'], config['password'],
                config['server'], config['database']))

    if config['system'] == 'postgresql':
        engine = sqlalchemy.create_engine(
            'postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'.format(
                config['user'], config['password'],
                config['server'], config['port'],
                config['database']),
            pool_size=100,
            max_overflow=200,
            client_encoding='utf8')
    return engine


def get_id() -> List[Union[int, str]]:
    """
    Retrieves a list of document IDs from the database.

    Returns:
        list[int | str]: List of document IDs.
    """
    db_engine = get_database_engine(config)
    sql = """select top 10 intAttachmentId from dAttachmentBinaryDocuments"""
    df = pd.read_sql(sql, db_engine)
    col_name = df.columns[0]
    document_ids = df[col_name].to_list()
    no_records = len(document_ids)
    return document_ids, no_records


def produce_data_to_kafka(document_ids: List[int], topic: str, bootstrap_servers: List[str]):
    """
    Produces document IDs to a Kafka topic.

    Args:
        document_ids (list[int]): List of document IDs to be sent to Kafka.
        topic (str): The Kafka topic to which the messages will be sent.
        bootstrap_servers (list[str]): List of Kafka broker addresses.
    """
    logging.info('Start produce data...')
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    for document_id in document_ids:
        producer.send(topic, json.dumps(str(document_id)).encode('utf-8'))
        producer.flush()
        time.sleep(2)
    logging.info('Produce data completely')


if __name__ == '__main__':
    ids, no_records = get_id()
    produce_data_to_kafka(ids, 'extract_data', ['kafka:19092'])

# kafka-server-start.bat D:\Apps\Kafka\config\server.properties
# zookeeper-server-start.bat D:\Apps\Kafka\config\zookeeper.properties
