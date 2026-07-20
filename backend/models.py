from pydantic import BaseModel
from typing import List, Optional, Union

class EmotionPlan(BaseModel):
    primary: str
    secondary: Optional[str] = None
    intensity: Union[float, str]

class BodyLanguagePlan(BaseModel):
    posture: str
    weight_shift: Optional[str] = None
    energy: Union[float, str]
    tension: Optional[Union[float, str]] = None

class HeadMotionPlan(BaseModel):
    type: str
    frequency: Optional[Union[float, str]] = None
    amplitude: Optional[Union[float, str]] = None

class EyeBehaviorPlan(BaseModel):
    target: str
    eye_darts: bool
    blink_rate: Union[float, str]
    avoid_eye_contact: Optional[bool] = None

class FacialExpressionPlan(BaseModel):
    brows: str
    mouth: str
    jaw: str

class BreathingPlan(BaseModel):
    rate: Union[float, str]
    depth: Optional[Union[float, str]] = None

class LipSyncPlan(BaseModel):
    enabled: bool
    audio_file: Optional[str] = None
    transcript: Optional[str] = None

class GesturePlan(BaseModel):
    type: str
    target: Optional[str] = None
    start: float
    end: float
    intensity: Optional[Union[float, str]] = 1.0

class CameraPlan(BaseModel):
    shot: str
    movement: str

class TimelineEvent(BaseModel):
    time: float
    action: str

class AnimationIntentPlan(BaseModel):
    reasoning: Optional[str] = None
    character: str
    duration_seconds: float
    emotion: Optional[EmotionPlan] = None
    body_language: Optional[BodyLanguagePlan] = None
    head_motion: Optional[HeadMotionPlan] = None
    eye_behavior: Optional[EyeBehaviorPlan] = None
    facial_expression: Optional[FacialExpressionPlan] = None
    breathing: Optional[BreathingPlan] = None
    lip_sync: Optional[LipSyncPlan] = None
    gestures: Optional[List[GesturePlan]] = []
    timeline: Optional[List[TimelineEvent]] = []
    locomotion: Optional[dict] = None
    camera: Optional[CameraPlan] = None
    notes: Optional[str] = None
