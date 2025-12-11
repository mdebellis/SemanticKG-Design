from prefect import flow

@flow
def hello():
    print("Prefect is working locally!")

if __name__ == "__main__":
    hello()
