import os
import datetime
import json

def log_data(log_file, tamil_input, data_source, output_text, output_file):
    """
    Log transliteration data to file.
    
    Args:
        log_file: Path to log file
        tamil_input: Original Tamil text
        data_source: Source of training data (csv/google_sheet)
        output_text: Generated Arwi text
        output_file: Path to output file
    """
    
    try:
        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "tamil_input": tamil_input,
            "data_source": data_source,
            "arwi_output": output_text,
            "success": True
        }
        
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Write to log file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # Also write to output file if specified
        if output_file:
            try:
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(output_text)
            except Exception as e:
                print(f"Error writing to output file: {e}")
        
        print(f"Logged transliteration: {tamil_input} -> {output_text}")
        
    except Exception as e:
        print(f"Error logging data: {e}")
        # Create error log entry
        error_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tamil_input": tamil_input,
            "data_source": data_source,
            "error": str(e),
            "success": False
        }
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error_entry, ensure_ascii=False) + "\n")
        except:
            pass  # If we can't log the error, just continue

def get_logs(log_file, limit=100):
    """
    Read recent log entries.
    
    Args:
        log_file: Path to log file
        limit: Maximum number of entries to return
        
    Returns:
        List of log entries
    """
    
    try:
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        # Get the last 'limit' lines
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        for line in recent_lines:
            try:
                log_entry = json.loads(line.strip())
                logs.append(log_entry)
            except json.JSONDecodeError:
                continue
        
        return logs
        
    except Exception as e:
        print(f"Error reading logs: {e}")
        return []

# Test function
if __name__ == "__main__":
    # Test logging
    test_log_file = "test_output.log"
    test_output_file = "test_temp_output.txt"
    
    log_data(
        test_log_file,
        "வணக்கம்",
        "google_sheet",
        "وَنَكَّمْ",
        test_output_file
    )
    
    # Test reading logs
    logs = get_logs(test_log_file)
    print(f"Found {len(logs)} log entries")
    if logs:
        print("Latest log:", logs[-1])
    
    # Clean up test files
    for file in [test_log_file, test_output_file]:
        if os.path.exists(file):
            os.remove(file)