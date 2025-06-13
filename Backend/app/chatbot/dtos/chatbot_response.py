from pydantic import BaseModel, Field, ValidationError, field_validator, root_validator

class ChatbotResponse(BaseModel):
    """Schema for the structured JSON returned by the LLM.

    The assistant is expected to always reply with a JSON object that follows
    this exact structure:

    {
        "response": "<natural-language reply>",
        "is_booking": true | false,
        "is_human_handoff": true | false
    }
    """

    response: str = Field(..., description="The assistant's natural-language reply")
    is_booking: bool = Field(..., description="Whether a booking should be initiated")
    is_human_handoff: bool = Field(..., description="Whether to hand off the conversation to a human agent")

    # Pydantic v1 & v2 compatibility validator.
    @root_validator(pre=True)
    def check_required_keys(cls, values):
        required_keys = {"response", "is_booking", "is_human_handoff"}
        missing = required_keys.difference(values.keys())
        if missing:
            raise ValueError(f"Missing key(s) in LLM response: {', '.join(missing)}")
        return values

    # Additional optional validation example: ensure response is non-empty
    @field_validator("response", mode="before")
    def non_empty_response(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("'response' must be a non-empty string")
        return v

    @root_validator(pre=True)
    def check_response_format(cls, values):
        if not isinstance(values["response"], str) or not values["response"].strip():
            raise ValueError("'response' must be a non-empty string")
        return values

    @root_validator(pre=True)
    def check_booking_format(cls, values):
        if not isinstance(values["is_booking"], bool):
            raise ValueError("'is_booking' must be a boolean")
        return values

    @root_validator(pre=True)
    def check_handoff_format(cls, values):
        if not isinstance(values["is_human_handoff"], bool):
            raise ValueError("'is_human_handoff' must be a boolean")
        return values

    @root_validator(pre=True)
    def check_response_and_handoff_consistency(cls, values):
        if values["is_booking"] and values["is_human_handoff"]:
            raise ValueError("'is_booking' and 'is_human_handoff' cannot both be true")
        return values 