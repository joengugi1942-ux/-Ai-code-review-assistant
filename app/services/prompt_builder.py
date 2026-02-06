from app.schemas.review import ReviewRequest


class PromptBuilder:
    def build_review_prompt(self, payload: ReviewRequest) -> str:
        # Simple structured prompt; can be evolved later
        parts: list[str] = ["You are an expert code reviewer."]
        if payload.focus_areas:
            parts.append(f"Focus areas: {', '.join(payload.focus_areas)}.")
        for target in payload.targets:
            parts.append(f"\nFile: {target.filename} (lang={target.language})\n")
            parts.append(target.content)
        return "\n".join(parts)




