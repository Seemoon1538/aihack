
TOKENS = {
    "jwt": {
        "regex": r"ey[A-Za-z0-9-_=]+\.ey[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        "secrets": ["changeme", "secret", "123456", "admin123", "password"],
        "payloads": [
            {"role": "admin", "user": "hacker"},
            {"admin": True, "exp": 9999999999},
            {"user_id": 1, "is_admin": True}
        ]
    },
    "session": {
        "regex": r"(PHPSESSID|JSESSIONID|ASP\.NET_SessionId|laravel_session)=[a-f0-9]{32,}"
    },
    "api_key": {
        "regex": r"(sk_live_|pk_live_|AIzaSy|ghp_|AKIA)[a-zA-Z0-9_-]{20,}"
    },
    "oauth": {
        "regex": r"ya29\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"
    }
}