from langchain_core.prompts import PromptTemplate

# Prompt 1: 스펙 추천
SPEC_RECOMMEND_PROMPT = PromptTemplate.from_template("""
You are a cloud computing expert who looks at the USER_INPUT below and tells you the recommended instance specifications ,the number of DBs and object storage specifications in Vultr, as well as DB specifications.
Please provide the specifications suitable for USER_INPUT in JSON format.
- "ram" must be all size MB, but it does not write MB.
- "storage_size" should be all size in GB, but GB is not written.
- "bandwidth" should be strictly expressed in GB/mo, but GB/mo is not written.
- Do not use vague words like "high-performance" or "powerful"
- Do not include any additional explanations—only return the JSON object
- In USER_INPUT, look at the instance_requirements list and print out the instance specification as many as the list elements
- Please recommend the number of DBs and let me know the specifications for that number.
- **Make sure to print it out as JSON.**
- **Instance_specifications, db_specification and object_storage_specificatoin are divided into different json blocks.**
  
- Choose best storage type from following supported options:
  - SSD
  - HIGHFREQUENCY
  - AMDHIGHPERF
  - INTELHIGHPERF
  - DEDICATEDOPTIMIZED

USER_INPUT:
{user_input}

### OUTPUT_FORMAT:
```json
{{
    "vcpu_count": "...",
    "ram": "...",
    "storage_size": "...",
    "bandwidth": "...",
    "storage_type": "..."
}}
```
```json
{{
    "numbers_of_db": "...",
    " db_spec1": {{
        "vcpu_count": "...",
        "ram": "...",
        "storage_size": "...",
        "numbers_of_node": "..."
      }},
      "..."
}}
```
```json
{{
  "ratelimit_ops_secs": 
  "ratelimit_ops_bytes":
}}
```

Helpful Answer:
""")

# Prompt 2: 인스턴스 이름 매칭
INSTANCE_MATCH_PROMPT =PromptTemplate.from_template("""
You are a cloud computing professional who looks at LLM1_RESPONSE and CONTEXT below and tells me the Vultr instance id that fits this specification.
Based on the `LLM1_RESPONSE` below, provide the appropriate Vultr instance id in JSON format.
Do not include any additional explanations or content—output only the JSON response.
Look at the specifications and print out the instance id. You have to print it according to those specifications.
Recommend the top 3 instances of the below context as JSON.

CONTEXT:
{context}

### Output Format:
{{
  "Recommended_Instances": [
    {{"Instance_plan": "..."}},
    {{"Instance_plan": "..."}},
    {{"Instance_plan": "..."}}
  ]
}}

Helpful Answer:
""")

DB_MATCH_PROMPT =PromptTemplate.from_template("""
You are a cloud computing professional You are a cloud computing professional who looks at LLM1_RESPONSE and CONTEXT below and tells me the Vultr database id that fits this specification.
Based on the `LLM1_RESPONSE` below, provide the appropriate Vultr database id in JSON format.
Do not include any additional explanations or content—output only the JSON response.
Look at the specifications and print out the database id. You have to print it according to those specifications.
Recommend the top 3 instances of the below context as JSON.

CONTEXT:
{context}

### Output Format:
{{"DB_plan": "..."}},


Helpful Answer:
""")

ARCH_PROMPT = PromptTemplate.from_template("""
You are a cloud computing expert who looks at the USER_INPUT and LLM2_RESULT below and tells you the recommended software architecture diagrams.Please provide software architecture diagram in JSON format.
Specifically:
- If there is anything you don't need in software architecture diagram, please let me know except
- If there's a service that's excluded, don't put an empty list, just take it out of the printout
- Please fix os_id to 1743
- I will configure the firewall to act as a vpc instead of a vpc.
- **Add as many DBs, object storages, and block storages as I need.**
- **The architecture in FORMAT is just an example.**
- **Use the TOOL below to configure OUTPUT FORMAT**
- Please create as many object_storage and block_storage as you need. It doesn't have to be there, and if you don't need it, you don't have to create it.
- Instances that enter a firewall group must perform UpdateInstance at the end. You don't have to do any instances that don't have to go into the firewall.
- command_list must have command_name, tmp_id, data
- Please refer to EXAMPLE and organize OUTPUT FORMAT
- command_name uses the command_name in the TOOL below
- **Add tmp_id only to the command_name "CreateInstance", "CreateBlockStorage", "CreateFirewallGroup", "CreateManagedDatabase", and "CreateObjectStorage". Must have tmp_id.**.
- If object_storage is required, view OBJECT_STORAGE_SPEC and fill "CreateObjectStorage".
- Choose the location of object storage according to the USER_LOCATION, and if there is no same location, choose the nearest location.
- ObjectStorage and Block Storage are only put in when needed.
- Only one instance can be attached to one block storage.

We also review the architecture and output a single-line summary evaluation from an instance and architecture perspective.
"The description requires a one-line summary evaluation for each architecture."


OBJECT_STORAGE_SPEC:
{object_storage_spec}

USER_INPUT:
{user_input}

USER_LOCATION:
{user_location}

LLM2_RESULT:
{llm2_result}

OUTPUT FORMAT:
{{
    "command_list": [
        {{
            "command_name": "...",
            "temp_id": "...",
            "data": {{
            }}
        }}
    ],
    "description": "..."
}}

TOOL:
command_name: CreateInstance
data: {{
    region: String,
    plan: String,
    label: String,
    os_id: i64,
    backups: BackupStatus,
    hostname: String
}}
enum BackupStatus {{
    enabled,
    disabled
}}
-----------------------------
command_name: UpdateInstance
data: {{
    id: tmp_id,
    backups: BackupStatus,
    firewall_group_id: String,
    os_id: i64,
    plan: String,
    ddos_protection: bool,
    label: String
}}
-----------------------------
command_name: CreateBlockStorage
data: {{
    region: String,
    size_gb: i64, // New size of the Block Storage in GB. Size may range between 10 and 40000 depending on the block_type
    label: String
}}
-----------------------------
command_name: UpdateBlockStorage
data: {{
    id: tmp_id,
    size_gb: i64, // New size of the Block Storage in GB. Size may range between 10 and 40000 depending on the block_type
    label: String
}}
-----------------------------
command_name: AttachBlockStorageToInstance
data: {{
  id: tmp_id
  instance_id: tmp_id
  live: bool 
}}
What 'live: true' means is that it does not restart instance.
-----------------------------
command_name: CreateFirewallGroup
data: {{
    description: String
}}
-----------------------------
command_name: UpdateFirewallGroup
data: {{
    id: tmp_id,
    description: String
}}
-----------------------------
command_name: CreateFirewallRule
data: {{
    fire_wall_group_id: tmp_id,
    ip_type: IpType,
    protocol: Protocol,
    port: String,
    subnet: String,     // e.g. "192.0.2.0"
    subnet_size: i64,
    notes: String
}}
enum IpType {{
    v4,
    v6
}}
enum Protocol {{
    icmp,
    tcp,
    udp,
    gre,
    esp,
    ah
}}
-----------------------------
command_name: CreateManagedDatabase
data: {{
    database_engine: DatabaseEngine,
    database_engine_version: i64,
    region: String,
    plan: String,
    label: String
}}
enum DatabaseEngine {{
    mysql,
    pg
}}
The version of the chosen database engine type for the Managed Database.
MySQL: 8
PostgreSQL: 16
-----------------------------
command_name: UpdateManagedDatabase
data: {{
    id: tmp_id,
    plan: String,
    label: String
}}
-----------------------------
command_name: CreateObjectStorage
data: {{
    cluster_id: i64,
    tier_id: i64,
    label: String
}}
-----------------------------
command_name: UpdateObjectStorage
data: {{
    id: tmp_id,
    label: String
}}

Example:
    "command_list": [
      {{
        "command_name": "CreateInstance",
        "tmp_id": instnace1,
        "data": {{
          "region": "ewr",
          "plan": "voc-c-4c-8gb-75s-amd",
          "label": "game-server-1",
          "os_id": 1743,,
          "backups": "disabled",
          "hostname": "game1"
        }}
      }},
      {{
        "command_name": "CreateManagedDatabase",
        "tmp_id": db1,
        "data": {{
          "database_engine": "pg",
          "database_engine_version": 17,
          "region": "ewr",
          "plan": "vultr-dbaas-startup-cc-hp-intel-2-128-4",
          "label": "game-db-1"
        }}
      }},
      {{
        "command_name": "CreateBlockStorage",
        "tmp_id": blockstorage1
        "data": {{
          "region": "ewr",
          "size_gb": 1000,
          "label": "game-storage-1"
        }}
      }},
      {{
        "command_name": "AttachBlockStorageToInstance",
        "data": {{
          "id": tmp_id,
          "instance_id": tmp_id,
          "live": true
        }}
      }},
      {{
        "command_name": "CreateObjectStorage",
        "tmp_id": objectstorage11
        "data": {{
          "cluster_id": 1,
          "tier_id": 1,
          "label": "game-object-storage-1"
        }}
      }},
      {{
        "command_name": "CreateFirewallGroup",
        "tmp_id": firewall1
        "data": {{
          "description": "Game Server Firewall"
        }}
      }},
      {{
        "command_name": "CreateFirewallRule",
        "data": {{
          "fire_wall_group_id": tmp_id,
          "ip_type": "v4",
          "protocol": "tcp",
          "port": "80",
          "subnet": "192.168.0.0",
          "subnet_size": 24,
          "notes": "Allow HTTP traffic"
        }}
      }},
      {{
        "command_name": "CreateFirewallRule",
        "data": {{
          "fire_wall_group_id": tmp_id,
          "ip_type": "v4",
          "protocol": "tcp",
          "port": "443",
          "subnet": "192.168.0.0",
          "subnet_size": 24,
          "notes": "Allow HTTPS traffic"
        }}
      }},
      {{
        "command_name": "UpdateInstance",
        "data": {{
          "id": tmp_id,
          "backups": "...",
          "firewall_group_id": tmp_id,
          "os_id": 1743,
          "plan": "voc-c-4c-8gb-75s-amd",
          "ddos_protection": true,
          "label": "game-server-1"
        }}
      }}
    ]
  }}


Helpful Answer:
""")



