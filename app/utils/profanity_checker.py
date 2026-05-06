from better_profanity import profanity

BLOCKED_SCORE = 1.0
CLEAN_SCORE = 0.0

def check_profanity(value):
    if not isinstance(value, str):
        message = "Input must be a string"
        return {"valid": False, "message": message, "msg": message, "score": BLOCKED_SCORE}

    if profanity.contains_profanity(value):
        message = "Inappropriate language detected"
        return {
            "valid": False,
            "message": message,
            "msg": message,
            "score": BLOCKED_SCORE
        }

    message = "Input is clean"
    return {
        "valid": True,
        "message": message,
        "msg": message,
        "score": CLEAN_SCORE
    }
