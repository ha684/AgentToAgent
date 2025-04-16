import os
import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable, Any, Tuple

import torch
from llama_index.core import (
    load_index_from_storage,
    PromptTemplate,
    get_response_synthesizer,
    StorageContext,
)
from llama_index.core.postprocessor import (
    LongContextReorder,
    PrevNextNodePostprocessor,
    SimilarityPostprocessor,
    MetadataReplacementPostProcessor,
)
from llama_index.core.prompts import (
    SelectorPromptTemplate,
    ChatPromptTemplate,
)
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.prompts.utils import is_chat_model
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.indices.keyword_table.retrievers import KeywordTableRAKERetriever
from llama_index.core.retrievers import VectorIndexRetriever

from source.rag.rerank import SentenceTransformerRerank
from apis.vectordb_api.vector_db_api.documents_management import DocumentManagement
from apis.utils.data_class import DBConfig
from source.rag.prompt import (
    DEFAULT_KEYWORD_EXTRACT_TEMPLATE_TMPL,
    DEFAULT_QUERY_KEYWORD_EXTRACT_TEMPLATE_TMPL,
    DEFAULT_TEXT_QA_PROMPT_TMPL,
    DEFAULT_REFINE_PROMPT_TMPL,
    TEXT_QA_PROMPT_TMPL_MSGS,
    CHAT_REFINE_PROMPT_TMPL_MSGS,
)

@dataclass
class IndexConfig:
    persist_dir: Path
    top_k: int
    rerank_top: int
    similarity_cutoff: float
    num_queries: int

class QueryEngine(DocumentManagement):
    def __init__(self, llm, embed_model, db_config):
        super().__init__(db_config)
        self.config = self._load_config()
        self.llm = llm
        self.embed_model = embed_model
        self.logger = logging.getLogger(__name__)
        self.postprocessors = self._setup_postprocessors()
        self.retriever_initializers = {
            "vector": self._init_vector_retriever,
            "bm25": self._init_bm25_retriever
        }
        
    def _load_config(self) -> IndexConfig:
        """Load configuration from environment variables."""
        return IndexConfig(
            persist_dir=Path(os.getenv("PERSIST_DIR", "./document_storage")),
            top_k=20,
            rerank_top=10,
            similarity_cutoff=0.5,
            num_queries=int(os.getenv("NUM_QUERIES", 1)),
        )

    @lru_cache(maxsize=8)
    def _get_safe_top_k(self, index_id: str, requested_top_k: int) -> int:
        """
        Determine a safe top_k value based on available documents.
        """
        try:
            index = self._get_index_by_id(index_id)
            total_docs = len(index.docstore.docs)
            safe_top_k = min(requested_top_k, total_docs)
            if safe_top_k < requested_top_k:
                self.logger.warning(
                    f"Requested top_k={requested_top_k} exceeds available documents ({total_docs}). "
                    f"Using top_k={safe_top_k}."
                )
            return max(1, safe_top_k)
        except Exception as e:
            self.logger.warning(f"Error calculating safe top_k: {e}. Using default value of 3.")
            return 3
    
    def _get_index_by_id(self, index_id: str):
        """Helper method to load index by id."""
        return load_index_from_storage(
            self.storage_context,
            index_id=index_id,
        )
        
    def _init_vector_retriever(self, db_config: DBConfig):
        """Initialize vector retriever."""
        vector_index = self._get_index_by_id(db_config.llamaindex.vector_index)
        safe_top_k = self._get_safe_top_k(db_config.llamaindex.vector_index, self.config.top_k)
        return VectorIndexRetriever(
            index=vector_index,
            similarity_top_k=safe_top_k,
            embed_model=self.embed_model,
        )

    def _init_bm25_retriever(self, db_config: DBConfig):
        """Initialize BM25 retriever."""
        safe_top_k = min(self.config.top_k, len(self.doc_store.docs))
        return BM25Retriever.from_defaults(
            docstore=self.doc_store,
            similarity_top_k=safe_top_k,
        )

    def _initialize_retrievers(self, db_config: DBConfig) -> List:
        """Initialize retrievers with error handling for each type."""
        retrievers = []
        retriever_types = ["vector", "bm25"]
        
        for retriever_type in retriever_types:
            try:
                initializer = self.retriever_initializers[retriever_type]
                retriever = initializer(db_config)
                retrievers.append(retriever)
                print(f"{retriever_type.capitalize()} retriever initialized successfully.")
            except Exception as e:
                retrievers.append(None)
                print(f"Failed to initialize {retriever_type} retriever: {e}")
        
        return retrievers

    def _setup_postprocessors(self) -> Dict[str, object]:
        """Set up postprocessors with better error handling."""
        postprocessors = {}
        
        # Core postprocessors
        core_processors = {
            "reorder": lambda: LongContextReorder(),
            "semantic_similarity": lambda: SimilarityPostprocessor(
                similarity_cutoff=self.config.similarity_cutoff
            ),
            "metadata": lambda: MetadataReplacementPostProcessor(target_metadata_key="window"),
        }
        
        # Initialize core postprocessors
        for name, initializer in core_processors.items():
            try:
                postprocessors[name] = initializer()
                self.logger.info(f"{name.capitalize()} postprocessor initialized successfully.")
            except Exception as e:
                self.logger.warning(f"Failed to initialize {name} postprocessor: {e}")
        
        # Optional postprocessors that depend on other components
        # if self.doc_store:
        #     try:
        #         postprocessors["prevnextnode"] = PrevNextNodePostprocessor(
        #             docstore=self.doc_store,
        #             num_nodes=1,
        #             mode="both",
        #         )
        #         self.logger.info("PrevNextNode postprocessor initialized successfully.")
        #     except Exception as e:
        #         self.logger.warning(f"Failed to initialize PrevNextNode postprocessor: {e}")
    
        # try:
        #     postprocessors["rerank"] = SentenceTransformerRerank(
        #         model=os.getenv("RERANK_MODEL", "ha684/ha_embedding"),
        #         top_n=self.config.rerank_top,
        #         device="cuda" if torch.cuda.is_available() else "cpu",
        #         trust_remote_code=True,
        #         keep_retrieval_score=True,
        #     )
        #     self.logger.info("Rerank postprocessor initialized successfully.")
        # except Exception as e:
        #     self.logger.warning(f"Failed to initialize rerank postprocessor: {e}")

        return postprocessors
    
    def _build_postprocessor_pipeline(self, pipeline_config=None):
        """Build a postprocessor pipeline from configuration."""
        if pipeline_config is None:
            pipeline_config = ["metadata", "semantic_similarity","reorder"]
            
        active_postprocessors = []
        for processor_name in pipeline_config:
            if processor_name in self.postprocessors:
                active_postprocessors.append(self.postprocessors[processor_name])
            else:
                self.logger.warning(f"Requested postprocessor '{processor_name}' not available.")
                
        return active_postprocessors
    
    def _create_response_synthesizer(self):
        """Create and return a response synthesizer with proper templates."""
        return get_response_synthesizer(
            response_mode="refine",
            llm=self.llm,
            text_qa_template=SelectorPromptTemplate(
                PromptTemplate(
                    DEFAULT_TEXT_QA_PROMPT_TMPL,
                    prompt_type=PromptType.QUESTION_ANSWER,
                ),
                conditionals=[
                    (
                        is_chat_model,
                        ChatPromptTemplate(message_templates=TEXT_QA_PROMPT_TMPL_MSGS),
                    )
                ],
            ),
            refine_template=SelectorPromptTemplate(
                PromptTemplate(
                    DEFAULT_REFINE_PROMPT_TMPL,
                    prompt_type=PromptType.REFINE,
                ),
                conditionals=[
                    (
                        is_chat_model,
                        ChatPromptTemplate(
                            message_templates=CHAT_REFINE_PROMPT_TMPL_MSGS
                        ),
                    )
                ],
            ),
            streaming=True,
        )
    
    def _setup_query_engine(self, retriever) -> Optional[RetrieverQueryEngine]:
        """Set up a query engine with a specific retriever."""
        if not retriever:
            return None
            
        active_postprocessors = self._build_postprocessor_pipeline()
        response_synthesizer = self._create_response_synthesizer()
        
        return RetrieverQueryEngine.from_args(
            retriever=retriever,
            llm=self.llm,
            node_postprocessors=active_postprocessors,
            response_synthesizer=response_synthesizer,
            use_async=True,
            streaming=True,
        )

    def _setup_query_engines(self, db_config) -> Tuple[Optional[RetrieverQueryEngine], ...]:
        """Set up and return query engines for each retriever type."""
        retrievers = self._initialize_retrievers(db_config)
        if not any(retrievers):
            self.logger.error("No retrievers available to set up query engines.")
            return None, None
            
        return tuple(self._setup_query_engine(retriever) for retriever in retrievers)