# utils.py
from profanity_check import predict_prob

THRESHOLD = 0.8  # adjust sensitivity

def check_profanity(value):
    if not isinstance(value, str):
        return {"valid": False, "message": "Input must be a string"}

    score = predict_prob([value])[0]

    if score >= THRESHOLD:
        return {
            "valid": False,
            "message": "Inappropriate language detected",
            "score": round(float(score), 2)
        }

    return {
        "valid": True,
        "message": "Input is clean",
        "score": round(float(score), 2)
    }
