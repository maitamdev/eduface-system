"""HTTP/auth/Mongo checks for named exams, targeted practice and the mistake book."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from collections import Counter
import pytest
from tests.test_mongo_integration import live, URI
from tests.test_toeic_integration import student, start
from core.toeic_content import content, PART_COUNTS

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(not URI, reason="Local Mongo replica set required")]


@pytest.mark.parametrize("exam_id,total,minutes", [("dhv-full-01-v1",200,120),("dhv-listening-01-v1",100,45),("dhv-reading-01-v1",100,75),("dhv-mini-01-v1",50,35)])
async def test_named_exam_contract_deadline_and_retry(live, exam_id, total, minutes):
    db,http=live
    _,headers=await student(db)
    attempt,payload=await start(http,headers,kind="exam",exam_id=exam_id)
    assert len(attempt["questions"])==total and attempt["exam_id"]==exam_id and attempt["title"]
    assert (datetime.fromisoformat(attempt["deadline"])-datetime.fromisoformat(attempt["started_at"])).total_seconds()==minutes*60
    retry=await http.post("/api/toeic/attempts",headers=headers,json=payload)
    assert retry.status_code==200 and retry.json()["id"]==attempt["id"]
    payload["exam_id"]="dhv-full-02-v1"
    assert (await http.post("/api/toeic/attempts",headers=headers,json=payload)).status_code==409
    if total==200: assert Counter(q["part"] for q in attempt["questions"])==PART_COUNTS
    assert all(not {"correct","explanation","transcript","evidence"}&q.keys() for q in attempt["questions"])


async def test_topic_graphic_and_evidence_visibility_through_submit(live):
    db,http=live
    _,headers=await student(db)
    graphic,_=await start(http,headers,kind="topic",topic_id="p3-graphic")
    assert graphic["topic_id"]=="p3-graphic" and len(graphic["questions"])==6
    assert all(q["graphic"]["rows"] and q["audio_id"] for q in graphic["questions"])
    attempt,payload=await start(http,headers,kind="topic",topic_id="p7-cross-reference")
    assert 0<len(attempt["questions"])<=15 and not any(q.get("evidence") for q in attempt["questions"])
    stored=await db.toeic_attempts.find_one({"_id":attempt["id"]})
    answers={q["id"]:q["correct"] for q in stored["questions"]}
    result=await http.post(f"/api/toeic/attempts/{attempt['id']}/submit",headers=headers,json={"answers":answers})
    assert result.status_code==200 and result.json()["result"]["percent"]==100
    assert all(q["explanation"] for q in result.json()["questions"])
    for q,original in zip(result.json()["questions"],stored["questions"]):
        assert q.get("evidence")==original.get("evidence")
    payload["topic_id"]="p7-purpose"
    assert (await http.post("/api/toeic/attempts",headers=headers,json=payload)).status_code==409


async def test_mistakes_are_private_latest_answer_wins_and_active_attempts_do_not_count(live):
    db,http=live
    uid,headers=await student(db)
    _,other=await student(db,"second-learner")
    assert (await http.get("/api/toeic/review")).status_code==403
    assert (await http.get("/api/toeic/review",headers=headers)).json()["count"]==0
    attempt,_=await start(http,headers)
    assert (await http.get("/api/toeic/review",headers=headers)).json()["count"]==0
    await http.post(f"/api/toeic/attempts/{attempt['id']}/submit",headers=headers,json={"answers":{}})
    book=(await http.get("/api/toeic/review",headers=headers)).json()
    assert book["window"]==50 and book["count"]==10
    assert all(not {"correct","explanation","transcript","evidence"}&q.keys() for q in book["items"])
    assert (await http.get("/api/toeic/review",headers=other)).json()["count"]==0
    retry,_=await start(http,headers,kind="review",part=2)
    stored=await db.toeic_attempts.find_one({"_id":retry["id"]})
    answers={q["id"]:q["correct"] for q in stored["questions"]}
    response=await http.post(f"/api/toeic/attempts/{retry['id']}/submit",headers=headers,json={"answers":answers})
    assert response.status_code==200 and response.json()["result"]["correct"]==10
    assert (await http.get("/api/toeic/review",headers=headers)).json()["count"]==0
    assert await db.toeic_attempts.count_documents({"user_id":uid})==2


async def test_review_window_excludes_older_submissions_and_preserves_group(live):
    db,http=live
    uid,headers=await student(db)
    now=datetime.now(timezone.utc)
    question=next(q for q in content()["questions"] if q["part"]==3)
    old=next(q for q in content()["questions"] if q["part"]==5)
    docs=[{"_id":f"history-{i}","user_id":uid,"status":"submitted","submitted_at":now-timedelta(minutes=i),"questions":[old if i==50 else question],"answers":{}} for i in range(51)]
    await db.toeic_attempts.insert_many(docs)
    book=(await http.get("/api/toeic/review",headers=headers)).json()
    assert [q["id"] for q in book["items"]]==[question["id"]]
    attempt,_=await start(http,headers,kind="review",part=3)
    assert len(attempt["questions"])==3
    assert all(q["group_id"]==question["group_id"] for q in attempt["questions"])


@pytest.mark.parametrize("payload", [{"kind":"exam"},{"kind":"exam","exam_id":"missing"},{"kind":"topic","topic_id":"missing"},{"kind":"topic","topic_id":"p5-passive","part":5},{"kind":"review","exam_id":"dhv-full-01-v1"},{"kind":"review"}])
async def test_invalid_selection_and_empty_review_return_actionable_422(live,payload):
    db,http=live
    _,headers=await student(db)
    response=await http.post("/api/toeic/attempts",headers=headers,json=payload|{"request_id":str(uuid4())})
    assert response.status_code==422 and response.json()["detail"]
    assert await db.toeic_attempts.count_documents({})==0
