from .views import PaycomMethodView
from .decorators import authorize


class Paycom:
    def __init__(self, db):
        self.account_data = []
        self.validator = None
        self.db = db
        
        class Payme_Transaction(db.Model):
            __tablename__ = 'payme_transaction'
            id = db.Column(db.Integer, primary_key = True)
            payme_id = db.Column(db.Integer, unique=True)
            transaction_id = db.Column(db.String, unique=True)
            time = db.Column(db.BigInteger, nullable=True)
            amount = db.Column(db.Integer, nullable=True)
            state = db.Column(db.Integer, default=1)
            created_at = db.Column(db.BigInteger, nullable=False)
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
        
    def init_app(self, app, url_prefix='/payme'):
        view = PaycomMethodView.as_view('paycom',models=self.models, db=self.db, account_data=self.account_data, validator=self.validator)
        view = authorize(key=app.config.get('PAYCOM_KEY'))(view)
        app.add_url_rule(url_prefix, view_func=view, methods=['POST'])
    
    def Register_Account_Data(self, account_data):
        self.account_data = account_data
    
    def Register_Validators(self, valitdator):
        self.validator = valitdator
    