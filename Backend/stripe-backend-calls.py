import json
from os import environ
from botocore.exceptions import ClientError
import boto3
import botocore.vendored.requests as requests
import pymssql
import logging
import traceback

logger=logging.getLogger()
logger.setLevel(logging.INFO)

def log_err(errmsg):
	logger.error(errmsg)
	return {"body": errmsg, "headers": {}, "statusCode": 400,"isBase64Encoded":"false"}
logger.info("Cold start complete.") 

def handler(event, context):
    stripe.api_key = 'x'
    if vars[0] == "stripeTrainerSetup":
        response = stripe.OAuth.token(
            grant_type='authorization_code',
            code=event['queryStringParameters']['code'],
            )
        query = "exec attachStripeIdToTrainer '"+event['queryStringParameters']['state']+"','"+response['stripe_user_id']+"'"
    elif vars[0] == "stripeTrainerTransactions":
        #return {"body": event['queryStringParameters']['trainerStripeId'], "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}
        return {"body":  str(stripe.Account.create_login_link(event['queryStringParameters']['trainerStripeId']).url), "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}
        #return stripe.issuing.Transaction.list(cardholder=event['queryStringParameters']['trainerStripeId'])
    elif vars[0] == "getStripeKey":
        return "x"
    elif vars[0] == "setupStripeCard":
        setup_intent = stripe.SetupIntent.create()
        return {"body":  setup_intent.client_secret, "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}
    elif vars[0] == "attachStripeCardAndCreateCustomer":
        if event['queryStringParameters'] is not None and event['queryStringParameters']['paymentMethodId'] is not None:
            customer = stripe.Customer.create(
                payment_method=event['queryStringParameters']['paymentMethodId']
                )
            query = "exec attachStripeCardAndCreateCustomer '" + event['queryStringParameters']['token'] +"','" + customer.id + "'"
    elif vars[0] == "createStripeCustomer":
        if event['queryStringParameters'] is not None:
            customer = stripe.Customer.create()
            query = "exec attachStripeCardAndCreateCustomer '" + event['queryStringParameters']['token'] +"','" + customer.id + "'"
    elif vars[0] == "getCustomerEphimeralKey":
        key = stripe.EphemeralKey.create(customer=event['queryStringParameters']['customerStripeId'], stripe_version=event['queryStringParameters']['apiVersion'])
        return {"body":  str(key), "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}
    elif vars[0] == "createStripePaymentIntent":
        cards = stripe.PaymentMethod.list(
            customer=event['queryStringParameters']['customerStripeId'],
            type="card",
            )
        #return {"body":  transfer_data["destination"], "headers": {}, "statusCode": 200,"isBase64Encoded":"false"}
        intent = stripe.PaymentIntent.create(
            amount=int(event['queryStringParameters']['amount']),
            currency='cad',
            payment_method_types=['card'],
            customer=event['queryStringParameters']['customerStripeId'],
            payment_method=cards.data[0].id,
            application_fee_amount=math.ceil(int(event['queryStringParameters']['amount'])*0.05), #percent
            transfer_data={
                'destination': event['queryStringParameters']['trainerStripeId'],
                },
            )

        return {"body":  intent.client_secret, "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}
    elif vars[0] == "createStripePaymentReferralIntent":
        cards = stripe.PaymentMethod.list(
            customer=event['queryStringParameters']['customerStripeId'],
            type="card",
            )
        #return {"body":  transfer_data["destination"], "headers": {}, "statusCode": 200,"isBase64Encoded":"false"}
        intent = stripe.PaymentIntent.create(
            amount=int(event['queryStringParameters']['amount']),
            currency='cad',
            payment_method_types=['card'],
            customer=event['queryStringParameters']['customerStripeId'],
            payment_method=cards.data[0].id,
            application_fee_amount=math.ceil(int(event['queryStringParameters']['amount'])*0.05), #percent taken
            transfer_data={
                'destination': event['queryStringParameters']['trainerStripeId'],
                },
            )

        return {"body":  intent.client_secret, "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}
    elif vars[0] == "createStripeRecurringPaymentReferralIntent":
        cards = stripe.PaymentMethod.list(
            customer=event['queryStringParameters']['customerStripeId'],
            type="card",
            )
        #return {"body":  transfer_data["destination"], "headers": {}, "statusCode": 200,"isBase64Encoded":"false"}
        intent = stripe.Subscription.create(
            items={'price_data' : {'currency':'cad','unit_amount': int(event['queryStringParameters']['amount']),'recurring': {'interval': 'week','interval_count':1}}},
            current_period_start=event['queryStringParameters']['startTimestamp'],
            current_period_end=event['queryStringParameters']['endTimestamp'],
            currency='cad',
            customer=event['queryStringParameters']['customerStripeId'],
            billing_cycle_anchor=event['queryStringParameters']['startTimestamp'],
            application_fee_amount=math.ceil(int(event['queryStringParameters']['amount'])*0.5), #percent taken
            transfer_data={
                'destination': event['queryStringParameters']['trainerStripeId'],
                },
            )

        return {"body":  intent.client_secret, "headers": {"Access-Control-Allow-Headers" : "Content-Type","Access-Control-Allow-Origin": allowedOrigin,"Access-Control-Allow-Methods": "OPTIONS,POST,GET"}, "statusCode": 200,"isBase64Encoded":"false"}

    elif vars[0] == "modifyStripePaymentIntent":
        if event['queryStringParameters'] is not None and event['queryStringParameters']['token'] is not None:
            if event['queryStringParameters']['amount'] is not None:
                stripe.PaymentIntent.modify(
                    event['queryStringParameters']['token'],
                    amount=event['queryStringParameters']['amount'],
                    )