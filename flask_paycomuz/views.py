from flask import request
from flask.views import MethodView
from .errors import PaycomErrors
import time
p_errors = PaycomErrors()

class Paycom_JSON_RPC():
    def __init__(self, db, models, account_data, validator, callback):
        self.models = models
        self.db = db
        self.Payme_Transaction, self.Payme_Account = self.models
        self.account_data = account_data
        self.validator = validator
        self.callback = callback


    def CheckPerformTransaction(self, data):
        validate, detail = self.validator(data['params']['account'])
        res = {"result" : {
                "allow" : True
            }}
        if not validate:
            return p_errors.NotExist(data['id'])
        if len(detail) != 0:
            res['detail'] = detail
        return res
        
        
        
    def CreateTransaction(self,data):
        validate, _d = self.validator(data['params']['account']) 
        if validate:
            transaction_id = data['params']['id']
            tr = self.Payme_Transaction.query.filter(self.Payme_Transaction.transaction_id == transaction_id).first()
            if tr:
                if tr.state != 1:
                    return p_errors.CantCreateTr(data['id'])
                return tr.result()
            tr = self.Payme_Transaction(
                payme_id = data['id'],
                transaction_id = data['params']['id'],
                time = data['params']['time'],
                amount = data['params']['amount'],
                created_at = int(time.time() * 1000)
            )
            self.db.session.add(tr)
            self.db.session.commit()
            for key, value in data['params']['account'].items():
                ac = self.Payme_Account(
                    transaction_id = tr.transaction_id,
                    key = key,
                    value = value
                )
                self.db.session.add(ac)
                self.db.session.commit()
            self.callback(tr)
            return tr.result()
        return p_errors.NotExist(data['id'])
        
        
    def CheckTransaction(self,data):
        tr = self.Payme_Transaction.query.filter(self.Payme_Transaction.transaction_id == data['params']['id']).first()
        if not tr:
            return p_errors.TransactionNotFound(data['id'])
        per_time = tr.time if tr.state == 2 else 0
        can_time = tr.time if tr.state == -1 else 0
        return {
            "result" : {
                "create_time" : tr.created_at,
                "perform_time" : per_time,
                "cancel_time" : can_time,
                "transaction" : tr.transaction_id,
                "state" : tr.state,
                "reason" : tr.reason
            }
        }
        
    def PerformTransaction(self,data):
        tr = self.Payme_Transaction.query.filter(self.Payme_Transaction.transaction_id == data['params']['id']).first()
        if not tr:
            return p_errors.TransactionNotFound(data['id'])
        if tr.state == -1:
            return p_errors.TransactionNotFound(data['id'])
        if tr.state != 2:
            tr.time = int(time.time() * 1000)
            tr.state = 2
            self.db.session.add(tr)
            self.db.session.commit()
            self.callback(tr)
        return {"result" : {
                "transaction" : tr.transaction_id,
                "perform_time" : tr.time,
                "state" : tr.state
            }}
    
    def CancelTransaction(self,data):
        tr = self.Payme_Transaction.query.filter(self.Payme_Transaction.transaction_id == data['params']['id']).first()
        if not tr:
            return p_errors.TransactionNotFound(data['id'])
        if tr.state == 1:
            tr.state = -1
            tr.time = int(time.time() * 1000)
            tr.reason = int(data['params']['reason'])
            self.db.session.add(tr)
            self.db.session.commit()
            return {
                "result" : {
                    "transaction" : tr.transaction_id,
                    "cancel_time" : tr.time,
                    "state" : tr.state,
                    "reason" : tr.reason
                }
            }
            
        return p_errors.CantCancel(data['id'])
        
        
    def Paycom_Rotate(self, data):
        if data['method'] == 'CheckPerformTransaction':
            return self.CheckPerformTransaction(data)
        if data['method'] == 'CreateTransaction':
            return self.CreateTransaction(data)
        if data['method'] == 'CheckTransaction':
            return self.CheckTransaction(data)
        if data['method'] == 'PerformTransaction':
            return self.PerformTransaction(data)
        if data['method'] == 'CancelTransaction':
            return self.CancelTransaction(data)


class PaycomMethodView(MethodView):
    init_every_request = False
    def __init__(self, models, account_data, validator, db, callback):
        self.models = models
        self.db = db
        self.account_data = account_data
        self.validator = validator
        self.callback = callback
        
        
    def post(self):
        data = request.get_json()
        jrpc = Paycom_JSON_RPC(self.db, self.models, self.account_data, self.validator, self.callback)
        return jrpc.Paycom_Rotate(data)
        
    