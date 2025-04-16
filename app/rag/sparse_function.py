from abc import ABC, abstractmethod
from typing import List, Dict
import sys
import logging
from enum import Enum
from llama_index.core.bridge.pydantic import (
    BaseModel,
    StrictFloat,
    StrictInt,
    StrictStr,
)
from typing import (
    Dict,
    List,
    Optional,
    Union,
)
from llama_index.core.vector_stores.types import (
    FilterCondition,
)
from llama_index.core.vector_stores.types import (
    MetadataFilters,
    FilterOperator,
)


logger = logging.getLogger(__name__)

class BaseSparseEmbeddingFunction(ABC):
    @abstractmethod
    def encode_queries(self, queries: List[str]) -> List[Dict[int, float]]:
        pass

    @abstractmethod
    def encode_documents(self, documents: List[str]) -> List[Dict[int, float]]:
        pass


class BGEM3SparseEmbeddingFunction(BaseSparseEmbeddingFunction):
    def __init__(self,model) -> None:
        try:
            self.model = model
        except Exception as ImportError:
            error_info = (
                "Cannot import BGEM3FlagModel from FlagEmbedding. It seems it is not installed. "
                "Please install it using:\n"
                "pip install FlagEmbedding\n"
            )
            logger.fatal(error_info)
            sys.exit(1)

    def encode_queries(self, queries: List[str]):
        outputs = self.model.encode(
            queries, return_dense=False, return_sparse=True, return_colbert_vecs=False
        )["lexical_weights"]
        return [self._to_standard_dict(output) for output in outputs]

    def encode_documents(self, documents: List[str]):
        outputs = self.model.encode(
            documents, return_dense=False, return_sparse=True, return_colbert_vecs=False
        )["lexical_weights"]
        return [self._to_standard_dict(output) for output in outputs]

    def _to_standard_dict(self, raw_output):
        result = {}
        for k in raw_output:
            result[int(k)] = raw_output[k]
        return result


def sparse_embedding_function(model) -> BGEM3SparseEmbeddingFunction:
    return BGEM3SparseEmbeddingFunction(model)
