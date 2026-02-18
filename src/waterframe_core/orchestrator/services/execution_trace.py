"""Execution trace service for tracking agent workflows.

This service records agent interactions in a tree structure to enable
timeline visualization of agent workflows. Traces are persisted to SQLite.
"""

import json
import logging
import sqlite3
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Types of agents that can be tracked."""

    ORCHESTRATOR = "orchestrator"
    SPARQL = "sparql"
    SIMULATION = "simulation"
    OPTIMIZATION = "optimization"
    COMPOSITION = "composition"
    LLM = "llm"


@dataclass
class ExecutionNode:
    """A single node in an execution trace."""

    node_id: str
    trace_id: str
    parent_id: Optional[str]
    agent_type: str
    agent_id: str
    timestamp: datetime
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    processing: str
    children: List[str] = field(default_factory=list)


@dataclass
class ExecutionTrace:
    """An execution trace representing a complete agent workflow."""

    trace_id: str
    root_agent: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    nodes: List[ExecutionNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "root_agent": self.root_agent,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "status": self.status,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "trace_id": n.trace_id,
                    "parent_id": n.parent_id,
                    "agent_type": n.agent_type,
                    "agent_id": n.agent_id,
                    "timestamp": n.timestamp.isoformat(),
                    "inputs": n.inputs,
                    "outputs": n.outputs,
                    "processing": n.processing,
                    "children": n.children,
                }
                for n in self.nodes
            ],
        }


class ExecutionTraceService:
    """Service for recording and querying execution traces.

    Traces are persisted to SQLite for later analysis and visualization.
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the trace service.

        Args:
            db_path: Path to SQLite database. Defaults to traces.db in app data.
        """
        if db_path:
            self._db_path = Path(db_path)
        else:
            self._db_path = Path("traces.db")

        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database schema."""
        try:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row

            cursor = self._conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    root_agent TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT DEFAULT 'running'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    parent_id TEXT,
                    agent_type TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    inputs_json TEXT,
                    outputs_json TEXT,
                    processing TEXT,
                    FOREIGN KEY (trace_id) REFERENCES traces(trace_id)
                )
            """)
            self._conn.commit()
            logger.info(f"Trace database initialized at {self._db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize trace database: {e}")

    def start_trace(self, root_agent: str, inputs: Dict[str, Any]) -> str:
        """Start a new execution trace.

        Args:
            root_agent: The initial agent that started this trace.
            inputs: Initial inputs for the trace.

        Returns:
            The trace_id for the new trace.
        """
        trace_id = str(uuid.uuid4())
        now = datetime.utcnow()

        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "INSERT INTO traces (trace_id, root_agent, started_at, status) VALUES (?, ?, ?, ?)",
                (trace_id, root_agent, now.isoformat(), "running"),
            )

            node_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO nodes 
                   (node_id, trace_id, parent_id, agent_type, agent_id, timestamp, inputs_json, outputs_json, processing)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    node_id,
                    trace_id,
                    None,
                    AgentType.ORCHESTRATOR.value,
                    root_agent,
                    now.isoformat(),
                    json.dumps(inputs),
                    json.dumps({}),
                    "Started execution trace",
                ),
            )
            self._conn.commit()
            logger.info(f"Started trace {trace_id} for agent {root_agent}")
            return trace_id
        except Exception as e:
            logger.error(f"Failed to start trace: {e}")
            return trace_id

    def add_node(
        self,
        trace_id: str,
        parent_id: Optional[str],
        agent_type: AgentType,
        agent_id: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        processing: str,
    ) -> str:
        """Add a node to an existing trace.

        Args:
            trace_id: The trace to add the node to.
            parent_id: The parent node ID (for branching).
            agent_type: Type of agent.
            agent_id: ID of the agent.
            inputs: What the agent received.
            outputs: What the agent sent.
            processing: Description of what the agent did.

        Returns:
            The node_id of the added node.
        """
        node_id = str(uuid.uuid4())
        now = datetime.utcnow()

        try:
            cursor = self._conn.cursor()

            cursor.execute(
                """INSERT INTO nodes 
                   (node_id, trace_id, parent_id, agent_type, agent_id, timestamp, inputs_json, outputs_json, processing)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    node_id,
                    trace_id,
                    parent_id,
                    agent_type.value,
                    agent_id,
                    now.isoformat(),
                    json.dumps(inputs),
                    json.dumps(outputs),
                    processing,
                ),
            )

            if parent_id:
                cursor.execute(
                    "SELECT children FROM nodes WHERE node_id = ?",
                    (parent_id,),
                )
                row = cursor.fetchone()
                if row:
                    children = json.loads(row["children"]) if row["children"] else []
                    children.append(node_id)
                    cursor.execute(
                        "UPDATE nodes SET children = ? WHERE node_id = ?",
                        (json.dumps(children), parent_id),
                    )

            self._conn.commit()
            logger.debug(f"Added node {node_id} to trace {trace_id}")
            return node_id
        except Exception as e:
            logger.error(f"Failed to add node: {e}")
            return node_id

    def complete_trace(self, trace_id: str, status: str = "completed"):
        """Mark a trace as completed.

        Args:
            trace_id: The trace to complete.
            status: Final status ('completed', 'failed').
        """
        now = datetime.utcnow()
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "UPDATE traces SET completed_at = ?, status = ? WHERE trace_id = ?",
                (now.isoformat(), status, trace_id),
            )
            self._conn.commit()
            logger.info(f"Completed trace {trace_id} with status {status}")
        except Exception as e:
            logger.error(f"Failed to complete trace: {e}")

    def get_trace(self, trace_id: str) -> Optional[ExecutionTrace]:
        """Retrieve a complete trace.

        Args:
            trace_id: The trace to retrieve.

        Returns:
            The ExecutionTrace, or None if not found.
        """
        try:
            cursor = self._conn.cursor()

            cursor.execute(
                "SELECT * FROM traces WHERE trace_id = ?",
                (trace_id,),
            )
            trace_row = cursor.fetchone()
            if not trace_row:
                return None

            cursor.execute(
                "SELECT * FROM nodes WHERE trace_id = ? ORDER BY timestamp",
                (trace_id,),
            )
            node_rows = cursor.fetchall()

            nodes = []
            for row in node_rows:
                node = ExecutionNode(
                    node_id=row["node_id"],
                    trace_id=row["trace_id"],
                    parent_id=row["parent_id"],
                    agent_type=row["agent_type"],
                    agent_id=row["agent_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    inputs=json.loads(row["inputs_json"]) if row["inputs_json"] else {},
                    outputs=json.loads(row["outputs_json"])
                    if row["outputs_json"]
                    else {},
                    processing=row["processing"] or "",
                    children=json.loads(row["children"]) if row["children"] else [],
                )
                nodes.append(node)

            return ExecutionTrace(
                trace_id=trace_row["trace_id"],
                root_agent=trace_row["root_agent"],
                started_at=datetime.fromisoformat(trace_row["started_at"]),
                completed_at=datetime.fromisoformat(trace_row["completed_at"])
                if trace_row["completed_at"]
                else None,
                status=trace_row["status"],
                nodes=nodes,
            )
        except Exception as e:
            logger.error(f"Failed to get trace: {e}")
            return None

    def list_traces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent traces.

        Args:
            limit: Maximum number of traces to return.

        Returns:
            List of trace summaries.
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute(
                "SELECT * FROM traces ORDER BY started_at DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()

            traces = []
            for row in rows:
                traces.append(
                    {
                        "trace_id": row["trace_id"],
                        "root_agent": row["root_agent"],
                        "started_at": row["started_at"],
                        "completed_at": row["completed_at"],
                        "status": row["status"],
                    }
                )
            return traces
        except Exception as e:
            logger.error(f"Failed to list traces: {e}")
            return []

    def export_trace_turtle(self, trace_id: str) -> str:
        """Export a trace to Turtle format for RDF.

        Args:
            trace_id: The trace to export.

        Returns:
            Turtle-formatted string.
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return ""

        lines = [
            "@prefix wf: <https://ugentbiomath.github.io/waterframe#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            "",
            f"wf:Trace_{trace.trace_id} a wf:ExecutionTrace ;",
            f'    wf:traceId "{trace.trace_id}" ;',
            f'    wf:rootAgent "{trace.root_agent}" ;',
            f'    wf:startedAt "{trace.started_at.isoformat()}"^^xsd:dateTime ;',
            f'    wf:traceStatus "{trace.status}" .',
            "",
        ]

        for node in trace.nodes:
            lines.extend(
                [
                    f"wf:Node_{node.node_id} a wf:ExecutionNode ;",
                    f'    wf:nodeId "{node.node_id}" ;',
                    f'    wf:agentType "{node.agent_type}" ;',
                    f'    wf:agentId "{node.agent_id}" ;',
                    f'    wf:timestamp "{node.timestamp.isoformat()}"^^xsd:dateTime ;',
                    f'    wf:processing "{node.processing}" ;',
                    f"    wf:inTrace wf:Trace_{trace.trace_id} .",
                    "",
                ]
            )

        return "\n".join(lines)


execution_trace_service = ExecutionTraceService()
