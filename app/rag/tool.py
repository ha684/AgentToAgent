from llama_index.core.tools import FunctionTool
from source.rag.query import QueryEngine
from llama_index.core import QueryBundle
from typing import List, Any, Optional, Set
import asyncio
from llama_index.core.schema import NodeWithScore
from apis.utils.data_class import Document
import hashlib

class Tool(QueryEngine):
    def __init__(self, llm, embed_model, db_config):
        super().__init__(llm, embed_model, db_config)
        self.query_engines = self._setup_query_engines(db_config=db_config)
    
    def create_function_tools(self) -> List[FunctionTool]:
        """Deprecated"""
        tool = FunctionTool.from_defaults(
            fn=self.helper_function,
            name="truy_xuất_thông_tin_cơ_sở_dữ_liệu",
            description="""
                Tra cứu thông tin từ cơ sở dữ liệu.
                - **Mục đích:** Lấy thông tin chính xác từ nguồn dữ liệu
                - **Sử dụng khi:**
                    1. Cần thông tin chi tiết về người, tổ chức
                    2. Kiểm tra nội dung hợp đồng, văn bản
                - **Ngừng ngay nếu không có kết quả**
                - **Không dùng cho:** 
                    1. Câu hỏi chung chung 
                    2. Yêu cầu ý kiến
            """
        )
        return [tool]
    
    def get_tools(self) -> List[FunctionTool]:
        """deprecated"""
        try:
            tools = self.create_function_tools()
            return tools
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve tools: {e}")
    
    def convert_nodes_for_response(self, nodes: List[NodeWithScore]) -> List[Document]:
        """Convert LlamaIndex nodes to serializable format with retriever type info"""
        excluded_keys = {
            "chunk_context", "document_title", "questions_this_excerpt_can_answer",
            "section_summary", "excerpt_keywords", "file_path", "file_size",
            "file_type", "file_name", "creation_date", "last_modified_date"
        }
            
        return [
            Document(
                doc_id=node.node_id,
                text=node.text,
                metadata={k: v for k, v in node.metadata.items() if k not in excluded_keys} if hasattr(node, 'metadata') and node.metadata else None,
                ref_doc_id=node.metadata.get("ref_doc_id") if hasattr(node, 'metadata') else None
            )
            for node in nodes
        ]
        
    async def helper_function(self, query: str) -> List[dict]:
        """Helper function for concurrent node retrieval with duplicate removal using hash comparison"""
        if not self.query_engines or not any(self.query_engines):
            print("No query engines available")
            return None
            
        query_bundle = QueryBundle(query)
        retriever_types = ["vector", "bm25"]
        retrieval_tasks = [
            engine.aretrieve(query_bundle) if engine is not None
            else asyncio.create_task(asyncio.sleep(0))
            for engine in self.query_engines
        ]
        
        try:
            results = await asyncio.gather(*retrieval_tasks, return_exceptions=True)
            
            seen_ids = set()
            seen_hashes = set()
            processed_nodes = []
            
            for result, retriever_type in zip(results, retriever_types):
                if isinstance(result, Exception):
                    print(f"{retriever_type} retriever failed: {result}")
                    continue
                
                if not result:
                    continue
                    
                for node in result:
                    content_hash = hashlib.md5(node.text.encode()).hexdigest()
                    if content_hash in seen_hashes:
                        continue

                    if hasattr(node, 'metadata'):
                        node.metadata["retriever_type"] = retriever_type

                    processed_nodes.append(node)
                    seen_hashes.add(content_hash)
            
            if not processed_nodes:
                print("No nodes retrieved from any engine")
                return None
                
            return self.convert_nodes_for_response(processed_nodes)
            
        except Exception as e:
            print(f"Error during concurrent node retrieval: {e}")
            raise e