import re

def normalize_date(date_str: str | None) -> str | None:
    """Normalize date string to YYYY-MM-DD format."""
    if not date_str:
        return None
        
    date_str = date_str.strip()
    
    # Handle DD-MM-YYYY or DD/MM/YYYY
    dmy_pattern = r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$"
    match = re.match(dmy_pattern, date_str)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
    return date_str
