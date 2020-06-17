from .models import MyUserManager, credentials, account, bankingCard, transaction, loans, MyUser
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout, authenticate, login
import random, decimal, string, datetime
from datetime import date, datetime
from django.db.models import Sum, Count, Case, When, IntegerField, Q, F, Value
from rest_framework_api_key.models import APIKey
class RegisterUser:
	"""
	THIS FUNCTION IS USED TO REGISTER USER.
	"""
	def __init__(self):
		self.auth = MyUserManager()
		self.accGenerator = generateAccount()

	def register(self,email,secure_code,password1,password2):
		self.email = self.clean_email(email)
		self.sec = secure_code
		self.psw = self.clean_password(password1,password2)
		

		if not self.psw:
			return "Password do not Match!"

		#IF EMAIL IS NOT TRUE
		if not self.email:
			return 'User Already Exist!'

		if self.psw and self.email:
			user = self.auth.create_user(self.email,self.sec,self.psw)
			accountNum = self.accGenerator.accNumberGenerator()
			creditNum = self.accGenerator.creditCardNumber()
			creditCvc = self.accGenerator.create_unique_cvc()
			expiration = self.accGenerator.addYears()
			api_key, key = APIKey.objects.create_key(name=str(accountNum))
			if accountNum:
				accountObject = account(
					account_number=accountNum,
					account_type="Checking",
					account_balance=0.00000,
					user_id=user,
					api_key=key
					)
				accountObject.save()

				cardObject = bankingCard(
					card_number=creditNum,
					cvv=creditCvc,
					expiration_date=expiration,
					user_id=accountObject
					)

				accountObject.save()
				cardObject.save()
				

			return user



	def clean_password(self,password1,password2):

		if password1 and password2 and password1 != password2:
			return False

		return password2

	def clean_email(self,email):

		try:

			match = MyUser.objects.get(email=email)
			return False

		except ObjectDoesNotExist:
			return email

	def insertCredentials(self,fname,lname,mname,street,city,province,barrangay,postal_code,user_id):

		my_user = MyUser.objects.get(pk=user_id)
		credObjects = credentials(
			fname = fname,
			lname = lname,
			mname = mname,
			street = street,
			city = city,
			province = province,
			barrangay = barrangay,
			postal_code = postal_code,
			user_id = my_user
			)
		credObjects.save()
		return credObjects

class LoggingUser:
	"""docstring for LoggingUser"""
	def logmein(self,email,secure_code,password):
		try:
			user = MyUser.objects.filter(email=email,secure_code=secure_code)
			
			return user
		except ObjectDoesNotExist:
			return False
		
class generateAccount:
	"""docstring for generateAccount"""
	def accNumberGenerator(self):
		accNumber = self.create_unique_id()
		unique = False
		try:
			while not unique:
				if not account.objects.get(account_number=accNumber):
					unique = True
				else:
					accNumber = self.create_unique_id()
				
			return accNumber

		except ObjectDoesNotExist:
			return accNumber

	def creditCardNumber(self):
		ccnumber = self.create_unique_creditcard()
		unique = False
		try:
			while not unique:
				if not bankingCard.objects.get(card_number=ccnumber):
					unique = True
				else:
					ccnumber = self.create_unique_creditcard()

			return ccnumber

		except ObjectDoesNotExist:
			return ccnumber
		
	def create_unique_id(self):
		return ''.join(random.choices(string.digits, k=12))

	def create_unique_creditcard(self):
		return ''.join(random.choices(string.digits, k=16))
	
	def create_unique_cvc(self):
		return ''.join(random.choices(string.digits, k=3))

	def addYears(self):
		try:
			d = datetime.now()
			return d.replace(year =d.year + 3)
		except ValueError:
			return d + (date(d.year + years, 3, 3)-date(d.year,3 ,3))

class getUserDetails:
	"""docstring for getUserDetails"""
	def getUserAccountDetails2(self,account_number):
		try:
			account1 = account.objects.filter(account_number=account_number)
			return account1
		except ObjectDoesNotExist:
			return False

	def getMyUser(self,userID):
		try:
			user = MyUser.objects.filter(pk=userID)
			return user
		except ObjectDoesNotExist:
			return False

	def getUserBalance(self,account_number):
		try:
			balance = account.objects.values('account_balance').filter(account_number=account_number).first()
			if balance is None:
				return 0
			return balance['account_balance']
		except ObjectDoesNotExist:
			return False
		
	def updateUserBalance(self,newBalance,account_number):
		try:
			account.objects.filter(account_number=account_number).update(account_balance=newBalance)
			return True
		except ObjectDoesNotExist:
			return False

	def updateUserCurrentLoan(self,newbalance,accountId):
		try:
			if newbalance == 0:
				loans.objects.filter(account_id=accountId,isPaid=False).update(\
					balance=newbalance,isPaid=True)
			else:
				loans.objects.filter(account_id=accountId,isPaid=False).update(balance=newbalance)
		except ObjectDoesNotExist:
			return False

	def getUserLoanPaymentCount(self,accountId):
		try:

			paymentCount = loans.objects.values('numberOfPayments')\
				.filter(account_id=accountId,isPaid=False).first()

			return paymentCount['numberOfPayments']

		except ObjectDoesNotExist:
			return False
		
	def getUserLoanPrincipalAmount(self,accountId):
		try:
			principalAmount = loans.objects.values('parent_amount')\
			.filter(account_id=accountId,isPaid=False).first()
			return principalAmount['parent_amount']

		except ObjectDoesNotExist:
			return False

	def getUserInformation(self,accountId):
		try:
			credentials1 = credentials.objects.filter(user_id=accountId)

			return credentials1
		except ObjectDoesNotExist:
			return False

	def getUserAccountDetails(self,accountId):
		try:
			account1 = account.objects.filter(pk=accountId)
			return account1
		except ObjectDoesNotExist:
			return False

	def getUserTotalLoans(self,accountId):
		try:
			loans1 = loans.objects.filter(account_id=accountId).aggregate(total=Sum('parent_amount'))

			if loans1['total'] is None:
				return 0
			else:
				return loans1['total']
		except ObjectDoesNotExist:
			return False

	def getUserCardDetails(self,accountId):
		try:
			card = bankingCard.objects.filter(user_id__id=accountId)
			return card
		except ObjectDoesNotExist:
			return False
			
	def getUserTotalAmountofLoans(self,accountId):
		try:
			loans1 = loans.objects.values('balance').filter(account_id=accountId,isPaid=False).first()
			if loans1 is None:
				return 0
			return loans1['balance']
		except ObjectDoesNotExist:
			return False

	def getUserTransactionList(self,accountId):
		try:
			transactions = transaction.objects.filter(transacOwner=accountId)
			return transactions
		except ObjectDoesNotExist:
			return False
