# Author: Miles Baird (https://github.com/kilometers)
# Portfolio analysis module

from portfolio.config import compare_blank_template, use_all_competencies

def generate_prompt():
    """Generate the prompt for portfolio analysis"""
    
    template = """
    Using the list of compentencies, you inspect high school student portfolios to identify points of alignment and deviation from our standards. Based on the competencies and output format below, rate and give feedback on the student portfolio presented to you. All student portfolios follow the same format, so avoid focusing on the organization of their website. There are some images which show their work, and beneath these you'll find descriptions of their experience and contributions, so you should comment on these and factor them into your analysis.
    
    Competencies:
    1. Sense of Belonging - Feeling connected to a learning community
    2. Growth Mindset - Belief that abilities can grow with effort
    3. STEAM Interest - Exploration of identity through STEAM
    4. Creativity - Ability to generate and adapt ideas
    5. Communication - Clear exchange of information
    6. Teamwork - Cooperative work with diverse peers
    7. Adaptability - Adjusting to change and uncertainty
    8. Problem-Solving - Identifying and solving challenges
    9. STEAM Agency - Capability with STEAM tools
    10. Self-Efficacy - Confidence in ability to succeed
    11. Persistence - Sustaining effort through challenges
    12. Opportunity Recognition - Identifying learning opportunities
    13. Continuous Learning - Ongoing skill development
    14. Social Capital - Building and leveraging connections
    
    Each competency is evaluated on a 1-10 scale across three levels:
    - Emerging (1-3)
    - Developing (4-7)
    - Proficient (8-10)
    
    Share your analysis in the following format:
    {
        "overall_feedback": "string"
        "competencies": {
            "creativity": {
                "value": 5,
                "evidence": "Student shows strong creativity...",
                "areas_for_improvement": "Student could work on...",
                "examples": "I ultimately got where I wanted...",
            },
            "adaptability": {
                "value": 7,
                "evidence": "The student shows strong..",
                "areas_for_improvement": "Further development could...",
                "examples": "And you just have to look...",
            }
            ...
        }
    }
    
    DO NOT leave further commentary outside of this format. If no competencies can be extracted, return an empty object for the competencies field.
    """
    
    return template
