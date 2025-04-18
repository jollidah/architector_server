from pydantic import BaseModel
from typing import List, Optional, Literal


class UserInput(BaseModel):
    service_type: str
    computing_service_model: str
    target_stability: str
    anticipated_rps: int
    requirements_for_data_processing: str
    additional_requirements: str

class VultrInstance(BaseModel):
    plan: str
    region: str
    os_id: int
    label: str
    ssh_key_ids: List[str]
    tags: List[str]
    vpc_id: Optional[str] = None

class VultrVPC(BaseModel):
    region: str
    label: str
    v4_subnet: str
    v4_subnet_mask: int

class VultrObjectStorage(BaseModel):
    cluster_id: int
    region: str
    label: str

class VultrBlockStorage(BaseModel):
    region: str
    size_gb: int
    label: str
    attached_to_instance: str


class VultrDatabase(BaseModel):
    database_engine: Literal["mysql", "pg", "valkey", "kafka"]
    database_engine_version: str
    region: str
    plan: str
    label: str
    trusted_ips: List[str]
    vpc_id: Optional[str] = None

class Connection(BaseModel):
    from_: str
    to: str
    type: str

class Resources(BaseModel):
    vultr_instance: Optional[List[VultrInstance]] = []
    vultr_vpc: Optional[List[VultrVPC]] = []
    vultr_object_storage: Optional[List[VultrObjectStorage]] = []
    vultr_block_storage: Optional[List[VultrBlockStorage]] = []
    vultr_database: Optional[List[VultrDatabase]] = []

class TerraformInput(BaseModel):
    version: str
    environment: str
    resources: Resources
    connections: List[Connection]
    
class ArchitectureResponse(BaseModel):
    version: str
    environment: str
    resources: dict
    connections: list

class TerraformResponse(BaseModel):
    terraform_code: str
