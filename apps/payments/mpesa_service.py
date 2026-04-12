"""
KekiCakes – M-Pesa Daraja API Service
Handles STK Push initiation and access token retrieval
"""
import requests
import base64
from datetime import datetime
from django.conf import settings


class MpesaService:
    """Wrapper around the Safaricom Daraja API."""

    def __init__(self):
        self.consumer_key = settings.DARAJA_CONSUMER_KEY
        self.consumer_secret = settings.DARAJA_CONSUMER_SECRET
        self.shortcode = settings.DARAJA_SHORTCODE
        self.passkey = settings.DARAJA_PASSKEY
        self.environment = settings.DARAJA_ENVIRONMENT
        self.callback_url = settings.DARAJA_CALLBACK_URL

        self.base_url = (
            'https://sandbox.safaricom.co.ke'
            if self.environment == 'sandbox'
            else 'https://api.safaricom.co.ke'
        )

    def get_access_token(self) -> str | None:
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        try:
            r = requests.get(
                url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=10,
            )
            if r.status_code == 200:
                return r.json().get('access_token')
            print(f'[M-Pesa] Auth Error {r.status_code}: {r.text}')
        except Exception as e:
            print(f'[M-Pesa] Auth Exception: {e}')
        return None

    def _get_password(self, timestamp: str) -> str:
        raw = f'{self.shortcode}{self.passkey}{timestamp}'
        return base64.b64encode(raw.encode('utf-8')).decode('utf-8')

    @staticmethod
    def format_phone(phone: str) -> str:
        """Normalise phone to 2547XXXXXXXX format."""
        phone = ''.join(filter(str.isdigit, phone))
        if phone.startswith('0') and len(phone) == 10:
            return '254' + phone[1:]
        if phone.startswith('254') and len(phone) == 12:
            return phone
        if len(phone) == 9:
            return '254' + phone
        return phone

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: float | int,
        reference: str,
        description: str = 'Keki Cakes Order',
    ) -> dict:
        """
        Trigger an M-Pesa STK Push prompt on the customer's phone.
        Returns the Daraja API response dict or an error dict.
        """
        token = self.get_access_token()
        if not token:
            return {'error': 'Failed to obtain access token', 'ResponseCode': '99'}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self._get_password(timestamp)
        formatted_phone = self.format_phone(str(phone_number))

        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(float(amount)),
            'PartyA': formatted_phone,
            'PartyB': self.shortcode,
            'PhoneNumber': formatted_phone,
            'CallBackURL': self.callback_url,
            'AccountReference': str(reference)[:12],
            'TransactionDesc': str(description)[:13],
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        try:
            r = requests.post(
                f'{self.base_url}/mpesa/stkpush/v1/processrequest',
                headers=headers,
                json=payload,
                timeout=15,
            )
            data = r.json()
            if r.status_code == 200:
                return data
            return {
                'error': data.get('errorMessage', 'Unknown error'),
                'ResponseCode': '99',
                'raw': data,
            }
        except Exception as e:
            print(f'[M-Pesa] STK Push Exception: {e}')
            return {'error': str(e), 'ResponseCode': '99'}
