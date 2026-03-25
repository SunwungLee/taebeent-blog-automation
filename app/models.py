from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class KeywordRow:
    keyword_id: str
    main_keyword: str
    content_type: str = "info"
    score: float = 0.0
    status: str = "keyword_collected"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

@dataclass
class PostRow:
    post_id: str
    keyword_id: str
    title: str
    draft_html: str
    publish_status: str = "draft"
    external_url: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

@dataclass
class GeneratedContent:
    keyword_id: str
    title: str
    html: str
    faq: str
    content_type: str
    meta_description: Optional[str] = None

@dataclass
class PublishResult:
    post_id: str
    success: bool
    url: Optional[str] = None
    error_message: Optional[str] = None
