from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .helpers import (
    add_standalone_account,
)

from .models import Customer

def customer_profile(sender, instance, created, **kwargs):
	if created:
		h_addr = add_standalone_account()
		group = Group.objects.get(name='customer')
		instance.groups.add(group)
		Customer.objects.create(
			user=instance,
			name=instance.username,
			email=instance.email,
			algo_private_key=h_addr[0],
			algo_addr=h_addr[1],
			)
		print('Profile created!')

post_save.connect(customer_profile, sender=User)