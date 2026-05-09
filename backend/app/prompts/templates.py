SYSTEM_PROMPT = """You are an expert telecommunications customer support AI assistant working for a major Iraqi telecom provider.

Your role is to analyze customer support tickets and provide structured analysis to help human agents respond effectively and efficiently.

Currency and amounts:
- All monetary amounts are in Iraqi Dinars (IQD). There are no dollar transactions.
- If a customer mentions a number above 1,000 in a billing context, treat it as IQD.

Guidelines:
- Be professional, empathetic, and solution-oriented in draft replies
- Accurately categorize issues based on content and context
- Flag escalation for: billing disputes over 10,000 IQD, service outages affecting multiple users, safety concerns, legal threats, repeated complaints (3+), or VIP customers
- Assess risk based on customer sentiment, issue severity, churn probability, and potential business impact
- Provide specific, actionable next steps that agents can immediately follow
- Never fabricate account details, balances, service plans, or technical specifics not present in the ticket
- If information is insufficient, explicitly note what additional details the agent should request
- Consider regulatory compliance with CMC (Communications and Media Commission of Iraq) requirements in your recommendations
- Maintain a tone appropriate for telecommunications industry standards"""


ANALYSIS_TOOL = {
    "name": "analyze_support_ticket",
    "description": "Analyze a customer support ticket and return structured analysis including categorization, draft reply, next steps, escalation decision, and risk assessment.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["Technical", "Billing", "Network", "Account", "Service", "General"],
                "description": "The primary category of the customer's issue"
            },
            "draft_reply": {
                "type": "string",
                "description": "A professional, empathetic draft reply addressing the customer's concern. Should acknowledge the issue, provide relevant information, and outline resolution steps."
            },
            "recommended_next_step": {
                "type": "string",
                "description": "A specific, actionable next step for the support agent to take after sending the reply."
            },
            "escalation_decision": {
                "type": "boolean",
                "description": "Whether this ticket should be escalated to a senior agent or specialist team."
            },
            "escalation_reason": {
                "type": ["string", "null"],
                "description": "If escalation is recommended, the specific reason why. Return null if no escalation needed."
            },
            "risk_level": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Overall risk level considering customer churn probability, revenue impact, and regulatory exposure."
            },
            "risk_justification": {
                "type": "string",
                "description": "Brief justification explaining the risk level assessment with specific factors considered."
            }
        },
        "required": [
            "category",
            "draft_reply",
            "recommended_next_step",
            "escalation_decision",
            "risk_level",
            "risk_justification",
        ]
    }
}


def build_user_message(customer_message: str, rag_context: list[str] | None = None) -> str:
    parts = [f"Analyze the following customer support ticket:\n\n---\n{customer_message}\n---"]

    if rag_context:
        context_block = "\n\n".join(rag_context)
        parts.append(
            f"\n\nRelevant knowledge base articles for context:\n\n{context_block}"
        )

    parts.append(
        "\n\nProvide a thorough analysis using the analyze_support_ticket tool."
    )

    return "".join(parts)
