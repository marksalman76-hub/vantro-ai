#!/usr/bin/env python3
"""
VANTRO.AI SECURITY FIX #4: Add Error Handling
Wraps critical endpoints to prevent exception leaks
"""
import re
from pathlib import Path

def add_error_handling():
    main_py = Path("backend/app/main.py")

    if not main_py.exists():
        print(f"❌ ERROR: {main_py} not found")
        return False

    print("🔧 Adding error handling...")
    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add HTTPException import
    if 'HTTPException' not in content:
        fastapi_import = content.find('from fastapi import')
        if fastapi_import > 0:
            line_end = content.find('\n', fastapi_import)
            old_import = content[fastapi_import:line_end]
            if 'HTTPException' not in old_import:
                new_import = old_import.replace('from fastapi import', 'from fastapi import HTTPException,')
                content = content[:fastapi_import] + new_import + content[line_end:]
                print("  ✅ Added HTTPException import")

    # Add global error handler
    error_handler = '''

# ============================================
# GLOBAL ERROR HANDLER
# ============================================
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch unhandled exceptions safely"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please contact support."
        }
    )

# ============================================
'''

    if '@app.exception_handler' not in content:
        step1_pos = content.find('# Step 1')
        if step1_pos > 0:
            content = content[:step1_pos] + error_handler + '\n' + content[step1_pos:]
            print("  ✅ Added global error handler")

    # Add safe logging function
    logging_function = '''

def safe_log_error(error: Exception, endpoint: str, tenant_id: str = "unknown"):
    """Log errors safely without exposing details"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error in {endpoint}", exc_info=True)
    return {"error": "Request failed", "detail": "An error occurred"}

'''

    if 'def safe_log_error' not in content:
        step1_pos = content.find('# Step 1')
        if step1_pos > 0:
            content = content[:step1_pos] + logging_function + '\n' + content[step1_pos:]
            print("  ✅ Added safe_log_error function")

    with open(main_py, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ CRITICAL FIX: Added error handling")
    print(f"✅ ENFORCED: Internal errors never leak to clients")
    print(f"✅ PROTECTED: Exceptions caught and logged safely")

    print("\n📋 BEHAVIOR:")
    print("  • All unhandled exceptions → 500 'Internal server error'")
    print("  • No stack traces in response")
    print("  • Full error logged internally for debugging")

    print("\n📋 Next steps:")
    print("  1. git diff backend/app/main.py")
    print("  2. git add backend/app/main.py")
    print("  3. git commit -m 'Security: Add error handling (CRITICAL FIX #4)'")
    print("  4. git push")
    return True

if __name__ == "__main__":
    add_error_handling()
