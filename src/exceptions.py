class BankException(Exception):
    """Exceção base para erros de negócio bancário."""

    def __init__(
        self,
        message: str,
        code: str = "BANK_ERROR",
        status_code: int = 400,
        details: list | None = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class SaldoInsuficienteException(BankException):

    def __init__(
        self, message: str = "Saldo insuficiente para concluir a transação."
    ):
        super().__init__(
            message=message, code="INSUFFICIENT_FUNDS", status_code=400
        )


class ContaInvalidaException(BankException):

    def __init__(self, message: str = "Conta não encontrada ou inativa."):
        super().__init__(
            message=message, code="ACCOUNT_NOT_FOUND", status_code=404
        )


class OperacaoNaoPermitidaException(BankException):

    def __init__(self, message: 
                 str = "Operação não permitida para esta conta."):
        super().__init__(
            message=message, code="FORBIDDEN_OPERATION", status_code=403
        )
