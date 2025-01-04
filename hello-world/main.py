import os

def hello_world():
    print("Hello World")
    print(f"input: {os.getenv("INPUT_HELLO_WORLD")}")

if __name__ == "__main__":
    hello_world()
