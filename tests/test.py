import unittest, random, time,datetime
import json
from app import create_app, db



app = create_app()
class TestAPI(unittest.TestCase):
    def setUp(self):
        self.headers = {
            "Authorization": "Basic dGVzdF9pZDp0ZXN0X2tleQ=="
        }
        with app.app_context():
            db.drop_all()
            db.create_all()
    def tearDown(self):
        pass
    def test_unauthorized(self):
        data = {
            "jsonrpc": "2.0",
            "id": 77554,
            "method": "CheckPerformTransaction",
            "params": {
                "amount": 50000,
                "account": {}
            }
        }
        head = {"Authorization": "Basic UGF5Y29tOlV6Y2FyZDpzb21lUmFuZG9tU3RyaW5nMTU0NTM0MzU0MzU0NQ=="}
        
        with app.test_client() as client:
            res = client.post('/payme', headers=head, json=data)
            self.assertEqual(json.loads(res.data)['error']['code'],-32504)
    def test_checkperform(self):
        data = {
                "jsonrpc": "2.0",
                "id": 97774,
                "method": "CheckPerformTransaction",
                "params": {
                    "amount": 200000,
                    "account": {
                        "order_id": "1"
                    }
                }
            }
        
        with app.test_client() as client:
            res = client.post('/payme', headers=self.headers, json=data)
            res = json.loads(res.data)
            self.assertEqual(res['result']['allow'],True)
    def test_cancel_tr(self):
        data = {
                    "jsonrpc": "2.0",
                    "id": 6110,
                    "method": "CancelTransaction",
                    "params": {
                        "id": "631ae0bcf10971cd09f18389",
                        "reason": 3
                    }
                }
        with app.test_client() as client:
            res = client.post('/payme', headers = self.headers, json=data)
            res = json.loads(res.data)
            self.assertEqual(res['error']['code'], -31008)
            
    def test_create_tr(self):
        data = {
                "jsonrpc": "2.0",
                "id": 77570,
                "method": "CreateTransaction",
                "params": {
                    "account": {
                        "order_id": "1"
                    },
                    "amount": 3000,
                    "id": "631ae0bcf10971cd09f18389",
                    "time": 1662705852684
                }
            }
        data2 = {
                "jsonrpc": "2.0",
                "id": 77572,
                "method": "CheckTransaction",
                "params": {
                    "id": "631ae0bcf10971cd09f18389"
                }
            }
        with app.test_client() as client:
            res = client.post('/payme', headers = self.headers, json=data)
            res = json.loads(res.data)
            self.assertEqual(res['result']['state'], 1)
            
            res = client.post('/payme', headers = self.headers, json=data2)
            res = json.loads(res.data)
            self.assertEqual(res['result']['state'], 1)
            
    
    def test_perform_tr(self):
        data = {
                "jsonrpc": "2.0",
                "id": 77570,
                "method": "CreateTransaction",
                "params": {
                    "account": {
                        "order_id": "1"
                    },
                    "amount": 3000,
                    "id": "631ae0bcf10971cd09f18389",
                    "time": 1662705852684
                }
            }
        data1 = {
            "jsonrpc": "2.0",
            "id": 77574,
            "method": "PerformTransaction",
            "params": {
                "id": "631ae0bcf10971cd09f18389"
            }
        }
        
        data2 = {
            "jsonrpc": "2.0",
            "id": 77576,
            "method": "CheckTransaction",
            "params": {
                "id": "631ae0bcf10971cd09f18389"
            }
        }
        
        with app.test_client() as client:
            res = client.post('/payme', headers = self.headers, json=data)
            res = json.loads(res.data)
            self.assertEqual(res['result']['state'], 1)
            
            res = client.post('/payme', headers = self.headers, json=data1)
            res = json.loads(res.data)
            self.assertEqual(res['result']['state'], 2)
            
            res = client.post('/payme', headers = self.headers, json=data2)
            res = json.loads(res.data)
            self.assertEqual(res['result']['state'], 2)

                
if __name__ == '__main__':
    unittest.main()