"""Real HTTP/auth/Mongo replica-set verification; each test owns its temporary DB."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from pymongo.errors import OperationFailure
from motor.motor_asyncio import AsyncIOMotorCollection
from tests.test_mongo_integration import live, URI

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(not URI, reason="Local Mongo replica set required")]


async def student(db, name="learner"):
    from core.auth import create_access_token
    inserted = await db.users.insert_one({"username":name,"role":"student","is_active":True,"created_at":datetime.now(timezone.utc)})
    uid = str(inserted.inserted_id)
    return uid, {"Authorization":"Bearer " + create_access_token(uid,name,"student")[0]}


async def start(http, headers, kind="lesson", **extra):
    payload={"kind":kind,"request_id":str(uuid4()), **extra}
    if kind=="lesson": payload.setdefault("lesson_id","f01")
    response=await http.post("/api/toeic/attempts",json=payload,headers=headers)
    assert response.status_code==200,response.text
    return response.json(), payload


async def test_toeic_auth_private_ownership_and_hidden_answers(live):
    db,http=live
    assert (await http.get("/api/toeic/catalog",headers={"X-API-Key":""})).status_code==401
    assert (await http.get("/api/toeic/progress")).status_code==403
    uid,headers=await student(db)
    _,other=await student(db,"another")
    catalog=(await http.get("/api/toeic/catalog",headers=headers)).json()
    assert catalog["question_count"]==268 and "questions" not in catalog
    attempt,_=await start(http,headers)
    assert all("correct" not in q and "transcript" not in q for q in attempt["questions"])
    assert (await http.get(f"/api/toeic/attempts/{attempt['id']}",headers=other)).status_code==404
    assert (await http.put(f"/api/toeic/attempts/{attempt['id']}/answers",headers=other,json={"answers":{}})).status_code==404
    assert (await http.post(f"/api/toeic/attempts/{attempt['id']}/submit",headers=other,json={"answers":{}})).status_code==404
    assert (await http.get("/api/toeic/progress",headers=other)).json()["active"]==[]


async def test_toeic_start_retry_and_parameters(live):
    db,http=live
    _,headers=await student(db)
    attempt,payload=await start(http,headers)
    retry=await http.post("/api/toeic/attempts",headers=headers,json=payload)
    assert retry.json()["id"]==attempt["id"] and await db.toeic_attempts.count_documents({})==1
    payload["lesson_id"]="f02"
    assert (await http.post("/api/toeic/attempts",headers=headers,json=payload)).status_code==409
    assert (await http.post("/api/toeic/attempts",headers=headers,json={"kind":"part","request_id":str(uuid4())})).status_code==422
    assert (await http.post("/api/toeic/attempts",headers=headers,json={"kind":"mock","lesson_id":"f01","request_id":str(uuid4())})).status_code==422


async def test_toeic_save_revision_and_resume(live):
    db,http=live
    _,headers=await student(db)
    attempt,_=await start(http,headers)
    path=f"/api/toeic/attempts/{attempt['id']}"
    answers={attempt["questions"][0]["id"]:1}
    saved=await http.put(path+"/answers",headers=headers,json={"answers":answers,"revision":0})
    assert saved.status_code==200 and saved.json()["revision"]==1
    assert (await http.put(path+"/answers",headers=headers,json={"answers":{},"revision":0})).status_code==409
    assert (await http.post(path+"/submit",headers=headers,json={"answers":{},"revision":0})).status_code==409
    resumed=(await http.get(path,headers=headers)).json()
    assert resumed["answers"]==answers and resumed["revision"]==1
    assert (await http.put(path+"/answers",headers=headers,json={"answers":{"other":0},"revision":1})).status_code==422
    assert (await http.put(path+"/answers",headers=headers,json={"answers":{attempt['questions'][0]['id']:3},"revision":1})).status_code==422


async def test_toeic_grading_completion_and_retry_are_idempotent(live):
    db,http=live
    uid,headers=await student(db)
    attempt,_=await start(http,headers)
    stored=await db.toeic_attempts.find_one({"_id":attempt["id"]})
    answers={q["id"]:q["correct"] for q in stored["questions"]}
    path=f"/api/toeic/attempts/{attempt['id']}/submit"
    result=await http.post(path,headers=headers,json={"answers":answers})
    assert result.status_code==200,result.text
    assert result.json()["result"]["percent"]==100
    assert result.json()["questions"][0]["transcript"]
    retry=await http.post(path,headers=headers,json={"answers":{}})
    assert retry.json()["result"]["percent"]==100
    p=(await http.get("/api/toeic/progress",headers=headers)).json()
    assert p["lessons"]["f01"]==100 and p["streak"]==1
    assert len(p["recent"])==1 and p["days"][0]["questions"]==10 and not p["active"]
    assert (await db.toeic_activity.find_one({"user_id":uid}))["questions"]==10


async def test_toeic_expired_attempt_uses_only_server_saved_answers(live):
    db,http=live
    _,headers=await student(db)
    attempt,_=await start(http,headers)
    doc=await db.toeic_attempts.find_one({"_id":attempt["id"]})
    first=doc["questions"][0]
    await db.toeic_attempts.update_one({"_id":attempt["id"]},{"$set":{"deadline":datetime.now(timezone.utc)-timedelta(minutes=1),"answers":{first["id"]:first["correct"]}}})
    path=f"/api/toeic/attempts/{attempt['id']}"
    assert (await http.put(path+"/answers",headers=headers,json={"answers":{}})).status_code==409
    forged={q["id"]:q["correct"] for q in doc["questions"]}
    result=await http.post(path+"/submit",headers=headers,json={"answers":forged})
    assert result.status_code==200 and result.json()["result"]["correct"]==1


async def test_toeic_submit_rolls_back_when_profile_write_fails(live,monkeypatch):
    db,http=live
    _,headers=await student(db)
    attempt,_=await start(http,headers)
    original=AsyncIOMotorCollection.update_one
    async def fail(self,*args,**kwargs):
        if self.name=="toeic_profiles": raise OperationFailure("Injected learning progress failure",code=123)
        return await original(self,*args,**kwargs)
    with monkeypatch.context() as m:
        m.setattr(AsyncIOMotorCollection,"update_one",fail)
        response=await http.post(f"/api/toeic/attempts/{attempt['id']}/submit",headers=headers,json={"answers":{}})
        assert response.status_code==503,response.text
    assert (await db.toeic_attempts.find_one({"_id":attempt["id"]}))["status"]=="active"
    assert await db.toeic_activity.count_documents({})==0
    assert (await http.post(f"/api/toeic/attempts/{attempt['id']}/submit",headers=headers,json={"answers":{}})).status_code==200


async def test_toeic_fsrs_schedule_private_idempotent_and_due_checked(live):
    db,http=live
    uid,headers=await student(db)
    _,other=await student(db,"other")
    payload={"rating":3,"expected_version":0,"event_id":str(uuid4())}
    path="/api/toeic/vocabulary/f01-v01/review"
    response=await http.post(path,headers=headers,json=payload)
    assert response.status_code==200,response.text
    assert response.json()["version"]==1
    assert datetime.fromisoformat(response.json()["due"])>datetime.now(timezone.utc)
    assert (await http.post(path,headers=headers,json=payload)).json()==response.json()
    stale=payload|{"event_id":str(uuid4())}
    assert (await http.post(path,headers=headers,json=stale)).status_code==409
    assert (await http.post(path,headers=headers,json=stale|{"expected_version":1})).status_code==409
    cards=(await http.get("/api/toeic/vocabulary",headers=other)).json()
    assert all(c["version"]==0 for c in cards)
    assert (await db.toeic_activity.find_one({"user_id":uid}))["reviews"]==1
    stored=await db.toeic_cards.find_one({"user_id":uid})
    assert stored["reviews"]==1 and "stability" in stored["fsrs"]


async def test_toeic_review_transaction_rolls_back_and_preferences_are_private(live,monkeypatch):
    db,http=live
    uid,headers=await student(db)
    _,other=await student(db,"other")
    original=AsyncIOMotorCollection.update_one
    async def fail(self,*args,**kwargs):
        if self.name=="toeic_activity": raise OperationFailure("Injected activity failure",code=123)
        return await original(self,*args,**kwargs)
    with monkeypatch.context() as m:
        m.setattr(AsyncIOMotorCollection,"update_one",fail)
        result=await http.post("/api/toeic/vocabulary/f01-v01/review",headers=headers,json={"rating":3,"expected_version":0,"event_id":str(uuid4())})
        assert result.status_code==503,result.text
    assert await db.toeic_cards.count_documents({})==0
    assert (await http.put("/api/toeic/preferences",headers=headers,json={"target":900,"daily_minutes":45})).status_code==200
    assert (await http.get("/api/toeic/progress",headers=headers)).json()["target"]==900
    assert (await http.get("/api/toeic/progress",headers=other)).json()["target"]==650
    assert (await http.put("/api/toeic/preferences",headers=headers,json={"target":999,"daily_minutes":45})).status_code==422


async def test_toeic_full_mock_has_200_questions_and_active_limit(live):
    db,http=live
    _,headers=await student(db)
    attempt,_=await start(http,headers,kind="mock")
    assert len(attempt["questions"])==200
    assert (datetime.fromisoformat(attempt["deadline"])-datetime.fromisoformat(attempt["started_at"])).total_seconds()==7200
    for _ in range(4): await start(http,headers)
    assert (await http.post("/api/toeic/attempts",headers=headers,json={"kind":"mock","request_id":str(uuid4())})).status_code==409
