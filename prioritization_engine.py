from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields as dataclass_fields
from math import inf
from typing import Any, Dict, List, Optional, Tuple
import re


PRIORITY_LEVELS = ("P1", "P2", "P3", "P4", "P5", "P6")
PRIORITY_TO_NUM = {p: i + 1 for i, p in enumerate(PRIORITY_LEVELS)}
NUM_TO_PRIORITY = {i + 1: p for i, p in enumerate(PRIORITY_LEVELS)}

CLIENT_CLASSES = ("C1", "C2", "C3", "C4")
CLIENT_CLASS_TO_NUM = {c: i + 1 for i, c in enumerate(CLIENT_CLASSES)}
NUM_TO_CLIENT_CLASS = {i + 1: c for i, c in enumerate(CLIENT_CLASSES)}

ALARM_LEVELS = {"blocking", "reliability", "minor"}

# Lower number = higher priority
PM_TYPE_RANK = {
    "quinquennial": 1,
    "monthly": 2,
    "annual_csa": 3,
    "annual": 4,
    "full_inspection": 5,
    "generator_inspection": 6,
}

PM_TYPE_ALIASES = {
    "quinquennial": "quinquennial",
    "annual_csa": "annual_csa",
    "annualcsa": "annual_csa",
    "monthly": "monthly",
    "annual": "annual",
    "full_inspection": "full_inspection",
    "fullinspection": "full_inspection",
    "generator_inspection": "generator_inspection",
    "generatorinspection": "generator_inspection",
    "ats": "quinquennial",
    "ats_inverter": "quinquennial",
    "inverter": "quinquennial",
}

ALARM_ALIASES = {
    "blocking": "blocking",
    "blocking_alarm": "blocking",
    "block": "blocking",
    "blocked": "blocking",
    "shutdown": "blocking",
    "shutdown_active": "blocking",
    "ats_fault": "blocking",
    "ats_failure": "blocking",
    "start_failure": "blocking",
    "start_failure_alarm": "blocking",
    "start_alarm": "blocking",
    "won_t_start": "blocking",
    "cannot_start": "blocking",
    "unit_down": "blocking",
    "unit_unavailable": "blocking",
    "reliability": "reliability",
    "reliability_alarm": "reliability",
    "battery_charger_fault": "reliability",
    "battery_low": "reliability",
    "low_fuel": "reliability",
    "fuel_low": "reliability",
    "block_heater_fault": "reliability",
    "heater_fault": "reliability",
    "fuel_leak": "reliability",
    "leak": "reliability",
    "minor": "minor",
    "minor_alarm": "minor",
    "warning": "minor",
    "sensor_fault": "minor",
    "sensor_failure": "minor",
    "indicator_light": "minor",
    "maintenance_reminder": "minor",
    "lamp_témoin": "minor",
}

FIELD_ALIASES = {
    "customerClass": "customer_class",
    "clientRank": "client_rank",
    "unitAvailable": "unit_available",
    "alarmLevel": "alarm_level",
    "noRedundancy": "no_redundancy",
    "healthSafetyRisk": "health_safety_risk",
    "pmMoveCount": "pm_move_count",
    "pmType": "pm_type",
    "techCount": "tech_count",
    "p1BreakdownWaiting": "p1_breakdown_waiting",
    "requestAgeHours": "request_age_hours",
    "nonUrgent": "non_urgent",
    "isGovernment": "is_government",
    "isDatacenter": "is_datacenter",
    "isHospital": "is_hospital",
    "isCriticalInfrastructure": "is_critical_infrastructure",
    "isTelecom": "is_telecom",
    "hasMaintenanceContract": "has_maintenance_contract",
    "isResidential": "is_residential",
}

BOOL_FIELDS = {
    "commissioning",
    "is_pm",
    "is_service_call",
    "unit_available",
    "no_redundancy",
    "health_safety_risk",
    "non_urgent",
    "is_government",
    "is_datacenter",
    "is_hospital",
    "is_critical_infrastructure",
    "is_telecom",
    "has_maintenance_contract",
    "is_residential",
    "p1_breakdown_waiting",
}

INT_FIELDS = {"client_rank", "pm_move_count", "tech_count"}
FLOAT_FIELDS = {"request_age_hours"}
TEXT_FIELDS = {"customer_class", "alarm_level", "pm_type", "notes"}


@dataclass
class JobInput:
    """
    Structured inputs for the dispatch prioritization engine.

    This model is intentionally permissive so it can be fed from direct JSON,
    form inputs, or extracted assistant payloads.
    """

    # Core identity
    customer_class: Optional[str] = None  # C1..C4
    client_rank: Optional[int] = None  # lower = better within same class

    # Job category
    commissioning: Optional[bool] = None
    is_pm: Optional[bool] = None
    is_service_call: Optional[bool] = None

    # Service / alarm state
    unit_available: Optional[bool] = None
    alarm_level: Optional[str] = None  # blocking | reliability | minor | None
    no_redundancy: Optional[bool] = None
    health_safety_risk: Optional[bool] = None

    # PM information
    pm_move_count: Optional[int] = None
    pm_type: Optional[str] = None
    tech_count: Optional[int] = None
    p1_breakdown_waiting: Optional[bool] = None

    # Service information
    request_age_hours: Optional[float] = None
    non_urgent: Optional[bool] = None

    # Misc. helpful context
    notes: str = ""

    # External classification helpers (optional)
    is_government: Optional[bool] = None
    is_datacenter: Optional[bool] = None
    is_hospital: Optional[bool] = None
    is_critical_infrastructure: Optional[bool] = None
    is_telecom: Optional[bool] = None
    has_maintenance_contract: Optional[bool] = None
    is_residential: Optional[bool] = None


JOB_INPUT_FIELD_NAMES = {f.name for f in dataclass_fields(JobInput)}


@dataclass
class PriorityResult:
    priority: Optional[str]
    client_class: Optional[str]
    schedule_code: Optional[str]
    compact_schedule_code: Optional[str]
    reason: str
    decision_path: List[str] = field(default_factory=list)
    missing_info: List[str] = field(default_factory=list)
    needs_human_review: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _normalize_token(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or None


def _normalize_customer_class(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text if text in CLIENT_CLASSES else text or None


def _normalize_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"yes", "y", "true", "1", "on"}:
            return True
        if v in {"no", "n", "false", "0", "off"}:
            return False
    return None


def _normalize_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_alarm_level(value: Any) -> Optional[str]:
    token = _normalize_token(value)
    if token is None:
        return None
    return ALARM_ALIASES.get(token, token)


def _normalize_pm_type(value: Any) -> Optional[str]:
    token = _normalize_token(value)
    if token is None:
        return None
    return PM_TYPE_ALIASES.get(token, token)


def normalize_job(job: Any) -> JobInput:
    """Accept either a JobInput instance or a plain dict."""
    if isinstance(job, JobInput):
        normalized = job
    elif isinstance(job, dict):
        data: Dict[str, Any] = {}
        for key, value in job.items():
            key = FIELD_ALIASES.get(key, key)
            if key in JOB_INPUT_FIELD_NAMES:
                data[key] = value
        normalized = JobInput(**data)
    else:
        raise TypeError("job must be a dict or JobInput")

    payload = asdict(normalized)

    for field_name in BOOL_FIELDS:
        payload[field_name] = _normalize_bool(payload.get(field_name))

    for field_name in INT_FIELDS:
        payload[field_name] = _normalize_int(payload.get(field_name))

    for field_name in FLOAT_FIELDS:
        payload[field_name] = _normalize_float(payload.get(field_name))

    payload["customer_class"] = _normalize_customer_class(payload.get("customer_class"))
    payload["alarm_level"] = _normalize_alarm_level(payload.get("alarm_level"))
    payload["pm_type"] = _normalize_pm_type(payload.get("pm_type"))
    payload["notes"] = str(payload.get("notes") or "").strip()

    # Blocked equipment cannot be treated as minor/reliability in the final decision.
    if payload.get("unit_available") is False:
        payload["alarm_level"] = "blocking"

    return JobInput(**payload)


def determine_client_class(job: JobInput) -> Tuple[Optional[str], List[str]]:
    """Infer or validate C1..C4."""
    missing: List[str] = []

    if job.customer_class in CLIENT_CLASSES:
        return job.customer_class, missing

    if job.customer_class is not None and job.customer_class not in CLIENT_CLASSES:
        missing.append("customer_class")
        return None, missing

    if any(
        flag is True
        for flag in (
            job.is_government,
            job.is_datacenter,
            job.is_hospital,
            job.is_critical_infrastructure,
        )
    ):
        return "C1", missing

    if job.is_telecom is True:
        return "C2", missing

    if job.has_maintenance_contract is True:
        return "C3", missing

    if job.is_residential is True or job.has_maintenance_contract is False:
        return "C4", missing

    missing.append("customer_class")
    return None, missing


def determine_alarm_level(job: JobInput) -> Tuple[Optional[str], List[str]]:
    """
    Determine alarm type.

    The prioritization document distinguishes three states:
    - blocking
    - reliability
    - minor

    In structured inputs, unit_available=False is treated as blocking.
    """
    missing: List[str] = []

    if job.unit_available is False:
        return "blocking", missing

    if job.alarm_level in ALARM_LEVELS:
        return job.alarm_level, missing

    if job.alarm_level is not None:
        missing.append("alarm_level")
        return None, missing

    if job.unit_available is True:
        return None, missing

    missing.append("alarm_level")
    return None, missing


def determine_pm_type_rank(pm_type: Optional[str]) -> Optional[int]:
    if pm_type is None:
        return None
    return PM_TYPE_RANK.get(pm_type)


def _schedule_code(priority: str, client_class: str) -> Tuple[str, str]:
    compact = f"{priority}{client_class}"
    return f"{priority}-{client_class}", compact


def _job_category_rank(job: JobInput) -> int:
    """
    Compare jobs with the same P and C.

    Lower is better.
    """
    if job.commissioning is True:
        return 0
    if job.is_pm is True or job.pm_type is not None or job.pm_move_count is not None:
        return 1
    if job.is_service_call is True or job.non_urgent is True or job.alarm_level == "minor":
        return 2
    return 9


def _job_subtype_rank(job: JobInput) -> Tuple[int, float]:
    """
    Within a category, apply the documented tie-breaks.

    - PMs: quinquennial > annual CSA > annual > full inspection > generator inspection
    - Services: older request wins
    - Commissioning: no further tie-break is documented, so it stays ahead of other categories only
    """
    if job.commissioning is True:
        return (0, 0.0)

    if job.is_pm is True or job.pm_type is not None or job.pm_move_count is not None:
        pm_rank = determine_pm_type_rank(job.pm_type)
        if pm_rank is None:
            pm_rank = 99
        return (pm_rank, 0.0)

    if job.is_service_call is True or job.non_urgent is True or job.alarm_level == "minor":
        if job.request_age_hours is None:
            return (99, inf)
        # Older request first => lower sort key.
        return (0, -float(job.request_age_hours))

    return (99, inf)


def _sort_key(job: Any) -> Tuple[int, int, int, int, int, float]:
    result = determine_priority(job)
    if result.priority is None:
        return (99, 99, 99, 99, 99, inf)

    priority_num = PRIORITY_TO_NUM[result.priority]
    client_num = CLIENT_CLASS_TO_NUM.get(result.client_class, 99) if result.client_class else 99

    normalized = normalize_job(job)
    client_rank = normalized.client_rank if normalized.client_rank is not None else 999999
    category_rank = _job_category_rank(normalized)
    subtype_rank, subtype_tiebreak = _job_subtype_rank(normalized)

    return (priority_num, client_num, client_rank, category_rank, subtype_rank, subtype_tiebreak)


def determine_priority(job: Any) -> PriorityResult:
    """
    Rule engine aligned to the document's six-question decision tree.

    Returns the highest confidence result possible from structured inputs.
    If a full P#-C# code cannot be formed because customer_class is missing,
    the function still returns the priority when the document makes that
    possible (for example P1 health/safety, P1 commissioning, P4/P6 PM).
    """
    job = normalize_job(job)

    decision_path: List[str] = []
    missing_info: List[str] = []

    client_class, class_missing = determine_client_class(job)
    if class_missing:
        missing_info.extend(class_missing)

    # Alarm level is only a required input when the decision tree actually needs
    # it. Structured PM or commissioning inputs should not be penalized for
    # omitting alarm details.
    alarm_level = None
    if job.unit_available is False:
        alarm_level = "blocking"
    elif job.alarm_level in ALARM_LEVELS:
        alarm_level = job.alarm_level
    elif job.alarm_level is not None:
        missing_info.append("alarm_level")

    def build_result(
        priority: Optional[str],
        reason: str,
        *,
        needs_review: bool = False,
        decision_steps: Optional[List[str]] = None,
        extra_missing: Optional[List[str]] = None,
    ) -> PriorityResult:
        missing = sorted(set(missing_info + (extra_missing or [])))
        if priority is not None and client_class is not None:
            schedule_code, compact = _schedule_code(priority, client_class)
        else:
            schedule_code, compact = None, None
        return PriorityResult(
            priority=priority,
            client_class=client_class,
            schedule_code=schedule_code,
            compact_schedule_code=compact,
            reason=reason,
            decision_path=decision_steps or decision_path,
            missing_info=missing,
            needs_human_review=needs_review or bool(missing),
        )

    # R1: Health and safety always wins.
    if job.health_safety_risk is True:
        decision_path.append("health_safety_risk -> P1")
        return build_result(
            "P1",
            "Health and safety issue overrides other factors.",
        )

    # R2: Commissioning is P1 by default.
    if job.commissioning is True:
        decision_path.append("commissioning -> P1")
        return build_result(
            "P1",
            "Commissioning / mise en service is P1 by default.",
        )

    # Q1: Unit down / blocking alarm.
    if alarm_level == "blocking":
        decision_path.append("blocking condition detected")
        if client_class in {"C1", "C2"}:
            if job.no_redundancy is True:
                decision_path.append("C1-C2 + no redundancy -> P1")
                return build_result(
                    "P1",
                    "Blocking outage on a C1/C2 site without redundancy.",
                )
            if job.no_redundancy is False:
                decision_path.append("C1-C2 + redundancy present -> P2")
                return build_result(
                    "P2",
                    "Blocking outage on a C1/C2 site with redundancy.",
                )
            return build_result(
                None,
                "Need redundancy status to distinguish P1 from P2 for a C1/C2 outage.",
                needs_review=True,
                extra_missing=["no_redundancy"],
            )

        if client_class in {"C3", "C4"}:
            decision_path.append("C3-C4 blocking condition -> P2")
            return build_result(
                "P2",
                "Blocking outage on a C3/C4 site.",
            )

        return build_result(
            None,
            "Need customer class to distinguish P1 from P2 for a blocking outage.",
            needs_review=True,
            extra_missing=["customer_class"],
        )

    # Q2: Reliability alarm, unit still available.
    if alarm_level == "reliability":
        decision_path.append("reliability alarm detected")
        if client_class in {"C1", "C2"}:
            return build_result("P2", "Reliability alarm on a C1/C2 site.")
        if client_class in {"C3", "C4"}:
            return build_result("P3", "Reliability alarm on a C3/C4 site.")
        return build_result(
            None,
            "Need customer class to distinguish P2 from P3 for a reliability alarm.",
            needs_review=True,
            extra_missing=["customer_class"],
        )

    # Q4: PM already moved?
    if job.pm_move_count is not None:
        if job.pm_move_count < 0:
            return build_result(
                None,
                "PM move count cannot be negative.",
                needs_review=True,
                extra_missing=["pm_move_count"],
            )
        if job.pm_move_count >= 2:
            decision_path.append("PM moved 2+ times -> P3")
            return build_result("P3", "PM moved twice or more; anti-backlog escalation applies.")
        if job.pm_move_count == 1:
            decision_path.append("PM moved once -> P4")
            return build_result("P4", "PM moved once.")

    # Q5: Service call / minor alarm.
    if job.is_service_call is True or job.non_urgent is True or alarm_level == "minor":
        decision_path.append("service / minor alarm branch")
        if client_class in {"C1", "C2", "C3"}:
            return build_result("P3", "Non-urgent service call or minor alarm for a C1-C3 customer.")
        if client_class == "C4":
            return build_result("P5", "Non-urgent service call or minor alarm for a C4 customer.")
        return build_result(
            None,
            "Need customer class to distinguish P3 from P5 for a non-urgent service call.",
            needs_review=True,
            extra_missing=["customer_class"],
        )

    # Q6: PM classification.
    if job.is_pm is True or job.pm_type is not None or job.p1_breakdown_waiting is not None:
        if job.pm_type in {"quinquennial", "monthly", "annual_csa"}:
            decision_path.append("critical PM type -> P4")
            return build_result("P4", "Critical PM type per the document.")
        if job.pm_type in {"annual", "full_inspection", "generator_inspection"}:
            decision_path.append("regular PM -> P6")
            return build_result("P6", "Regular PM per the document.")
        if job.is_pm is True and job.pm_type is None:
            return build_result(
                None,
                "Need PM type to distinguish P4 from P6.",
                needs_review=True,
                extra_missing=["pm_type"],
            )

    return build_result(
        None,
        "Could not determine a dispatch priority from the provided structured inputs.",
        needs_review=True,
        extra_missing=["job_category"],
    )


def priority_key(job: Any) -> Tuple[int, int, int, int, int, float]:
    """Sorting key for schedule ordering; lower is more urgent."""
    return _sort_key(job)


def compare_jobs(job_a: Any, job_b: Any) -> int:
    """
    Compare two jobs.

    Returns:
        -1 if job_a is higher priority than job_b
         0 if equal
         1 if job_b is higher priority than job_a
    """
    ka = priority_key(job_a)
    kb = priority_key(job_b)

    if ka < kb:
        return -1
    if ka > kb:
        return 1
    return 0


def higher_priority_job(
    job_a: Any, job_b: Any
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], str]:
    """Return the winner, loser, and a short explanation."""
    ra = determine_priority(job_a)
    rb = determine_priority(job_b)

    comp = compare_jobs(job_a, job_b)
    if comp < 0:
        return (
            {
                "priority": ra.priority,
                "schedule_code": ra.schedule_code,
                "client_class": ra.client_class,
                "reason": ra.reason,
            },
            {
                "priority": rb.priority,
                "schedule_code": rb.schedule_code,
                "client_class": rb.client_class,
                "reason": rb.reason,
            },
            f"{ra.schedule_code or ra.priority} outranks {rb.schedule_code or rb.priority}",
        )
    if comp > 0:
        return (
            {
                "priority": rb.priority,
                "schedule_code": rb.schedule_code,
                "client_class": rb.client_class,
                "reason": rb.reason,
            },
            {
                "priority": ra.priority,
                "schedule_code": ra.schedule_code,
                "client_class": ra.client_class,
                "reason": ra.reason,
            },
            f"{rb.schedule_code or rb.priority} outranks {ra.schedule_code or ra.priority}",
        )

    return (
        {
            "priority": ra.priority,
            "schedule_code": ra.schedule_code,
            "client_class": ra.client_class,
            "reason": ra.reason,
        },
        {
            "priority": rb.priority,
            "schedule_code": rb.schedule_code,
            "client_class": rb.client_class,
            "reason": rb.reason,
        },
        "Jobs are tied by the current inputs.",
    )


def should_pull_technician_from_commissioning(
    commissioning_job: Any,
    pending_p1_job: Any,
) -> bool:
    """
    Apply the commissioning exception from the document.

    Commissioning is P1 by default, but if a commissioning job has 2+ technicians
    and a P1 breakdown is waiting, one technician can be pulled to cover the
    outage while the commissioning continues in reduced mode.
    """
    cj = normalize_job(commissioning_job)
    pj = normalize_job(pending_p1_job)

    if cj.commissioning is not True:
        return False

    if cj.tech_count is None or cj.tech_count < 2:
        return False

    if pj.p1_breakdown_waiting is True:
        return True

    pending_priority = determine_priority(pj)
    return pending_priority.priority == "P1"


def explain_priority(value: Any) -> str:
    """
    Human-readable explanation for coordinators.

    Accepts either a raw job input or an already computed PriorityResult.
    """
    result = value if isinstance(value, PriorityResult) else determine_priority(value)

    lines = [
        f"Priority: {result.priority or 'UNDETERMINED'}",
        f"Customer class: {result.client_class or 'UNDETERMINED'}",
    ]
    if result.schedule_code:
        lines.append(f"Schedule code: {result.schedule_code}")
        lines.append(f"Compact code: {result.compact_schedule_code}")
    else:
        lines.append("Schedule code: unavailable until the missing fields are known.")
    lines.append(f"Reason: {result.reason}")
    if result.decision_path:
        lines.append("Decision path: " + " -> ".join(result.decision_path))
    if result.missing_info:
        lines.append("Missing info: " + ", ".join(result.missing_info))
    if result.needs_human_review:
        lines.append("Human review recommended.")
    return "\n".join(lines)


if __name__ == "__main__":
    samples = [
        {
            "name": "C2 blocking outage",
            "input": {
                "customer_class": "C2",
                "unit_available": False,
                "no_redundancy": True,
            },
            "expected": "P1-C2",
        },
        {
            "name": "C4 reliability alarm",
            "input": {
                "customer_class": "C4",
                "unit_available": True,
                "alarm_level": "reliability",
            },
            "expected": "P3-C4",
        },
        {
            "name": "C1 annual CSA PM",
            "input": {
                "customer_class": "C1",
                "is_pm": True,
                "pm_type": "annual CSA",
            },
            "expected": "P4-C1",
        },
        {
            "name": "C1 annual regular PM",
            "input": {
                "customer_class": "C1",
                "is_pm": True,
                "pm_type": "annual",
            },
            "expected": "P6-C1",
        },
        {
            "name": "Commissioning with missing class",
            "input": {
                "commissioning": True,
            },
            "expected": "P1",
        },
    ]

    for sample in samples:
        result = determine_priority(sample["input"])
        print(f"\n--- {sample['name']} ---")
        print(explain_priority(result))
        if result.schedule_code is not None:
            print(f"Expected schedule code: {sample['expected']}")
        else:
            print(f"Expected priority: {sample['expected']}")

    print("\nSelf-test run complete.")