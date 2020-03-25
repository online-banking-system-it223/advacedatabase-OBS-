from .models import logs, transaction, loans, notifications, bankingCard, apiTransaction
from django.core.exceptions import ObjectDoesNotExist
import random, string, datetime, decimal
from datetime import date
from datetime import datetime
from .userManagement import getUserDetails
from django.http import HttpResponse
from math import floor, ceil
from cryptography.fernet import Fernet
class bankingMethod:
	"""docstring for bankTransfer"""
	def __init__(self):
		#GET OTHER CLASS
		self.userObjects = getUserDetails()
		self.notifier = notifier()
		self.logger = logsTrigger()
		self.transac = transactionRecorder()

		#METHOD FOR TRANSFERING FUND
	def methodTransfer(self,account_number,accountId,amount):
		#GET SENDER ID
		sender = self.userObjects.getUserAccountDetails(accountId)
		#GET RECEIVER ID
		receiver = self.userObjects.getUserCredentials(account_number)
		#GET SENDER BALANCE
		senderBalance = self.userObjects.getUserBalance(accountId)
		#GET RECEIVER BALANCE
		receiverBalance = self.userObjects.getUserBalance(account_number)

		for x in sender:
			senderAccNumber = x.account_number

		for x in receiver:
			receiverAccNumber = x.account_number

		senderBalance = self.userObjects.getUserBalance(senderAccNumber)

		receiverBalance = self.userObjects.getUserBalance(receiverAccNumber)



		#CHECK IF THE RECEIVER IS FOUND
		if not receiver:
			return "Receiver not found!"

		#CHECK IF SENDER HAS SUFFICIENT FUNDS FOR TRANSFER
		if senderBalance < amount:
			return "Non-sufficient funds!"

		#FINAL CONDITION FOR TRANSFERING FUNDS
		if senderBalance > amount or receiver:
			#THE NEW SENDER BALANCE
			senderNewBalance = senderBalance - amount
			#THE NEW RECEIVER BALANCE
			receiverNewBalance = receiverBalance + amount

			#UPDATE EACH OTHER USER BALANCE
			self.userObjects.updateUserBalance(senderNewBalance,senderAccNumber)
			self.userObjects.updateUserBalance(receiverNewBalance,receiverAccNumber)

			#SEND NOTIFICATION TO RECEIVER
			notifObject = self.notifier.sendNotif(
				'Received Funds',
				f'You have Received {amount} From {senderAccNumber}. Your new balance is {floor(receiverNewBalance)}',
				sender.first(),receiver.first()
				)
			#SEND NOTIFICATION TO SENDER
			notifObject2 = self.notifier.sendNotif(
				'Transfer Funds',
				f'You have Transfered {amount} to {receiverAccNumber}. Your new balance is {floor(senderNewBalance)}',
				sender.first(),sender.first()
				)

			#RECORD TRANSACTION
			transacObject = self.transac.transac(
				'TRANSFER FUNDS',receiver.first(),amount,senderNewBalance,sender.first()
				)
			treansacObject2 = self.transac.transac(
				"RECEIVED FUNDS",receiver.first(),amount,receiverNewBalance,receiver.first()
				)
			#RECORD  LOGS
			self.logger.insertLogs(
				'TRANSFER',sender.first(),notifObject2,transacObject
				)

			self.logger.insertLogs(
				'RECEIVED',receiver.first(),notifObject,treansacObject2
				)
		return True

		#METHOD FOR WITHDRAWING FUNDS
	def methodWithdraw(self,accountId,amount):
		userInstance = self.userObjects.getUserAccountDetails(accountId)

		for x in userInstance:
			accNumber = x.account_number

		userBalance = self.userObjects.getUserBalance(accNumber)

		if userBalance < amount:
			return "Non-sufficient funds!"

		else:
			userNewBalance = userBalance - amount
			updating = self.userObjects.updateUserBalance(userNewBalance,accNumber)

			notifObject = self.notifier.sendNotif(
				'Withdrew Funds',
				f'You have Withdrew {amount} From your account. Your new balance is {userNewBalance}',
				userInstance.first(),userInstance.first()
				)

			transacObject = self.transac.transac(
				'WITHDREW FUNDS',userInstance.first(),amount,userNewBalance,userInstance.first()
				)

			self.logger.insertLogs(
				'WITHDREW',userInstance.first(),notifObject,transacObject
				)

		return True

		#METHOD FOR DEPOSITING FUNDS
	def methodDeposit(self,accountId,amount):
		userInstance = self.userObjects.getUserAccountDetails(accountId)

		for x in userInstance:
			accNumber = x.account_number
		userBalance = self.userObjects.getUserBalance(accNumber)

		userNewBalance = userBalance + amount
		
		self.userObjects.updateUserBalance(userNewBalance,accNumber)

		notifObject = self.notifier.sendNotif(
				'Deposited Funds',
				f'You have Deposited {amount} To your account. Your new balance is {userNewBalance}',
				userInstance.first(),userInstance.first()
				)

		transacObject = self.transac.transac(
				'DEPOSITED FUNDS',userInstance.first(),amount,userNewBalance,userInstance.first()
				)

		self.logger.insertLogs(
				'DEPOSIT',userInstance.first(),notifObject,transacObject
				)

		return True

	def methodLoan(self,accountId,amount,yearsToPay):
		userInstance = self.userObjects.getUserAccountDetails(accountId)

		for x in userInstance:
			accNumber = x.account_number
			accId = x.id

		totalLoans = self.userObjects.getUserTotalAmountofLoans(accId)

		if totalLoans > 0:
			return "Please pay your current Loan first"

		userBalance = self.userObjects.getUserBalance(accNumber)

		userNewBalance = userBalance + amount

		if userBalance < 500:
			return "Required Balance is Not enough"

		try:
			d = datetime.now()
			duedate = d.replace(year =d.year + int(yearsToPay))

		except ValueError:
			duedate = d + (date(d.year + years, int(yearsToPay), int(yearsToPay))-date(\
				d.year,int(yearsToPay) ,int(yearsToPay)))


		self.userObjects.updateUserBalance(userNewBalance,accNumber)

		numberOfPayment = yearsToPay * 12

		notifObject = self.notifier.sendNotif(
			'Loaned Money',
			f'You have Loaned {amount} To your account. With an interest of 15%,\
			 Total number of payments is {numberOfPayment}. Loan Due Date {duedate}\
			 Please pay the loan before the due date. You can pay your loan in advance to save interest',
			 userInstance.first(),
			 userInstance.first(),
			)

		transacObject = self.transac.transac(
			'LOANED MONEY',userInstance.first(),amount,userNewBalance,userInstance.first()
			)

		self.logger.insertLogs(
			'LOANED MONEY',userInstance.first(),notifObject,transacObject
			)

		loanObject = self.userLoanInsert(
			amount,9,datetime.now(),duedate,numberOfPayment,userInstance.first(),transacObject
			)

		totalLoans = self.userObjects.getUserTotalAmountofLoans(accountId)

		return totalLoans

	def methodPayLoan(self,amount,accountId):
		userInstance = self.userObjects.getUserAccountDetails(accountId)

		for x in userInstance:
			accNumber = x.account_number
			accId = x.id



		loansPayable = self.userObjects.getUserTotalAmountofLoans(accId)

		paymentCount = self.userObjects.getUserLoanPaymentCount(accId)

		loanPrincipalAmount = self.userObjects.getUserLoanPrincipalAmount(accId)

		interest = decimal.Decimal((0.15 / paymentCount)) * loanPrincipalAmount

		minimumpayment = (loansPayable / paymentCount) + (interest * paymentCount)

		loansPayable = loansPayable + interest


		if paymentCount == 0:
			return "You do not have a loan to pay!"

		if amount < minimumpayment:
			return f"Minimum amount of payment is {floor(minimumpayment)}"
		
		if amount > loansPayable:
			change = amount - loansPayable

			userBalance = self.userObjects.getUserBalance(accNumber)

			userNewBalance = userBalance + change

			self.userObjects.updateUserBalance(userNewBalance,accNumber)

			notifObject = self.notifier.sendNotif(
			'Change Payment',
			f'You have received {floor(change)} To your account due to an excess payment of your loan,\
			 You can withdraw this amount anytime you like\
			 Your account balance is {floor(userNewBalance)}',
			 userInstance.first(),
			 userInstance.first(),
			)

			transacObject = self.transac.transac(
			'Loan Change',userInstance.first(),change,userNewBalance,userInstance.first()
			)

			self.logger.insertLogs(
				'Loan Change',userInstance.first(),notifObject,transacObject
			)

		else:
			print("change")
			change = 0


		credited = (amount - change) - interest

		loanNewBalance = loansPayable - (amount - interest)

		if loanNewBalance < 0:
			loanNewBalance = 0

		loanObject = self.userObjects.updateUserCurrentLoan(loanNewBalance,accId)

		notifObject = self.notifier.sendNotif(
			'Loan Payment',
			f'You have Paid {amount} To your exiting loan with an interstest of {floor(interest)},\
			 Credited to principal amount is {floor(credited)}.\
			 Please pay the loan before the due date. You can pay your loan in advance to save interest',
			 userInstance.first(),
			 userInstance.first(),
			)

		transacObject = self.transac.transac(
			'Loan Payment',userInstance.first(),amount,loanNewBalance,userInstance.first()
			)

		self.logger.insertLogs(
			'Paid Loan',userInstance.first(),notifObject,transacObject
			)

		return True

	def externalApiAccount(self,amount,creditcard,cvc,companyacc):
		cards = bankingCard.objects.filter(card_number=creditcard,cvc=cvc)

		if not cards:
			return False
		for x in cards:
			userid = x.user_id.id
			payeraccNumber = x.user_id.account_number

		userInformation = self.userObjects.getUserInformation(userid)

		for x in userInformation:
			fname = x.fname
			lname = x.lname
			mname = x.mname
			street = x.street
			city = x.city
			province = x.province
			barrangay = x.barrangay
			postal_code = x.postal_code
			email  = x.user_id.email

		companyInstance = self.userObjects.getUserCredentials(companyacc)

		payerInstance = self.userObjects.getUserCredentials(payeraccNumber)

		for x in payerInstance:
			accNumber = x.account_number
			client_secret = x.user_id.secure_code




		payerBalance = self.userObjects.getUserBalance(payeraccNumber)
		
		companyBalance = self.userObjects.getUserBalance(companyacc)

		if payerBalance < amount:
			return "Non-sufficient funds!"

		payerBalancenewBalance = payerBalance - amount

		companyBalancenewBalance = companyBalance + amount

		self.userObjects.updateUserBalance(payerBalancenewBalance,payeraccNumber)

		self.userObjects.updateUserBalance(companyBalancenewBalance,companyacc)

		#SEND NOTIFICATION TO RECEIVER
		notifObject = self.notifier.sendNotif('Received Payment',
			f'You have Received {amount} From {payeraccNumber}.\
			 Your new balance is {floor(companyBalancenewBalance)}',
			payerInstance.first(),companyInstance.first()
			)

		#SEND NOTIFICATION TO SENDER
		notifObject2 = self.notifier.sendNotif('Payment',
			f'You have Paid {amount} to {companyacc}. \
			Your new balance is {floor(payerBalancenewBalance)}',
			payerInstance.first(),payerInstance.first()
			)

		#RECORD TRANSACTION
		transacObject = self.transac.transac(
			'Paid Something',companyInstance.first(),amount,payerBalancenewBalance,payerInstance.first()
			)

		transacObject2 = self.transac.transac(
			"Received Payment",companyInstance.first(),amount,companyBalancenewBalance,companyInstance.first(),cards.first()
			)

		#RECORD  LOGS
		self.logger.insertLogs(
			'PAID',payerInstance.first(),notifObject2,transacObject
			)

		self.logger.insertLogs(
			'RECEIVED',companyInstance.first(),notifObject,transacObject2
			)


	
		context = {"id":transacObject2.id,"intent":"Sale","amount":float(amount),"amount_capturable":float(amount),\
			"amount_received":float(amount),"capture_method":"automatic","client_secret":client_secret,\
			"confirmation_method":"automatic","created":str(datetime.now()),"currency":"PHP","fname":fname,\
			"lname":lname,"mname":mname,"street":street,"city":city,"province":province,\
			"barrangay":barrangay,"postal_code":postal_code,"email":email,"description":None,\
			"invoice":None,"last_payment_error":None,"payment_method_types":"Card","status":True}
			
		api = apiTransaction(
			owner=companyInstance.first(),
			parentTransaction=transacObject2,
			transaction=context
			)
		api.save()
		return context

	def userLoanInsert(self,pamount,inte,ldate,ddate,number,accid,tranid):
		loanInstance = loans(
			parent_amount = pamount,
			interest = inte,
			loan_date = ldate,
			due_date = ddate,
			balance = pamount,
			numberOfPayments = number,
			account_id = accid,
			transaction_id = tranid
			)
		
		loanInstance.save()
		return loanInstance

class notifier:
	"""docstring for notifier"""
	def sendNotif(self,title,body,sender_id,receiver_id):
		notifObject = notifications(
			title=title,
			body=body,
			date = datetime.now(),
			status = 'Unread',
			sender_id=sender_id,
			receiver_id=receiver_id
			)
		notifObject.save()
		return notifObject
		

class logsTrigger:
	"""docstring for logsTrigger"""
	def insertLogs(self,event_name,account_id,notification_id,transaction_id):
		logsObject = logs(
			event_name=event_name,
			date = datetime.now(),
			account_id = account_id,
			notification_id = notification_id,
			transaction_id = transaction_id
			)
		logsObject.save()
		return True

class transactionRecorder:
	"""docstring for transactionRecorder"""
	def transac(self,transaction_type,receiver_account_id,amount,balance,account_id,creditcard_id=None):
		trasacObjects = transaction(
			transaction_type = transaction_type,
			receiver_account_id = receiver_account_id,
			date = datetime.now(),
			amount = amount,
			balance = balance,
			account_id = account_id,
			creditcard_id = creditcard_id
			)
		trasacObjects.save()
		return trasacObjects