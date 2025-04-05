import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from fixthaipdf import clean


load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001")
vector_store = Chroma(embedding_function=embeddings)


file_path = "CR99_2024Th.pdf"
loader = PyPDFLoader(file_path)
pages = loader.load_and_split()
pages[0]
for page in pages:
  page.page_content = clean(page.page_content)
print(pages[0])


from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(pages)
print(f"Split blog post into {len(all_splits)} sub-documents.")


document_ids = vector_store.add_documents(documents=all_splits)
print(document_ids[:3])


from langchain import hub
prompt = hub.pull("rlm/rag-prompt")
example_messages = prompt.invoke(
    {"context": "(context goes here)", "question": "(question goes here)"}
).to_messages()
assert len(example_messages) == 1
print(example_messages[0].content)


from langchain_core.documents import Document
from typing_extensions import List, TypedDict

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


from langgraph.graph import START, StateGraph
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))



question = "บัตรนิสิตหายต้องทำยังไง"
result = graph.invoke({"question": question})
print(f'Context: {result["context"]}\n\n')
print(f'Answer: {result["answer"]}')


for step in graph.stream(
    {"question": question}, stream_mode="updates"):
    print(f"{step}\n\n----------------\n")
for message, metadata in graph.stream(
    {"question": question}, stream_mode="messages"):
    print(message.content, end="|")