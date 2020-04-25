from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.index, name='index'),
    path('register',views.userRegistration,name='register'),
    path('login',views.userLogin,name='login'),
    path('withdraw',views.fundsDrawing,name='withdraw'),
    path('logout_view',views.logout_view,name='logout_view'),
    path('credentialsInsert',views.credentialsInsert,name='credentialsInsert'),
    path('deposit',views.fundsDeposit,name='deposit'),
    path('loans',views.loanFunds,name='loans'),
    path('pay',views.loanPayment,name='pay'),
    path('trans',views.fundsTransfer,name='trans'),
    path('api/payments',views.receivePayment,name='payment'),
    path('developers.obs',views.paymentslink,name='payments'),
    path('api/paymentslist',views.paymentsList,name='list'),
    path('confirm',views.confirmPayments,name='confirm'),
    path('api/payments/sale/<int:paymentid>/',views.paymentHateoas,name='parent_payment'),
    path('api/payments/sale/<int:paymentid>/cancel/',views.paymentCancel,name='payment_cancel'),
    path('emails/<int:emailId>/',views.specificEmail,name='view_email'),
    path('emails/all',views.emailList,name='view_all_mail'),
    path('transactions/all',views.transactionList,name='view_all_transactions'),
    path('cancelpayment',views.cancelpayment,name='cancelpayment'),
]

