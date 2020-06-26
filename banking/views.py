from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from .userManagement import RegisterUser, LoggingUser, getUserDetails, generateAccount
from .bankManagement import bankingMethod
from django.contrib.auth import logout, login, authenticate
from django.utils.html import strip_tags
import decimal
from .models import bankingCard, account, credentials, ApiPayments, apiTransaction, cancelledPayments, emails, transaction
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_api_key.models import APIKey
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import urllib.request
from django.contrib import messages

from django.core.paginator import Paginator
from datetime import datetime

def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False
# test


def emailList(request):
    if not connect():
        return HttpResponse("No internet",status=500)
    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("/admin")
        
        userObject = getUserDetails()
        user = userObject.getUserInformation(request.user.id)
        account1 = userObject.getUserAccountDetails(request.user.id)
        emails1 = emails.objects.filter(receiver=request.user.id)
        newMails = emails.objects.filter(receiver=request.user.id)[:5]
        paginator = Paginator(emails1, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if not user:
            user = False
        context = {"user":user,
        "account":account1,
        "emails":page_obj,
        "newmails":newMails}

        return render(request, 'banking/emaillist.html',context)
    else:
       return redirect('login')

def transactionList(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("/admin")
        
        userObject = getUserDetails()
        user = userObject.getUserInformation(request.user.id)
        account1 = userObject.getUserAccountDetails(request.user.id)
        trans = transaction.objects.filter(transacOwner_id=request.user.id)
        print(request.user.id)
        newMails = emails.objects.filter(receiver=request.user.id)[:5]
        paginator = Paginator(trans, 25)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        print(trans)
        if not user:
            user = False
        context = {"user":user,
        "account":account1,
        "transactions":page_obj,
        "newmails":newMails}

        return render(request, 'banking/transactions.html',context)
    else:
       return redirect('login')

def specificEmail(request,emailId):
    if not connect():
        return HttpResponse("No internet",status=500)

    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("/admin")
        
        userObject = getUserDetails()
        user = userObject.getUserInformation(request.user.id)
        account1 = userObject.getUserAccountDetails(request.user.id)
   
        emails1 = emails.objects.filter(pk=emailId,receiver=request.user.id).first()
        emails.objects.filter(pk=emailId,receiver=request.user.id,opened=False).update(opened=True)
        newMails = emails.objects.filter(receiver=request.user.id)[:5]
        if not user:
            user = False

        if not emails1:
            emails1 = False
        context = {"user":user,
        "account":account1,
        "emails":emails1,
        "newmails":newMails}

        return render(request, 'banking/email.html',context)
    else:
       return redirect('login')

    

def index(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("/admin")
        
        userObject = getUserDetails()
        user = userObject.getUserInformation(request.user.id)
        account1 = userObject.getUserAccountDetails(request.user.id)
        for x in account1:
           accountId = x.id
        newMails = emails.objects.filter(receiver=request.user.id)[:5]
        loans = userObject.getUserTotalLoans(request.user.id)
        totalLoans = userObject.getUserTotalAmountofLoans(request.user.id)
        transactions = userObject.getUserTransactionList(accountId)
        loansPayable = userObject.getUserTotalAmountofLoans(accountId)
        loanedTotal = userObject.getUserTotalLoans(accountId)
        cardDetails = userObject.getUserCardDetails(accountId)
        payments = ApiPayments.objects.filter(payer__id=accountId,pending=False,deleted=False)

        currdate = datetime.now()
        currMonth = currdate.strftime("%m")
        currYear = currdate.strftime("%Y")
        for x in cardDetails:
            cardDate = x.expiration_date
            cardNumbah = x.card_number
        
        cardMonth = cardDate.strftime("%m")
        cardYear = cardDate.strftime("%Y")

        if cardMonth == currMonth and cardYear == currYear:
            userObject1 = generateAccount()
            newCard = userObject1.creditCardNumber()
            newExpiration = userObject1.addYears()
            newCvv = userObject1.create_unique_cvc()
            bankingCard.objects.filter(card_number=cardNumbah).update(card_number=newCard,cvv=newCvv,expiration_date=newExpiration)

        if not user:
            user = False
    
        context = {"user":user,
        "account":account1,
        "loans":loans,
        "totalLoans":totalLoans,
        "transactions":transactions,
        "loansPayable":loansPayable,
        "totalLoaned":loanedTotal,
        "Card":cardDetails,
        "payments":payments,
        "newmails":newMails}

        return render(request, 'banking/index.html',context)
    else:
       return redirect('login')

    
def userRegistration(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    if not request.user.is_authenticated:

        if request.method == "POST":
            email = strip_tags(request.POST.get("email",None))
            code = strip_tags(request.POST.get("securecode",None))
            pass1 = strip_tags(request.POST.get("pass1",'123'))
            pass2 = strip_tags(request.POST.get("pass2",'1234'))
            regObject = RegisterUser()
            
            regis = regObject.register(email,code,pass1,pass2)
            if regis == "Password do not Match!":
                return render(request, "banking/register.html", {"messages": "Password do not Match!"})

            elif regis == 'User Already Exist!':
                return render(request, "banking/register.html", {"messages": "User Already Exist!"})
            else:
                login(request, regis)
                return redirect('index')
        else:
            return render (request, 'banking/register.html')
    else:
        return redirect('index')

def userLogin(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    if not request.user.is_authenticated:

        if request.method == "POST":
            logging = LoggingUser()
            email = strip_tags(request.POST.get("email",None))
            code = strip_tags(request.POST.get("securecode",None))
            password = strip_tags(request.POST.get("password",None))
            logging1 = logging.logmein(email,code,password)
            if not logging1:
                return render(request, "banking/login.html", {"messages": "Incorrect Email or Secure Code!"})
            else:
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                else:
                    return render(request, "banking/login.html", {"messages": "Incorrect Email or Password!"})
            return redirect('index')

        else:
             return render (request, 'banking/login.html')
    else:
         return redirect('index')

def fundsDrawing(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    #CHECK IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #CHECK IF METHOD IS POST
        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            #PUT THE DATA IN HERE
            amount = decimal.Decimal(request.POST.get("amount",0))
            try:
                userSecretCode = int(request.POST.get("securecode",0))
            except ValueError:
                return HttpResponse("Secure Code Error!",status=403)
            usercode = request.user.secure_code

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount bust be Greater than 0!",status=403)

            bankInstance = bankObject.methodWithdraw(request.user.id, amount,request.user)
            account1 = userObject.getUserAccountDetails(request.user.id)

            if bankInstance == 'Non-sufficient funds!':
                return HttpResponse("Non-sufficient funds!",status=403)

            else:
                for x in account1:
                    bal =  x.account_balance
                    print(bal)
                return HttpResponse(bal,status=200)
        else:
            return redirect('index')
    else:
        return redirect('index')

def fundsDeposit(request):
    if not connect():
        return HttpResponse("No internet",status=500)

     #CHECK IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #CHECK IF METHOD IS POST
        if request.method == "POST":
            bankObject = bankingMethod()
            #PUT THE DATA IN HERE
            userObject = getUserDetails()
            amount = decimal.Decimal(request.POST.get("amount",0))
            try:
                userSecretCode = int(request.POST.get("securecode",0))
            except ValueError:
                return HttpResponse("Secure Code Error!",status=403)
           
            usercode = request.user.secure_code

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount bust be Greater than 0!",status=403)
            
            bankInstance = bankObject.methodDeposit(request.user.id,amount,request.user)
            account1 = userObject.getUserAccountDetails(request.user.id)
            
            for x in account1:
               bal =  x.account_balance
            return HttpResponse(bal,status=200)
        else:
            return redirect('index')
    else:
        return redirect('index')

def loanFunds(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    if request.user.is_authenticated:

        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            amount = decimal.Decimal(request.POST.get("amount",0))
            try:
                userSecretCode = int(request.POST.get("securecode",0))
            except ValueError:
                return HttpResponse("Secure Code Error!",status=403)

            yearsToPay = int(request.POST.get("yearstoPay",0))
            usercode = request.user.secure_code

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount must be Greater than 0!",status=403)

            if yearsToPay < 0:
                return HttpResponse("Years to pay must be Greater than 0!",status=403)

            account1 = userObject.getUserAccountDetails(request.user.id)

            bankInstane = bankObject.methodLoan(request.user.id,amount,yearsToPay,request.user)
            if bankInstane == "Please pay your current Loan first":
                return HttpResponse("Please pay your current Loan first",status=403)

            if bankInstane == "Required Balance is Not enough":
                return HttpResponse("Required Balance is Not enough",status=403)

            for x in account1:
                accNumber =  x.account_number
                bal = x.account_balance
                accid = x.id
            totalLoan = userObject.getUserTotalLoans(accid)
            loanPayable = userObject.getUserTotalAmountofLoans(accid)
            #return HttpResponse("Years to pay must be Greater than 0!",status=200)
            context = {"UserBalance":bal,"TotalLoan":totalLoan,"loanPayable":loanPayable}
            return JsonResponse(context, safe=False)
        else:
            return redirect('index')

    else:
        return redirect('index') 


def loanPayment(request):
    if not connect():
        return HttpResponse("No internet",status=500)

    if request.user.is_authenticated:

        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            amount = decimal.Decimal(request.POST.get("amount",0))
            userSecretCode = int(request.POST.get("securecode",0))
            try:
                userSecretCode = int(request.POST.get("securecode",0))
            except ValueError:
                return HttpResponse("Secure Code Error!",status=403)

            account1 = userObject.getUserAccountDetails(request.user.id)

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount must be Greater than 0!",status=403)

            for x in account1:
                accid = x.id
                accNum = x.account_number

            loanPayable = userObject.getUserTotalAmountofLoans(accid)

            if loanPayable == 0:
                return HttpResponse("You do not have a loan to pay!",status=403)

            loanObject = bankObject.methodPayLoan(amount,request.user.id,request.user)

            if loanObject == "You do not have a loan to pay!":
                return HttpResponse("You do not have a loan to pay!",status=403)
            try:
                if "Minimum" in  loanObject:
                    return HttpResponse(loanObject,status=403)
            except TypeError:
                print("")


            if loanObject:
                totalLoan = userObject.getUserTotalLoans(accid)
                loanPayable = userObject.getUserTotalAmountofLoans(accid)
                bal = userObject.getUserBalance(accNum)
                context = {"UserBalance":bal,"TotalLoan":totalLoan,"loanPayable":loanPayable}
                return JsonResponse(context, safe=False)
                
            else:
                return HttpResponse("Something Went Wrong. Please try again later",status=403)
            
        else:
            return redirect('index')
    else:
        return redirect('index')

#811444613230
def fundsTransfer(request):
    if not connect():
        return HttpResponse("No internet",status=500)
     #CHECK IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #CHECK IF METHOD IS POST
        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            #PUT THE DATA IN HERE
            amount = decimal.Decimal(request.POST.get("amount",0))
            try:
                userSecretCode = int(request.POST.get("securecode",0))
            except ValueError:
                return HttpResponse("Secure Code Error!",status=403)
                
            receiverAcc = int(request.POST.get("useracc",0))
            usercode = request.user.secure_code
            account1 = userObject.getUserAccountDetails(request.user.id)

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount bust be Greater than 0!",status=403)

            receiver = userObject.getUserAccountDetails2(receiverAcc)

            if not receiver:
                return HttpResponse("Receiver Not Found. Please Check the account number",status=403)


            bankInstance = bankObject.methodTransfer(receiverAcc,request.user.id,amount,request.user)

            if bankInstance == "Receiver not found!":
                return HttpResponse("Receiver Not Found. Please Check the account number",status=403)

            if bankInstance == "Non-sufficient funds!":
                return HttpResponse("Balance is Not enough",status=403)
            
            for x in account1:
                accNumber =  x.account_number
                bal = x.account_balance
                accid = x.id
            totalLoan = userObject.getUserTotalLoans(accid)
            loanPayable = userObject.getUserTotalAmountofLoans(accid)
            #return HttpResponse("Years to pay must be Greater than 0!",status=200)
            context = {"UserBalance":bal,"TotalLoan":totalLoan,"loanPayable":loanPayable}
            return JsonResponse(context, safe=False)
        else:
           return redirect('index') 
    else:
        return redirect('index')

def logout_view(request):
    logout(request)
    return redirect('index')

def credentialsInsert(request):
    if not connect():
        return HttpResponse("No internet",status=500)
        
    if request.method == "POST":
        regObject = RegisterUser()

        fname = strip_tags(request.POST.get("fname",None))
        lname = strip_tags(request.POST.get("lname",None))
        mname = strip_tags(request.POST.get("mname",None))
        Province = strip_tags(request.POST.get("Province",None))
        City = strip_tags(request.POST.get("City",None))
        Street = strip_tags(request.POST.get("Street",None))
        Barangay = strip_tags(request.POST.get("Barangay",None))
        zipcode = strip_tags(request.POST.get("zip",None))
        userid = request.user.id
        reg = regObject.insertCredentials(fname,lname,mname,Street,City,Province,Barangay,zipcode,userid)
        return redirect('index')
    else:
        return redirect('index')

#API ZONE DO NOT ENTER

@csrf_exempt
def receivePayment(request):

    if request.method == 'POST':
        cvv = request.META.get("HTTP_CVV", False)
        cardnumber = request.META.get("HTTP_CARDNUMBER", False)
        amount = decimal.Decimal(request.META.get("HTTP_AMOUNT", False))
        companyAccNumber = request.META.get("HTTP_ACCOUNTNUMBER", False)
        intent = request.META.get("HTTP_INTENT", False)
        apiKey = request.META.get("HTTP_X_API_KEY", False)
        charge = request.META.get("HTTP_INVOICEID", False)
        expiration = request.META.get("HTTP_EXPIRATION", False)
        checkApi = account.objects.filter(api_key=apiKey)

        if not checkApi:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Incorrect Api key"}
            return JsonResponse(context, safe=False,status=401)

        if intent != "Sale":
            context = {"error":"INVALID_REQUEST","error_description":"Intent Error"}
            return JsonResponse(context, safe=False,status=400)

        if not cvv:
            context = {"error":"INVALID_REQUEST","error_description":"Cvv is empty"}
            return JsonResponse(context, safe=False,status=400)

        if not cardnumber:
            context = {"error":"INVALID_REQUEST","error_description":"Card number is empty"}
            return JsonResponse(context, safe=False,status=400)

        if amount < 0:
            context = {"error":"INVALID_REQUEST","error_description":"Amount is lessthan 0"}
            return JsonResponse(context, safe=False,status=400)

        if not companyAccNumber:
            context = {"error":"INVALID_REQUEST","error_description":"Company acc number is empty"}
            return JsonResponse(context, safe=False,status=400)

        if not charge:
            context = {"error":"INVALID_REQUEST","error_description":"Invoice ID is empty"}
            return JsonResponse(context, safe=False,status=400)

        if not expiration:
            context = {"error":"INVALID_REQUEST","error_description":"Expiration date is empty"}
            return JsonResponse(context, safe=False,status=400)

        bankObject = bankingMethod()

        apiInstance = bankObject.recordPaymentRequest(amount,cardnumber,cvv,companyAccNumber,charge,expiration,apiKey)

        if apiInstance == 1:
            context = {"error":"INVALID_REQUEST","error_description":"Card is locked"}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 2:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Company Account Number Error.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 3:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Api key Error, \
                your api key does not match your company key.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 4:
            context = {"error":"INVALID_REQUEST","error_description":"Non suffienct funds"}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 5:
            context = {"error":"INVALID_REQUEST","error_description":"Card is disabled"}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 6:
            context = {"error":"INVALID_REQUEST","error_description":"You are using an expired card"}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 7:
            context = {"error":"INVALID_REQUEST","error_description":"Card details invalid"}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance == 8:
            context = {"error":"INVALID_REQUEST","error_description":"Card not found"}
            return JsonResponse(context, safe=False,status=400)

        if apiInstance:
            return JsonResponse(apiInstance, safe=False)
    else:
        context = {"error":"METHOD_NOT_SUPPORTED","error_description":"Invalid request method"}
        return JsonResponse(context, safe=False,status=405)

def confirmPayments(request):
    if request.method == 'POST':
        paymentId = request.POST.get("paymentid",None)
        if paymentId is None:
            return HttpResponse("Something Went Wrong. Please try again later",status=403)
        bankObject = bankingMethod()
        bankInstance = bankObject.confirmPendingPayment(paymentId)
        print(bankInstance)
        if bankInstance == 2:
            return HttpResponse("This Payment is already Confirmed",status=403)

        if bankInstance:
            return HttpResponse("Payment Confirmed",status=200)
    else:
        return redirect('index')

def cancelpayment(request):
    if request.method == 'POST':

        bankObject = bankingMethod()
        paymentId = strip_tags(request.POST.get("paymentid",None))
        paymentInstanceTrue = ApiPayments.objects.filter(pending=False,pk=paymentid,deleted=False)
        if paymentInstanceTrue:
            
            bankInstance = bankObject.cancelPayment(paymentid,paymentInstanceTrue)
            return HttpResponse("Deleted",status=200)
        else:
            return HttpResponse("Error, Something went wrong. Please Reload the page to continue",status=500)
    else:
        return redirect('index')

        
def paymentHateoas(request,paymentid):
    if request.method == 'GET':
        userObject = getUserDetails()
        apiKey = request.META.get("HTTP_X_API_KEY", False)
        companyAccNumber = request.META.get("HTTP_ACCOUNTNUMBER", False)
        checkApi = account.objects.filter(api_key=apiKey)
        comapanyAcc = userObject.getUserAccountDetails2(companyAccNumber)

        if not checkApi:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":\
            "Api key Error. If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        if not comapanyAcc:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":\
            "Company Account Number Error. If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        for x in comapanyAcc:
            compId = x.id
            companyKey = x.api_key

        if apiKey != companyKey:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Api key Error, \
                your api key does not match your company key.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        ApiInstance = apiTransaction.objects.values().filter(parentTransaction__id=paymentid)
        
        if not ApiInstance:
            context = {"error":"INVALID_REQUEST","error_description":"Trasaction does not exist or not yet confirmed"}
            return JsonResponse(context, safe=False,status=400)
        else:
            for x in ApiInstance:
                context = {"transaction_id":paymentid,"transaction_details":[x['transaction']],"status":True}
                return JsonResponse(context, safe=False,status=200)
    else:
        context = {"error":"METHOD_NOT_SUPPORTED","error_description":"Invalid request method"}
        return JsonResponse(context, safe=False,status=405)


@csrf_exempt
def paymentRefund(request):
    if request.method == 'POST':
        userObject = getUserDetails()
        apiKey = request.META.get("HTTP_X_API_KEY", False)
        companyAccNumber = request.META.get("HTTP_ACCOUNTNUMBER", False)
        checkApi = account.objects.filter(api_key=apiKey)
        comapanyAcc = userObject.getUserAccountDetails2(companyAccNumber)

        if not checkApi:
            context = {"Msg":"Api key Error","status":False,"errcode":403}
            return JsonResponse(context, safe=False,status=403)

        if not comapanyAcc:
            context = {"Msg":"Your company account Number is invalid","status":False,"errcode":422}
            return JsonResponse(context, safe=False,status=403)

        for x in comapanyAcc:
            compId = x.id
            companyKey = x.api_key

        if apiKey != companyKey:
            context = {"Msg":"Your Api key doesn't match your company key.","status":False,"errcode":424}
            return JsonResponse(context, safe=False,status=403)

    else:
        context = {"Msg":"Invalid Request Method","status":False,"errcode":403}
        return JsonResponse(context, safe=False,status=403)

@csrf_exempt
def paymentCancel(request,paymentid):
    if request.method == 'POST':
        userObject = getUserDetails()
        bankObject = bankingMethod()
        apiKey = request.META.get("HTTP_X_API_KEY", False)
        companyAccNumber = request.META.get("HTTP_ACCOUNTNUMBER", False)
        checkApi = account.objects.filter(api_key=apiKey)
        comapanyAcc = userObject.getUserAccountDetails2(companyAccNumber)

        if not checkApi:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Api key Error.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        if not comapanyAcc:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Company Account Number Error.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        for x in comapanyAcc:
            compId = x.id
            companyKey = x.api_key

        if apiKey != companyKey:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Api key Error, \
                your api key does not match your company key.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        paymentInstanceTrue = ApiPayments.objects.filter(pending=True,pk=paymentid,deleted=False)

        paymentInstanceFalse = ApiPayments.objects.filter(pending=False,pk=paymentid,deleted=True)

        if paymentInstanceTrue:
            context = {"error":"INVALID_REQUEST","error_description":"You are trying to cancel a confirmed payment"}
            return JsonResponse(context, safe=False,status=400)

        if not paymentInstanceFalse:
            context = {"error":"RESOURCE_NOT_FOUND","error_description":"resource does not exist"}
            return JsonResponse(context, safe=False,status=404)

        bankInstance = bankObject.cancelPayment(paymentid,paymentInstanceFalse)

        return JsonResponse(bankInstance, safe=False,status=200)
    else:
        context = {"error":"METHOD_NOT_SUPPORTED","error_description":"Invalid request method"}
        return JsonResponse(context, safe=False,status=405)

def paymentsList(request):
    try:
        userObject = getUserDetails()
        apiKey = request.META.get("HTTP_X_API_KEY", False)
        companyAccNumber = request.META.get("HTTP_ACCOUNTNUMBER", False)
        queryLimit = request.GET.get('querysize',0)
        offset = request.GET.get('offset',0)
        endtime = request.GET.get('end_time',timezone.now())
        comapanyAcc = userObject.getUserAccountDetails2(companyAccNumber)
        
        if not comapanyAcc:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Company Account Number Error.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)

        for x in comapanyAcc:
            compId = x.id
            companyKey = x.api_key

        if apiKey != companyKey:
            context = {"error":"AUTHENTICATION_FAILURE","error_description":"Api key Error, \
                your api key does not match your company key.\
                If you are the user please contact the system administrator."}
            return JsonResponse(context, safe=False,status=401)
        try:
            queryset = ApiPayments.objects.filter(seller__id=compId,dateCreated__lte=endtime,deleted=False)[int(offset):int(queryLimit)]
        except AssertionError:
            queryset = ApiPayments.objects.filter(seller__id=compId,deleted=False)[:10]

        results = []
        if queryset:
            for x in queryset:
                case = {"invoice_id":x.invoiceId,"confirmed":x.pending,"amount":float(x.amount),
                    "payer":x.payer.id,"seller":x.seller.id,
                    "dateCreated":str(x.dateCreated),"dateConfirmed":str(x.dateConfirmed),
                    "links":[
                    {'href':f'http://192.168.1.6:8888/api/payments/sale/{x.id}',
                        'rel':'self','method':'GET'},
                        
                    {'href':f'http://192.168.1.6:8888/api/payments/sale/{x.id}/cancel',
                        'rel':'refund','method':'POST'}]}
                results.append(case)

            return JsonResponse(results, safe=False,status=200)
        else:
            context = {}
            return JsonResponse(context, safe=False,status=200)

    except ObjectDoesNotExist:
        context = {"error":"RESOURCE_NOT_FOUND","error_description":"resource does not exist"}
        return JsonResponse(context, safe=False,status=404)


def paymentslink(request):
    return render(request,"banking/payments.html")

def error_404(request, exception):
    return render(request, "banking/404.html")

def error_500(request):
    return render(request, "banking/500.html")