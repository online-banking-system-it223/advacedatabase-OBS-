from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.postgres.fields import JSONField

class MyUserManager(BaseUserManager):
    def create_user(self, email, secure_code, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not secure_code:
            raise ValueError('Users must have an secure code')

        user = MyUser(
            email=MyUserManager.normalize_email(email),
            secure_code = secure_code,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, secure_code, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        u = self.create_user(email=email,
                        password=password,
                        secure_code = secure_code
                    )
        u.is_admin = True
        u.save(using=self._db)
        return u


class MyUser(AbstractBaseUser):
    email = models.EmailField(
                        verbose_name='email address',
                        max_length=255,
                        unique=True,
                    )
    secure_code = models.IntegerField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['secure_code']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class credentials(models.Model):
	"""docstring for credentials"""

	fname = models.CharField(max_length=50)
	lname = models.CharField(max_length=50)
	mname = models.CharField(max_length=50)
	street = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	province = models.CharField(max_length=50)
	barrangay = models.CharField(max_length=50)
	postal_code = models.IntegerField()	
	user_id = models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="user_credentials")

	def __str__(self):
		return f"{self.getFullName()}"

	def __unicode__(self):
		return f"Full Name: {self.getFullName()} Address: {self.getFullAddress()}"

	def getFullName(self):
		return f"{self.fname} {self.mname} {self.lname}"

	def getFullAddress(self):
		return f"{self.street}, {self.street}, {self.barrangay}, {self.city}, {self.province}, {self.postal_code}"

class account(models.Model):
	"""docstring for account"""

	account_number = models.BigIntegerField(unique=True)
	account_type = models.CharField(max_length=50)
	account_balance = models.DecimalField(max_digits = 30, decimal_places = 5)
	isLocked = models.BooleanField(default=False)
	user_id = models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="user_account")
	api_key = models.CharField(max_length=50)

	def __str__(self):
		return f"{self.id}"

	def get_account_number(self):
		return self.account_number

	def get_account_balance(self):
		return self.account_balance

	def __unicode__(self):
		return self.account_number

class bankingCard(models.Model):
	"""docstring for creditcard"""
	STANDARD = 'ST'
	STUDENT = 'SC'
	CHARGE = 'CC'
	SECURE = 'SECC'
	PREPAID = 'PR'

	typeschoices = (
		("ST", "Standard"),
		("SC", "Student Credit"),
		("CC", "Charge Cards"),
		("SECC", "Secured Credit"),
		("PR", "Prepaid"),)

	card_number = models.CharField(max_length=19,unique=True)
	cvv = models.IntegerField()
	expiration_date = models.DateField(('DATE'))
	isDisabled = models.BooleanField(default=False)
	cardType = models.CharField(max_length = 5,choices = typeschoices, default = STANDARD)
	user_id = models.ForeignKey(account,on_delete=models.CASCADE,related_name="user_creditcard")

	def __str__(self):
		return self.get_card_number()

	def get_card_number(self):
		return self.card_number

	def __unicode__(self):
		return self.card_number

class transaction(models.Model):
	"""docstring for transaction"""
	transaction_type = models.CharField(max_length=50)
	transacReceiver = models.ForeignKey(account,on_delete=models.CASCADE,null=True,related_name="transaction_receiver")
	date = models.DateField(('DATE'),auto_now_add=True)
	amount = models.DecimalField(max_digits = 30, decimal_places = 5)
	newBalance = models.DecimalField(max_digits = 30, decimal_places = 5)
	transacOwner = models.ForeignKey(account,on_delete=models.CASCADE,related_name="transaction_sender")

	class Meta:
		ordering = ["-date"]

	def __str__(self):
		return self.transaction_type

class loans(models.Model):
	"""docstring for loans"""
	parent_amount = models.DecimalField(max_digits = 30, decimal_places = 5)
	interest = models.IntegerField()
	loan_date = models.DateField(('DATE'))
	due_date = models.DateField(('DATE'))
	balance = models.DecimalField(max_digits = 30, decimal_places = 5)
	isPaid = models.BooleanField(default=False)
	numberOfPayments = models.IntegerField()
	account_id = models.ForeignKey(account,on_delete=models.CASCADE,related_name="loaner")
	transaction_id = models.ForeignKey(transaction,on_delete=models.CASCADE,related_name="transaction_id")

	def __unicode__(self):
		return f"Loan by: {self.account_id.account_number}"

class emails(models.Model):
	sender = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,related_name="email_owner")
	receiver = models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="email_receiver")
	date = models.DateTimeField(('DATE'),auto_now_add=True)
	subject = models.CharField(max_length=50)
	body = models.TextField()
	opened = models.BooleanField(default=False)

	class Meta:
		ordering = ["-date"]

	def __str__(self):
		return self.subject


class ApiPayments(models.Model):
	"""
	This model is for payment confirmation. 
	"""
	invoiceId = models.CharField(max_length=50)
	pending = models.BooleanField(default=False)
	amount = models.DecimalField(max_digits = 30, decimal_places = 5)
	payer = models.ForeignKey(account,on_delete=models.CASCADE,related_name="payer")
	seller = models.ForeignKey(account,on_delete=models.CASCADE,related_name="seller")
	dateCreated = models.DateTimeField(('DATE'),auto_now_add=True)
	dateConfirmed = models.DateTimeField(('DATE'),null=True)
	deleted = models.BooleanField(default=False)
	def __str__(self):
		return self.invoiceId		

class apiTransaction(models.Model):
	"""docstring for apiTransaction"""
	owner = models.ForeignKey(account,on_delete=models.CASCADE,related_name="transactionOwner")
	parentTransaction = models.ForeignKey(ApiPayments,on_delete=models.CASCADE,related_name="parent_transaction")
	transaction = JSONField()

	def __int__(self):
		return self.owner.account_number

class cancelledPayments(models.Model):
	"""docstring for cencelledPayments"""
	Payment = models.ForeignKey(ApiPayments,on_delete=models.CASCADE,related_name="parent_payment")
	dateCancelled = models.DateTimeField(('DATE'),auto_now_add=True)
	transaction = JSONField()
	def __str__(self):
		return self.dateCancelled


#logs for trigger and procedure
class logs(models.Model):
	eventname = models.CharField(max_length=50)
	sender = models.CharField(max_length=50)
	receiver = models.CharField(max_length=50,null=True)
	date = models.DateTimeField(('DATE'))

	def __str__(self):
		return self.date

#this is the functional code for the views
class recent_mails(models.Model):
	sender = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,related_name="views_sender")
	receiver = models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="views_receiver")
	date = models.DateTimeField(('DATE'),auto_now_add=True)
	subject = models.CharField(max_length=50)
	body = models.TextField()
	opened = models.BooleanField(default=False)

	class Meta:
		ordering = ["-date"]
		managed = False
		db_table = 'recent_mails_views'

	def __str__(self):
		return self.subject

class readed_mails(models.Model):
	sender = models.ForeignKey(MyUser,on_delete=models.CASCADE,null=True,related_name="views_sender")
	receiver = models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="views_receiver")
	date = models.DateTimeField(('DATE'),auto_now_add=True)
	subject = models.CharField(max_length=50)
	body = models.TextField()
	opened = models.BooleanField(default=False)

	class Meta:
		ordering = ["-date"]
		managed = False
		db_table = 'readed_mails_views'

	def __str__(self):
		return self.subject