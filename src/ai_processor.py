import json
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional

# IMPORTANT: KEEP THIS COMMENT
# Using Gemini integration blueprint - user requested Gemini 2.0 Flash
# The SDK is google-genai (not google-generativeai)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class EmailClassification(BaseModel):
    """Email classification result"""
    category: str
    confidence: float
    subcategory: Optional[str] = None


class PriorityAnalysis(BaseModel):
    """Priority and sentiment analysis"""
    priority: str
    sentiment: str
    urgency_score: float


class ExtractedEntity(BaseModel):
    """Extracted entity from email"""
    entity_type: str
    value: str
    confidence: float


class EntityExtraction(BaseModel):
    """Entity extraction results"""
    entities: List[ExtractedEntity]


class EmailSummary(BaseModel):
    """Email summary with bullet points"""
    summary_points: List[str]


class CombinedEmailAnalysis(BaseModel):
    """Combined email analysis result"""
    classification: str
    priority: str
    sentiment: str
    entities: List[ExtractedEntity]
    summary_narrative: str


def analyze_email_combined(email_subject: str, email_body: str, sender_email: str) -> dict:
    """
    Combined AI analysis: classification, priority, sentiment, entities, and summary in ONE API call.
    This reduces API usage from 4 separate calls to 1 call.
    """
    try:
        system_prompt = """You are an expert email analyst. Analyze the email and provide:

1. CLASSIFICATION: Categorize the email (e.g., "Sales Inquiry", "Technical Support", "Invoice/Billing", "HR Request", "Partnership", "Complaint", "General Inquiry", "Spam")

2. PRIORITY: Assign priority level:
   - P0 (Critical): Urgent matters requiring immediate attention (legal issues, system outages, executive requests)
   - P1 (High): Important but not critical (sales opportunities, customer complaints, time-sensitive requests)
   - P2 (Medium): Standard business correspondence (general inquiries, routine requests)
   - P3 (Low): Non-urgent (newsletters, marketing, FYI emails)

3. SENTIMENT: Analyze tone (Positive, Neutral, Negative, Urgent)

4. ENTITIES: Extract key information (names, dates, amounts, phone numbers, addresses, companies, products)

5. SUMMARY: Write a concise 2-3 sentence narrative summary that:
   - Explains what the email is about
   - Highlights the key information
   - Clearly states the ACTION REQUIRED or SUGGESTED (if any)
   Format the action as: "Action: [specific action needed]" at the end if applicable.

Return all analysis in the specified JSON format."""

        prompt = f"""Sender: {sender_email}
Subject: {email_subject}

Body: {email_body}"""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=CombinedEmailAnalysis,
            ),
        )

        if response.text:
            result = json.loads(response.text)
            return {
                'classification': result.get('classification', 'General Inquiry'),
                'priority': result.get('priority', 'P2'),
                'sentiment': result.get('sentiment', 'Neutral'),
                'entities': result.get('entities', []),
                'summary_narrative': result.get('summary_narrative', '')
            }
        
        return {
            'classification': 'General Inquiry',
            'priority': 'P2',
            'sentiment': 'Neutral',
            'entities': [],
            'summary_narrative': ''
        }

    except Exception as e:
        print(f"Error in combined email analysis: {e}")
        return {
            'classification': 'General Inquiry',
            'priority': 'P2',
            'sentiment': 'Neutral',
            'entities': [],
            'summary_narrative': ''
        }


def generate_email_summary(email_subject: str, email_body: str) -> List[str]:
    """
    Generate a concise bullet-point summary of the email content.
    Returns a list of 2-4 key points summarizing the email.
    """
    try:
        system_prompt = """You are an expert at summarizing emails concisely.
        
        Generate 2-4 bullet points that capture the key information and main points of the email.
        Each bullet point should be:
        - Concise (1-2 sentences maximum)
        - Focus on actionable information or key facts
        - Clear and easy to understand
        
        Return only the bullet points as a JSON array of strings, without bullet symbols."""
        
        prompt = f"Subject: {email_subject}\n\nBody: {email_body}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=EmailSummary,
            ),
        )
        
        if response.text:
            result = json.loads(response.text)
            return result.get('summary_points', [])
        return []
    
    except Exception as e:
        print(f"Error generating email summary: {e}")
        return []


def classify_email(email_subject: str, email_body: str) -> dict:
    """
    Classify email into categories like Sales Inquiry, Technical Support, 
    Invoice/Billing, HR Request, Spam, etc.
    """
    try:
        system_prompt = """You are an email classification expert. Analyze the email and classify it into one of these categories:
        - Sales Inquiry
        - Technical Support
        - Invoice/Billing
        - HR Request
        - General Inquiry
        - Complaint
        - Spam
        
        Provide a confidence score between 0 and 1, and optionally a subcategory.
        Respond in JSON format: {"category": "string", "confidence": number, "subcategory": "string or null"}"""
        
        prompt = f"Subject: {email_subject}\n\nBody: {email_body}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=EmailClassification,
            ),
        )
        
        if response.text:
            return json.loads(response.text)
        return {"category": "General Inquiry", "confidence": 0.5, "subcategory": None}
    
    except Exception as e:
        print(f"Error classifying email: {e}")
        return {"category": "General Inquiry", "confidence": 0.5, "subcategory": None}


def analyze_priority_sentiment(email_subject: str, email_body: str, sender_email: str) -> dict:
    """
    Analyze email priority (P0-Critical, P1-High, P2-Medium, P3-Normal) 
    and sentiment (Positive, Neutral, Negative)
    """
    try:
        system_prompt = """You are an email priority and sentiment analysis expert.
        
        Analyze the email and determine:
        1. Priority level: P0 (Critical/Urgent), P1 (High), P2 (Medium), P3 (Normal)
        2. Sentiment: Positive, Neutral, Negative
        3. Urgency score: 0.0 to 1.0
        
        Consider factors like:
        - Use of urgent language, deadlines, or time sensitivity
        - Emotional tone and language
        - Subject matter importance
        - Sender context
        
        Respond in JSON: {"priority": "string", "sentiment": "string", "urgency_score": number}"""
        
        prompt = f"From: {sender_email}\nSubject: {email_subject}\n\nBody: {email_body}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=PriorityAnalysis,
            ),
        )
        
        if response.text:
            return json.loads(response.text)
        return {"priority": "P3", "sentiment": "Neutral", "urgency_score": 0.3}
    
    except Exception as e:
        print(f"Error analyzing priority/sentiment: {e}")
        return {"priority": "P3", "sentiment": "Neutral", "urgency_score": 0.3}


def extract_entities(email_subject: str, email_body: str) -> dict:
    """
    Extract structured data like Customer Name, Order ID, Date, Product SKU, Amount, etc.
    """
    try:
        system_prompt = """You are a data extraction expert. Extract structured entities from the email.
        
        Look for and extract:
        - Customer/Person Names
        - Order IDs or Reference Numbers
        - Dates (requested dates, deadlines, etc.)
        - Product names or SKUs
        - Amounts or Prices
        - Email addresses
        - Phone numbers
        - Company names
        
        For each entity found, specify:
        - entity_type: type of entity (e.g., "order_id", "customer_name", "amount")
        - value: the extracted value
        - confidence: confidence score 0.0 to 1.0
        
        Respond in JSON: {"entities": [{"entity_type": "string", "value": "string", "confidence": number}]}"""
        
        prompt = f"Subject: {email_subject}\n\nBody: {email_body}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=EntityExtraction,
            ),
        )
        
        if response.text:
            return json.loads(response.text)
        return {"entities": []}
    
    except Exception as e:
        print(f"Error extracting entities: {e}")
        return {"entities": []}


def generate_draft_response(
    email_subject: str,
    email_body: str,
    sender_email: str,
    classification: str,
    template: Optional[str] = None
) -> dict:
    """
    Generate a draft response email based on the incoming email and optional template
    """
    try:
        system_prompt = f"""You are a professional email response assistant.
        
        Generate a polite, professional draft response to the following email.
        The email has been classified as: {classification}
        
        Guidelines:
        - Be professional and courteous
        - Address the main points from the original email
        - Keep the response concise but complete
        - Use appropriate tone for the classification category
        {"- Use this template as a guide: " + template if template else ""}
        
        Respond with JSON containing "subject" and "body" fields:
        {{"subject": "Re: original subject or new subject", "body": "email body text"}}"""
        
        prompt = f"From: {sender_email}\nSubject: {email_subject}\n\nBody: {email_body}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
            ),
        )
        
        if response.text:
            return json.loads(response.text)
        return {"subject": f"Re: {email_subject}", "body": "Thank you for your email. We will review and respond shortly."}
    
    except Exception as e:
        print(f"Error generating draft: {e}")
        return {"subject": f"Re: {email_subject}", "body": "Thank you for your email. We will review and respond shortly."}
