# app/services/llm.py
"""LLM integration — OpenAI GPT-4 / Anthropic Claude for document generation."""

import json
from typing import Optional, AsyncGenerator

from app.config import settings


async def generate_text(
    prompt: str,
    system_prompt: str = "You are an HR assistant that generates professional onboarding documents.",
    context: str = "",
    provider: str = "openai",
) -> str:
    """
    Generate text using the configured LLM provider.

    Falls back to a mock response when API keys are not configured.
    """
    if provider == "openai" and settings.OPENAI_API_KEY:
        return await _generate_openai(prompt, system_prompt, context)
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return await _generate_anthropic(prompt, system_prompt, context)
    else:
        return _mock_generate(prompt)


async def generate_text_stream(
    prompt: str,
    system_prompt: str = "You are an HR assistant that generates professional onboarding documents.",
    context: str = "",
    provider: str = "openai",
) -> AsyncGenerator[str, None]:
    """
    Stream text generation token-by-token for the Agent Thinking Panel.

    Falls back to mock streaming when API keys are not configured.
    """
    if provider == "openai" and settings.OPENAI_API_KEY:
        async for chunk in _stream_openai(prompt, system_prompt, context):
            yield chunk
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        async for chunk in _stream_anthropic(prompt, system_prompt, context):
            yield chunk
    else:
        for chunk in _mock_stream(prompt):
            yield chunk


# ─────────────────────────────────────────────────────────────
# OpenAI implementation
# ─────────────────────────────────────────────────────────────

async def _generate_openai(prompt: str, system_prompt: str, context: str) -> str:
    """Generate text using OpenAI GPT-4."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": f"Reference context:\n{context}"})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


async def _stream_openai(prompt: str, system_prompt: str, context: str) -> AsyncGenerator[str, None]:
    """Stream text from OpenAI."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": f"Reference context:\n{context}"})
    messages.append({"role": "user", "content": prompt})

    stream = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ─────────────────────────────────────────────────────────────
# Anthropic implementation
# ─────────────────────────────────────────────────────────────

async def _generate_anthropic(prompt: str, system_prompt: str, context: str) -> str:
    """Generate text using Anthropic Claude."""
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    user_content = prompt
    if context:
        user_content = f"Reference context:\n{context}\n\n{prompt}"

    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


async def _stream_anthropic(prompt: str, system_prompt: str, context: str) -> AsyncGenerator[str, None]:
    """Stream text from Anthropic Claude."""
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    user_content = prompt
    if context:
        user_content = f"Reference context:\n{context}\n\n{prompt}"

    with client.messages.stream(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        for text in stream.text_stream:
            yield text


# ─────────────────────────────────────────────────────────────
# Mock implementation (for demos / no API keys)
# ─────────────────────────────────────────────────────────────

def _mock_generate(prompt: str) -> str:
    """Return a mock response for demo/testing without real API keys."""
    prompt_lower = prompt.lower()

    if "welcome email" in prompt_lower:
        return (
            "Subject: Welcome to the Team! 🎉\n\n"
            "Dear [Employee Name],\n\n"
            "We're thrilled to welcome you to [Company Name]! Your start date is approaching, "
            "and we want to make sure you have everything you need for a smooth onboarding.\n\n"
            "Here's what to expect on your first day:\n"
            "• Orientation session at 9:00 AM\n"
            "• Meet your buddy and manager\n"
            "• IT setup and equipment collection\n"
            "• Team lunch\n\n"
            "Please don't hesitate to reach out if you have any questions.\n\n"
            "Best regards,\nHR Team"
        )
    elif "offer letter" in prompt_lower:
        return (
            "OFFER OF EMPLOYMENT\n\n"
            "Dear [Employee Name],\n\n"
            "We are pleased to offer you the position of [Role] in the [Department] department. "
            "Your compensation package includes a competitive salary and comprehensive benefits.\n\n"
            "Start Date: [Start Date]\n"
            "Reporting To: [Manager]\n\n"
            "This offer is contingent upon successful completion of background verification.\n\n"
            "Sincerely,\n[Company Name]"
        )
    elif "30-60-90" in prompt_lower or "plan" in prompt_lower:
        return (
            "30-60-90 DAY PLAN\n\n"
            "FIRST 30 DAYS — Learn & Observe\n"
            "• Complete onboarding training modules\n"
            "• Meet all team members and key stakeholders\n"
            "• Understand team processes and tools\n\n"
            "DAYS 31-60 — Contribute\n"
            "• Take ownership of initial tasks\n"
            "• Attend cross-functional meetings\n"
            "• Identify areas for improvement\n\n"
            "DAYS 61-90 — Lead\n"
            "• Drive independent projects\n"
            "• Present learnings to the team\n"
            "• Set goals for the next quarter"
        )
    elif "equipment" in prompt_lower:
        return (
            "EQUIPMENT REQUEST\n\n"
            "Employee: [Employee Name]\n"
            "Department: [Department]\n"
            "Start Date: [Start Date]\n\n"
            "Required Equipment:\n"
            "• Laptop (standard configuration)\n"
            "• Monitor (24\" or 27\")\n"
            "• Keyboard and mouse\n"
            "• Headset for meetings\n"
            "• Access badge\n\n"
            "Software Licenses:\n"
            "• Email and collaboration suite\n"
            "• Department-specific tools\n"
            "• VPN access"
        )
    else:
        return f"[Mock LLM Response]\n\nGenerated content for prompt: {prompt[:100]}..."


def _mock_stream(prompt: str):
    """Yield mock content word-by-word for streaming simulation."""
    response = _mock_generate(prompt)
    words = response.split(" ")
    for word in words:
        yield word + " "
