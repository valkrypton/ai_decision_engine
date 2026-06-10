def enrich_hirestream(candidates: list[dict], entities: dict, intent: str) -> list[dict]:
    if intent == "find_jobs":
        return _enrich_jobs(candidates, entities)
    return _enrich_candidates(candidates, entities)


def _enrich_candidates(candidates: list[dict], entities: dict) -> list[dict]:
    skills_raw = entities.get("skills", "")
    query_skills = {s.strip().lower() for s in skills_raw.split(",") if s.strip()} if skills_raw else set()
    exp_req_raw = entities.get("experience_years", "")
    exp_req = float(exp_req_raw) if exp_req_raw else None
    query_location = entities.get("location", "").lower()

    enriched = []
    for c in candidates:
        entry = dict(c)
        cand_skills = {s.lower() for s in c.get("skills", [])}

        if query_skills:
            matched = len(query_skills & cand_skills)
            entry["skill_match"] = matched / len(query_skills)
        else:
            entry["skill_match"] = 1.0

        if exp_req is not None:
            actual = float(c.get("experience_years", 0))
            entry["experience_fit"] = min(actual / exp_req, 1.0) if exp_req > 0 else 1.0
        else:
            entry["experience_fit"] = 1.0

        cand_loc = c.get("location", "").lower()
        if not query_location or cand_loc == "remote" or query_location in cand_loc:
            entry["location_match"] = 1.0
        else:
            entry["location_match"] = 0.0

        enriched.append(entry)
    return enriched


def _enrich_jobs(jobs: list[dict], entities: dict) -> list[dict]:
    skills_raw = entities.get("skills", "")
    candidate_skills = {s.strip().lower() for s in skills_raw.split(",") if s.strip()} if skills_raw else set()
    exp_actual_raw = entities.get("experience_years", "")
    exp_actual = float(exp_actual_raw) if exp_actual_raw else None
    query_location = entities.get("location", "").lower()

    enriched = []
    for j in jobs:
        entry = dict(j)
        required = {s.lower() for s in j.get("required_skills", [])}

        if candidate_skills and required:
            matched = len(candidate_skills & required)
            entry["skill_match"] = matched / len(required)
        else:
            entry["skill_match"] = 1.0

        min_exp = j.get("min_experience_years", 0)
        if exp_actual is not None:
            entry["experience_fit"] = 1.0 if exp_actual >= min_exp else exp_actual / max(min_exp, 1)
        else:
            entry["experience_fit"] = 1.0

        job_loc = j.get("location", "").lower()
        if not query_location or job_loc == "remote" or query_location in job_loc:
            entry["location_match"] = 1.0
        else:
            entry["location_match"] = 0.0

        enriched.append(entry)
    return enriched
