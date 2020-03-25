from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.urls import reverse
from .userManagement import RegisterUser, LoggingUser, getUserDetails
from .bankManagement import bankingMethod
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.utils.html import strip_tags
import decimal
from rest_framework import viewsets, status, permissions
from .serializers import creditSerializer, credentialsSerializer
from .models import bankingCard, account, credentials
from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework_api_key.models import APIKey
from cryptography.fernet import Fernet
def index(request):

    if request.user.is_authenticated:
        if request.user.is_admin:
            return redirect("/admin")
            
        userObject = getUserDetails()
        user = userObject.getUserInformation(request.user.id)
        account1 = userObject.getUserAccountDetails(request.user.id)
        for x in account1:
           num = x.id
        loans = userObject.getUserTotalLoans(request.user.id)
        totalLoans = userObject.getUserTotalAmountofLoans(request.user.id)
        transactions = userObject.getUserTransactionList(num)
        notif = userObject.getUserNotificationList(num)
        loansPayable = userObject.getUserTotalAmountofLoans(num)
        loanedTotal = userObject.getUserTotalLoans(num)
        cardDetails = userObject.getUserCardDetails(num)


        if not user:
            user = False
    
        context = {"user":user,
        "account":account1,
        "loans":loans,
        "totalLoans":totalLoans,
        "transactions":transactions,
        "notif":notif,
        "loansPayable":loansPayable,
        "totalLoaned":loanedTotal,
        "Card":cardDetails}

        return render(request, 'banking/index.html',context)
    else:
       return redirect('login')

    
def userRegistration(request):

    if not request.user.is_authenticated:

        if request.method == "POST":
            email = strip_tags(request.POST.get("email",None))
            code = strip_tags(request.POST.get("securecode",None))
            pass1 = strip_tags(request.POST.get("pass1",'123'))
            pass2 = strip_tags(request.POST.get("pass2",'1234'))
            regObject = RegisterUser()
            
            regis = regObject.register(email,code,pass1,pass2)
            if regis == "Password do not Match!":
                messages.error(request, regis)
                return HttpResponse(regis,status=400)

            elif regis == 'User Already Exist!':
                messages.error(request, regis)
                return HttpResponse(regis,status=400)
            else:
                login(request, regis)
                return redirect('index')
    
        else:
            return render (request, 'banking/register.html')
    else:
        return redirect('index')

def userLogin(request):
    if not request.user.is_authenticated:

        if request.method == "POST":
            logging = LoggingUser()
            email = strip_tags(request.POST.get("email",None))
            code = strip_tags(request.POST.get("securecode",None))
            password = strip_tags(request.POST.get("password",None))
            logging1 = logging.logmein(email,code,password)
            if not logging1:
                return render(request, "banking/login.html", {"messages": "Incorrect Email or Secure Code!"})
                return redirect('login')
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
    #CHECK IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #CHECK IF METHOD IS POST
        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            #PUT THE DATA IN HERE
            amount = decimal.Decimal(request.POST.get("amount",0))
            userSecretCode = int(request.POST.get("securecode",0))
            usercode = request.user.secure_code
            print(amount)
            print(userSecretCode)
            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount bust be Greater than 0!",status=403)

            bankInstance = bankObject.methodWithdraw(request.user.id, amount)
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

     #CHECK IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #CHECK IF METHOD IS POST
        if request.method == "POST":
            bankObject = bankingMethod()
            #PUT THE DATA IN HERE
            userObject = getUserDetails()
            amount = decimal.Decimal(request.POST.get("amount",0))
            userSecretCode = int(request.POST.get("securecode",0))
            usercode = request.user.secure_code

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount bust be Greater than 0!",status=403)
            
            bankInstance = bankObject.methodDeposit(request.user.id,amount)
            account1 = userObject.getUserAccountDetails(request.user.id)
            
            for x in account1:
               bal =  x.account_balance
            return HttpResponse(bal,status=200)
        else:
            return redirect('index')
    else:
        return redirect('index')

def loanFunds(request):

    if request.user.is_authenticated:

        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            amount = decimal.Decimal(request.POST.get("amount",0))
            userSecretCode = int(request.POST.get("securecode",0))
            yearsToPay = int(request.POST.get("yearstoPay",0))
            usercode = request.user.secure_code

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount must be Greater than 0!",status=403)

            if yearsToPay < 0:
                return HttpResponse("Years to pay must be Greater than 0!",status=403)

            account1 = userObject.getUserAccountDetails(request.user.id)

            bankInstane = bankObject.methodLoan(request.user.id,amount,yearsToPay)
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
    if request.user.is_authenticated:

        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            amount = decimal.Decimal(request.POST.get("amount",0))
            userSecretCode = int(request.POST.get("securecode",0))
            usercode = request.user.secure_code
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

            loanObject = bankObject.methodPayLoan(amount,request.user.id)

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
     #CHECK IF USER IS LOGGED IN
    if request.user.is_authenticated:
        #CHECK IF METHOD IS POST
        if request.method == "POST":
            bankObject = bankingMethod()
            userObject = getUserDetails()
            #PUT THE DATA IN HERE
            amount = decimal.Decimal(request.POST.get("amount",0))
            userSecretCode = int(request.POST.get("securecode",0))
            receiverAcc = int(request.POST.get("useracc",0))
            usercode = request.user.secure_code
            account1 = userObject.getUserAccountDetails(request.user.id)

            if userSecretCode != usercode:
                return HttpResponse("Secure Code Error!",status=403)

            if amount < 0:
                return HttpResponse("Amount bust be Greater than 0!",status=403)

            receiver = userObject.getUserCredentials(receiverAcc)

            if not receiver:
                return HttpResponse("Receiver Not Found. Please Check the account number",status=403)


            bankInstance = bankObject.methodTransfer(receiverAcc,request.user.id,amount)

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
        print(reg)
        return redirect('index')
    else:
        return redirect('index')

def checkifCardExist(request):
    cvc = request.META.get("HTTP_CVC", "")
    cardnumber = request.META.get("HTTP_CARDNUMBER", "")
    amount = decimal.Decimal(request.META.get("HTTP_AMOUNT", ""))
    companyAccNumber = request.META.get("HTTP_ACCOUNTNUMBER", "")
    intent = request.META.get("HTTP_INTENT", None)
    apiKey = request.META.get("HTTP_API_KEY", None)
    checkApi = APIKey.objects.filter(prefix=apiKey)

    if not checkApi:
        context = {"Msg":"API KEY ERROR","status":False,"errcode":401}
        return JsonResponse(context, safe=False,status=403)

    if intent != "Sale":
        context = {"Msg":"Intent Error, Please Set your intent into 'Sale' ","status":False,"errcode":402}
        return JsonResponse(context, safe=False,status=403)
    bankObject = bankingMethod()
    
    paySomething  = bankObject.externalApiAccount(amount,cardnumber,cvc,companyAccNumber)
    
    if paySomething == 'Non-sufficient funds!':
        context = {"Msg":paySomething,"status":False,"errcode":412}
        return JsonResponse(context, safe=False,status=403)

    if paySomething:
        return JsonResponse(paySomething, safe=False)

    else:
        context = {"Msg":"Credit Card Credentials Error","status":False,"errcode":405}
        return JsonResponse(context, safe=False,status=403)

    
def paymentslink(request):
    return render(request,"banking/payments.html")
class CreditCard(viewsets.ModelViewSet):
    serializer_class = creditSerializer
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get_queryset(self):
        try:
            # cvc = self.request.query_params.get('cvc')
            # cardnumber = self.request.query_params.get('cardnumber')
            cvc = self.request.META.get("HTTP_CVC", "")
            cardnumber = self.request.META.get("HTTP_CARDNUMBER", "")
            queryset = bankingCard.objects.filter(card_number=cardnumber,cvc=cvc)
           
            if queryset:
                return queryset
            else:
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
            
            
class userCredentials(viewsets.ModelViewSet):
    serializer_class = credentialsSerializer
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get_queryset(self):
        try:
            cvc = self.request.META.get("HTTP_CVC", "")
            cardnumber = self.request.META.get("HTTP_CARDNUMBER", "")
            cards = bankingCard.objects.filter(card_number=cardnumber,cvc=cvc)

            for x in cards:
                accounts = account.objects.filter(pk=x.user_id.id)

            for x in accounts:
                queryset = credentials.objects.filter(user_id__id=x.user_id.id)
            
            if queryset:
                return queryset
            else:
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
