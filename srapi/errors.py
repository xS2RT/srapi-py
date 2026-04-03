class SrapiError(Exception):
    """Raised for any speedrun.com API error."""

    def __init__(self, message: str, status_code: int = 0, url: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.url = url

    def __str__(self) -> str:
        parts = [self.args[0]]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.url:
            parts.append(f"at {self.url}")
        return " ".join(parts)
