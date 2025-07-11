from langchain_community.document_loaders  import (
    DirectoryLoader,
    TextLoader,
    PDFMinerLoader,
    UnstructuredWordDocumentLoader
)
from config import Config

def load_documents(data_dir):
    loaders = {
        '.txt': TextLoader,
        '.pdf': PDFMinerLoader,
        '.docx': UnstructuredWordDocumentLoader
    }
    
    documents = []
    for ext, loader_cls in loaders.items():
        loader = DirectoryLoader(
            str(data_dir),
            glob=f"**/*{ext}",
            loader_cls=loader_cls,
            # loader_kwargs={'autodetect_encoding': True}
        )
        documents.extend(loader.load())
    return documents