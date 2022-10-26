from .views import PaycomMethodView
from .decorators import authorize
from .exeptions import Flask_Paycom_Exception
import base64
from flask import Flask


class Paycom:
    def __init__(self, db):
        self.account_data = []
        self.validator = None
        self.db = db
        self.paycom_key = None
        self.paycom_id = None
        
        class Payme_Transaction(db.Model):
            __tablename__ = 'payme_transaction'
            id = db.Column(db.Integer, primary_key = True)
            payme_id = db.Column(db.Integer, unique=True)
            transaction_id = db.Column(db.String, unique=True)
            time = db.Column(db.BigInteger, nullable=True)
            amount = db.Column(db.Integer, nullable=True)
            state = db.Column(db.Integer, default=1)
            created_at = db.Column(db.BigInteger, nullable=False)
            reason  = db.Column(db.Integer, nullable=True)
            account = db.relationship('Payme_Account', backref='payme_transaction')

            def result(self):
                return {"result" : {
                            "create_time" : self.created_at,
                            "transaction" : self.transaction_id,
                            "state" : self.state}
                    }
            
        
        
        class Payme_Account(db.Model):
            __tablename__ = 'payme_account'
            id = db.Column(db.Integer, primary_key = True)
            transaction_id = db.Column(db.ForeignKey("payme_transaction.transaction_id"))
            key = db.Column(db.String, nullable=True)
            value = db.Column(db.String, nullable=True)
        self.models = [Payme_Transaction, Payme_Account]
        
        
    def init_app(self, app:Flask, url_prefix='/payme'):
        paycom_key = app.config.get('PAYCOM_KEY')
        if not paycom_key:
            raise Flask_Paycom_Exception('PAYCOM_KEY is not set, please set it in Flask config')
        paycom_id = app.config.get('PAYCOM_ID')
        if not paycom_id:
            raise Flask_Paycom_Exception('PAYCOM_ID is not set, please set it in Flask config')
        if self.validator is None:
            raise Flask_Paycom_Exception('Please set validator before init app, use Register_Validators method to set')
        if self.callback is None:
            raise Flask_Paycom_Exception('Please register callback function before init app, use Register_Callback method to set')
        
        self.paycom_key = paycom_key
        self.paycom_id = paycom_id

        view = PaycomMethodView.as_view('paycom',models=self.models, db=self.db, account_data=self.account_data, validator=self.validator, callback = self.callback)
        view = authorize(key=paycom_key)(view)
        app.add_url_rule(url_prefix, view_func=view, methods=['POST'])
    
    
    def Register_Account_Data(self, account_data):
        self.account_data = account_data
    
    
    def Register_Validators(self, valitdator):
        self.validator = valitdator
        
    
    def Register_Callback(self, callback):
        self.callback = callback
    
    
    def Generate(self, amount, return_url=None, **kwargs):
        if len(self.account_data) == 0:
            raise Flask_Paycom_Exception('Please set account data before generate, Example: paycom.Register_Account_Data(["order_id"])')
        m = self.paycom_id
        res = 'm=%s'%m
        for item in self.account_data:
            key = kwargs.get(item)
            if key is None:
                raise Flask_Paycom_Exception('%s is not set'%item)
            res += ';ac.%s=%s'%(item, key)
        res += ';a=%s'%amount
        if return_url:
            res += ';c=%s'%return_url
        sample_string_bytes = res.encode("ascii")
        base64_bytes = base64.b64encode(sample_string_bytes)
        base64_string = base64_bytes.decode("ascii")
        url = 'https://checkout.paycom.uz/'
        return url+base64_string

    