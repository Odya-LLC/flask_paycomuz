class PaycomErrors:
    errors = {
        "bad_auth" : -32504,
        "not_exist" : -31099,
        "cant_create_tr" : -31008,
        'tr_not_found' : -31003,
        "cant_cancel" : -31008
    }
    messages = {
        -32504 : {
            "ru" : "Неверная авторизация",
            "uz" : "Auth hato",
            "en" : "Unauthorized"
        },
        -31099 : {
            "ru" : "Неверные данные",
            "uz" : "Hato malumotlar",
            "en" : "Not exist"
        },
        -31008 : {
            "ru" : "Невозможно выполнить операцию",
            "uz" : "Невозможно выполнить операцию",
            "en" : "Невозможно выполнить операцию"
        },
        -31003 : {
            "ru" : "Транзакция не найдена",
            "uz" : "Tranzaksiya topilmadi",
            "en" : "Transaction not found"
        },
        -31007 : {
            "ru" : "Невозможно отменить транзакцию",
            "uz" : "Tranzaksiya bekor qilib bo'lmaydi",
            "en" : "Can't cancel transaction"
        }
    }
    def __init__(self):
        pass
    def __return_Error(self, code, id):
        ret = {
            "error" : {
                "code" : self.errors[code],
                "message" : self.messages[self.errors[code]]
            },
            "id" : int(id)
        }
        
        return ret
        

    def Unauthorized(self, id):
        return self.__return_Error('bad_auth', id)
    
    
    def NotExist(self, id):
        return self.__return_Error('not_exist', id)
    
    
    def CantCreateTr(self, id):
        return self.__return_Error('cant_create_tr', id)
    
    
    def TransactionNotFound(self, id):
        return self.__return_Error('tr_not_found', id)
    
    def CantCancel(self, id):
        return self.__return_Error('cant_cancel', id)

