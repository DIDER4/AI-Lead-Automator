"""
Document Data Model
Defines the structure for knowledge base documents
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

from src.config import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    """Knowledge base document model"""
    
    # Required fields
    filename: str
    content: str
    doc_type: str  # "pdf", "txt", "docx"
    
    # Metadata
    file_size: int = 0  # bytes
    num_chunks: int = 0
    upload_date: str = field(default_factory=lambda: datetime.now().isoformat())
    file_path: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    id: Optional[str] = None  # ChromaDB document ID
    
    # Enhanced metrics
    char_count: int = 0  # Total character count
    token_count: int = 0  # Estimated token count
    avg_chunk_size: float = 0.0  # Average characters per chunk
    last_modified: Optional[str] = None  # ISO format datetime
    embedding_cost_estimate: float = 0.0  # Estimated cost in USD
    summary: str = ""  # First 200 chars of content
    
    def __post_init__(self):
        """Validate fields after initialization"""
        if not self.filename:
            raise ValueError("Document filename cannot be empty")
        
        if not self.content:
            logger.warning(f"Document {self.filename} has empty content")
        
        # Validate document type
        valid_types = ["pdf", "txt", "docx"]
        if self.doc_type.lower() not in valid_types:
            logger.warning(f"Unknown document type: {self.doc_type}")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Document':
        """Create Document from dictionary"""
        return cls(**data)
    
    def get_display_size(self) -> str:
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_short_filename(self, max_length: int = 30) -> str:
        """Get shortened filename for display"""
        if len(self.filename) <= max_length:
            return self.filename
        return self.filename[:max_length-3] + "..."
    
    def get_formatted_token_count(self) -> str:
        """Get formatted token count with commas"""
        return f"{self.token_count:,}"
    
    def get_formatted_char_count(self) -> str:
        """Get formatted character count with commas"""
        return f"{self.char_count:,}"
    
    def get_formatted_cost(self) -> str:
        """Get formatted embedding cost estimate"""
        if self.embedding_cost_estimate < 0.01:
            return f"${self.embedding_cost_estimate:.4f}"
        return f"${self.embedding_cost_estimate:.2f}"
    
    def get_upload_date_formatted(self) -> str:
        """Get formatted upload date"""
        try:
            dt = datetime.fromisoformat(self.upload_date)
            return dt.strftime("%d %b %Y %H:%M")
        except:
            return self.upload_date
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
        return int(len(text) / 4)
