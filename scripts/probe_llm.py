from src.clients.llm_client import get_llm_model


def main():
    llm = get_llm_model(model="azure-gpt-5.4")
    response = llm.invoke("hi")
    print(response.content)


if __name__ == "__main__":
    main()
