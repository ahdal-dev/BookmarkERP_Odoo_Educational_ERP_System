import os
from typing import List, Tuple, Optional

from neo4j import GraphDatabase, Driver

from llm import get_gemini


_NEO4J_URI = "neo4j+s://ba804be3.databases.neo4j.io"
_NEO4J_USER = "neo4j"
_NEO4J_PASSWORD ="ZlLUvIpEgybcMO53fjds_ubVj6nTSYrIbiajBSCouNY"

_driver: Driver = None


def get_neo4j_driver() -> Driver:
    global _driver
    if _driver is None:
        if not _NEO4J_URI or not _NEO4J_USER or not _NEO4J_PASSWORD:
            raise RuntimeError("Neo4j credentials are not set (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)")
        _driver = GraphDatabase.driver(_NEO4J_URI, auth=(_NEO4J_USER, _NEO4J_PASSWORD))
    return _driver


def extract_triplets_llm(text: str, max_triplets: int = 10) -> List[Tuple[str, str, str]]:
    if not text or not text.strip():
        return []

    model = get_gemini()
    prompt = f"""
You are a reasoning model that extracts knowledge-graph triplets from text.

Your task is to extract only strong and meaningful subject–predicate–object relations that represent real factual or logical connections.

Before creating any triplet, evaluate:
Does this predicate represent an actual semantic relation (causation, property, function, association)?
Or is it a grammatical, redundant, or uncertain connector?
Discard any that are not semantically informative.

When you detect different surface forms of the same predicate (for example plural/singular, verb/noun, or auxiliary variants),
normalize them conceptually — output a single canonical predicate that captures their shared meaning.
Treat “has symptom”, “symptoms”, and “has symptoms” as one concept, without repeating or fragmenting them.
Do this semantically, not by fixed rules.

If it is weak, uncertain, or syntactically generic, discard it.
Do not extract that relation.

Only include a relation if it represents a clear and informative link such as:
any strong conceptual or domain-relevant predicate.

Guidelines:
Use concise entity names (nouns or noun phrases only).
Use only the main verb or verb phrase that conveys the relation.
Exclude uncertain, auxiliary, or descriptive expressions that do not add real meaning.
Remove duplicates and self-links.
Return only the {max_triplets} most meaningful relations.
Output strictly valid JSON array of objects with keys: subject, predicate, object.
Do not add explanations or examples.

Text:
{text}

JSON:
"""

  

    out = model.generate_content(prompt)
    raw = (getattr(out, "text", "") or "").strip()

    import json, re
    try:
        cleaned = raw
        if cleaned.startswith("```json"):
            cleaned = re.sub(r'^```json\s*', '', cleaned)
        if cleaned.endswith("```"):
            cleaned = re.sub(r'\s*```$', '', cleaned)
        data = json.loads(cleaned)
        triplets: List[Tuple[str, str, str]] = []
        for item in data:
            s = (item.get("subject") or "").strip()
            p = (item.get("predicate") or "").strip()
            o = (item.get("object") or "").strip()
            if s and p and o:
                triplets.append((s, p, o))
        return triplets
    except Exception:
        return []


def extract_triplets_from_chunks(
    chunks: List[str],
    window_size: int = 3,
    stride: int = 2,
    per_window_triplets: int = 30,
    total_cap: Optional[int] = 500,
) -> List[Tuple[str, str, str]]:
    
    if not chunks:
        return []
    n = len(chunks)
    unique: Set[Tuple[str, str, str]] = set()
    i = 0
    while i < n:
        j = min(i + window_size, n)
        window_text = "\n\n".join(chunks[i:j])
        trip = extract_triplets_llm(window_text, max_triplets=per_window_triplets)
        for t in trip:
            if t[0] and t[1] and t[2]:
                unique.add((t[0], t[1], t[2]))
        if total_cap and len(unique) >= total_cap:
            break
        i += max(1, stride)
    out = list(unique)
    if total_cap:
        out = out[: total_cap]
    return out

def _sanitize_rel_type_from_text(predicate: str) -> str:
    """Turn arbitrary predicate text into a safe Neo4j relationship type without changing semantics."""
    import re
    t = (predicate or "").strip().upper()
    t = re.sub(r"[^A-Z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    return t or "RELATED"


def upsert_triplets(
    org_id: str,
    source_id: str,
    triplets: List[Tuple[str, str, str]],
    *,
    use_dynamic_rel: bool = True,
):
    if not triplets:
        return 0

    driver = get_neo4j_driver()

    cypher_apoc = """
    UNWIND $rows AS row
    MERGE (s:Entity {name: row.s, org_id: $org})
    MERGE (o:Entity {name: row.o, org_id: $org})
    WITH s, o, row
    CALL apoc.merge.relationship(
      s,
      row.relType,
      {org_id: $org},
      {org_id: $org, predicate: row.p},
      o
    ) YIELD rel
    SET rel.sources = apoc.coll.toSet( (coalesce(rel.sources, []) + row.src) )
    RETURN count(*)
    """

    cypher_related = """
    UNWIND $rows AS row
    MERGE (s:Entity {name: row.s, org_id: $org})
    MERGE (o:Entity {name: row.o, org_id: $org})
    MERGE (s)-[r:RELATED {predicate: row.p, org_id: $org}]->(o)
    SET r.sources = coalesce(r.sources, []) + row.src
    RETURN count(*)
    """

    processed_rows = []
    for (s, p, o) in triplets:
        rel_type = _sanitize_rel_type_from_text(p)
        processed_rows.append({
            "s": s,
            "p": p,
            "o": o,
            "relType": rel_type,
            "src": source_id
        })

    with driver.session() as session:
        try:
            if use_dynamic_rel:
                res = session.run(cypher_apoc, {"rows": processed_rows, "org": org_id})
            else:
                res = session.run(cypher_related, {"rows": processed_rows, "org": org_id})
            _ = res.consume()
        except Exception:
            res = session.run(cypher_related, {"rows": processed_rows, "org": org_id})
            _ = res.consume()

    return len(triplets)


def clear_graph(org_id: str, source_id: Optional[str] = None) -> int:
    driver = get_neo4j_driver()
    with driver.session() as session:
        if source_id:
            delete_rel = """
            MATCH (s:Entity {org_id: $org})-[r {org_id: $org}]->(o:Entity {org_id: $org})
            WHERE $src IN coalesce(r.sources, [])
            DELETE r
            """
            session.run(delete_rel, {"org": org_id, "src": source_id}).consume()
            delete_orphans = """
            MATCH (n:Entity {org_id: $org})
            WHERE NOT (n)--()
            DELETE n
            """
            session.run(delete_orphans, {"org": org_id}).consume()
            return 0
        else:
            delete_all = """
            MATCH (s:Entity {org_id: $org})-[r {org_id: $org}]->(o:Entity {org_id: $org})
            DELETE r
            """
            session.run(delete_all, {"org": org_id}).consume()
            delete_nodes = """
            MATCH (n:Entity {org_id: $org})
            DELETE n
            """
            session.run(delete_nodes, {"org": org_id}).consume()
            return 0


