from pydantic import BaseModel
from typing import List, Union, Literal
from enum import Enum

# ===== 사용자 입력 =====
class InstanceRequirements(BaseModel):
    target_stability: str
    anticipated_rps: int
    requirements_for_data_processing: str

class UserInput(BaseModel):
    location: str
    service_type: str
    computing_service_model: str
    additional_requirements: str
    instance_requirements: List[InstanceRequirements]

# ===== Enums =====
class ResourceType(str, Enum):
    block_storage = "BlockStorage"
    compute = "Compute"
    managed_database = "ManagedDatabase"
    object_storage = "ObjectStorage"
    firewall_group = "FirewallGroup"
    firewall_rule = "FirewallRule"

class BackupStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"

class DatabaseEngine(str, Enum):
    mysql = "mysql"
    pg = "pg"

class IpType(str, Enum):
    v4 = "v4"
    v6 = "v6"

class Protocol(str, Enum):
    icmp = "icmp"
    tcp = "tcp"
    udp = "udp"
    gre = "gre"
    esp = "esp"
    ah = "ah"

class Position(BaseModel):
    y: int
    x: int

# ===== 리소스 별 Attributes =====
class BlockStorageAttributes(BaseModel):
    region_id: str
    id: str
    mount_id: str
    attached_to_instance: str
    size_gb: int
    label: str

class ComputeAttributes(BaseModel):
    region_id: str
    auto_backups: BackupStatus
    id: str
    plan: str
    status: str
    main_ip: str
    label: str
    os_id: int
    firewall_group_id: str

class ManagedDatabaseAttributes(BaseModel):
    region_id: str
    id: str
    status: str
    plan: str
    database_engine: str
    database_engine_version: int
    latest_backup: str
    label: str

class ObjectStorageAttributes(BaseModel):
    tier_id: int
    id: str
    cluster_id: int
    label: str

class FirewallGroupAttributes(BaseModel):
    id: str
    description: str

class FirewallRuleAttributes(BaseModel):
    id: str
    action: str
    port: str
    ip_type: str
    protocol: str
    subnet: str
    subnet_size: int
    notes: str

class BlockStorageResource(BaseModel):
    temp_id: str
    resource_type: Literal["BlockStorage"]
    position: Position
    attributes: BlockStorageAttributes

class ComputeResource(BaseModel):
    temp_id: str
    resource_type: Literal["Compute"]
    position: Position
    attributes: ComputeAttributes

class ManagedDatabaseResource(BaseModel):
    temp_id: str
    resource_type: Literal["ManagedDatabase"]
    position: Position
    attributes: ManagedDatabaseAttributes

class ObjectStorageResource(BaseModel):
    temp_id: str
    resource_type: Literal["ObjectStorage"]
    position: Position
    attributes: ObjectStorageAttributes

class FirewallGroupResource(BaseModel):
    temp_id: str
    resource_type: Literal["FirewallGroup"]
    position: Position
    attributes: FirewallGroupAttributes

class FirewallRuleResource(BaseModel):
    temp_id: str
    resource_type: Literal["FirewallRule"]
    position: Position
    attributes: FirewallRuleAttributes

Resource = Union[
    BlockStorageResource,
    ComputeResource,
    ManagedDatabaseResource,
    ObjectStorageResource,
    FirewallGroupResource,
    FirewallRuleResource,
]

class ArchitectureRecommendation(BaseModel):
    architecture: List[Resource]
    description: str

class FinalArchitectureResponse(BaseModel):
    rec1: ArchitectureRecommendation
    rec2: ArchitectureRecommendation
    rec3: ArchitectureRecommendation
