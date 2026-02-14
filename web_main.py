"""
Web-compatible entry point for Chain Hockey.
This is the main file that pygbag will compile for web.
"""

# Import the main function from main.py
# Pygbag will handle async/await requirements
import asyncio
from main import main

async def main_async():
    """Async wrapper for main function (required by pygbag)"""
    # Pygbag requires async main
    await asyncio.sleep(0)  # Yield to event loop
    main()

if __name__ == "__main__":
    # For web build, use async
    try:
        asyncio.run(main_async())
    except RuntimeError:
        # If already in event loop (web environment)
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_async())

