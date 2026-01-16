"""Simulation status panel component for displaying running jobs."""

import streamlit as st
import time
from datetime import datetime
from typing import Optional


# In-memory job tracking (would be replaced with actual API calls in production)
def _get_default_jobs() -> list[dict]:
    """Get default demo jobs."""
    return [
        {
            "job_id": "job-001",
            "model_name": "WWTP-1",
            "status": "running",
            "progress": 45,
            "started_at": datetime.now().isoformat(),
            "inputs": {"flow_rate": 500, "bod_in": 120},
        },
        {
            "job_id": "job-002",
            "model_name": "WWTP-2",
            "status": "completed",
            "progress": 100,
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "inputs": {"flow_rate": 300, "bod_in": 80},
        },
    ]


def render_simulation_status(
    jobs: list[dict] | None = None,
    auto_refresh: bool = True,
    refresh_interval: int = 5,
) -> None:
    """Render the simulation status panel.
    
    Args:
        jobs: List of job dictionaries. If None, uses default demo jobs.
        auto_refresh: Whether to show auto-refresh option.
        refresh_interval: Refresh interval in seconds.
    """
    st.markdown("### Simulation Status")
    
    if jobs is None:
        jobs = _get_default_jobs()
    
    if not jobs:
        st.info("No active simulation jobs.")
        return
    
    # Auto-refresh toggle
    if auto_refresh:
        col1, col2 = st.columns([1, 3])
        with col1:
            should_refresh = st.checkbox("Auto-refresh", value=True, key="auto_refresh")
        with col2:
            if should_refresh:
                st.empty()
                time.sleep(refresh_interval)
                st.rerun()
    
    # Display jobs
    for job in jobs:
        _render_job_card(job)
    
    # Show refresh button if auto-refresh is off
    if not auto_refresh or not st.session_state.get("auto_refresh", True):
        if st.button("Refresh Status", key="refresh_jobs"):
            st.rerun()


def _render_job_card(job: dict) -> None:
    """Render a single job status card.
    
    Args:
        job: Job dictionary with status information.
    """
    status = job.get("status", "unknown")
    model_name = job.get("model_name", "Unknown Model")
    job_id = job.get("job_id", "N/A")
    progress = job.get("progress", 0)
    
    # Status styling
    status_config = {
        "running": ("🟡 Running", "orange"),
        "completed": ("✅ Completed", "green"),
        "failed": ("❌ Failed", "red"),
        "pending": ("⏳ Pending", "gray"),
    }
    
    status_text, status_color = status_config.get(status, ("⚪ Unknown", "gray"))
    
    # Job card container
    with st.container():
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
                background-color: #fafafa;
            ">
                <strong>{model_name}</strong> {status_text}<br>
                <small>Job ID: {job_id}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Progress bar
        if status == "running":
            st.progress(progress / 100, text=f"Progress: {progress}%")
        elif status == "completed":
            st.progress(100, text="Complete")
        
        # Job details
        with st.expander("Job Details"):
            if "inputs" in job:
                st.markdown("**Inputs:**")
                for key, value in job["inputs"].items():
                    st.markdown(f"- {key}: {value}")
            
            if "started_at" in job:
                st.markdown(f"**Started:** {job['started_at']}")
            if "completed_at" in job:
                st.markdown(f"**Completed:** {job['completed_at']}")
            
            # Cancel button for running jobs
            if status == "running":
                if st.button("Cancel Job", key=f"cancel_{job_id}"):
                    st.warning(f"Job {job_id} cancellation requested.")


def add_job(jobs: list[dict], job: dict) -> list[dict]:
    """Add a new job to the jobs list.
    
    Args:
        jobs: Current list of jobs.
        job: New job to add.
        
    Returns:
        Updated list of jobs.
    """
    jobs.append(job)
    return jobs


def update_job_status(jobs: list[dict], job_id: str, updates: dict) -> list[dict]:
    """Update a job's status.
    
    Args:
        jobs: Current list of jobs.
        job_id: ID of the job to update.
        updates: Dictionary of fields to update.
        
    Returns:
        Updated list of jobs.
    """
    for job in jobs:
        if job.get("job_id") == job_id:
            job.update(updates)
            break
    return jobs


def remove_job(jobs: list[dict], job_id: str) -> list[dict]:
    """Remove a job from the jobs list.
    
    Args:
        jobs: Current list of jobs.
        job_id: ID of the job to remove.
        
    Returns:
        Updated list of jobs.
    """
    return [j for j in jobs if j.get("job_id") != job_id]
