# coding=utf-8
import os
import sys
import math
import uuid
import time
import click
import numpy
import pandas
import signal
import psutil
import codecs
import gevent
# import random
import settings

from utils.logger_utils import logger

from gevent import monkey
from multiprocessing import Process

from utils import file_writer as file_operator
# from utils import postgresql_utils as db
from website_class.baidu_spider import BaiduSpider
from website_class.sougou_spider import SougouSpider
from website_class.ip138_spider import get_restful_from_mobile_ip138


reload(sys)
sys.setdefaultencoding('utf-8')

monkey.patch_all()

BAIDU_SPIDER = BaiduSpider()
SOUGOU_SPIDER = SougouSpider()

GLOBAL_TABLE_NAME = ""

SPLIT_NUMBER = 4

PROCESS_LIST = []
PART_OF_FILE_PREFIX = ""

SAVED_PHONES_DICT = {}

pool = None


def create_directory(directory_path):
    try:
        os.makedirs(directory_path)
    except Exception:
        pass


def is_process_alive(pid):
    try:
        if not pid:
            return False
        psutil.Process(pid)
        return True
    except psutil.NoSuchProcess:
        return False


def monitor_process():
    global PROCESS_LIST, PART_OF_FILE_PREFIX

    success_count = 0
    failed_count = 0

    while 1:
        logger.info("monitor process...")
        for _ in xrange(len(PROCESS_LIST)):
            process = PROCESS_LIST.pop()

            if not process.is_alive():

                if process.exitcode == 0:
                    success_count += 1
                elif process.exitcode != 1:
                    failed_count += 1
            else:
                PROCESS_LIST.append(process)

            if success_count + failed_count == 4:
                logger.info("task done. success : {success_count}, failed : {failed_count}".format(success_count=success_count,
                                                                                                   failed_count=failed_count))
                if success_count == 4:
                    combine_file(PART_OF_FILE_PREFIX)

                exit(0)

        time.sleep(5)


def combine_file(part_of_file_prefix):
    line_count = 0

    temp_upload_file_path = settings.LOCAL_STORAGE_FILE_PATH + "/" + part_of_file_prefix + "_temp.txt"

    file_operator.create_file(temp_upload_file_path, short_header=False)

    with open(temp_upload_file_path, 'wb') as write_file:
        for filename in os.listdir(settings.LOCAL_STORAGE_FILE_PATH):
            if part_of_file_prefix in filename and part_of_file_prefix + "_temp.txt" != filename:
                with open(settings.LOCAL_STORAGE_FILE_PATH + "/" + filename) as read_file:
                    read_file.readline()
                    for line in read_file:
                        line_count += 1
                        write_file.write(str(line_count) + "^" + line)

    target_upload_file_path = settings.LOCAL_STORAGE_UPLOAD_PATH + "/MobileTags_" + part_of_file_prefix + ".txt"

    if os.path.exists(target_upload_file_path):
        os.remove(target_upload_file_path)

    os.rename(temp_upload_file_path, target_upload_file_path)


def split_file(file_path, split_number):
    counter = 0
    line_limit = 0

    file_path_list = []

    if os.path.isfile(file_path):
        line_limit = math.ceil(get_file_lines_count(file_path) / float(split_number))
        file_path_list.append(file_path)

    for file_path_unit in file_path_list:
        with open(file_path_unit) as fin:
            output_filename = "{save_path}_{counter}.txt".format(save_path=file_path[:-4], counter=counter)

            counter += 1
            fout = open(output_filename, "wb")
            for i, line in enumerate(fin):
                fout.write(line)
                if (int(i) + 1) % line_limit == 0:
                    fout.close()

                    output_filename = "{save_path}_{counter}.txt".format(save_path=file_path[:-4], counter=counter)
                    counter += 1
                    fout = open(output_filename, "wb")

        fout.close()


def get_error_log_path(file_name_prefix):
    file_name_prefix = file_name_prefix.encode("utf-8")

    file_count = len([filename for filename in os.listdir(settings.LOCAL_STORAGE_FILE_PATH) if file_name_prefix in filename])

    file_path = settings.LOCAL_STORAGE_FILE_PATH + "/" + file_name_prefix + "_" + str(file_count + 1) + ".txt"

    return file_path


def get_file_lines_count(file_path):

    counter = 0
    with open(file_path) as fin:
        for _ in fin:
            counter += 1

    return counter


# def make_table_exist():
#     db.create_table_if_not_exist()


def crawl_phone_tag(file_path):
    global SAVED_PHONES_DICT

    generator = get_phone(file_path)

    file_name = "" + file_path[file_path.rfind("/") + 1:-4] + ".txt"
    file_path = settings.LOCAL_STORAGE_FILE_PATH + "/" + file_name

    if not os.path.exists(file_path):
        file_operator.create_file(file_path)

    SAVED_PHONES_DICT = pandas.read_table(file_path, sep="^", header=0, usecols=['phone'], low_memory=False)
    SAVED_PHONES_DICT = set(numpy.array(SAVED_PHONES_DICT['phone']).tolist())

    logger.info("load crawled phone success, number is {number}".format(
        number=len(SAVED_PHONES_DICT)))

    tasks = []

    counter = 0
    for phone in generator:
        tasks.append(gevent.spawn(fetch_page, file_path, phone))
        counter += 1

        if counter % 25 == 0:
            gevent.joinall(tasks)
            tasks = []

        return
    if len(tasks):
        gevent.joinall(tasks)


def fetch_page(file_path, phone):

    retry_times = 0

    while 1:

        with gevent.Timeout(30, False):

            try:
                # db.set_table_name(table_name)

                if not is_number(phone):
                    logger.warning("phone {phone} invalid, skip this one.".format(phone=phone))
                    return

                # if db.is_exist(phone=phone):
                #     return

                phone_item = dict()

                phone_item["phone"] = phone.encode("utf-8")

                if int(phone) not in SAVED_PHONES_DICT and str(phone) not in SAVED_PHONES_DICT:
                    logger.info("crawling phone {phone}...".format(phone=phone))

                    try:
                        logger.info("crawling phone {phone} 's ip138...".format(phone=phone))
                        phone_item["city"], phone_item["corp"] = get_restful_from_mobile_ip138(phone)
                    except Exception:
                        logger.warning("phone {phone} unable crawl ip138's data, using default value.".format(phone=phone))
                        phone_item["city"], phone_item["corp"] = "", ""

                    tag_set = set()
                    try:
                        logger.info("crawling phone {phone} 's baidu...".format(phone=phone))
                        tag_set.update([str(BAIDU_SPIDER.query(phone).get("tag", ""))])
                    except Exception:
                        logger.warning("phone {phone} unable crawl baidu's data, using default value.".format(phone=phone))
                        tag_set.update([u"百度错误了"])

                    try:
                        logger.info("crawling phone {phone} 's sougou...".format(phone=phone))
                        tag_set.update([str(SOUGOU_SPIDER.query(phone).get("tag", ""))])
                    except Exception:
                        logger.warning("phone {phone} unable crawl sogou's data, using default value.".format(phone=phone))
                        tag_set.update([u"搜狗错误了"])

                    phone_item["tag"] = "|".join(tag_set)
                    phone_item["crawl_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    phone_item = format_phone_item(phone_item)

                    # phone_id = str(uuid.uuid5(uuid.NAMESPACE_URL, repr(phone_item)))
                    phone_item['uuid'] = str(uuid.uuid5(uuid.NAMESPACE_URL, repr(phone_item)))

                    # db.push_item(phone_id, phone_item)

                    result = file_operator.push_item(file_path, [phone_item['uuid'], phone_item['phone'], phone_item['city'],
                                                                 phone_item['corp'], phone_item['tag'], phone_item['crawl_time']])

                    if not result:
                        # file_operator.record_error_log(error_log_file_path, phone_item['phone'])
                        logger.warning("phone {phone} crawl failed.".format(phone=phone))

                    logger.info("phone {phone} crawl done.".format(phone=phone))

                file_operator.counter += 1
                return True

            except Exception as e:
                if "Failed to establish a new connection" in str(e):
                    logger.warning("network look like crash, sleep 1 second.")
                    time.sleep(1)
                else:
                    logger.warning(e)

                retry_times += 1

                if retry_times >= 30:
                    return False


def format_phone_item(phone_item):
    try:
        if phone_item["tag"][0] == "|":
            phone_item["tag"] = phone_item["tag"][1:]
    except IndexError:
        pass

    try:
        if phone_item["tag"][-1] == "|":
            phone_item["tag"] = phone_item["tag"][:-1]
    except IndexError:
        pass

    return phone_item


def is_number(phone):
    return phone.isdigit()


def is_param_file_exist(param_file_path):
    return os.path.exists(param_file_path)


def get_phone(param_file_path):
    with codecs.open(param_file_path, 'rb', 'utf-8') as f:
        for line in f:
            if "^" in line:
                phone_prefix = line.split("^")[1]

                for i in xrange(10000):
                    yield phone_prefix + str(i).zfill(4)
            elif is_number(line):
                yield line


def _exit(signum, frame):
    _ = signum
    _ = frame

    # db.flush_item()
    # db.close()
    logger.info("closing program..")
    exit()


signal.signal(signal.SIGINT, _exit)
signal.signal(signal.SIGTERM, _exit)


@click.command()
@click.option("--table_name")
@click.option("--param_file_path")
def main(table_name, param_file_path):
    global GLOBAL_TABLE_NAME, PROCESS_LIST, PART_OF_FILE_PREFIX, pool

    GLOBAL_TABLE_NAME = table_name

    PART_OF_FILE_PREFIX = param_file_path[param_file_path.rfind("/") + 1: param_file_path.rfind(".")]

    # ERROR_LOG_FILE_NAME = get_error_log_path("crawler_error_" + PART_OF_FILE_PREFIX)

    create_directory(settings.LOCAL_STORAGE_FILE_PATH)
    create_directory(settings.LOCAL_STORAGE_UPLOAD_PATH)

    # db.set_table_name(GLOBAL_TABLE_NAME)

    # make_table_exist()

    split_file(file_path=param_file_path, split_number=SPLIT_NUMBER)

    logger.info("start crawl")

    # pool = ProcessPoolExecutor(4)

    if is_param_file_exist(param_file_path=param_file_path):
        for file_index in xrange(SPLIT_NUMBER):
            file_path = str("{save_path}_{counter}.txt".format(save_path=param_file_path[:-4], counter=file_index))

            # PROCESS_LIST.append(pool.submit(crawl_phone_tag, file_path))
            process = Process(target=crawl_phone_tag, args=(file_path, ))
            process.start()

            PROCESS_LIST.append(process)

    monitor_process()


def sayHello():
    print("hello")


if __name__ == "__main__":
    main()
