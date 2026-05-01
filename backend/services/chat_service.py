"""
chat_service.py
---------------
AI chat assistant for farmers.
- If OPENAI_API_KEY is set: uses GPT-4o-mini with context-aware prompts
- Otherwise: falls back to an enhanced rule-based knowledge base
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ── System prompt for LLM ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert agricultural advisor AI assistant called "KrishiBot".
You help farmers in India make better decisions about crop selection, soil management,
fertilizers, irrigation, pest control, and profit maximization.

Guidelines:
- Give practical, actionable advice
- Use simple language (avoid jargon)
- Mention specific quantities when relevant (e.g., "apply 120 kg/ha of urea")
- Reference Indian farming context (INR prices, Indian crops, seasons)
- If the user shares their prediction result, use it to give personalized advice
- Keep responses concise (3-5 sentences max unless asked for detail)
- Be encouraging and supportive

If asked about a specific crop prediction result, explain:
1. Why that crop was recommended
2. How to maximize yield
3. Expected profit range
4. Key risks to watch out for
"""


def get_chat_response(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    history: Optional[list] = None,
) -> Dict[str, str]:
    """
    Get a chat response for the given message.

    Parameters
    ----------
    message : user's message
    context : optional prediction result to give context-aware answers
    history : optional list of previous messages [{"role": "user/assistant", "text": "..."}]

    Returns
    -------
    dict with "response" and "source" keys
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if api_key:
        try:
            return _openai_response(message, context, history, api_key)
        except Exception as e:
            logger.warning(f"OpenAI API failed: {e}. Falling back to rule-based.")

    return _rule_based_response(message, context)


def _openai_response(message, context, history, api_key):
    """Call OpenAI Chat Completions API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    client = OpenAI(api_key=api_key)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject prediction context if available
    if context:
        ctx_text = (
            f"The farmer's latest prediction result: "
            f"Recommended crop: {context.get('crop', 'N/A')}, "
            f"Confidence: {context.get('confidence_pct', 'N/A')}, "
            f"Expected yield: {context.get('expected_yield', 'N/A')} t/ha, "
            f"Explanation: {context.get('explanation', 'N/A')}. "
            f"Profit: {context.get('profit', {}).get('profit_label', 'N/A')}."
        )
        messages.append({"role": "system", "content": ctx_text})

    # Add conversation history (last 6 turns)
    if history:
        for turn in history[-6:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            messages.append({"role": role, "content": turn.get("text", "")})

    messages.append({"role": "user", "content": message})

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=300,
        temperature=0.7,
    )

    return {
        "response": resp.choices[0].message.content.strip(),
        "source":   "openai",
    }


# ── Enhanced rule-based fallback ──────────────────────────────────────────────
KB = [
    {
        "patterns": ["hello", "hi", "hey", "namaste", "start", "help"],
        "response": (
            "Hello! I'm KrishiBot, your AI farming assistant. I can help you with:\n"
            "- Crop selection and growing tips\n"
            "- Soil and fertilizer advice\n"
            "- Profit and market price guidance\n"
            "- Pest and disease management\n\n"
            "Ask me anything about farming!"
        ),
    },
    {
        "patterns": ["why not rice", "why rice not", "rice not recommended", "not rice"],
        "response": (
            "Rice needs very specific conditions: humidity above 80%, rainfall above 150mm, "
            "and temperatures between 20-35°C. If your conditions don't match these, "
            "the model recommends a more suitable crop. "
            "Try increasing humidity input or check if your region gets enough rainfall for rice."
        ),
    },
    {
        "patterns": ["best fertilizer", "fertilizer for", "which fertilizer", "fertilizer recommend"],
        "response": (
            "Fertilizer choice depends on your crop and soil test results:\n"
            "- Nitrogen-deficient soil: Apply Urea (46% N) at 100-150 kg/ha\n"
            "- Phosphorus-deficient: DAP (18-46-0) at 100 kg/ha\n"
            "- Potassium-deficient: MOP (0-0-60) at 50-80 kg/ha\n"
            "Always do a soil test first for precise recommendations."
        ),
    },
    {
        "patterns": ["increase yield", "improve yield", "better yield", "more yield", "maximize"],
        "response": (
            "To increase yield:\n"
            "1. Use certified high-yield variety seeds\n"
            "2. Apply balanced NPK fertilizers based on soil test\n"
            "3. Ensure proper irrigation (drip irrigation saves 30-50% water)\n"
            "4. Control weeds in the first 30-45 days\n"
            "5. Use integrated pest management (IPM)\n"
            "6. Maintain optimal plant spacing for your crop"
        ),
    },
    {
        "patterns": ["profit", "money", "income", "revenue", "earn", "price"],
        "response": (
            "Profit depends on yield, market price, and input costs. "
            "High-value crops like grapes (Rs.60,000/tonne), pomegranate (Rs.70,000/tonne), "
            "and coffee (Rs.1,80,000/tonne) give the best returns but need more investment. "
            "Cereals like rice and wheat are safer with lower risk. "
            "Use the Profit Calculator in the Predict tab to see your exact numbers."
        ),
    },
    {
        "patterns": ["soil ph", "ph level", "acidic soil", "alkaline soil", "ph correction"],
        "response": (
            "Soil pH affects nutrient availability:\n"
            "- pH < 6: Acidic — add agricultural lime (2-4 tonnes/ha) to raise pH\n"
            "- pH 6-7.5: Ideal for most crops\n"
            "- pH > 7.5: Alkaline — add gypsum or sulfur to lower pH\n"
            "Test soil pH every 2-3 years. Most crops prefer pH 6.0-7.0."
        ),
    },
    {
        "patterns": ["pest", "insect", "disease", "fungal", "blight", "wilt"],
        "response": (
            "Integrated Pest Management (IPM) steps:\n"
            "1. Monitor crops weekly for early detection\n"
            "2. Use resistant varieties when available\n"
            "3. Biological control: neem oil spray (5ml/L water)\n"
            "4. Chemical control only when pest threshold is crossed\n"
            "5. Rotate crops to break pest cycles\n"
            "Contact your local Krishi Vigyan Kendra (KVK) for region-specific advice."
        ),
    },
    {
        "patterns": ["water", "irrigation", "drought", "rainfall", "moisture"],
        "response": (
            "Irrigation tips:\n"
            "- Drip irrigation: most efficient, saves 40-50% water vs flood irrigation\n"
            "- Sprinkler: good for vegetables and small grains\n"
            "- Critical stages: water stress during flowering reduces yield by 30-50%\n"
            "- Rainwater harvesting can supplement irrigation in dry spells\n"
            "- Mulching reduces soil moisture loss by 25-30%"
        ),
    },
    {
        "patterns": ["weather", "temperature", "humidity", "climate", "season"],
        "response": (
            "Weather affects crop choice significantly:\n"
            "- Kharif season (June-Nov): rice, maize, cotton, soybean — needs monsoon rain\n"
            "- Rabi season (Nov-Apr): wheat, mustard, chickpea — needs cool dry weather\n"
            "- Zaid season (Mar-Jun): watermelon, cucumber — needs hot dry weather\n"
            "Use the weather fetch feature to auto-fill current conditions for your city."
        ),
    },
    {
        "patterns": ["organic", "natural farming", "chemical free", "bio"],
        "response": (
            "Organic farming tips:\n"
            "- Replace urea with vermicompost (4-5 tonnes/ha) or FYM (10 tonnes/ha)\n"
            "- Use Jeevamrit (fermented cow dung solution) as soil conditioner\n"
            "- Neem cake (200 kg/ha) controls soil pests naturally\n"
            "- Organic produce fetches 20-40% premium in markets\n"
            "- Certification takes 3 years but opens export markets"
        ),
    },
    {
        "patterns": ["government scheme", "subsidy", "loan", "pm kisan", "kcc"],
        "response": (
            "Key government schemes for farmers:\n"
            "- PM-KISAN: Rs.6,000/year direct income support\n"
            "- Kisan Credit Card (KCC): low-interest crop loans at 4-7%\n"
            "- PM Fasal Bima Yojana: crop insurance at subsidized premium\n"
            "- Soil Health Card: free soil testing every 2 years\n"
            "- eNAM: online mandi platform for better crop prices\n"
            "Contact your nearest Agriculture Department office to apply."
        ),
    },
    {
        "patterns": ["rice", "paddy", "dhan"],
        "response": (
            "Rice cultivation guide:\n"
            "- Season: Kharif (June-November)\n"
            "- Water requirement: 1200-2000mm per season\n"
            "- Fertilizer: 120-150 kg N/ha, 60 kg P/ha, 60 kg K/ha\n"
            "- Yield potential: 4-6 tonnes/ha with HYV seeds\n"
            "- Market price: ~Rs.20,000/tonne (MSP 2024)\n"
            "- Key pests: Brown planthopper, stem borer — monitor weekly"
        ),
    },
    {
        "patterns": ["wheat", "gehu"],
        "response": (
            "Wheat cultivation guide:\n"
            "- Season: Rabi (November-April)\n"
            "- Temperature: 15-25°C ideal\n"
            "- Fertilizer: 120 kg N/ha, 60 kg P/ha, 40 kg K/ha\n"
            "- Yield potential: 4-5 tonnes/ha\n"
            "- Market price: ~Rs.22,000/tonne (MSP 2024)\n"
            "- Sow by November 15 for best results in North India"
        ),
    },
    {
        "patterns": ["cotton", "kapas"],
        "response": (
            "Cotton cultivation guide:\n"
            "- Season: Kharif (April-November)\n"
            "- Requires well-drained black cotton soil\n"
            "- Fertilizer: 150 kg N/ha, 75 kg P/ha, 75 kg K/ha\n"
            "- Yield: 2-3 tonnes/ha (lint)\n"
            "- Market price: ~Rs.65,000/tonne\n"
            "- Bt cotton reduces pesticide costs significantly"
        ),
    },
]

FALLBACK_RESPONSE = (
    "That's a great question! For the most accurate advice, I'd recommend:\n"
    "1. Consulting your local Krishi Vigyan Kendra (KVK)\n"
    "2. Using the Soil Health Card scheme for free soil testing\n"
    "3. Calling the Kisan Call Centre: 1800-180-1551 (free, 24/7)\n\n"
    "You can also ask me about specific crops, fertilizers, irrigation, or profit calculations!"
)


def _rule_based_response(message: str, context: Optional[Dict] = None) -> Dict[str, str]:
    """Enhanced rule-based fallback with context awareness."""
    msg_lower = message.lower()

    # Context-aware: if user asks about "this crop" or "my result"
    if context and any(w in msg_lower for w in ["this crop", "my result", "recommended", "why this", "explain"]):
        crop = context.get("crop", "the recommended crop")
        conf = context.get("confidence_pct", "N/A")
        expl = context.get("explanation", "")
        profit = context.get("profit", {})
        profit_label = profit.get("profit_label", "N/A") if profit else "N/A"
        return {
            "response": (
                f"Based on your farm data, {crop} was recommended with {conf} confidence. "
                f"{expl} "
                f"Expected profit: {profit_label} per hectare. "
                f"To maximize yield, ensure proper fertilization and timely irrigation."
            ),
            "source": "rule-based-context",
        }

    # Match knowledge base
    for entry in KB:
        if any(p in msg_lower for p in entry["patterns"]):
            return {"response": entry["response"], "source": "rule-based"}

    return {"response": FALLBACK_RESPONSE, "source": "rule-based"}
