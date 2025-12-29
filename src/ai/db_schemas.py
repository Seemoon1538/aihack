
DB_SCHEMAS = {
    "mysql": {
        "tables": ["users", "admin", "customers", "sessions", "tokens", "auth_log"],
        "columns": {
            "users": ["id", "username", "password", "email", "role", "token", "created_at"],
            "admin": ["id", "login", "pass", "level"]
        }
    },
    "wordpress": {
        "tables": ["wp_users", "wp_usermeta", "wp_posts"],
        "columns": {
            "wp_users": ["ID", "user_login", "user_pass", "user_email", "user_registered"],
            "wp_usermeta": ["user_id", "meta_key", "meta_value"]
        }
    },
    "django": {
        "tables": ["auth_user", "django_session", "auth_permission"],
        "columns": {
            "auth_user": ["id", "username", "password", "email", "is_staff", "is_superuser"]
        }
    },
    "laravel": {
        "tables": ["users", "password_resets", "sessions"],
        "columns": {
            "users": ["id", "name", "email", "password", "remember_token", "role"]
        }
    }
}