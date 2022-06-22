import requests
import base64
import boto3
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient

def lambda_handler(event, context):   
    blob = event["body"]
    s3 = boto3.resource("s3")
    bucket_name = os.environ["BUCKET"]
    file_name = "image.jpg"

    # store to s3
    obj = s3.Object(bucket_name, file_name)
    obj.put(Body=base64.b64decode(blob))

    # get s3 url
    s3_url = os.environ["S3_URL"]

    # put s3 url into ocr api
    form_recognizer_client = FormRecognizerClient(os.environ["ENDPOINT"], AzureKeyCredential(os.environ["AZURE_KEY"]))
    
    # get ocr results
    poller = form_recognizer_client.begin_recognize_identity_documents_from_url(s3_url)
    result = poller.result()[0]
    fields = result.fields["MachineReadableZone"].value
    # format api response
    return {
        "FirstName": fields["FirstName"].value,
        "LastName": fields["LastName"].value,
        "CountryRegion": fields["CountryRegion"].value,
        "DateOfBirth": fields["DateOfBirth"].value.strftime('%Y-%m-%d'),
        "DateOfExpiration": fields["DateOfExpiration"].value.strftime('%Y-%m-%d'),
        "DocumentNumber": fields["DocumentNumber"].value,
        "Nationality": fields["Nationality"].value,
        "Sex": fields["Sex"].value,
    }
