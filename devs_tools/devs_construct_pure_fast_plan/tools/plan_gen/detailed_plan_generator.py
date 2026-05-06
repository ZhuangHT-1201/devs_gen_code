from typing import Optional, Literal
import json
import re
import time
import litellm
from litellm import completion
from pydantic import BaseModel, Field

litellm.drop_params = True

from ...base_types import (
    GlobalPlanNode, DetailedPlan, SimpleDetailedPlan,
    ModelSpecification, TypedEntity, PortEntity, ProtocolSpec
)
from ...utils import get_content_strict, extract_json
from ...wrapped_completion import completion_with_logging


# ====== Raw LLM response schemas (String formats for prompts) ======
_RAW_ATOMIC_SCHEMA = """{
  "class_name": "ModelName",
  "model_type": "atomic",
  "function": "pure responsibility, state machine, event handling, and timing.",
  "logging": "ALL logging/output requirements: event names, payload key names & types, format, timing",
  "model_init_args": [{"name": "name of the arg", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}."}, ...],
  "input_ports": [{"name": "name of the port", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}.", "protocol": {"initial_state": "...", "initial_signal": "...", "description": "..."}}, ...],
  "output_ports": [{"name": "name of the port", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}.", "protocol": {"initial_state": "...", "initial_signal": "...", "description": "..."}}, ...]
}"""

_RAW_COUPLED_SCHEMA = """{
  "class_name": "ModelName",
  "model_type": "coupled",
  "function": "overall purpose and capability of this entire subsystem as a whole. No active routing logic inside the coupled wrapper itself.",
  "coupling_specification": "describe EIC/IC/EOC. Must specify model_name.IN/OUT.port_name.",
  "model_init_args": [{"name": "name of the arg", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}."}, ...],
  "input_ports": [{"name": "name of the port", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}.", "protocol": {"initial_state": "...", "initial_signal": "...", "description": "..."}}, ...],
  "output_ports": [{"name": "name of the port", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}.", "protocol": {"initial_state": "...", "initial_signal": "...", "description": "..."}}, ...]
}"""

_RAW_SIMPLE_SCHEMA = """{
  "class_name": "ModelName",
  "model_type": "atomic" or "coupled",
  "function": "1-2 sentences responsibility",
  "logging": "1-2 sentences",
  "model_init_args": [{"name": "name of the arg", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}."}, ...],
  "input_ports": [{"name": "name of the port", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}.", "protocol": {"initial_state": "...", "initial_signal": "...", "description": "..."}}, ...],
  "output_ports": [{"name": "name of the port", "type": "int/str/float/dict/list/...", "structure": "Description. IF dict/list, MUST use strict code format like {'key': type}.", "protocol": {"initial_state": "...", "initial_signal": "...", "description": "..."}}, ...]
}"""


def _build_prompt(
    target_name: str,
    requirements: str,
    global_plan_str: str,
    children_names_str: str,
    parent_simple_str: str,
    parent_detail_str: str,
    is_root: bool,
    is_coupled: bool,
) -> str:
    """Build the dynamic prompt based on module type."""

    if is_root:
        context = "Root model, keep the input/output ports minimal."
        inherent = f"""
- **model_init_args**: get essential args.
- **input_ports / output_ports**: keep ports minimal, only contain the required function.
""".strip()
    else:
        context = f"""
**Model's Simple Plan** (this model's initial interface from parent):
{parent_simple_str}

**Parent's Detailed Plan** (system context):
{parent_detail_str}
""".strip()
        inherent = f"""
- **model_init_args**: inherit from Parent's Simple Plan.
- **input_ports / output_ports**: inherit from Parent's Simple Plan.
""".strip()
    
    if is_coupled:
        instruction = f"""
## [Task]
Generate a detailed specification for the COUPLED module `{target_name}` and simple specifications for its direct children ({children_names_str}).

### STEP 1: Design Coupled Wrapper (`detailed_plan`)
- **function**: Describe the overall purpose and capability of this entire subsystem as a unified whole. While the coupled wrapper itself only contains structural connections (no active routing/state logic), this field should summarize what the encapsulated subsystem achieves.
{inherent}

### STEP 2: Design Children (`children_plans`)
- **function**: 1-2 sentences.
- **logging**: 1-2 sentences, mention what logging items should be covered in the model.
- **model_init_args**: full args (name/type/structure); always start with name (str) and parent (Coupled | None); 
- **input_ports / output_ports**: full port definitions for sibling and parent matching. MUST make sure the structures of ports match strictly, and the name aligned with the coupling_specification.
Children with children in the global plan -> `coupled`; leaf children -> `atomic`.

### STEP 3: Design coupling_specification:
- MUST define the network routing here. It's ONLY allowed to use these 3 strict DEVS connection patterns. List them clearly line-by-line:
    1. **EIC (External Input Coupling)**: Routing external data IN to a child. Format: `parent.IN.port_name -> child.IN.port_name`
    2. **IC (Internal Coupling)**: Data flowing between siblings. Format: `child_A.OUT.port_name -> child_B.IN.port_name`
    3. **EOC (External Output Coupling)**: Routing child results OUT to the parent. Format: `child.OUT.port_name -> parent.OUT.port_name`
- **CRITICAL COUPLING RULES**:
    1. **NO HALLUCINATIONS**: Every port name you use MUST EXACTLY MATCH either the Parent's inherited ports or the Children's ports you defined in STEP 1. DO NOT invent ports.
    2. **NOT ALL PORTS NEED PARENT CONNECTIONS**: Children can communicate entirely with each other via IC. Do NOT force an EIC for a child's input if it should be driven by a sibling. Some ports may remain uncoupled.
"""
        output_format = f"""
## [Output Format]
Return ONLY a JSON object with exactly THREE keys: `detailed_plan`, `children_plans`, and `coupling_specification`.
- `detailed_plan` has the structure: {_RAW_COUPLED_SCHEMA}
- `children_plans` is a list of: {_RAW_SIMPLE_SCHEMA}
- `coupling_specification` is a string
"""
    else:
        instruction = f"""
## [Task]
Generate a detailed specification for the ATOMIC module `{target_name}`.

### For the detailed ATOMIC `{target_name}` plan:
- **function**: pure responsibility, state machine, event handling, timing. Do NOT describe logging here.
- **logging**: Extract ALL logging/output requirements from the original requirements that apply to this model. Include payload structure, format, and timing.
- **model_init_args**: copy from Model's Simple Plan.
- **input_ports / output_ports**: copy from Model's Simple Plan.
"""
        output_format = f"""
## [Output Format]
Return ONLY a JSON object matching this exact structure:
{_RAW_ATOMIC_SCHEMA}
"""

    return f"""
## [Role]
You are a **DEVS System Architect**. 

## [Input]
**Target Module**: {target_name}
**Children in Global Plan**: {children_names_str}
**Original Requirements**:
{requirements}

**Global Plan Overview** (full module hierarchy):
{global_plan_str}

{context}

{instruction.strip()}

## [Field Guidance]
- For ANY `model_init_args`, `input_ports`, or `output_ports` that use `dict` or `list` types, you MUST use a strict **Python Dict/List representation** to define the structure.
- **Strict Format Examples**:
    - BAD (Vague Summary): "Information about the sent packet including sequence number and retry flag."
    - BAD (Vague List): "A list of jobs."
    - GOOD (Strict Dict): "Packet info. Format: {{'sequence_number': int, 'control_bit': str, 'is_retry': bool}}."
    - GOOD (Strict List): "List of jobs. Format: [{{'job_id': int, 'priority': float}}]."
    - GOOD (Nested): "Format: {{'metadata': {{'timestamp': float, 'source': str}}, 'payload': list[int]}}."
- Types allowed: int, float, bool, str, dict, list. 
- Port protocol: Must include initial_state (state at T=0), initial_signal (signal at startup), description.
""".strip() + "\n" + output_format.strip()

# ====== Pydantic raw response models ======

class _RawAtomicDetailed(BaseModel):
    class_name: str = Field(description="Name of the atomic model class.")
    model_type: Literal["atomic"] = Field(description="Must be 'atomic'.")
    function: str = Field(description="Pure responsibility, state machine, event handling, and timing.")
    logging: str = Field(description="ALL logging details — event names, payload keys/types, format, timing.")
    model_init_args: list[TypedEntity] = Field(default_factory=list)
    input_ports: list[PortEntity] = Field(default_factory=list)
    output_ports: list[PortEntity] = Field(default_factory=list)

class _RawCoupledDetailed(BaseModel):
    class_name: str = Field(description="Name of the coupled model class.")
    model_type: Literal["coupled"] = Field(description="Must be 'coupled'.")
    function: str = Field(description="Overall purpose and capability of this entire subsystem as a whole. No active routing logic inside the coupled wrapper itself.")
    model_init_args: list[TypedEntity] = Field(default_factory=list)
    input_ports: list[PortEntity] = Field(default_factory=list)
    output_ports: list[PortEntity] = Field(default_factory=list)

class _RawSimple(BaseModel):
    class_name: str = Field(description="Name of the model class.")
    model_type: Literal["atomic", "coupled"] = Field(description="Children with children -> 'coupled'; leaf -> 'atomic'.")
    function: str = Field(description="1-2 sentences describing responsibility.")
    logging: str = Field(description="ALL logging details.")
    model_init_args: list[TypedEntity] = Field(default_factory=list)
    input_ports: list[PortEntity] = Field(default_factory=list)
    output_ports: list[PortEntity] = Field(default_factory=list)

# Distinct Response Envelopes
class _RawCoupledResponse(BaseModel):
    detailed_plan: _RawCoupledDetailed = Field(description="Detailed specification for the coupled module.")
    children_plans: list[_RawSimple] = Field(default_factory=list, description="Simple specifications for direct children.")
    coupling_specification: str = Field(description="Describe EIC/IC/EOC clearly.")


class PlanGenResult:
    def __init__(self, detailed_plan: DetailedPlan, children_plans: list[SimpleDetailedPlan]):
        self.detailed_plan = detailed_plan
        self.children_plans = children_plans


def _make_detailed_atomic(raw: _RawAtomicDetailed) -> DetailedPlan:
    return DetailedPlan(
        class_name=raw.class_name,
        model_type="atomic",
        specification=ModelSpecification(
            function=raw.function,
            logging=raw.logging,
            model_init_args=raw.model_init_args,
            input_ports=raw.input_ports,
            output_ports=raw.output_ports,
        ),
        coupling_specification=None,  # Forced None for atomic
    )

def _make_detailed_coupled(raw: _RawCoupledDetailed, coupling: str) -> DetailedPlan:
    return DetailedPlan(
        class_name=raw.class_name,
        model_type="coupled",
        specification=ModelSpecification(
            function=raw.function,
            logging="",  # Forced empty string for coupled
            model_init_args=raw.model_init_args,
            input_ports=raw.input_ports,
            output_ports=raw.output_ports,
        ),
        coupling_specification=coupling,
    )

def _make_simple(raw: _RawSimple) -> SimpleDetailedPlan:
    return SimpleDetailedPlan(
        class_name=raw.class_name,
        model_type=raw.model_type if raw.model_type in ("atomic", "coupled") else "atomic",
        function=raw.function,
        logging=raw.logging,
        model_init_args=raw.model_init_args,
        input_ports=raw.input_ports,
        output_ports=raw.output_ports,
    )

# ====== Generator ======

class DetailedPlanGenerator:
    """Single method: generate detailed plan for a model + simple plans for its children."""

    def __init__(self, model_id: dict[str, str], disable_check: bool = True):
        self.model_id = model_id
        self.disable_check = disable_check

    def _get_model(self) -> str:
        if isinstance(self.model_id, dict):
            return self.model_id.get('strong', self.model_id.get('default', ''))
        return self.model_id

    def _fmt_global(self, plan: list[GlobalPlanNode]) -> str:
        lines = []
        for n in plan:
            ci = f" -> children: {', '.join(n.children_names)}" if n.children_names else " -> (atomic)"
            lines.append(f"- {n.name}: {n.description}{ci}")
        return "\n".join(lines)

    def _fmt_simple(self, plan: SimpleDetailedPlan) -> str:
        parts = [
            f"class_name: {plan.class_name}",
            f"model_type: {plan.model_type}",
            f"function: {plan.function}",
            f"logging: {plan.logging}",
        ]
        if plan.model_init_args:
            parts.append("model_init_args: " + ", ".join(f"{a.name} ({a.type}): {a.structure}" for a in plan.model_init_args))
        if plan.input_ports:
            parts.append("input_ports: " + ", ".join(f"{p.name} ({p.type}): {p.structure}" for p in plan.input_ports))
        if plan.output_ports:
            parts.append("output_ports: " + ", ".join(f"{p.name} ({p.type}): {p.structure}" for p in plan.output_ports))
        return "\n".join(parts)

    def _fmt_detailed(self, plan: DetailedPlan) -> str:
        s = plan.specification
        parts = [
            f"class_name: {plan.class_name}",
            f"model_type: {plan.model_type}",
            f"function: {s.function[:300]}",
            f"logging: {s.logging[:300]}",
            f"coupling_specification: {plan.coupling_specification or 'null'}",
        ]
        if s.input_ports:
            parts.append("input_ports: " + ", ".join(f"{p.name} ({p.type}): {p.structure}" for p in s.input_ports))
        if s.output_ports:
            parts.append("output_ports: " + ", ".join(f"{p.name} ({p.type}): {p.structure}" for p in s.output_ports))
        return "\n".join(parts)

    def generate(
        self,
        target_name: str,
        requirements: str,
        global_plan: list[GlobalPlanNode],
        children_names: list[str],
        parent_simple_plan: Optional[SimpleDetailedPlan] = None,
        parent_detailed_plan: Optional[DetailedPlan] = None,
        retry: int = 3,
    ) -> PlanGenResult:
        is_root = parent_simple_plan is None
        is_coupled = len(children_names) > 0  # 动态判断节点类型

        gstr = self._fmt_global(global_plan)
        cstr = ", ".join(children_names) if children_names else "None (leaf)"
        pstr = self._fmt_simple(parent_simple_plan) if parent_simple_plan else "(N/A - root)"
        dstr = self._fmt_detailed(parent_detailed_plan) if parent_detailed_plan else "(N/A - root)"

        model = self._get_model()

        # 根据类型动态选择 ResponseFormat
        # 注意：Atomic 模式下直接使用 _RawAtomicDetailed，不再包额外的一层 response wrapper
        ResponseModel = _RawCoupledResponse if is_coupled else _RawAtomicDetailed

        for attempt in range(retry):
            try:
                prompt = _build_prompt(
                    target_name=target_name,
                    requirements=requirements,
                    global_plan_str=gstr,
                    children_names_str=cstr,
                    parent_simple_str=pstr,
                    parent_detail_str=dstr,
                    is_root=is_root,
                    is_coupled=is_coupled, # 将类型传入，用于隔离 Prompt
                )
                
                resp = completion_with_logging(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    phase=f"phase1b_detailed_plan_{'coupled' if is_coupled else 'atomic'}",
                    target=target_name,
                    attempt=attempt,
                    temperature=0.5,
                    response_format=ResponseModel, # 动态传入精确 Schema
                )
                
                raw = extract_json(get_content_strict(resp))
                parsed = ResponseModel.model_validate(raw)

                if is_coupled:
                    assert isinstance(parsed, _RawCoupledResponse)
                    det = _make_detailed_coupled(parsed.detailed_plan, parsed.coupling_specification)
                    chs = [_make_simple(c) for c in getattr(parsed, "children_plans", [])]
                else:
                    # 对于 Atomic, 解析出来的 parsed 直接就是 detailed_plan 的主体
                    assert isinstance(parsed, _RawAtomicDetailed)
                    det = _make_detailed_atomic(parsed)
                    chs = [] # Atomic 永远返回空子节点列表

                if det.class_name != target_name:
                    raise ValueError(f"Expected '{target_name}', got '{det.class_name}'")
                
                if is_coupled and children_names:
                    got = {c.class_name for c in chs}
                    for cn in children_names:
                        if cn not in got:
                            raise ValueError(f"Child '{cn}' missing")

                print(f"[DetailedPlan] {target_name}: type={det.model_type}, children={len(chs)}")
                return PlanGenResult(detailed_plan=det, children_plans=chs)

            except Exception as e:
                es = str(e)
                if "rate" in es.lower() or "429" in es:
                    wait = 10 * (attempt + 1)
                    print(f"[DetailedPlan] Rate limited, waiting {wait}s...")
                    time.sleep(wait)
                print(f"[DetailedPlan] Attempt {attempt + 1} failed for '{target_name}': {e}")
                if attempt < retry - 1:
                    time.sleep(2)

        raise Exception(f"Failed to generate plan for '{target_name}' after {retry} attempts")