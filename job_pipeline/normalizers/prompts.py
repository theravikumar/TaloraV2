# job_pipeline/normalizers/prompts.py
"""
LLM prompts for job normalization.
"""

JOB_NORMALIZATION_PROMPT = """You are a job description normalization system.

Your task is to extract structured information from the job description text below
and output it in the EXACT schema provided.

IMPORTANT RULES:
- Extract ONLY what is explicitly stated in the JD
- Do NOT invent requirements or preferences
- Distinguish between REQUIRED (must-have) and PREFERRED (nice-to-have) expectations
- Each expectation should describe ONE coherent requirement
- Break down complex requirements into multiple work units
- Use the candidate's/JD's original wording where possible
- If constraints (scale, performance, etc.) are NOT mentioned, use empty list []
- Confidence: "explicit" if directly stated, "implicit" if inferred from context
- Output ONLY valid JSON. No explanations. No comments.

Schema:
{{
  "role": string | null,
  "domain": string | null,
  "required_expectations": [
    {{
      "priority": "required",
      "confidence": "explicit" | "implicit",
      "work_units": [
        {{
          "type": "requirement",
          "action": string,
          "object": string,
          "tools": string[],
          "constraints": string[],
          "outcome": null
        }}
      ]
    }}
  ],
  "preferred_expectations": [
    {{
      "priority": "preferred",
      "confidence": "explicit" | "implicit",
      "work_units": [
        {{
          "type": "requirement",
          "action": string,
          "object": string,
          "tools": string[],
          "constraints": string[],
          "outcome": null
        }}
      ]
    }}
  ]
}}

Examples:

JD Text: "5+ years building scalable backend APIs using Python (Django/FastAPI). Experience with PostgreSQL required. Knowledge of Redis preferred."

Output:
{{
  "role": "Backend Engineer",
  "domain": "backend",
  "required_expectations": [
    {{
      "priority": "required",
      "confidence": "explicit",
      "work_units": [
        {{
          "type": "requirement",
          "action": "Build",
          "object": "scalable backend APIs",
          "tools": ["Python", "Django", "FastAPI"],
          "constraints": ["scalable", "5+ years experience"],
          "outcome": null
        }},
        {{
          "type": "requirement",
          "action": "Use",
          "object": "database",
          "tools": ["PostgreSQL"],
          "constraints": [],
          "outcome": null
        }}
      ]
    }}
  ],
  "preferred_expectations": [
    {{
      "priority": "preferred",
      "confidence": "explicit",
      "work_units": [
        {{
          "type": "requirement",
          "action": "Use",
          "object": "caching",
          "tools": ["Redis"],
          "constraints": [],
          "outcome": null
        }}
      ]
    }}
  ]
}}

Job Description Text:
<<<
{jd_text}
>>>
"""


HTML_CLEANING_SYSTEM_PROMPT = """You are an HTML to clean text converter.
Extract ONLY the actual job description content.
Remove:
- Navigation menus
- Footers
- Advertisements
- Social media buttons
- Unrelated text

Return ONLY the cleaned job description text. No JSON, no formatting."""
