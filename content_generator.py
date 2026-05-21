import streamlit as st
from groq import Groq
import os

# ── API key ──────────────────────────────────────────────────────────────────
# Reads from .streamlit/secrets.toml locally, or Streamlit Cloud secrets panel
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.environ.get("GROQ_API_KEY", "")

if not api_key:
    st.error("No API key found. Add GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

client = Groq(api_key=api_key)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Social Content Generator", page_icon="✦")

st.title("✦ Social Media Content Generator")
st.write("Generate scroll-stopping social content for any industry — in one click.")

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
industry = st.text_input(
    "What industry or niche are you in?",
    placeholder="e.g. luxury skincare, architecture firm, fitness coaching, SaaS startup",
)

content_angle = st.selectbox(
    "What type of content?",
    [
        "Product or service spotlight",
        "Industry tip or how-to",
        "Behind the scenes",
        "Customer success story",
        "Myth vs. fact",
        "Awareness or education post",
        "Company news or milestone",
        "Trending topic or industry insight",
    ],
)

custom_topic = st.text_input(
    "Add any specific detail or angle (optional)",
    placeholder="e.g. new product launch, a stat you found, an awareness month",
)

platform = st.selectbox(
    "Which platform?",
    ["Instagram", "LinkedIn", "Facebook"],
)

tone = st.selectbox(
    "What tone?",
    [
        "Authoritative & Expert",
        "Friendly & Conversational",
        "Urgent & Awareness-Driven",
        "Educational & Informative",
        "Motivational & Empowering",
        "Bold & Direct",
    ],
)

# ── Generate ──────────────────────────────────────────────────────────────────
if st.button("Generate Content", type="primary"):
    if not industry.strip():
        st.warning("Please enter your industry or niche before generating.")
        st.stop()

    detail = f" Specific angle: {custom_topic}." if custom_topic.strip() else ""

    prompt = f"""You are an expert social media strategist and copywriter working with a {industry} brand.

Create a complete {platform} post about: {content_angle}.{detail}
Tone: {tone}

Format your response EXACTLY like this:

HEADLINE:
[One scroll-stopping headline — bold, punchy, makes people stop scrolling]

CAPTION:
[Full {platform}-optimized caption copy. Engaging, on-brand, with a clear call to action at the end.]

HASHTAGS:
[20 highly relevant hashtags — mix of broad, niche, and industry-specific for {industry}]

DESIGN BRIEF:
[Describe exactly what the graphic or image should look like — colors, imagery, text overlay suggestions — so a designer or Canva user can create it instantly]

IMAGE PROMPT:
[A detailed, ready-to-use prompt for an AI image generator like Midjourney, DALL-E, or Leonardo AI. Include style, lighting, mood, colors, subject, and composition. Format it so it can be pasted directly into an image generator.]

VIDEO PROMPT:
[A short video script for a 15-30 second Reel, TikTok, or LinkedIn video. Include: HOOK (first 3 seconds to stop the scroll), SCRIPT (what to say on camera or as voiceover), VISUALS (what to show on screen), and CTA (closing call to action).]
"""

    with st.spinner("Creating your content..."):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.choices[0].message.content

    # ── Parse sections ────────────────────────────────────────────────────────
    headline = caption = hashtags = design = image_prompt = video_prompt = ""
    current = ""

    for line in result.split("\n"):
        if line.startswith("HEADLINE:"):
            current = "headline"
        elif line.startswith("CAPTION:"):
            current = "caption"
        elif line.startswith("HASHTAGS:"):
            current = "hashtags"
        elif line.startswith("IMAGE PROMPT:"):
            current = "image_prompt"
        elif line.startswith("VIDEO PROMPT:"):
            current = "video_prompt"
        elif line.startswith("DESIGN BRIEF:"):
            current = "design"
        else:
            if current == "headline":
                headline += line + "\n"
            elif current == "caption":
                caption += line + "\n"
            elif current == "hashtags":
                hashtags += line + "\n"
            elif current == "design":
                design += line + "\n"
            elif current == "image_prompt":
                image_prompt += line + "\n"
            elif current == "video_prompt":
                video_prompt += line + "\n"

    # ── Display ───────────────────────────────────────────────────────────────
    st.success("Your content is ready!")
    st.divider()

    st.subheader("Scroll-Stopping Headline")
    st.info(headline.strip())

    st.subheader("Caption Copy")
    st.write(caption.strip())

    st.subheader("Hashtags")
    st.success(hashtags.strip())

    st.subheader("Design Brief")
    st.warning(design.strip())

    st.subheader("🎨 AI Image Prompt")
    st.info(image_prompt.strip())
    st.caption("Copy and paste this directly into Midjourney, DALL-E, or Leonardo AI.")

    st.subheader("🎬 Video Script Prompt")
    st.write(video_prompt.strip())
    st.caption("Use this for Instagram Reels, TikTok, or LinkedIn video.")

    st.divider()

    # ── Download ──────────────────────────────────────────────────────────────
    safe_name = industry.strip().lower().replace(" ", "_")[:20]
    full_post = (
        f"HEADLINE:\n{headline.strip()}\n\n"
        f"CAPTION:\n{caption.strip()}\n\n"
        f"HASHTAGS:\n{hashtags.strip()}\n\n"
        f"DESIGN BRIEF:\n{design.strip()}\n\n"
        f"AI IMAGE PROMPT:\n{image_prompt.strip()}\n\n"
        f"VIDEO SCRIPT PROMPT:\n{video_prompt.strip()}"
    )
    st.download_button(
        "Download Full Post",
        full_post,
        file_name=f"{safe_name}_post.txt",
    )
