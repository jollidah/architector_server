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
- Please refer to EXAMPLE and organize OUTPUT FORMAT
- Choose the location of object storage according to the USER_LOCATION, and if there is no same location, choose the nearest location.
- ObjectStorage and Block Storage are only put in when needed.
- Only one instance can be attached to one block storage.
- resource_type must be used in ResourceType.
- **The every details of the things in TOOL should go in**


We also review the architecture and output a single-line summary evaluation from an instance and architecture perspective.
"The description requires a one-line summary evaluation for each architecture."

**Without additional explanation**


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
  "architecture": [
      {{
        "temp_id": "string",
        "resource_type": ResourceType,
        "position": {{
          "y": 0,
          "x": 0
        }},
        "attributes": {{
          "..."
        }}
      }}
    ],
    "description": "string"
}}

enum ResourceType {{
    BlockStorage,
    Compute,
    ManagedDatabase,
    ObjectStorage,
    FirewallGroup,
    FirewallRule,
}}

TOOL:
BlockStorageAttributes:
{{
    #[serde(skip_deserializing)]
    region_id: str, // e.g."ewr"
    id: str,
    mount_id: str,
    attached_to_instance: str,
    size_gb: int,
    label: str,
}}

-------------------------------
FirewallGroupAttributes:
{{
    id: str
    description: str
}}
-------------------------------
FirewallRuleAttributes:
{{
    id: str
    action: str
    port: str
    ip_type: str
    protocol: str
    subnet: str
    subnet_size: int
    notes: str
}}
-------------------------------
enum IpType {{
    v4,
    v6,
}}
-------------------------------
enum Protocol {{
    icmp,
    tcp,
    udp,
    gre,
    esp,
    ah,
}}
-------------------------------
ComputeAttributes:
{{
    region_id: str
    auto_backups: BackupStatus
    id: str
    plan: str
    status: str
    main_ip: str
    label: str
    os_id: int
    firewall_group_id: str
}}
-------------------------------
enum BackupStatus {{
    enabled,
    disabled,
}}
-------------------------------
ManagedDatabaseAttributes:
{{
    region_id: str
    id: str
    status: str
    plan: str
    database_engine: str
    database_engine_version: int
    latest_backup: str
    label: str
}}
-------------------------------
The version of the chosen database engine type for the Managed Database.
MySQL: 8
PostgreSQL: 16

enum DatabaseEngine {{
    mysql,
    pg,
}}

-------------------------------
ObjectStorageAttributes:
{{
    tier_id: int
    id: str
    cluster_id: int
    label: str
}}

-------------------------------

EXAMPLE:
{{
  "architecture": [
    {{
      "temp_id": "instance-1",
      "resource_type": "Compute",
      "position": {{ "y": 200 , "x": 100 }},
      "attributes": {{
        "region_id": "ewr",
        "auto_backups": "disabled",
        "id": "uuid-instance-1",
        "plan": "voc-g-8c-32gb-160s-amd",
        "status": "active",
        "main_ip": "192.168.1.1",
        "label": "Game Server Instance",
        "os_id": 1743,
        "firewall_group_id": "uuid-firewall-group-1"
      }}
    }},
    {{
      "temp_id": "managed_db-1",
      "resource_type": "ManagedDatabase",
      "position": {{ "y": 200, "x": 300 }},
      "attributes": {{
        "region_id": "ewr",
        "id": "uuid-db-1",
        "status": "active",
        "plan": "vultr-dbaas-premium-occ-so-24-3840-192",
        "database_engine": "mysql",
        "database_engine_version": 8,
        "latest_backup": "2023-03-15",
        "label": "Game Database"
      }}
    }},
    {{
      "temp_id": "object_storage-1",
      "resource_type": "ObjectStorage",
      "position": {{ "y": 100, "x": 200 }},
      "attributes": {{
        "tier_id": 5,
        "id": "uuid-object-storage-1",
        "cluster_id": 9,
        "label": "Game Assets Storage",
      }}
    }},
    {{
      "temp_id": "block_storage-1",
      "resource_type": "BlockStorage",
      "position": {{ "y": 250, "x": 250 }},
      "attributes": {{
        "region_id": "ewr",
        "mount_id": "uuid-mount-1",
        "attached_to_instance": "uuid-instance-1",
        "size_gb": 100,
        "id": "uuid-block-storage-1",
        "label": "Game Block Storage",
      }}
    }},
    {{
      "temp_id": "firewall_group-1",
      "resource_type": "FirewallGroup",
      "position": {{ "y": 250, "x": 50 }},
      "attributes": {{
        "id": "uuid-firewall-group-1",
        "description": "Firewall for Game Services"
      }}
    }},
    {{
      "temp_id": "firewall_rule-1",
      "resource_type": "FirewallRule",
      "position": {{ "y": 275, "x": 75 }},
      "attributes": {{
        "action": "allow",
        "port": "80",
        "ip_type": "ipv4",
        "protocol": "tcp",
        "subnet": "192.168.1.0",
        "subnet_size": 24,
        "notes": "Allow HTTP traffic"
      }}
    }}
  ],
  "description": "The architecture provides a high-performance compute instance for real-time game processing, a managed database for storage needs, and object storage in the nearest available region. A dedicated firewall group enhances security."
}}


Helpful Answer:
""")



