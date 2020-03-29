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

class UnconfirmedPayments(viewsets.ModelViewSet):

    serializer_class = unprocessedpayments
    def get_queryset(self):
        try:

            userObject = getUserDetails()
            apiKey = self.request.META.get("HTTP_X_API_KEY", False)
            companyAccNumber = self.request.META.get("HTTP_ACCOUNTNUMBER", False)
            comapanyAcc = userObject.getUserCredentials(companyAccNumber)

            if not comapanyAcc:
                raise Http404

            for x in comapanyAcc:
                compId = x.id

            queryset = unconfirmedPayments.objects.filter(seller__id=compId)
            
            if queryset:
                return queryset
            else:
                raise Http404
        except ObjectDoesNotExist:
            raise Http404
