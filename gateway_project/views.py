from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.core.cache import cache
from .models import *
from django.http import HttpResponseRedirect




def response_func(status: bool, msg: str, data: dict):
    res = {
        'status': status,
        'message': msg,
        'data': data
    }
    return res



class Deposit(APIView):
    permission_classes = [IsAuthenticated]
    # throttle_classes = [UserRateThrottle]

    def post(self, request):
        header = {
            'accept': 'application/json',
            'content-type': 'application/json'
        }

    
        data = {
            'merchant_id': 'your merchant id',
            'amount': request.data['amount']*10, 
            'callback_url': 'your callback url',
            'description': 'test'
        }
        
        
        r = requests.post(url='https://api.zarinpal.com/pg/v4/payment/request.json',
                          json=data,
                          headers=header)
        
        authority = r.json()['data']['authority']

        
        if r.status_code == 200:
            obj = Transaction.objects.create(wallet_id=request.user.wallet.id,
                                             amount=request.data['amount']*10,
                                             transaction_code=authority,
                                             )
            
            cache.set(f'wallet{request.user.wallet.id}', request.data, 600)

            link = f'https://www.zarinpal.com/pg/StartPay/{authority}' 

            return Response(response_func(
                True,
                "gateway link",
                link
            ), status=status.HTTP_200_OK
            )
        




class WalletCallBack(APIView):


    def get(self, request):
        obj = Transaction.objects.get(transaction_code=request.GET['Authority'])
        print('walletCallback')
        header = {
                    'accept': 'application/json',
                    'content-type': 'application/json'
                }
                
        data = {
                    'merchant_id': 'your merchant id',
                    'amount': obj.amount,
                    'authority': obj.transaction_code
                }

        r = requests.post(url='https://api.zarinpal.com/pg/v4/payment/verify.json',
                                json=data, 
                                headers=header)

        try:
            if r.json()['data']['code'] == 100:
                obj.payment_status = 1
                obj.wallet.deposit(int(obj.amount))
                obj.save()
            
        except:
            print("wrong")
        return HttpResponseRedirect(f"http://192.168.1.177:3000/wallet/payment-result?tc={request.GET['Authority']}")

        