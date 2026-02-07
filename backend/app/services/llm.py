# app/services/llm.py
"""LLM integration — OpenAI GPT-4 / Anthropic Claude for document generation.

Uses the configured LLM_PROVIDER from settings to decide which provider to call.
Falls back to mock responses when API keys are not configured.
"""

import asyncio
from typing import AsyncGenerator

from app.config import settings
from app.prompts.templates import SYSTEM_PROMPT


def _get_provider() -> str:
    """Determine which LLM provider to use based on config + available keys."""
    provider = settings.LLM_PROVIDER.lower()

    # If the preferred provider has a key, use it
    if provider == "groq" and settings.GROQ_API_KEY:
        return "groq"
    if provider == "openai" and settings.OPENAI_API_KEY:
        return "openai"
    if provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        return "anthropic"

    # Fallback: use whichever key is available
    if settings.GROQ_API_KEY:
        return "groq"
    if settings.OPENAI_API_KEY:
        return "openai"
    if settings.ANTHROPIC_API_KEY:
        return "anthropic"

    # No keys at all → mock mode
    return "mock"


async def generate_text(
    prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    context: str = "",
) -> str:
    """
    Generate text using the configured LLM provider.

    Falls back to a mock response when no API keys are configured.
    """
    provider = _get_provider()

    if provider == "groq":
        return await _generate_groq(prompt, system_prompt, context)
    elif provider == "openai":
        return await _generate_openai(prompt, system_prompt, context)
    elif provider == "anthropic":
        return await _generate_anthropic(prompt, system_prompt, context)
    else:
        return _mock_generate(prompt)


async def generate_text_stream(
    prompt: str,
    system_prompt: str = SYSTEM_PROMPT,
    context: str = "",
) -> AsyncGenerator[str, None]:
    """
    Stream text generation token-by-token for the Agent Thinking Panel.

    Falls back to mock streaming when no API keys are configured.
    """
    provider = _get_provider()

    if provider == "groq":
        async for chunk in _stream_groq(prompt, system_prompt, context):
            yield chunk
    elif provider == "openai":
        async for chunk in _stream_openai(prompt, system_prompt, context):
            yield chunk
    elif provider == "anthropic":
        async for chunk in _stream_anthropic(prompt, system_prompt, context):
            yield chunk
    else:
        async for chunk in _mock_stream(prompt):
            yield chunk


def _build_messages(prompt: str, system_prompt: str, context: str) -> list[dict]:
    """Build the messages array used by OpenAI-compatible APIs (OpenAI, Groq)."""
    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({
            "role": "user",
            "content": f"Use the following company policy context to inform your response:\n\n{context}",
        })
    messages.append({"role": "user", "content": prompt})
    return messages


# ─────────────────────────────────────────────────────────────
# Groq implementation (OpenAI-compatible API)
# ─────────────────────────────────────────────────────────────

async def _generate_groq(prompt: str, system_prompt: str, context: str) -> str:
    """Generate text using Groq (Llama 3.3, Mixtral, etc.)."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    messages = _build_messages(prompt, system_prompt, context)

    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


async def _stream_groq(prompt: str, system_prompt: str, context: str) -> AsyncGenerator[str, None]:
    """Stream text from Groq."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    messages = _build_messages(prompt, system_prompt, context)

    stream = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ─────────────────────────────────────────────────────────────
# OpenAI implementation
# ─────────────────────────────────────────────────────────────

async def _generate_openai(prompt: str, system_prompt: str, context: str) -> str:
    """Generate text using OpenAI GPT-4."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    messages = _build_messages(prompt, system_prompt, context)

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
    )
    return response.choices[0].message.content or ""


async def _stream_openai(prompt: str, system_prompt: str, context: str) -> AsyncGenerator[str, None]:
    """Stream text from OpenAI."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    messages = _build_messages(prompt, system_prompt, context)

    stream = await client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7,
        max_tokens=2000,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ─────────────────────────────────────────────────────────────
# Anthropic implementation
# ─────────────────────────────────────────────────────────────

async def _generate_anthropic(prompt: str, system_prompt: str, context: str) -> str:
    """Generate text using Anthropic Claude."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    user_content = prompt
    if context:
        user_content = (
            f"Use the following company policy context to inform your response:\n\n"
            f"{context}\n\n---\n\n{prompt}"
        )

    message = await client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


async def _stream_anthropic(prompt: str, system_prompt: str, context: str) -> AsyncGenerator[str, None]:
    """Stream text from Anthropic Claude."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    user_content = prompt
    if context:
        user_content = (
            f"Use the following company policy context to inform your response:\n\n"
            f"{context}\n\n---\n\n{prompt}"
        )

    async with client.messages.stream(
        model="claude-3-sonnet-20240229",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


# ─────────────────────────────────────────────────────────────
# Mock implementation (for demos / no API keys)
# ─────────────────────────────────────────────────────────────

def _mock_generate(prompt: str) -> str:
    """Return a mock response for demo/testing without real API keys."""
    prompt_lower = prompt.lower()

    if "welcome email" in prompt_lower:
        return (
            "**Subject: Welcome to the Team! 🎉**\n\n"
            "Dear New Team Member,\n\n"
            "We're thrilled to welcome you! Your start date is approaching, "
            "and we want to make sure you have everything you need for a smooth onboarding.\n\n"
            "**Here's what to expect on your first day:**\n"
            "- ☀️ Orientation session at 9:00 AM\n"
            "- 🤝 Meet your buddy and manager\n"
            "- 💻 IT setup and equipment collection\n"
            "- 🍽️ Team lunch\n\n"
            "**First Week Overview:**\n"
            "- Day 1: Orientation & setup\n"
            "- Day 2: Manager 1:1 & tool walkthroughs\n"
            "- Day 3: Buddy meetup & department deep-dive\n"
            "- Day 4-5: Self-paced training & first project introduction\n\n"
            "Please don't hesitate to reach out if you have any questions.\n\n"
            "Best regards,\nHR Team\n\n"
            "---\n*[Mock response — connect an OpenAI or Anthropic API key for real AI generation]*"
        )
    elif "offer letter" in prompt_lower:
        return (
            "# OFFER OF EMPLOYMENT\n\n"
            "**CONFIDENTIAL**\n\n"
            "Dear Candidate,\n\n"
            "We are pleased to offer you a position with our company. "
            "Your compensation package includes a competitive salary and comprehensive benefits.\n\n"
            "**Position Details:**\n"
            "- Start Date: As specified\n"
            "- Reporting To: Your assigned manager\n"
            "- Employment Type: Full-time\n\n"
            "**Benefits Include:**\n"
            "- Health, dental, and vision insurance\n"
            "- 401(k) with company match\n"
            "- Unlimited PTO policy\n"
            "- Professional development budget\n\n"
            "This offer is contingent upon successful completion of background verification.\n\n"
            "Please sign and return within 5 business days.\n\n"
            "Sincerely,\nHR Department\n\n"
            "---\n*[Mock response — connect an OpenAI or Anthropic API key for real AI generation]*"
        )
    elif "30-60-90" in prompt_lower or "plan" in prompt_lower:
        return (
            "# 30-60-90 Day Onboarding Plan\n\n"
            "## 📘 First 30 Days — Learn & Orient\n"
            "- Complete all onboarding training modules\n"
            "- Meet all team members and key stakeholders\n"
            "- Understand team processes, tools, and workflows\n"
            "- Shadow senior team members on active projects\n"
            "- Weekly check-in with manager every Friday\n\n"
            "## 📗 Days 31-60 — Contribute & Collaborate\n"
            "- Take ownership of initial tasks and deliverables\n"
            "- Attend cross-functional meetings independently\n"
            "- Identify areas for improvement in current processes\n"
            "- Complete first independent code review / deliverable\n"
            "- Mid-point feedback session with manager\n\n"
            "## 📕 Days 61-90 — Own & Deliver\n"
            "- Drive independent projects end-to-end\n"
            "- Present learnings and findings to the team\n"
            "- Set goals for the next quarter with manager\n"
            "- Mentor the next new hire (if applicable)\n"
            "- 90-day performance review\n\n"
            "---\n*[Mock response — connect an OpenAI or Anthropic API key for real AI generation]*"
        )
    elif "equipment" in prompt_lower or "provisioning" in prompt_lower:
        return (
            "# IT Equipment Provisioning Request\n\n"
            "**Status:** 📋 Pending\n\n"
            "## Hardware\n"
            "- [x] Laptop (MacBook Pro 14\" or equivalent)\n"
            "- [x] Monitor (27\" 4K)\n"
            "- [x] Keyboard and mouse\n"
            "- [x] Headset for meetings\n"
            "- [x] Access badge\n\n"
            "## Software Licenses\n"
            "- [x] Email & collaboration suite\n"
            "- [x] Chat & video conferencing\n"
            "- [x] Department-specific tools\n"
            "- [x] VPN client\n"
            "- [x] Password manager\n\n"
            "## Access & Accounts\n"
            "- [x] Company email account\n"
            "- [x] Internal wiki / documentation\n"
            "- [x] Project management tool\n"
            "- [x] Code repository access (if applicable)\n\n"
            "**Estimated Provisioning Time:** 24-48 hours before start date\n\n"
            "---\n*[Mock response — connect an OpenAI or Anthropic API key for real AI generation]*"
        )
    elif "validate" in prompt_lower or "analyze" in prompt_lower or "parse" in prompt_lower:
        return (
            "# Employee Data Validation Summary\n\n"
            "**Status:** ✅ Ready for onboarding\n\n"
            "## Data Completeness Check\n"
            "- ✅ Name: Provided\n"
            "- ✅ Email: Valid format\n"
            "- ✅ Role: Provided\n"
            "- ✅ Department: Provided\n"
            "- ✅ Start Date: Valid date\n"
            "- ⚠️ Manager Email: Review needed\n"
            "- ⚠️ Buddy Email: Review needed\n\n"
            "## Readiness Assessment\n"
            "All critical fields are present. Employee is ready to proceed with onboarding.\n\n"
            "---\n*[Mock response — connect an OpenAI or Anthropic API key for real AI generation]*"
        )
    else:
        return (
            f"# Generated Content\n\n"
            f"Generated response for the requested task.\n\n"
            f"*Prompt summary:* {prompt[:150]}...\n\n"
            "---\n*[Mock response — connect an OpenAI or Anthropic API key for real AI generation]*"
        )


async def _mock_stream(prompt: str):
    """Yield mock content word-by-word for streaming simulation."""
    response = _mock_generate(prompt)
    words = response.split(" ")
    for word in words:
        await asyncio.sleep(0.03)  # Simulate realistic token delay
        yield word + " "
