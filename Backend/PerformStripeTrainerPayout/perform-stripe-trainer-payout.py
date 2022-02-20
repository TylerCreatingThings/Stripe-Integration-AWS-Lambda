#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from os import environ
import pymssql
import logging
import traceback
import stripe

endpoint = environ.get('ENDPOINT')
port = environ.get('PORT')
dbuser = environ.get('DBUSER')
password = environ.get('DBPASSWORD')
database = environ.get('DATABASE')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def make_connection():
    return pymssql.connect(
        server=endpoint,
        user=dbuser,
        password=password,
        port=int(port),
        database=database,
        autocommit=True,
        )


def log_err(errmsg):
    logger.error(errmsg)
    return {
        'body': errmsg,
        'headers': {},
        'statusCode': 400,
        'isBase64Encoded': 'false',
        }


logger.info('Cold start complete.')


def handler(event, context):

    # TODO implement

    stripe.api_key = 'x'
    query = "SELECT * FROM [yokd_db].[dbo].[RevenueSummary] where revenueType='Trainer'"
    try:
        try:
            cnx = make_connection()
            cursor = cnx.cursor()
            cursor.execute(query)
            r = []
            results_list = []
            for result in cursor:
                r.append(result)
                results_list = r
            
            #Loop through each record and payout to trainer
            for payoutRecord in results_list:
                stripeTrainerId = payoutRecord[2]
                payoutAmount = str(int(payoutRecord[4]*100)).replace("\n","")
                payout = stripe.Transfer.create(
                          amount=payoutAmount,
                          currency='cad',
                          destination=stripeTrainerId,
                          )
                if payoutRecord[0] != '':
                    query = 'update revenue set revenueCalculatedStatus=1 where revenueId in ('+ str(payoutRecord[0]) + ')'
                    cursor.execute(query)
        except:
            return log_err('ERROR: Cannot retrieve query data.\n{}'.format(traceback.format_exc()))
        cursor.close()
        return {
            'body': 'Successful Run: ' + str(results_list),
            'headers': {},
            'statusCode': 200,
            'isBase64Encoded': 'false',
            }
    except:
        return log_err('ERROR: Cannot connect to database from handler.\n{}'.format(traceback.format_exc()))
    finally:
        try:
            cnx.close()
        except:
            pass


if __name__ == '__main__':
    handler(None, None)