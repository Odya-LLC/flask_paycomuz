from flask_paycomuz import Paycom
from flask import *
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
paycom = Paycom(db)

orders = [1,2,3,4,5,6]

def CheckAllowment(account): # Before creating transaction Flask-PaycomUz send account data which will have key whick you gave to Register_Account_data to validate it. Return True/False to Validate
    order_id = account.get('order_id')
    detail = {
            "discount": { 
                "title": "Скидка 5%",
                "price": 10000
            },
            "shipping": { 
                "title": "Доставка до ттз-4 28/23",
                "price": 500000
            },
            "items": [ 
                {
                    "title": "Помидоры", 
                    "price": 505000, 
                    "count": 2, 
                    "code": "00702001001000001", 
                    "units": 241092, 
                    "vat_percent": 15, 
                    "package_code": "123456"
                }
            ]
        }
    if int(order_id) in orders:
        return True, detail
    return False, {}

def CallbackPayme(transaction): # After Creating and Performing transaction from Payme this function will call with Payme_Transaction as argument
    if transaction.state == 1: # Successful creating transaction in Payme
        print("State 1 got")
        pass
    if transaction.state == 2: # Successful performing transaction in Payme
        print('State 2 got')
        pass
    


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    
    paycom.Register_Account_Data(['order_id']) # Register Paycom payment details, requires to set before init app
    paycom.Register_Validators(CheckAllowment) # Register your Validator for payment, requires to set before init app
    paycom.Register_Callback(CallbackPayme) # Register your Callback function which will be called after Creating and Performing transaction
    paycom.init_app(app, url_prefix='/payme') # Init Paycom to your application, url_prefix to add view to app, defualt /payme, in that case Flask-PaycomUz register JSON-RPC route to recieve requests from PaycomUz as https://example.uz/payme
    db.init_app(app)
    @app.get("/")
    def index():
        return "Hello World"
    

    @app.get('/create_transaction')
    def create_transaction():
        amount = 10000
        order_id = 45 # Order ID to create Transaction in Paycom
        return_url = "https://example.uz/return_url" # return Url after successful or error payment 
        url = paycom.Generate(amount=amount, return_url=return_url, order_id = order_id)
        return jsonify({'msg' : url})

    with app.app_context():
        db.create_all() # Don't forget to create db, flask_paycomuz adds 2 table to db, Payme_Transaction and Payme_Account


    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)