import os

def hello_world():
    print(f"Hello World: {os.getenv('INPUT_HELLO_WORLD')}")

if __name__ == "__main__":
    hello_world()
