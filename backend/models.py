"""Pydantic schema for the Animation Intent Plan produced by the LLM planner.

The schema is intentionally permissive about *values* (many fields accept either
a number or a descriptive string such as "increased") because LLM output varies,
but strict about *structure*: required fields, non-empty names and coherent
timings are enforced so the compiler never receives an impossible plan.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

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
    type: str = Field(min_length=1)
    target: Optional[str] = None
    start: float = Field(ge=0, description="Start time in seconds")
    end: float = Field(ge=0, description="End time in seconds")
    intensity: Optional[Union[float, str]] = 1.0

    @model_validator(mode="after")
    def _end_after_start(self):
        if self.end < self.start:
            raise ValueError(
                f"gesture '{self.type}' ends before it starts (start={self.start}, end={self.end})"
            )
        return self

class CameraPlan(BaseModel):
    shot: str
    movement: str

class TimelineEvent(BaseModel):
    time: float = Field(ge=0, description="Event time in seconds")
    action: str

class AnimationIntentPlan(BaseModel):
    reasoning: Optional[str] = None
    character: str = Field(min_length=1)
    duration_seconds: float = Field(gt=0, description="Total clip length in seconds")
    emotion: Optional[EmotionPlan] = None
    body_language: Optional[BodyLanguagePlan] = None
    head_motion: Optional[HeadMotionPlan] = None
    eye_behavior: Optional[EyeBehaviorPlan] = None
    facial_expression: Optional[FacialExpressionPlan] = None
    breathing: Optional[BreathingPlan] = None
    lip_sync: Optional[LipSyncPlan] = None
    gestures: Optional[List[GesturePlan]] = Field(default_factory=list)
    timeline: Optional[List[TimelineEvent]] = Field(default_factory=list)
    locomotion: Optional[dict] = None
    camera: Optional[CameraPlan] = None
    notes: Optional[str] = None

    @field_validator("character")
    @classmethod
    def _strip_character(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("character must not be blank")
        return value

    @field_validator("gestures", "timeline", mode="before")
    @classmethod
    def _none_to_empty_list(cls, value):
        # LLMs frequently emit `null` for empty arrays.
        return [] if value is None else value
