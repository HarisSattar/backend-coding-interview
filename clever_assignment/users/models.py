
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

class UserManager(BaseUserManager):
	"""
	Custom manager for User model.
	Handles user and superuser creation.
	"""
	def create_user(self, email, password=None):
		"""
		Create a regular user with email and password.
		"""
		if not email:
			raise ValueError('The Email field must be set')
		email = self.normalize_email(email)
		user = self.model(email=email)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None):
		"""
		Create a superuser with email and password.
		"""
		user = self.create_user(email, password)
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

class User(AbstractBaseUser, PermissionsMixin):
	"""
	Custom user model for clever_assignment project.
	Uses email as unique identifier.
	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(unique=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	date_joined = models.DateTimeField(auto_now_add=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def __str__(self):
		"""
		String representation of User.
		"""
		return self.email
