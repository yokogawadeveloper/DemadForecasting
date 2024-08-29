from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	USER_CHOICES = (
	("official", "official"),
	("admin", "admin"),)

	roleOfEmployee = models.CharField(max_length = 20, choices = USER_CHOICES, default = "official")

	def __str__(self):
		return str(self.roleOfEmployee)
	
	class Meta:
		db_table = 'auth_user'
