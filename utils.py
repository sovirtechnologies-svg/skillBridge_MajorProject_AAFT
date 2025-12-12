import pandas as pd
import re
import os
import json

def load_csv(filename):
    """
    Tries to load a CSV file from the current directory or 'data/' folder.
    Handles different delimiters (like '|' for all.csv) automatically.
    """
    # Define potential paths
    paths = [filename, os.path.join('data', filename)]
    
    for path in paths:
        if os.path.exists(path):
            try:
                # First try standard comma
                return pd.read_csv(path)
            except:
                try:
                    # Fallback for pipe-separated files (like all.csv)
                    return pd.read_csv(path, sep='|', on_bad_lines='skip')
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    return None
    
    print(f"❌ Warning: Could not find {filename}")
    return None

def load_json(filename):
    """Loads a JSON file from the current directory or 'data/' folder."""
    paths = [filename, os.path.join('data', filename)]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading JSON {filename}: {e}")
                return []
    return []

def normalize_skill_text(s):
    """
    Cleans skill text to handle special characters like C++, C#, .NET, Node.js
    """
    if pd.isna(s):
        return ""
        
    s = str(s).lower()
    s = s.replace('/', ';')  # Handle 'Java/C++' as two skills
    
    # Allow: a-z, 0-9, semicolon, comma, plus, space, dash, dot, hash
    # This preserves "c#", ".net", "node.js", "c++"
    s = re.sub(r'[^a-z0-9;,+\s\-\.\#]', ' ', s)
    
    s = s.replace(',', ';')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def parse_skills(skill_field):
    """
    Splits a string of skills into a clean list.
    Handles both list objects (from JSON) and strings (from CSV).
    """
    if isinstance(skill_field, list):
        # If it's already a list (from JSON), just clean each item
        return [normalize_skill_text(i) for i in skill_field]
        
    s = normalize_skill_text(skill_field)
    items = re.split(r'[;]+', s)
    
    # Clean and remove duplicates while preserving order
    cleaned_items = []
    seen = set()
    for i in items:
        i = i.strip()
        if i and i not in seen:
            cleaned_items.append(i)
            seen.add(i)
            
    return cleaned_items