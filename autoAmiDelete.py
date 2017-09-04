
# This is a script that will automate the delete of backup of your EC2 instances that have
# the tag backup or Backup with a value of Yes. Will leverage AWS lambda but can
# be configured differently. Python 2.7.
# Author: Andrew Cheng

import boto3
import collections
import datetime
import time
import sys

ec = boto3.client('ec2', 'us-west-2')
ec2 = boto3.resource('ec2', 'us-west-2')
images = ec2.images.filter(Owners=["self"])

def lambda_handler(event, context):

    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag-key',
			'Values': ['backup', 'Backup']},
        ]
    ).get(
        'Reservations', []
    )
	
	instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print "Found %d instances that need evaluated" % len(instances)
	
	to_tag = collections.defaultdict(list)

    date = datetime.datetime.now()
    date_time = date.strftime('%Y-%m-%d')
	
	imagesList = []

    # Set to true once we confirm we have a backup taken today
    backupSuccess = False

    # Loop through all of our instances with a tag named "Backup"
    for instance in instances:
		imagecount = 0
		 # Loop through each image of our current instance
        for image in images:

            # Our other Lambda Function names its AMIs Lambda - i-instancenumber.
            # We now know these images are auto created
            if image.name.startswith('AutoBackup Lambda - ' + instance['InstanceId']):

	        imagecount = imagecount + 1

                try:
                    if image.tags is not None:
                        deletion_date = [
                            t.get('Value') for t in image.tags
                            if t['Key'] == 'DeleteOn'][0]
                        delete_date = time.strptime(deletion_date, "%m-%d-%Y")
                except IndexError:
                    deletion_date = False
                    delete_date = False

                today_time = datetime.datetime.now().strftime('%m-%d-%Y')
                # today_fmt = today_time.strftime('%m-%d-%Y')
                today_date = time.strptime(today_time, '%m-%d-%Y')

                # If image's DeleteOn date is less than or equal to today,
                # add this image to our list of images to process later
                if delete_date <= today_date:
                    imagesList.append(image.id)

                # Make sure we have an AMI from today and mark backupSuccess as true
                if image.name.endswith(date_fmt):
                    # Our latest backup from our other Lambda Function succeeded
                    backupSuccess = True
                    print "Latest backup from " + date_fmt + " was a success"

        print "instance " + instance['InstanceId'] + " has " + str(imagecount) + " AMIs"

    print "============="

	