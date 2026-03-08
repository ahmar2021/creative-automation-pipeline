def validate_message(message, banned_words):
    """Lambda-ready function to validate message against banned words"""
    flagged = []
    
    for word in banned_words:
        if word.lower() in message.lower():
            flagged.append(word)
    
    if flagged:
        raise ValueError(f"Message contains prohibited terms: {flagged}")
    
    return True

def lambda_handler(event, context):
    """AWS Lambda handler"""
    message = event.get("message")
    banned_words = event.get("banned_words", [])
    
    try:
        validate_message(message, banned_words)
        return {
            "statusCode": 200,
            "body": {"valid": True}
        }
    except ValueError as e:
        return {
            "statusCode": 400,
            "body": {"valid": False, "error": str(e)}
        }
