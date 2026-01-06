# Target schema: 
# { 
#     "action": "search" | "answer", 
#     "q": non-empty str # required iff action == "search" 
#     "k": int in [1, 5] (default 3) # optional 
# }

from typing import Any, Dict, List, Tuple 
import pytest

def validate_tool_call(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:  
    """  
    Returns (clean, errors). 'clean' strictly follows the schema with defaults applied.
    - Trim strings; coerce numeric strings to ints.
    - Remove unknown keys.
    - If action=='answer', ignore 'q' if present (no error).
    - On fatal errors (e.g., missing/invalid 'action', or missing/empty 'q' for search), return ({}, errors).  
    """ 

    cleaned = {}
    errors = []

    # ----------- 1. Validate 'action' -------------
    raw_action = payload.get("action") # returns None if missing key

    # Trim if its a string
    if isinstance(raw_action, str):
        raw_action = raw_action.strip()

    # checks if action is valid
    if raw_action not in ["search", "answer"]:
        errors.append("Error: action must be 'search' or 'answer'")
    else:
        cleaned["action"] = raw_action

    # ----------- 2. Validate 'q' -------------
    # Note: validate q only if action=='answer', else ignore q

    if cleaned.get("action") == "search":
        # returns None if missing key preventing KeyErrors
        raw_q =  payload.get("q") 

        # Trim if its a string
        if isinstance(raw_q, str):
            raw_q = raw_q.strip()

        # Checks for non-empty string
        if isinstance(raw_q, str) and len(raw_q) > 0:
            cleaned["q"] = raw_q
        else:
            errors.append("Error: q must be a non-empty string when action is 'search'")

    # ----------- 3. Validate 'k' -------------
    # Note: key is optional with default = 3
    raw_k = payload.get("k")

    if raw_k is None:
        cleaned["k"] = 3  # Apply default

    else:
        try:
            # If its a string strip and convert to float first
            if isinstance(raw_k, str):
                raw_k = raw_k.strip()
                raw_k = float(raw_k)
            else: # if input is a number (int or float)
                raw_k = float(raw_k)
            
            # check if raw_k is a whole number
            if not raw_k.is_integer():
                errors.append("Error: k must be a whole number")
            else:
                val_k = int(raw_k)

                # Check range
                if 1 <= val_k <= 5:
                    cleaned["k"] = val_k
                else:
                    errors.append("Error: k must be an integer in range [1,5]")


        except (ValueError, TypeError):
            # ValueError: int("abc") - invalid input
            # TypeError: int(object) - invalid data type
            errors.append("Error: k must be a valid integer")

    # ----------- 4. Return validated json -------------
    if errors:
        return ({}, errors)
    
    return (cleaned, errors)


# --- Happy Paths ---
def test_valid_search():
    payload = {"action": "search", "q": "python", "k": 5}
    expected = ({"action": "search", "q": "python", "k": 5}, [])
    assert validate_tool_call(payload) == expected

def test_valid_answer_ignores_q():
    # 'q' is present but should be removed because action is 'answer'
    payload = {"action": "answer", "q": "ignore me", "k": 2}
    expected = ({"action": "answer", "k": 2}, [])
    assert validate_tool_call(payload) == expected

def test_defaults_k():
    payload = {"action": "answer"}
    expected = ({"action": "answer", "k": 3}, [])
    assert validate_tool_call(payload) == expected

def test_whitespace_trimming():
    payload = {"action": " search ", "q": "  testing  ", "k": " 1 "}
    expected = ({"action": "search", "q": "testing", "k": 1}, [])
    assert validate_tool_call(payload) == expected

def test_removes_unknown_keys():
    payload = {"action": "answer", "random_junk": "delete me"}
    expected = ({"action": "answer", "k": 3}, [])
    assert validate_tool_call(payload) == expected

# --- Edge Cases & Coercion ---
def test_k_coercion_string():
    payload = {"action": "answer", "k": "4"}
    expected = ({"action": "answer", "k": 4}, [])
    assert validate_tool_call(payload) == expected

# --- Error Paths (Fatal) ---
def test_missing_action():
    payload = {"q": "foo"}
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: action must be 'search' or 'answer'" in errors[0]

def test_invalid_action_value():
    payload = {"action": "dance", "q": "foo"}
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: action must be 'search' or 'answer'" in errors[0]

def test_search_missing_q():
    payload = {"action": "search"}
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: q must be a non-empty string when action is 'search'" in errors[0]

def test_search_empty_q():
    payload = {"action": "search", "q": "   "} # Becomes empty string after strip
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: q must be a non-empty string when action is 'search'" in errors[0]

def test_k_out_of_range():
    payload = {"action": "answer", "k": 10}
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: k must be an integer in range [1,5]" in errors[0]

def test_k_bad_string():
    payload = {"action": "answer", "k": "abc"}
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: k must be a valid integer" in errors[0]

def test_k_float_string_fails():
    # int("2.5") raises ValueError
    payload = {"action": "answer", "k": "2.5"}
    clean, errors = validate_tool_call(payload)
    assert clean == {}
    assert "Error: k must be a whole number" in errors[0]