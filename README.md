# JSON-schema-validation

I implemented the solution using a defensive construction pattern. Instead of cleaning the raw input in place, the function builds a fresh cleaned dictionary by explicitly validating only the keys defined in the schema (action, q, k). This ensures that unknown keys are automatically discarded and defaults are reliably applied.

Key implementation details include:
- Strict Coercion: The logic handles k by accepting integers and "whole number" floats (e.g. 2.0), but explicitly rejects decimals (e.g. 2.5) to prevent silent data truncation.
- Conditional Logic: The q field is only validated and added to the output if action is set to "search".
- Automated Testing: I have included a comprehensive Pytest set within the file to verify the logic against happy paths, boundary conditions, and error scenarios.

The file can be executed using the “pytest test_json_validation.py” command.

Note: The file includes both the validate_tool_call() function and the comprehensive Pytest test set
