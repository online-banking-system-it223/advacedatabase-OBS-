from .models import logs, transaction, loans, notifications, bankingCard, apiTransaction, ApiPayments, cancelledPayments
from django.core.exceptions import ObjectDoesNotExist
import random, string, datetime, decimal
from datetime import date
from datetime import datetime
from .userManagement import getUserDetails
from django.http import HttpResponse
from math import floor, ceil
from cryptography.fernet import Fernet
from django.utils import timezone
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
		
		sender = self.userObjects.getUserAccountDetails(accountId)
		
		receiver = self.userObjects.getUserAccountDetails2(account_number)
		
		senderBalance = self.userObjects.getUserBalance(accountId)
		
		receiverBalance = self.userObjects.getUserBalance(account_number)

		for x in sender:
			senderAccNumber = x.account_number
			senderBalance = x.account_balance

		for x in receiver:
			receiverAccNumber = x.account_number
			receiverBalance = x.account_balance

		# senderBalance = self.userObjects.getUserBalance(senderAccNumber)

		# receiverBalance = self.userObjects.getUserBalance(receiverAccNumber)

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

	def confirmPayment(self,amount,sellerId,payerID,payerAccNumber,sellerAccNumber,objectInstance,invoiceId):
		userid = payerID
		payeraccNumber = payerAccNumber

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

		companyInstance = self.userObjects.getUserAccountDetails2(sellerAccNumber)

		payerInstance = self.userObjects.getUserAccountDetails2(payeraccNumber)
		
		companyBalance = self.userObjects.getUserBalance(sellerAccNumber)

		payerBalance = self.userObjects.getUserBalance(payeraccNumber)

		companyBalancenewBalance = companyBalance + amount

		self.userObjects.updateUserBalance(companyBalancenewBalance,sellerAccNumber)


		#SEND NOTIFICATION TO RECEIVER
		notifObject = self.notifier.sendNotif('Received Payment',
			f'You have Received {amount} From {payeraccNumber}.\
			 Your new balance is {floor(companyBalancenewBalance)}',
			payerInstance.first(),companyInstance.first()
			)

		#SEND NOTIFICATION TO SENDER
		notifObject2 = self.notifier.sendNotif('Payment',
			f'You have confirmed your payment amounting: {amount} to {sellerAccNumber}.',
			payerInstance.first(),payerInstance.first()
			)

		#RECORD TRANSACTION
		transacObject = self.transac.transac(
			'Paid Something',companyInstance.first(),amount,payerBalance,payerInstance.first()
			)

		transacObject2 = self.transac.transac(
			"Received Payment",companyInstance.first(),amount,companyBalancenewBalance,companyInstance.first()
			)

		#RECORD  LOGS
		self.logger.insertLogs(
			'PAID',payerInstance.first(),notifObject2,transacObject
			)

		self.logger.insertLogs(
			'RECEIVED',companyInstance.first(),notifObject,transacObject2
			)


	
		context = {"id":transacObject2.id,"intent":"Sale","amount":float(amount),"amount_capturable":float(amount),\
			"amount_received":float(amount),"capture_method":"automatic",\
			"confirmation_method":"manual","created":str(datetime.now()),"currency":"PHP","fname":fname,\
			"lname":lname,"mname":mname,"street":street,"city":city,"province":province,\
			"barrangay":barrangay,"postal_code":postal_code,"email":email,"description":None,\
			"invoice":invoiceId,"last_payment_error":None,"payment_method_types":"Card","status":True}
			
		api = apiTransaction(
			owner=companyInstance.first(),
			parentTransaction=objectInstance.first(),
			transaction=context
			)
		api.save()
		return True

	def confirmPendingPayment(self,paymentID):
		objectInstance = ApiPayments.objects.filter(pk=paymentID,deleted=False)


		for x in objectInstance:
			payerAccID = x.payer.id
			sellerAccID = x.seller.id
			payerAccNumber = x.payer.account_number
			sellerAccNumber = x.seller.account_number
			amount = x.amount
			isnotPending = x.pending
			invoiceId = x.invoiceId

		if isnotPending == True:
			return 2
		else:
			bankInstance = self.confirmPayment(amount,sellerAccID,payerAccID,payerAccNumber,sellerAccNumber,objectInstance,invoiceId)

		if bankInstance:
			ApiPayments.objects.filter(pk=paymentID,deleted=False).update(pending=True,dateConfirmed=timezone.now())

		return bankInstance

	def cancelPayment(self,paymentID,paymentInstance):

		

		for x in paymentInstance:
			paymentID = x.id
			userid = x.payer.id
			userBalance = x.payer.account_balance
			userAccNumber = x.payer.account_number
			amountReceivable = x.amount
			invoiceId = x.invoiceId
			sellerAccNumber = x.seller.account_number
			sellerBalance = x.seller.account_balance

		ApiPaymentsInstance = ApiPayments.objects.filter(pk=paymentID)
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

		newUserBalance = userBalance + amountReceivable

		self.userObjects.updateUserBalance(newUserBalance,userAccNumber)

		payerInstance = self.userObjects.getUserAccountDetails2(userAccNumber)

		companyInstance = self.userObjects.getUserAccountDetails2(sellerAccNumber)


		ApiPaymentsInstance.update(deleted=True)

        #SEND NOTIFICATION TO RECEIVER
		notifObject = self.notifier.sendNotif(
			'Payment Cancelled',
			f'A payment amounting {amountReceivable} has been cancelled by.\
			 {fname} {lname}',
			payerInstance.first(),companyInstance.first()
			)

		#SEND NOTIFICATION TO SENDER
		notifObject2 = self.notifier.sendNotif('Payment',
			f'The payment to {sellerAccNumber} has been cancelled. The amount of {amountReceivable} \
			was transfered back to your account',
			payerInstance.first(),payerInstance.first()
			)

		#RECORD TRANSACTION
		transacObject = self.transac.transac(
			'Cancelled Payment',companyInstance.first(),amountReceivable,newUserBalance,payerInstance.first()
			)

		transacObject2 = self.transac.transac(
			"Cancelled Payment",companyInstance.first(),amountReceivable,sellerBalance,companyInstance.first()
			)

		#RECORD  LOGS
		self.logger.insertLogs(
			'Cancelled',payerInstance.first(),notifObject2,transacObject
			)

		self.logger.insertLogs(
			'Cancelled',companyInstance.first(),notifObject,transacObject2
			)


		context = {"Msg":"Payment Has been cancelled","date":str(timezone.now()),
			"data":[{"id":transacObject2.id,
			"intent":"Cancel","amount":float(amountReceivable),\
        	"amount_capturable":float(amountReceivable),\
			"amount_received":0.00,"capture_method":"automatic",\
			"confirmation_method":"manual","created":str(datetime.now()),"currency":"PHP","fname":fname,\
			"lname":lname,"mname":mname,"street":street,"city":city,"province":province,\
			"barrangay":barrangay,"postal_code":postal_code,"email":email,"description":None,\
			"invoice":invoiceId,"last_payment_error":None,"payment_method_types":"Card","status":True}]}

		api = apiTransaction(
			owner=companyInstance.first(),
			parentTransaction=ApiPaymentsInstance.first(),
			transaction=context
			)
		deleteInstance = cancelledPayments(Payment=ApiPaymentsInstance.first(),transaction=context)
		deleteInstance.save()
		api.save()

		return context
	def recordPaymentRequest(self,amount,creditcard,cvv,companyacc,charge,expidate,apikey):

		companyInstance = self.userObjects.getUserAccountDetails2(companyacc)
		if not companyInstance:
			return 2

		for x in companyInstance:
			companyKey = x.api_key

		if apikey != companyKey:
			return 3

		cards = bankingCard.objects.filter(card_number=creditcard,cvv=cvv)

		if not cards:
			return 8

		for x in cards:
			payerId = x.user_id.id
			payeraccNumber = x.user_id.account_number
			payerBalance = x.user_id.account_balance
			expiDate = x.expiration_date
			isDisabled = x.isDisabled
			isLocked = x.user_id.isLocked

		if isLocked:
			return 1

		if payerBalance < amount:
			return 4



		if isDisabled:
			return 5

		if expiDate == datetime.now():
			return 6

		inputDate = datetime.strptime(expidate, '%Y-%m-%d')
		inputMonth = inputDate.strftime("%m")
		inputYear = inputDate.strftime("%Y")
		cardMonth = expiDate.strftime("%m")
		cardYear = expiDate.strftime("%Y")

		if inputMonth != cardMonth or inputYear != cardYear:
			return 7

		payerInstance = self.userObjects.getUserAccountDetails2(payeraccNumber)



		paymentInstance = ApiPayments(
			invoiceId = charge,
			amount = amount,
			payer = payerInstance.first(),
			seller = companyInstance.first(),
			dateCreated = datetime.now(),
			)

		paymentInstance.save()

		payerBalancenewBalance = payerBalance - amount

		self.userObjects.updateUserBalance(payerBalancenewBalance,payeraccNumber)

		self.notifier.sendNotif('Account Deducted',
			f'You have Deducted {amount}. \
			Your new balance is {floor(payerBalancenewBalance)}',
			payerInstance.first(),payerInstance.first()
			)

		context = {"Msg":"Payment has been saved. Waiting confirmation from the user",
			"status":True,"requestId":paymentInstance.id,"date":str(datetime.now()),
			"amount":float(amount),"invoice_id":charge,"confirmed":False,
			"links":[
			{'href':f'http://192.168.1.6:8888/api/payments/sale/{paymentInstance.id}',
				'rel':'self','method':'GET'},
			{'href':f'http://192.168.1.6:8888/api/payments/sale/{paymentInstance.id}/cancel',
			'rel':'cancel','method':'POST'}]}

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