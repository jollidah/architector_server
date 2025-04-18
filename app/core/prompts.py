from langchain_core.prompts import PromptTemplate

# Prompt 1: 스펙 추천
SPEC_RECOMMEND_PROMPT = PromptTemplate.from_template("""
You are a cloud computing expert who looks at the USER_INPUT below and lets me know the recommended specifications in Vultr and software architecture diagram.
Please provide the specifications suitable for USER_INPUT in JSON format. And provide software architecture diagram in JSON format, too.
Specifically:
- "GPU type" should include the **exact GPU model and VRAM size**
- If "GPU" is "No", fill "GPU type" with NaN
- "Memory" should specify the size with units
- "Storage" should specify both size in GB and type if possible
- "Bandwidth" must be expressed strictly in TB/mo
- Do not use vague words like "high-performance" or "powerful"
- Do not include any additional explanations—only return the JSON object
- Add to the software architecture diagram if the user needs additional services in addition to what is in the FORMAT
- If there is anything you don't need in software architecture diagram, please let me know except
- If there's a service that's excluded, don't put an empty list, just take it out of the printout
- If the user has to enter something unconditionally, fill it in with -1. For example, os_id

- Choose best database engine version from the following supported options:
  - **PostgreSQL**: `"17"`, `"16"`, `"15"`, `"14"`, `"13"`
  - **MySQL**: `"8.0"`
  - **Valkey**: `"7"`
  - **Kafka**: `"3.9"`, `"3.8"`

USER_INPUT:
{user_input}

FORMAT:
{{
    "Processor / vCPU": "...",
    "GPU": "Yes/No",
    "GPU type": "...",
    "Memory": "...",
    "Storage": "...",
    "Bandwidth": "..."
}}

{{
  "version": "1.0",
  "environment": "...",
  "resources": {{
    "vultr_instance": [
      {{
        "plan": "Any",
        "region": "..."
        "os_id": -1,
        "label": "my-web-server",
        "ssh_key_ids": ["ssh-key-id"],
        "tags": ["web", "my-project"],
        "vpc_id": "my-vpc"
      }}
    ],
    "vultr_vpc": [
      {{
        "region": "...",
        "label": "my-vpc",
        "v4_subnet": "-1.-1.-1.-1",
        "v4_subnet_mask": -1
      }}
    ],
    "vultr_object_storage": [
      {{
        "cluster_id": -1,
        "region": "Amsterdam/New Jersey/ Silicon Valley/ Singapore"
        "label": "my-object-storage"
      }}
    ],
    "vultr_block_storage": [
      {{
        "region": "...",
        "size_gb": "...",
        "label": "my-block-storage",
        "attached_to_instance": "my-web-server"
      }}
    ],
    "vultr_database": [
      {{
        "database_engine": "mysql/pg/valkey/kafka",
        "database_engine_version": "...",
        "region": "...",
        "plan": "vultr-dbaas-startup",
        "label": "my-database",
        "trusted_ips": ["0.0.0.0/0"],
        "vpc_id": "my-vpc"
      }}
    ]
  }},
  "connections": [
    {{
      "from_": "my-web-server",
      "to": "my-database",
      "type": "postgresql",
    }},
    {{
      "from_": "my-web-server",
      "to": "my-object-storage",
      "type": "object-storage",
    }},
    {{
      "from_": "my-web-server",
      "to": "my-block-storage",
      "type": "block-storage",
    }},
  ]
}}

Helpful Answer:
""")

# Prompt 2: 인스턴스 이름 매칭
INSTANCE_MATCH_PROMPT =PromptTemplate.from_template("""
You are a cloud computing professional who looks at LLM1_RESPONSE and CONTEXT below and tells me the Vultr instance name that fits this specification.
And show me architecture diagram, too.
Based on the `LLM1_RESPONSE` below, provide the appropriate Vultr instance name in JSON format. And provide software architecture diagram in JSON format, too.
If user need additional service, please recommand Vultr service name.
Do not include any additional explanations or content—output only the JSON response.
If GPU is Yes, please recommend a GPU type similar to the performance of the GPU type that comes in as input
Please refer to the instance, db_region, and storage_region and recommend the region of the instance accordingly

CONTEXT:
{context}

### Output Format:
{{
    "Instance_name": "..."
    "Region": "..."
}}


Helpful Answer:
""")

# Prompt 3: terraform code
TERRAFORM_GEN_PROMPT = PromptTemplate.from_template(
    """You are an expert DevOps engineer.

Convert the following architecture JSON into a valid Terraform code using the Vultr provider.

Architecture JSON:
{arch_json}

Return only the Terraform code, without explanation or markdown formatting.
If there's -1, return to -1
"""
)