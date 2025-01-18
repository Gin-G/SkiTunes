def sanitize_form_data(form_data):
    """Create a safe copy of form data with sensitive information redacted"""
    sensitive_fields = {'password', 'confirm_password', 'pwd', 'current_password', 'new_password'}
    
    # Convert ImmutableMultiDict to dict for manipulation
    safe_data = dict(form_data)
    
    # Redact sensitive fields
    for field in sensitive_fields:
        if field in safe_data:
            safe_data[field] = '********'
            
    return safe_data