from fastmcp import FastMCP
import bm25s
# import Stemmer
# from langchain_text_splitters import TokenTextSplitter

# text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=50)
# stemmer = Stemmer.Stemmer("english")
mcp = FastMCP("test")

@mcp.tool()
async def save(
    corpus: str,
    db_name: str
):
    if not corpus:
        raise ValueError("corpus is required")
    
    texts = text_splitter.split_text(corpus)
    corpus_tokens = bm25s.tokenize(texts, stopwords="en", stemmer=stemmer)
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)
    retriever.save(db_name, corpus=texts)
    
    return {
        "status": "success", 
        "report": "data have been saved"
    }
    
@mcp.tool()
async def search(
    query: str,
    db_name: str,
    top_k: int,
):
    """Process query"""
    if not query:
        raise ValueError("user query is required")
    
    query_tokens = bm25s.tokenize(query, stemmer=stemmer)
    retriever = bm25s.BM25.load(db_name, load_corpus=True)
    results, scores = retriever.retrieve(query_tokens, k=top_k)
    
    docs_with_scores = []
    for i in range(results.shape[1]):
        doc, score = results[0, i], scores[0, i]
        docs_with_scores.append({"document": doc, "score": float(score)})
    
    return {
        "status": "success",
        "results": docs_with_scores
    }
    
if __name__ == "__main__":
    mcp.run(transport="stdio")