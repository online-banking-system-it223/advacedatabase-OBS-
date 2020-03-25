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
    path('payment',views.checkifCardExist,name='payment'),
    path('developers.obs',views.paymentslink,name='payments'),
]