import time
import asyncio

async def brewCoffee():
    print("start coffee")
    await asyncio.sleep(3)
    print("end coffee")
    return "coffee ready"

async def toast():
    print("start tooast")
    await asyncio.sleep(5)
    print("end toast")
    return "toast toasted"

def main():
    start_time = time.time()

    result_coffee = brewCoffee()
    result_toast = toast()

    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f"sesult for coffee: {result_coffee}")
    print(f"result for toast: {result_toast}")
    print(f"time taken: {elapsed_time:.2f}")

main()