from rest_framework import serializers
from .models import credentials, bankingCard, account


class creditSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = bankingCard
		fields = ['card_number','isDisabled','expiration_date','cvc','cardType']

class credentialsSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = credentials
		fields = ['fname','lname','mname','street','city','province','barrangay','postal_code']


		