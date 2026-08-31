class SmartHomeException(Exception):
    def __init__(self, message: str, error_code: str = "GENERIC_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

class AuthenticationError(SmartHomeException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, error_code="AUTH_FAILED", status_code=401)

class AuthorizationError(SmartHomeException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, error_code="FORBIDDEN", status_code=403)

class NotFoundError(SmartHomeException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} '{identifier}' not found", error_code="NOT_FOUND", status_code=404)

class SafetyPolicyViolationError(SmartHomeException):
    def __init__(self, rule_name: str, reason: str):
        super().__init__(f"Action blocked by safety policy '{rule_name}': {reason}", error_code="SAFETY_VIOLATION", status_code=422)
