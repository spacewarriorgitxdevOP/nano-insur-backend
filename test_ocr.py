import asyncio
from ocr import extract_total

async def run_test():
    with open("assets/sample_bill.jpg", "rb") as image_file:
        image_bytes = image_file.read()
    
    print("Processing image...")
    result = await extract_total(image_bytes)
    print(f"✅ Success! Extracted Total: {result}")

asyncio.run(run_test())
