import argparse
from langchain_community.document_loaders import CSVLoader
from langchain.text_splitter import TokenTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import pipeline
from langchain.docstore.document import Document
from pathlib import Path

"""
Authors:
- Bartosz Stoklosa
- Sandor Baranyi
"""


def load_documents(file_path: str):
    loader = CSVLoader(
        file_path=file_path,
        csv_args={
            "delimiter": ",",
            "quotechar": '"',
            "fieldnames": [
                "data_id", "id", "date", "source", "title", "content", "author", "url",
                "published", "published_utc", "collection_utc", "category_level_1", "category_level_2"
            ]
        },
        content_columns=["title", "content"],
        metadata_columns=["id"],
        encoding="utf-8",
    )
    return loader.load()


def split_documents(documents):
    splitter = TokenTextSplitter(chunk_size=256, chunk_overlap=32, add_start_index=True)
    return splitter.split_documents(documents)


def embed_and_index(documents, persist_directory="./chroma_db"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # If index already exists, load it
    if Path(persist_directory).exists():
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print("Loaded existing vector index from disk.")
    else:
        vectordb = Chroma.from_documents(documents, embedding=embeddings, persist_directory=persist_directory)
        print("Created and saved new vector index.")
    return vectordb



def get_retrieved_documents(vectordb, query, strategy, ndocuments, kmarginal=None):
    if strategy == "ss":
        return vectordb.similarity_search(query, k=ndocuments)
    elif strategy == "mmr":
        return vectordb.max_marginal_relevance_search(query, fetch_k=ndocuments, k=kmarginal)
    else:
        raise ValueError("Invalid retrieval strategy. Use 'ss' or 'mmr'.")


def summarize_with_transformers(docs, summary_type):
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

    full_text = " ".join(doc.page_content for doc in docs)
    chunks = [full_text[i:i + 1000] for i in range(0, len(full_text), 1000)]
    summarized_parts = []

    for chunk in chunks:
        if summary_type == "simplified":
            prefix = "Please summarize this text for a young student using simple words:\n"
            max_len = 130
            min_len = 40
        else:  # advanced
            prefix = "Summarize this text with technical and analytical vocabulary for an expert reader:\n"
            max_len = 200
            min_len = 80

        summary = summarizer(prefix + chunk, max_length=max_len, min_length=min_len, do_sample=False)
        summarized_parts.append(summary[0]['summary_text'])

    return " ".join(summarized_parts)



def main():
    parser = argparse.ArgumentParser(description="RAG-based News Summarizer (Free version)")
    parser.add_argument("--query", "-q", required=True)
    parser.add_argument("--stype", "-t", choices=["simplified", "advanced"], required=True)
    parser.add_argument("--sretrieval", "-r", choices=["ss", "mmr"], required=True)
    parser.add_argument("--ndocuments", "-n", type=int, required=True)
    parser.add_argument("--kmarginal", "-k", type=int, help="Only for MMR strategy")
    parser.add_argument("--data", type=str, default="MN-DS-news-classification.csv", help="Path to news CSV file")

    args = parser.parse_args()

    print("Loading documents...")
    docs = load_documents(args.data)
    print(f"Loaded {len(docs)} documents.")

    print("Splitting documents...")
    split_docs = split_documents(docs)

    print("Embedding and indexing...")
    vectordb = embed_and_index(split_docs)

    print("Retrieving relevant documents...")
    retrieved = get_retrieved_documents(vectordb, args.query, args.sretrieval, args.ndocuments, args.kmarginal)

    print("Generating summary with Hugging Face model...")
    summary = summarize_with_transformers(retrieved, args.stype)

    label = "Simplified Summary" if args.stype == "simplified" else "Advanced Summary"
    print(f"\n{label}:\n{summary}")


if __name__ == "__main__":
    main()
