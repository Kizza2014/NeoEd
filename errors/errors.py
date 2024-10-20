class InsufficientFundsError(Exception):
    def __init__(self, message="Số dư trong tài khoản không đủ"):
        self.message = message
        super().__init__(self.message)

class InsufficientStockError(Exception):
    def __init__(self, message="Số lượng hàng không đủ"):
        self.message = message
        super().__init__(self.message)