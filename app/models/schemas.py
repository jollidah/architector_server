from pydantic import BaseModel, Field
from typing import List, Union, Literal, Annotated
from enum import Enum

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

class ArchitectureItem(BaseModel):
    description: str

class EvalRecommandedArchitecture(BaseModel):
    rec1: ArchitectureItem
    rec2: ArchitectureItem
    rec3: ArchitectureItem

# ENUM 정의
class BackupStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"

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

class DatabaseEngine(str, Enum):
    mysql = "mysql"
    pg = "pg"


# 각 Command의 data 스키마 정의
class CreateInstanceData(BaseModel):
    region: str
    plan: str
    label: str
    os_id: int
    backups: BackupStatus
    hostname: str

class UpdateInstanceData(BaseModel):
    id: str
    backups: BackupStatus
    firewall_group_id: str
    os_id: int
    plan: str
    ddos_protection: bool
    label: str

class CreateBlockStorageData(BaseModel):
    region: str
    size_gb: int
    label: str

class UpdateBlockStorageData(BaseModel):
    id: str
    size_gb: int
    label: str
    
class AttachBlockStorageToInstance(BaseModel):
  id: str
  instance_id: str
  live: bool 

class CreateFirewallGroupData(BaseModel):
    description: str

class UpdateFirewallGroupData(BaseModel):
    id: str
    description: str

class CreateFirewallRuleData(BaseModel):
    fire_wall_group_id: str
    ip_type: IpType
    protocol: Protocol
    port: str
    subnet: str
    subnet_size: int
    notes: str

class CreateManagedDatabaseData(BaseModel):
    database_engine: DatabaseEngine
    database_engine_version: int
    region: str
    plan: str
    label: str

class UpdateManagedDatabaseData(BaseModel):
    id: str
    plan: str
    label: str

class CreateObjectStorageData(BaseModel):
    cluster_id: int
    tier_id: int
    label: str

class UpdateObjectStorageData(BaseModel):
    id: str
    label: str

# Discriminated Union으로 command_name 구분
class CreateInstance(BaseModel):
    command_name: Literal["CreateInstance"]
    tmp_id: str
    data: CreateInstanceData

class UpdateInstance(BaseModel):
    command_name: Literal["UpdateInstance"]
    data: UpdateInstanceData

class CreateBlockStorage(BaseModel):
    command_name: Literal["CreateBlockStorage"]
    tmp_id: str
    data: CreateBlockStorageData

class UpdateBlockStorage(BaseModel):
    command_name: Literal["UpdateBlockStorage"]
    data: UpdateBlockStorageData

class AttachBlockStorageToInstance(BaseModel):
    command_name: Literal["AttachBlockStorageToInstance"]
    data: AttachBlockStorageToInstance

class CreateFirewallGroup(BaseModel):
    command_name: Literal["CreateFirewallGroup"]
    tmp_id: str
    data: CreateFirewallGroupData

class UpdateFirewallGroup(BaseModel):
    command_name: Literal["UpdateFirewallGroup"]
    data: UpdateFirewallGroupData

class CreateFirewallRule(BaseModel):
    command_name: Literal["CreateFirewallRule"]
    data: CreateFirewallRuleData

class CreateManagedDatabase(BaseModel):
    command_name: Literal["CreateManagedDatabase"]
    tmp_id: str
    data: CreateManagedDatabaseData

class UpdateManagedDatabase(BaseModel):
    command_name: Literal["UpdateManagedDatabase"]
    data: UpdateManagedDatabaseData

class CreateObjectStorage(BaseModel):
    command_name: Literal["CreateObjectStorage"]
    tmp_id: str
    data: CreateObjectStorageData

class UpdateObjectStorage(BaseModel):
    command_name: Literal["UpdateObjectStorage"]
    data: UpdateObjectStorageData



CommandUnion = Annotated[
    Union[
    CreateInstance,
    UpdateInstance,
    CreateBlockStorage,
    UpdateBlockStorage,
    AttachBlockStorageToInstance,
    CreateFirewallGroup,
    UpdateFirewallGroup,
    CreateFirewallRule,
    CreateManagedDatabase,
    UpdateManagedDatabase,
    CreateObjectStorage,
    UpdateObjectStorage
    ],
    Field(discriminator='command_name')
]


# 최종 요청 스키마
class CommandRequest(BaseModel):
    command_list: List[CommandUnion]
    description: str

class FinalArchitectureResponse(BaseModel):
    rec1: CommandRequest
    rec2: CommandRequest
    rec3: CommandRequest
