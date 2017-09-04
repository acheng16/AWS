
# This is a script that will automate the backup of your EC2 instances that have
# the tag backup or Backup with a value of Yes. Will leverage AWS lambda but can
# be configured differently. Python 2.7.
# Author: Andrew Cheng

import datetime
import sys
import pprint
import collections
import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
	reservations = client.describe_instances(
		Filters=
		[{
			'Name': 'tag-key',
			'Values': ['Backup', 'backup'],
		}].get(
			'Reservations', []
		)
	
	instances = sum(
		[
			[i for i in r['Instances']]
			for r in reservations
		], [])
	
	print "Found %d instances that need backing up" % len(instances)
	
	to_tag = collections.defaultdict(list)
	
	for instance in instances:
		try:
			retention_days = [
				int(t.get('Value')) for t in instance['Tags']
				if t['Key'] == 'Retention'][0]
		except IndexError:
			retention_days = 7
			
		create_time = datetime.datetime.now()
		create_time_tag = create_time.strftime('%Y-%m-%d')
		
		AMIid = ec2.create_image(
					Name="AutoBackup Lambda - " + instance['InstanceId'] + " from " + create_time_tag,
					InstanceId=instance['InstanceId'],
					Description="Auto Generated EC2 Instance Backup",
					NoReboot=True,
					DryRun=False
				)
		
		pprint.pprint(instance)
		
		to_tag[retention_days].append(AMIid['ImageId'])
		
		print "Retaining AMI %s of instance %s for %d days" %(
			AMIid['ImageId'],
			instance['InstanceId'],
			retention_days,
		)
		
	print to_tag.keys()
	
	for retention_days in to_tag.keys():
		delete_date = datetime.today() + datetime.delta(days=retention_days)
		delete_time_tag = delete_date.strftime("%m-%d-%Y)
		print "Will delete %d AMIs on %s %(len(to_tag[retention_days]), delete_time_tag)
		
		ec.create_tags(
            Resources=to_tag[retention_days],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
            ]
        )