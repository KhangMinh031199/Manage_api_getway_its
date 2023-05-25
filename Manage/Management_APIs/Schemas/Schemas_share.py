from bson.objectid import ObjectId
import pydantic
import struct
from pydantic import BaseModel

class BeeObjectId(ObjectId):
    # fix for FastApi/docs
    __origin__ = pydantic.typing.Literal
    __args__ = (str,)

    @property
    def timestamp(self):
        timestamp = struct.unpack(">I", self.binary[0:4])[0]
        return timestamp

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return v

# fix ObjectId & FastApi conflict
pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str
pydantic.json.ENCODERS_BY_TYPE[BeeObjectId] = str


class User(BaseModel):
    id: BeeObjectId
    name: str
    avatar: str = "/static/img/undraw_profile.svg"
    email: str
    password: str
    phone: str
    company: str
    job: str
    active: int
    api_key: str
    timestamp: str
    partner_id: BeeObjectId
    url_webhook: str