"""Tests for ModelRegistry service."""
import pytest
from ghent_water.orchestrator.services.model_registry import ModelRegistry
from ghent_water.orchestrator.schemas.models import ModelRegistrationRequest


class TestModelRegistry:
    """Test cases for ModelRegistry class."""

    def test_register_model(self, fresh_registry):
        """Test basic model registration."""
        request = ModelRegistrationRequest(
            id="dwp1",
            name="DWP1",
            description="Drinking Water Plant 1",
            endpoint="http://localhost:8001",
            capabilities=["SteadyStateSimulation"],
            entities=["ghent:DWP1"],
        )

        model = fresh_registry.register_model(request)

        assert model.id == "dwp1"
        assert model.name == "DWP1"
        assert model.endpoint == "http://localhost:8001"
        assert "SteadyStateSimulation" in model.capabilities

    def test_register_duplicate_model(self, fresh_registry):
        """Test updating an existing model registration."""
        request = ModelRegistrationRequest(
            id="dwp1",
            name="DWP1",
            description="Initial description",
            endpoint="http://localhost:8001",
            capabilities=["SteadyStateSimulation"],
            entities=["ghent:DWP1"],
        )
        fresh_registry.register_model(request)

        # Update with new description
        request_update = ModelRegistrationRequest(
            id="dwp1",
            name="DWP1 Updated",
            description="Updated description",
            endpoint="http://localhost:8001",
            capabilities=["SteadyStateSimulation", "MassBalance"],
            entities=["ghent:DWP1"],
        )
        model = fresh_registry.register_model(request_update)

        assert model.name == "DWP1 Updated"
        assert model.description == "Updated description"
        assert len(model.capabilities) == 2

    def test_get_model_exists(self, fresh_registry):
        """Test getting an existing model."""
        request = ModelRegistrationRequest(
            id="lieve_river",
            name="Lieve River",
            description="River segment",
            endpoint="http://localhost:8010",
            capabilities=["SteadyStateSimulation"],
            entities=["ghent:LIEVE_RIVER"],
        )
        fresh_registry.register_model(request)

        model = fresh_registry.get_model("lieve_river")

        assert model is not None
        assert model.id == "lieve_river"
        assert model.name == "Lieve River"

    def test_get_model_not_exists(self, fresh_registry):
        """Test getting a non-existent model returns None."""
        model = fresh_registry.get_model("nonexistent")
        assert model is None

    def test_unregister_model(self, fresh_registry):
        """Test unregistering a model."""
        request = ModelRegistrationRequest(
            id="wwtp1",
            name="WWTP1",
            description="Wastewater Treatment Plant",
            endpoint="http://localhost:8003",
            capabilities=["SteadyStateSimulation"],
            entities=["ghent:WWTP1"],
        )
        fresh_registry.register_model(request)

        result = fresh_registry.unregister_model("wwtp1")
        assert result is True
        assert fresh_registry.get_model("wwtp1") is None

    def test_unregister_model_not_exists(self, fresh_registry):
        """Test unregistering a non-existent model returns False."""
        result = fresh_registry.unregister_model("nonexistent")
        assert result is False

    def test_list_models(self, fresh_registry):
        """Test listing all registered models."""
        fresh_registry.register_model(ModelRegistrationRequest(
            id="dwp1", name="DWP1", description="", endpoint="http://localhost:8001",
            capabilities=[], entities=[]
        ))
        fresh_registry.register_model(ModelRegistrationRequest(
            id="wwtp1", name="WWTP1", description="", endpoint="http://localhost:8003",
            capabilities=[], entities=[]
        ))

        models = fresh_registry.list_models()

        assert len(models) == 2
        ids = {m.id for m in models}
        assert ids == {"dwp1", "wwtp1"}

    def test_find_models_by_capability(self, fresh_registry):
        """Test finding models by capability."""
        fresh_registry.register_model(ModelRegistrationRequest(
            id="dwp1", name="DWP1", description="", endpoint="http://localhost:8001",
            capabilities=["SteadyStateSimulation"], entities=[]
        ))
        fresh_registry.register_model(ModelRegistrationRequest(
            id="wwtp1", name="WWTP1", description="", endpoint="http://localhost:8003",
            capabilities=["SteadyStateSimulation", "MassBalance"], entities=[]
        ))

        steady_models = fresh_registry.find_models_by_capability("SteadyStateSimulation")
        balance_models = fresh_registry.find_models_by_capability("MassBalance")

        assert len(steady_models) == 2
        assert len(balance_models) == 1
        assert balance_models[0].id == "wwtp1"

    def test_create_job(self, fresh_registry):
        """Test creating a simulation job."""
        fresh_registry.register_model(ModelRegistrationRequest(
            id="dwp1", name="DWP1", description="", endpoint="http://localhost:8001",
            capabilities=[], entities=[]
        ))

        job_id = fresh_registry.create_job("dwp1", {"param1": "value1"})

        assert job_id is not None
        job = fresh_registry.get_job(job_id)
        assert job is not None
        assert job["model_id"] == "dwp1"
        assert job["status"] == "pending"
        assert job["parameters"]["param1"] == "value1"

    def test_update_job_status(self, fresh_registry):
        """Test updating job status."""
        job_id = fresh_registry.create_job("dwp1", {})

        fresh_registry.update_job_status(job_id, "running")
        job = fresh_registry.get_job(job_id)
        assert job["status"] == "running"
        assert job["started_at"] is not None

        results = {"output": "test_result"}
        fresh_registry.update_job_status(job_id, "completed", results=results)
        job = fresh_registry.get_job(job_id)
        assert job["status"] == "completed"
        assert job["results"] == results
        assert job["completed_at"] is not None

    def test_update_job_status_failed(self, fresh_registry):
        """Test updating job status to failed with error."""
        job_id = fresh_registry.create_job("dwp1", {})

        error_msg = "Connection refused"
        fresh_registry.update_job_status(job_id, "failed", error=error_msg)
        job = fresh_registry.get_job(job_id)
        assert job["status"] == "failed"
        assert job["error"] == error_msg

    def test_list_jobs_with_filters(self, fresh_registry):
        """Test listing jobs with filters."""
        fresh_registry.register_model(ModelRegistrationRequest(
            id="dwp1", name="DWP1", description="", endpoint="http://localhost:8001",
            capabilities=[], entities=[]
        ))

        job1 = fresh_registry.create_job("dwp1", {})
        job2 = fresh_registry.create_job("dwp1", {})

        fresh_registry.update_job_status(job1, "completed")
        fresh_registry.update_job_status(job2, "running")

        all_jobs = fresh_registry.list_jobs()
        assert len(all_jobs) == 2

        pending_jobs = fresh_registry.list_jobs(status="pending")
        assert len(pending_jobs) == 0

        completed_jobs = fresh_registry.list_jobs(status="completed")
        assert len(completed_jobs) == 1

    def test_get_job_stats(self, fresh_registry):
        """Test getting job statistics."""
        fresh_registry.register_model(ModelRegistrationRequest(
            id="dwp1", name="DWP1", description="", endpoint="http://localhost:8001",
            capabilities=[], entities=[]
        ))

        job1 = fresh_registry.create_job("dwp1", {})
        job2 = fresh_registry.create_job("dwp1", {})
        job3 = fresh_registry.create_job("dwp1", {})

        fresh_registry.update_job_status(job1, "completed")
        fresh_registry.update_job_status(job2, "failed")

        stats = fresh_registry.get_job_stats()

        assert stats["total"] == 3
        assert stats["pending"] == 1
        assert stats["completed"] == 1
        assert stats["failed"] == 1
