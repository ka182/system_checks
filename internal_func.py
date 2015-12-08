import shutil
import subprocess
import json
import logging
import logging.config
import os
import psycopg2

def setup_logging(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

if os.path.exists('conf.json'):
    with open("conf.json") as json_file:
        json_data = json.load(json_file)

def filesystem_space():
    b_to_gb = 1024 * 1024 * 1024
    levels = json_data["filesystem_treshold"]
    paths = json_data["path"]
    for path in paths:
        (total, used, free) = shutil.disk_usage(path)
        percentage_free = ((free / b_to_gb ) / (total / b_to_gb)) * 100
        if percentage_free <= levels[0]:
            logger.info("Path: %s is %.2f free status: Warning" % (path,percentage_free))
        elif percentage_free <= levels[1]:
            logger.error("Path: %s is %.2f free status: DANGER" % (path,percentage_free))
        else:
            logger.info("Path: %s is %.2f free status: OK" % (path,percentage_free))

def check_service():
    ps = subprocess.check_output(['ps', '-ef']).decode()
    list_services = json_data["service"]
    for service in list_services:
        if service in ps:
            logger.info("%s it is UP" % service)
        else:
            logger.error("%s it is DOWN" % service)
            try_count = 1
            while try_count < 4:
                logger.info("Starting %s ... %d" % (service,try_count))
                try:
                    cmd = json_data["service"][service]["cmd"]
                    subprocess.call(cmd, shell=True)
                    cps = subprocess.check_output(['ps', '-A']).decode()
                    if service in cps:
                        logger.info("Service %s started" % service)
                        break
                    else:
                        logger.error("Service %s not started .. %d" % (service,try_count))
                        try_count += 1
                except:
                    logger.error("I am unable to start service %s .. %d" % (service,try_count), exc_info=True)
                    try_count += 1

def check_db():
    dbname = json_data["DB"]["dbname"]
    logger.info("dbname=%s" % dbname )
    dbuser = json_data["DB"]["user"]
    logger.info("dbuser=%s" % dbuser )
    try:
        conn = psycopg2.connect("dbname=%s user=%s" % (dbname,dbuser))
        cur = conn.cursor()
        cur.execute("""SELECT numbackends from pg_stat_database where datname = '%s'""" % dbname)
        res = cur.fetchone()
        logger.info("Number of active connections for fms_db user is %d" % res[0])
        cur.execute("""SELECT max(modify_date) from case_cases_tbl""")
        res = cur.fetchone()
        logger.info("last case processed in system is %s" % res[0])
        cur.close()
        conn.close()
    except:
        logger.error("I am unable to connect to the DB", exc_info=True)