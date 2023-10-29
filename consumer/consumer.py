from kafka import KafkaConsumer, TopicPartition
from json import loads
import io
import pandas as pd
from config import config
import gzip
import logging
from typing import List
from producer import get_database_engine

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')


def get_file(id: str):
    """
Retrieves a file from the database using the given attachment ID and saves it locally.

Args:
    id (str): Attachment ID used to fetch the file from the database.

Raises:
    gzip.BadGzipFile: If the extracted file is not a valid GZIP file.
"""
    db_engine = get_database_engine(config)
    sql = f"""
        SELECT vchAttachmentName, convert(varbinary(max), binDocbytes, 1) as binDocBytes
        FROM dAttachmentBinaryDocuments ab
        join dAttachment a on ab.intAttachmentId = a.intAttachmentId
        where ab.intAttachmentId = {id}"""
    df = pd.read_sql(sql, db_engine)
    dest_path = 'file/'
    data = df.values
    file_name = data[0][0]
    varbinary = data[0][1]
    file_path = dest_path + file_name
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(varbinary), mode='rb') as f_in:
            with open(file_path, 'wb') as f_out:
                f_out.write(f_in.read())
    except gzip.BadGzipFile as err:
        logging.warn(f"{err}{file_name} can't be extract")


def save_offset(offset: int):
    """
Saves the provided offset to a file for resuming Kafka message consumption.

Args:
    offset (int): The offset value to be saved.
"""
    offset_file = 'offset.txt'
    with open(offset_file, 'w') as f:
        f.write(str(offset))


def read_offset() -> int | None:
    """
Reads the last saved offset from the file.

Returns:
    int or None: The last saved offset if the file exists, else None.
"""
    offset_file = 'offset.txt'
    try:
        with open(offset_file, 'r') as f:
            return int(f.read())
    except FileNotFoundError:
        return None


def get_no_records() -> int:
    db_engine = get_database_engine(config)
    sql = """select count(1) from dAttachmentBinaryDocuments"""
    df = pd.read_sql(sql, db_engine)
    col_name = df.columns[0]
    no_records = df[col_name].values[0]
    return no_records


def consume_data(topic: str, bootstrap_servers: List[str]):
    """
Consumes messages from the specified Kafka topic starting from the last saved offset.
Processes each message by fetching the corresponding file from the database.

Args:
    topic (str): The Kafka topic to consume messages from.
    bootstrap_servers (list[str]): List of Kafka broker addresses.
"""
    logging.info('Start consume data...')
    offset = read_offset()
    no_records = get_no_records()
    if offset is None:
        offset = 0
    print(offset)
    consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers,
                             value_deserializer=lambda x: loads(x.decode('utf-8')))

    partition = TopicPartition(topic, 0)
    consumer.assign([partition])
    consumer.seek(partition=partition, offset=offset)
    for message in consumer:
        offset = message.offset
        id = message.value
        print(f"Offset: {offset}, Value: {id}")
        get_file(id)
        next_offset = offset+1
        if next_offset <= 10:
        # if next_offset <= no_records:
            save_offset(next_offset)
        else:
            consumer.close()
            logging.info('Consume data completely')


if __name__ == '__main__':
    consume_data('extract_data', ['kafka:19092'])
