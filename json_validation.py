# Target schema: 
# { 
#     "action": "search" | "answer", 
#     "q": non-empty str # required iff action == "search" 
#     "k": int in [1, 5] (default 3) # optional 
# }

from typing import Any, Dict, List, Tuple 

def validate_tool_call(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:  
    """  
    Returns (clean, errors). 'clean' strictly follows the schema with defaults applied.
    - Trim strings; coerce numeric strings to ints.
    - Remove unknown keys.
    - If action=='answer', ignore 'q' if present (no error).
    - On fatal errors (e.g., missing/invalid 'action', or missing/empty 'q' for search), return ({}, errors).  
    """ 

    errors = []

    # remove unknown keys
    keys = ["action", "q", "k"] # valid keys

    extracted = {k: payload.get(k, None) for k in keys} #extracts only valid keys

    # trim strings
    cleaned = {
        k: v.strip() 
        if isinstance(v, str) else v 
        for k,v in extracted.items()
        }
    
    # check if k between [1,5]
    if (cleaned["k"].isdigit()):
        # coerce numeric strings to ints
        cleaned["k"] = int(cleaned["k"])

        if not (1 <= cleaned["k"] <= 5):
            errors.append("k must be integer in range of 1 and 5 - [1,5]")
    
    else:
        cleaned["k"] = 3

    # check if "action" = "search" | "answer", 
    if ((cleaned["action"] == "search") or (cleaned["action"] == "answer")) == False:
        errors.append("missing or incorrect 'action', action must be either 'search' or 'answer' ")

    # check if action=='search' then q non-empty str
    if cleaned["action"] == "search":
        if not (isinstance(cleaned["q"], str) and (len(cleaned["q"]) > 0)):
            errors.append("when 'action' = 'search', q must not be empty string")

    
    # return on fatal error
    if len(errors) > 0:
        return ({}, errors)
    
    return (cleaned, errors)

test1 = {
    "action": " search  ", 
    "q": " testing", # required iff action == "search" 
    "k": " 2" # optional 
}

print(validate_tool_call(test1))
