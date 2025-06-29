JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "error": {"type": "string"},
        "response": {"type": "string"},
        "events_tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "type": {"type": "string", "enum": ["task", "event"]},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "location": {"type": ["string", "null"]},
                    "date": {"type": ["string", "null"]},
                    "time": {"type": ["string", "null"]},
                },
                "required": [
                    "answer",
                    "type",
                    "title",
                    "description",
                    "location",
                    "date",
                    "time",
                ],
            },
        },
    },
    "required": ["error", "response", "events_tasks"],
}
