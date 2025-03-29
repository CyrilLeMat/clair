from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import asyncio
from enum import Enum

# Models
class SourceType(str, Enum):
    NOTION = "Notion"
    CONFLUENCE = "Confluence"
    SLACK = "Slack"

class ConnectionStatus(str, Enum):
    CONNECTED = "Connected"
    DISCONNECTED = "Not connected"
    ERROR = "Error"

class IssueType(str, Enum):
    CONTRADICTION = "Contradiction"
    OUTDATED = "Outdated"
    AMBIGUOUS = "Ambiguous"
    MISALIGNMENT = "Misalignment"

class IssueSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Source(BaseModel):
    id: str
    name: SourceType
    status: ConnectionStatus
    docs_count: int = 0
    last_scan: Optional[datetime] = None
    config: Dict[str, Any] = {}

class Issue(BaseModel):
    id: str
    type: IssueType
    title: str
    description: str
    source_doc: str
    target_doc: Optional[str] = None
    severity: IssueSeverity = IssueSeverity.MEDIUM
    created_at: datetime
    source_type: SourceType
    metadata: Dict[str, Any] = {}

class AuditSummary(BaseModel):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_docs_scanned: int = 0
    issues_found: int = 0
    sources_audited: List[str] = []
    status: str = "running"

class SourceCredentials(BaseModel):
    api_key: str
    workspace_id: Optional[str] = None
    base_url: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="Clair API",
    description="API for Clair - The Adversarial Documentation Auditor",
    version="0.1.0",
)

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database for demo purposes
# In production, you'd use a real database
db = {
    "sources": [],
    "issues": [],
    "audits": []
}

# Endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to Clair API", "version": "0.1.0"}

# Sources
@app.get("/sources", response_model=List[Source])
async def get_sources():
    return db["sources"]

@app.post("/sources", response_model=Source)
async def add_source(source_type: SourceType, credentials: SourceCredentials):
    # In a real implementation, you would verify credentials here
    new_source = Source(
        id=str(uuid.uuid4()),
        name=source_type,
        status=ConnectionStatus.CONNECTED,
        docs_count=0,
        last_scan=None,
        config=credentials.dict()
    )
    db["sources"].append(new_source)
    return new_source

@app.delete("/sources/{source_id}")
async def delete_source(source_id: str):
    for i, source in enumerate(db["sources"]):
        if source.id == source_id:
            db["sources"].pop(i)
            return {"message": f"Source {source_id} deleted"}
    raise HTTPException(status_code=404, detail="Source not found")

# Issues
@app.get("/issues", response_model=List[Issue])
async def get_issues(
    source_type: Optional[SourceType] = None,
    issue_type: Optional[IssueType] = None,
    severity: Optional[IssueSeverity] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    filtered_issues = db["issues"]
    
    if source_type:
        filtered_issues = [i for i in filtered_issues if i.source_type == source_type]
    
    if issue_type:
        filtered_issues = [i for i in filtered_issues if i.type == issue_type]
        
    if severity:
        filtered_issues = [i for i in filtered_issues if i.severity == severity]
    
    # Sort by created_at descending
    filtered_issues.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    return filtered_issues[offset:offset + limit]

@app.get("/issues/{issue_id}", response_model=Issue)
async def get_issue(issue_id: str):
    for issue in db["issues"]:
        if issue.id == issue_id:
            return issue
    raise HTTPException(status_code=404, detail="Issue not found")

# Audits
@app.post("/audits", response_model=AuditSummary)
async def start_audit(background_tasks: BackgroundTasks, source_ids: List[str] = []):
    # Validate source IDs
    valid_sources = []
    for source_id in source_ids:
        source = next((s for s in db["sources"] if s.id == source_id), None)
        if source:
            valid_sources.append(source)
    
    if not valid_sources and source_ids:
        raise HTTPException(status_code=404, detail="No valid sources found")
    
    # If no sources specified, use all connected sources
    if not source_ids:
        valid_sources = [s for s in db["sources"] if s.status == ConnectionStatus.CONNECTED]
    
    # Create audit
    audit = AuditSummary(
        id=str(uuid.uuid4()),
        started_at=datetime.now(),
        sources_audited=[s.id for s in valid_sources]
    )
    
    db["audits"].append(audit)
    
    # Start background audit task
    background_tasks.add_task(run_audit, audit.id, valid_sources)
    
    return audit

@app.get("/audits", response_model=List[AuditSummary])
async def get_audits(limit: int = Query(10, ge=1, le=100)):
    # Sort by started_at descending
    sorted_audits = sorted(db["audits"], key=lambda x: x.started_at, reverse=True)
    return sorted_audits[:limit]

@app.get("/audits/{audit_id}", response_model=AuditSummary)
async def get_audit(audit_id: str):
    for audit in db["audits"]:
        if audit.id == audit_id:
            return audit
    raise HTTPException(status_code=404, detail="Audit not found")

# Dashboard stats
@app.get("/stats/overview")
async def get_overview_stats():
    total_issues = len(db["issues"])
    total_docs = sum(source.docs_count for source in db["sources"])
    connected_sources = sum(1 for source in db["sources"] if source.status == ConnectionStatus.CONNECTED)
    total_sources = len(db["sources"])
    
    issues_by_type = {}
    for issue_type in IssueType:
        issues_by_type[issue_type] = sum(1 for issue in db["issues"] if issue.type == issue_type)
    
    latest_audit = None
    if db["audits"]:
        latest_audit = max(db["audits"], key=lambda x: x.started_at)
    
    return {
        "total_issues": total_issues,
        "total_docs": total_docs,
        "connected_sources": connected_sources,
        "total_sources": total_sources,
        "issues_by_type": issues_by_type,
        "latest_audit": latest_audit
    }

# Function to simulate running an audit
async def run_audit(audit_id: str, sources: List[Source]):
    # Find the audit
    audit = next((a for a in db["audits"] if a.id == audit_id), None)
    if not audit:
        return
    
    # Simulate work with delays
    total_docs = 0
    total_issues = 0
    
    for source in sources:
        # Simulate scanning documents
        await asyncio.sleep(2)  # Simulate work
        
        # Generate random doc count for the demo
        import random
        doc_count = random.randint(10, 100)
        total_docs += doc_count
        
        # Update source
        source.docs_count = doc_count
        source.last_scan = datetime.now()
        
        # Generate some sample issues
        for _ in range(random.randint(2, 8)):
            issue_type = random.choice(list(IssueType))
            severity = random.choice(list(IssueSeverity))
            
            new_issue = Issue(
                id=str(uuid.uuid4()),
                type=issue_type,
                title=f"Sample {issue_type.value} issue",
                description=f"This is a sample issue found in {source.name}",
                source_doc=f"document_{random.randint(1, doc_count)}.md",
                severity=severity,
                created_at=datetime.now(),
                source_type=source.name,
                metadata={}
            )
            
            # Add target document for contradictions
            if issue_type == IssueType.CONTRADICTION:
                new_issue.target_doc = f"document_{random.randint(1, doc_count)}.md"
                new_issue.description = f"Contradiction between {new_issue.source_doc} and {new_issue.target_doc}"
            
            db["issues"].append(new_issue)
            total_issues += 1
    
    # Update audit with results
    audit.completed_at = datetime.now()
    audit.total_docs_scanned = total_docs
    audit.issues_found = total_issues
    audit.status = "completed"

# Setup some sample data when the app starts
@app.on_event("startup")
async def startup_event():
    # Add sample sources
    notion_source = Source(
        id=str(uuid.uuid4()),
        name=SourceType.NOTION,
        status=ConnectionStatus.CONNECTED,
        docs_count=156,
        last_scan=datetime.now() - timedelta(hours=2)
    )
    
    confluence_source = Source(
        id=str(uuid.uuid4()),
        name=SourceType.CONFLUENCE,
        status=ConnectionStatus.CONNECTED,
        docs_count=243,
        last_scan=datetime.now() - timedelta(days=1)
    )
    
    slack_source = Source(
        id=str(uuid.uuid4()),
        name=SourceType.SLACK,
        status=ConnectionStatus.DISCONNECTED
    )
    
    db["sources"] = [notion_source, confluence_source, slack_source]
    
    # Add sample issues
    for i in range(1, 41):
        source = random.choice(db["sources"])
        issue_type = random.choice(list(IssueType))
        severity = random.choice(list(IssueSeverity))
        
        issue = Issue(
            id=str(uuid.uuid4()),
            type=issue_type,
            title=f"Sample issue #{i}",
            description=f"This is sample issue #{i} of type {issue_type}",
            source_doc=f"document_{random.randint(1, 100)}.md",
            severity=severity,
            created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
            source_type=source.name
        )
        
        if issue_type == IssueType.CONTRADICTION:
            issue.target_doc = f"document_{random.randint(1, 100)}.md"
            issue.description = f"Contradiction between {issue.source_doc} and {issue.target_doc}"
        
        db["issues"].append(issue)
    
    # Add a sample audit
    sample_audit = AuditSummary(
        id=str(uuid.uuid4()),
        started_at=datetime.now() - timedelta(hours=2),
        completed_at=datetime.now() - timedelta(hours=1),
        total_docs_scanned=399,
        issues_found=40,
        sources_audited=[s.id for s in db["sources"] if s.status == ConnectionStatus.CONNECTED],
        status="completed"
    )
    
    db["audits"] = [sample_audit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
