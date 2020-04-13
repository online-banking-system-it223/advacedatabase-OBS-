from .models import transaction, loans, bankingCard, apiTransaction, ApiPayments, cancelledPayments, emails, credentials
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
		self.transac = transactionRecorder()

		#METHOD FOR TRANSFERING FUND
	def methodTransfer(self,account_number,accountId,amount,myUserInstance):
		
		sender = self.userObjects.getUserAccountDetails(accountId)
		
		receiver = self.userObjects.getUserAccountDetails2(account_number)

		

		for x in sender:
			senderAccNumber = x.account_number
			senderBalance = x.account_balance

		#CHECK IF THE RECEIVER IS FOUND
		if not receiver:
			return "Receiver not found!"

		if senderBalance < amount:
			return "Non-sufficient funds!"

		userCredentials = self.userObjects.getUserInformation(accountId)

		for x in userCredentials:
			fname = x.fname
			lname = x.lname

		for x in receiver:
			receiverAccNumber = x.account_number
			receiverBalance = x.account_balance
			receiverMyuserID = x.user_id.id

		receiverCredentials = credentials.objects.filter(user_id__id=receiverMyuserID)

		for x in receiverCredentials:
			refname = x.fname
			relname = x.lname

		receiverInstance = self.userObjects.getMyUser(receiverMyuserID)

		#CHECK IF SENDER HAS SUFFICIENT FUNDS FOR TRANSFER


		#FINAL CONDITION FOR TRANSFERING FUNDS
		if senderBalance > amount or receiver:
			#THE NEW SENDER BALANCE
			senderNewBalance = senderBalance - amount
			#THE NEW RECEIVER BALANCE
			receiverNewBalance = receiverBalance + amount

			#UPDATE EACH OTHER USER BALANCE
			self.userObjects.updateUserBalance(senderNewBalance,senderAccNumber)
			self.userObjects.updateUserBalance(receiverNewBalance,receiverAccNumber)

			#RECORD TRANSACTION
			transacObject = self.transac.transac(
				'TRANSFER FUNDS',receiver.first(),amount,senderNewBalance,sender.first()
				)
			treansacObject2 = self.transac.transac(
				"RECEIVED FUNDS",receiver.first(),amount,receiverNewBalance,receiver.first()
				)

			mailObject = self.transac.mail(
				None,myUserInstance,"Withdraw",
				'<td style="border-radius: 10px;background: #fff;padding: 30px 60px 20px 60px;margin-top:'+ 
				'10px;display: block;">'+

				'<p style="font-family: Roboto;font-size: 14px;font-weight: 500;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;margin-bottom:'+ 
                f'10px;">Hi {fname} {lname},</p>'+

                '<p style="font-family: Roboto;font-size: 14px;font-weight: normal;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;"> '+
                f'You have transferd a total of ${round(amount,2)} to {receiverAccNumber}, your new account balance is ${round(senderNewBalance,2)}'+
                '</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style: normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;">Hope you enjoy our service, we are here if you have any questions, '+
                'drop us a line at info@bankofdnsc.com anytime.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style:normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;margin-bottom: 0px;"> Thank you for using Bank of Dnsc.</p>'+

                '<p style="font-family:'+
                'Roboto;font-size: 14px;font-weight: 500;font-style: normal;font-stretch: normal;line-height: 2.5;'+
                'letter-spacing: normal;color: #001737;margin-bottom: 0px;">Sincerly:  Bank of Dnsc team</p>'+

                '</td>'
				)

			mailObject = self.transac.mail(
				None,receiverInstance,"Withdraw",
				'<td style="border-radius: 10px;background: #fff;padding: 30px 60px 20px 60px;margin-top:'+ 
				'10px;display: block;">'+

				'<p style="font-family: Roboto;font-size: 14px;font-weight: 500;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;margin-bottom:'+ 
                f'10px;">Hi {refname} {relname},</p>'+

                '<p style="font-family: Roboto;font-size: 14px;font-weight: normal;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;"> '+
                f'{fname} {lname} transferd a total of ${round(amount,2)} to your account, your new account balance is ${round(receiverNewBalance,2)}'+
                '</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style: normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;">Hope you enjoy our service, we are here if you have any questions, '+
                'drop us a line at info@bankofdnsc.com anytime.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style:normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;margin-bottom: 0px;"> Thank you for using Bank of Dnsc.</p>'+

                '<p style="font-family:'+
                'Roboto;font-size: 14px;font-weight: 500;font-style: normal;font-stretch: normal;line-height: 2.5;'+
                'letter-spacing: normal;color: #001737;margin-bottom: 0px;">Sincerly:  Bank of Dnsc team</p>'+

                '</td>'
				)

		return True

		#METHOD FOR WITHDRAWING FUNDS
	def methodWithdraw(self,accountId,amount,myUserInstance):
		userInstance = self.userObjects.getUserAccountDetails(accountId)
		userCredentials = self.userObjects.getUserInformation(accountId)

		for x in userCredentials:
			fname = x.fname
			lname = x.lname

		for x in userInstance:
			accNumber = x.account_number
			userBalance = x.account_balance

		if userBalance < amount:
			return "Non-sufficient funds!"

		userNewBalance = userBalance - amount
		updating = self.userObjects.updateUserBalance(userNewBalance,accNumber)

		transacObject = self.transac.transac(
			'WITHDREW FUNDS',userInstance.first(),amount,userNewBalance,userInstance.first()
			)

		mailObject = self.transac.mail(
				None,myUserInstance,"Withdraw",
				'<td style="border-radius: 10px;background: #fff;padding: 30px 60px 20px 60px;margin-top:'+ 
				'10px;display: block;">'+

				'<p style="font-family: Roboto;font-size: 14px;font-weight: 500;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;margin-bottom:'+ 
                f'10px;">Hi {fname} {lname},</p>'+

                '<p style="font-family: Roboto;font-size: 14px;font-weight: normal;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;"> '+
                f'You have withdrawn a total of ${round(amount,2)} from your account, your new account balance is ${round(userNewBalance,2)}'+
                '</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style: normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;">Hope you enjoy our service, we are here if you have any questions, '+
                'drop us a line at info@bankofdnsc.com anytime.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style:normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;margin-bottom: 0px;"> Thank you for using Bank of Dnsc.</p>'+

                '<p style="font-family:'+
                'Roboto;font-size: 14px;font-weight: 500;font-style: normal;font-stretch: normal;line-height: 2.5;'+
                'letter-spacing: normal;color: #001737;margin-bottom: 0px;">Sincerly:  Bank of Dnsc team</p>'+

                '</td>'
				)

		return True

		#METHOD FOR DEPOSITING FUNDS
	def methodDeposit(self,accountId,amount,myUserInstance):
		userInstance = self.userObjects.getUserAccountDetails(accountId)
		userCredentials = self.userObjects.getUserInformation(accountId)

		for x in userInstance:
			accNumber = x.account_number
			userBalance = x.account_balance

		for x in userCredentials:
			fname = x.fname
			lname = x.lname

		userNewBalance = userBalance + amount
		
		self.userObjects.updateUserBalance(userNewBalance,accNumber)

	
		transacObject = self.transac.transac(
				'DEPOSITED FUNDS',userInstance.first(),amount,userNewBalance,userInstance.first()
				)

		mailObject = self.transac.mail(
				None,myUserInstance,"Deposit",
				'<td style="border-radius: 10px;background: #fff;padding: 30px 60px 20px 60px;margin-top:'+ 
				'10px;display: block;">'+

				'<p style="font-family: Roboto;font-size: 14px;font-weight: 500;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;margin-bottom:'+ 
                f'10px;">Hi {fname} {lname},</p>'+

                '<p style="font-family: Roboto;font-size: 14px;font-weight: normal;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;"> '+
                f'You have deposited a total of ${round(amount,2)} to your account, your new account balance is ${round(userNewBalance,2)}'+
                '</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style: normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;">Hope you enjoy our service, we are here if you have any questions, '+
                'drop us a line at info@bankofdnsc.com anytime.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style:normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;margin-bottom: 0px;"> Thank you for using Bank of Dnsc.</p>'+

                '<p style="font-family:'+
                'Roboto;font-size: 14px;font-weight: 500;font-style: normal;font-stretch: normal;line-height: 2.5;'+
                'letter-spacing: normal;color: #001737;margin-bottom: 0px;">Sincerly:  Bank of Dnsc team</p>'+

                '</td>'
				)

		return True

	def methodLoan(self,accountId,amount,yearsToPay,myUserInstance):
		userInstance = self.userObjects.getUserAccountDetails(accountId)
		userCredentials = self.userObjects.getUserInformation(accountId)

		for x in userInstance:
			accNumber = x.account_number
			accId = x.id
			userBalance = x.account_balance

		for x in userCredentials:
			fname = x.fname
			lname = x.lname

		totalLoans = self.userObjects.getUserTotalAmountofLoans(accId)

		if totalLoans > 0:
			return "Please pay your current Loan first"

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

		

		transacObject = self.transac.transac(
			'LOANED MONEY',userInstance.first(),amount,userNewBalance,userInstance.first()
			)

		loanObject = self.userLoanInsert(
			amount,9,datetime.now(),duedate,numberOfPayment,userInstance.first(),transacObject
			)

		totalLoans = self.userObjects.getUserTotalAmountofLoans(accountId)

		mailObject = self.transac.mail(
				None,myUserInstance,"Loan",
				'<td style="border-radius: 10px;background: #fff;padding: 30px 60px 20px 60px;margin-top:'+ 
				'10px;display: block;">'+

				'<p style="font-family: Roboto;font-size: 14px;font-weight: 500;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;margin-bottom:'+ 
                f'10px;">Hi {fname} {lname},</p>'+

                '<p style="font-family: Roboto;font-size: 14px;font-weight: normal;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;"> '+
                f'You have loaned a total of ${round(amount,2)} to your account, your new account balance is ${round(userNewBalance,2)}'+
                f'. Loan Interest is 9%, Payable up to {numberOfPayment} Months or {yearsToPay} Years.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style: normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;">Hope you enjoy our service, we are here if you have any questions, '+
                'drop us a line at info@bankofdnsc.com anytime.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style:normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;margin-bottom: 0px;"> Thank you for using Bank of Dnsc.</p>'+

                '<p style="font-family:'+
                'Roboto;font-size: 14px;font-weight: 500;font-style: normal;font-stretch: normal;line-height: 2.5;'+
                'letter-spacing: normal;color: #001737;margin-bottom: 0px;">Sincerly: Bank of Dnsc team</p>'+

                '</td>'
				)

		return totalLoans

	def methodPayLoan(self,amount,accountId,myUserInstance):
		userInstance = self.userObjects.getUserAccountDetails(accountId)
		userCredentials = self.userObjects.getUserInformation(accountId)

		for x in userInstance:
			accNumber = x.account_number
			accId = x.id
			userBalance = x.account_balance

		for x in userCredentials:
			fname = x.fname
			lname = x.lname

		loansPayable = self.userObjects.getUserTotalAmountofLoans(accId)

		paymentCount = self.userObjects.getUserLoanPaymentCount(accId)

		loanPrincipalAmount = self.userObjects.getUserLoanPrincipalAmount(accId)

		interest = decimal.Decimal((0.15 / paymentCount)) * loanPrincipalAmount
		interest1 = decimal.Decimal((0.15 / paymentCount)) * loansPayable

		minimumpayment = (loansPayable / paymentCount) + (interest1 * paymentCount)
		print(minimumpayment)
		loansPayable = loansPayable + interest

		userNewBalance = 0
		if paymentCount == 0:
			return "You do not have a loan to pay!"

		if amount < minimumpayment:
			return f"Minimum amount of payment is {floor(minimumpayment)}"
		
		if amount > loansPayable:
			change = amount - loansPayable

			userNewBalance = userBalance + change

			self.userObjects.updateUserBalance(userNewBalance,accNumber)

			transacObject = self.transac.transac(
			'Loan Change',userInstance.first(),change,userNewBalance,userInstance.first()
			)

		else:
			change = 0


		credited = (amount - change) - interest

		loanNewBalance = loansPayable - (amount - interest)

		if loanNewBalance < 0:
			loanNewBalance = 0

		loanObject = self.userObjects.updateUserCurrentLoan(loanNewBalance,accId)

	

		transacObject = self.transac.transac(
			'Loan Payment',userInstance.first(),amount,loanNewBalance,userInstance.first()
			)

		mailObject = self.transac.mail(
				None,myUserInstance,"Loan Payment",
				'<td style="border-radius: 10px;background: #fff;padding: 30px 60px 20px 60px;margin-top:'+ 
				'10px;display: block;">'+

				'<p style="font-family: Roboto;font-size: 14px;font-weight: 500;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;margin-bottom:'+ 
                f'10px;">Hi {fname} {lname},</p>'+

                '<p style="font-family: Roboto;font-size: 14px;font-weight: normal;font-style:'+
                'normal;font-stretch: normal;line-height: 1.71;letter-spacing: normal;color: #001737;"> '+
                f'You have paid a total of ${round(amount,2)} to your loan, your new loan balance is ${round(loanNewBalance,2)}.'
        		f' With a change of {round(change,2)} debited to your account,'+
        		f' your new account balance is {round(userBalance + change,2)}'+
                f'. Please rememeber that your loan Interest is 9%,'+
                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style: normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;">Hope you enjoy our service, we are here if you have any questions, '+
                'drop us a line at info@bankofdnsc.com anytime.</p>'+

                '<p style="font-family: Roboto;font-size: '+
                '14px;font-weight: normal;font-style:normal;font-stretch: normal;line-height: 1.71;letter-spacing: '+
                'normal;color: #001737;margin-bottom: 0px;"> Thank you for using Bank of Dnsc.</p>'+

                '<p style="font-family:'+
                'Roboto;font-size: 14px;font-weight: 500;font-style: normal;font-stretch: normal;line-height: 2.5;'+
                'letter-spacing: normal;color: #001737;margin-bottom: 0px;">Sincerly: Bank of Dnsc</p>'+

                '</td>'
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

		#RECORD TRANSACTION
		transacObject = self.transac.transac(
			'Paid Something',companyInstance.first(),amount,payerBalance,payerInstance.first()
			)

		transacObject2 = self.transac.transac(
			"Received Payment",companyInstance.first(),amount,companyBalancenewBalance,companyInstance.first()
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

      


		#RECORD TRANSACTION
		transacObject = self.transac.transac(
			'Cancelled Payment',companyInstance.first(),amountReceivable,newUserBalance,payerInstance.first()
			)

		transacObject2 = self.transac.transac(
			"Cancelled Payment",companyInstance.first(),amountReceivable,sellerBalance,companyInstance.first()
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


class transactionRecorder:
	"""docstring for transactionRecorder"""
	def transac(self,transaction_type,receiver_account_id,amount,balance,account_id):
		trasacObjects = transaction(
			transaction_type = transaction_type,
			transacReceiver = receiver_account_id,
			amount = amount,
			newBalance = balance,
			transacOwner = account_id,
			)

		trasacObjects.save()
		return trasacObjects

	def mail(self,sender,receiver,subject,body):
		
		instance = emails(
			sender = sender,
			receiver = receiver,
			subject = subject,
			body = body,
			)
		instance.save()

		return True