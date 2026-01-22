from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# -------------------------------------------------
# Create RAG chain (EXPORTED FUNCTION)
# -------------------------------------------------
def generation(vstore):
    retriever = vstore.as_retriever(search_kwargs={"k": 3})

    model = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
    )

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an ecommerce assistant. Use only the provided context to answer."),
        ("human", "Context:\n{context}\n\nQuestion:\n{input}")
    ])

    def retrieve_context(question) -> str:
    # ✅ Force question to string (CRITICAL FIX)
        if isinstance(question, list):
            question = " ".join(map(str, question))
        else:
            question = str(question)

        docs = retriever.invoke(question)
        return "\n\n".join(doc.page_content for doc in docs)

    # def retrieve_context(question: str) -> str:
    #     docs = retriever.invoke(question)
    #     return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": RunnableLambda(lambda x: retrieve_context(str(x["input"]))),
            "input": RunnableLambda(lambda x: x["input"]),
        }
        | qa_prompt
        | model
    )

    store = {}

    def get_session_history(session_id: str):
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

    conversational_rag = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
    )

    return conversational_rag


# -------------------------------------------------
# Optional local test (runs ONLY when file executed)
# -------------------------------------------------
if __name__ == "__main__":
    from flipkart.data_ingestion import data_ingestion

    vstore = data_ingestion("done")
    chain = generation(vstore)

    response = chain.invoke(
        {"input": "Recommend a good phone under 20k"},
        config={"configurable": {"session_id": "test_user"}}
    )

    print(response.content)
