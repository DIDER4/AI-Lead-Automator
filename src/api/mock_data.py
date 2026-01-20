"""
Mock Data Generator
Provides realistic mock data for testing without API keys
"""

import hashlib
from typing import Dict


class MockDataGenerator:
    """Generate consistent mock data for testing"""
    
    @staticmethod
    def get_mock_scraped_content(url: str) -> str:
        """
        Generate realistic mock website content
        
        Args:
            url: URL being scraped
            
        Returns:
            Mock markdown content
        """
        # Generate unique but consistent content based on URL
        url_hash = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
        
        companies = [
            ("TechFlow Solutions", "Cloud-based workflow automation", "B2B SaaS, Enterprise Software"),
            ("DataSync Pro", "Real-time data integration platform", "Data Analytics, API Integration"),
            ("CustomerFirst AI", "AI-powered customer success management", "AI/ML, Customer Service"),
            ("SecureVault Systems", "Enterprise security and compliance", "Cybersecurity, Compliance"),
            ("GrowthMetrics", "Marketing analytics and attribution", "Marketing Technology, Analytics")
        ]
        
        company, product, industry = companies[url_hash % len(companies)]
        employee_count = 20 + (url_hash % 180)
        founded_year = 2015 + (url_hash % 10)
        
        return f"""# {company}

## About Us
Welcome to {company}! We are a leading provider of {product.lower()}.
Founded in {founded_year}, we've been serving businesses across Europe and North America.

## Our Solution
Our platform offers:
- {product}
- Seamless integration with major business tools
- Enterprise-grade security and compliance
- 24/7 customer support
- Scalable infrastructure for growing businesses

## Industries We Serve
{industry}

## Company Information
- **Team Size**: {employee_count}+ employees
- **Founded**: {founded_year}
- **Headquarters**: Copenhagen, Denmark
- **Locations**: Denmark, UK, Germany, USA

## Our Clients
We work with Fortune 500 companies, mid-sized enterprises, and fast-growing startups.
Our clients value our commitment to innovation, security, and customer success.

## Technology Stack
Built with modern technologies:
- Cloud-native architecture (AWS/Azure)
- AI and machine learning capabilities
- RESTful APIs and webhooks
- SOC 2 Type II certified
- GDPR compliant

## Contact Information
Email: contact@{company.lower().replace(' ', '')}.com
Phone: +45 {20 + (url_hash % 80)} {10 + (url_hash % 90)} {1000 + (url_hash % 9000)}
Website: {url}

## Recent News
We recently closed a Series B funding round and expanded our operations to the US market.
Our platform now serves over {100 + (url_hash % 400)} enterprise customers worldwide.
"""
    
    @staticmethod
    def get_mock_metadata(url: str) -> dict:
        """
        Generate realistic mock metadata
        
        Args:
            url: URL being scraped
            
        Returns:
            Mock metadata dictionary
        """
        url_hash = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
        
        companies = [
            "TechFlow Solutions",
            "DataSync Pro", 
            "CustomerFirst AI",
            "SecureVault Systems",
            "GrowthMetrics"
        ]
        
        company = companies[url_hash % len(companies)]
        
        return {
            "title": f"{company} - Enterprise Software Solutions",
            "description": f"Leading provider of B2B software solutions for modern enterprises. {company} helps businesses automate and scale their operations.",
            "language": "en",
            "url": url,
            "statusCode": 200,
            "ogTitle": f"{company}",
            "ogDescription": "Enterprise software solutions for growing businesses"
        }
    
    @staticmethod
    def get_mock_lead_analysis(content: str, user_profile: Dict, url: str) -> Dict:
        """
        Generate realistic mock AI lead analysis
        
        Args:
            content: Scraped content (mock or real)
            user_profile: User's company profile
            url: URL being analyzed
            
        Returns:
            Mock analysis dictionary
        """
        # Generate consistent but varied results based on URL
        url_hash = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
        
        # Extract company name from content or generate one
        lines = content.split('\n')
        company_name = "Test Company"
        for line in lines:
            if line.startswith('# '):
                company_name = line.replace('# ', '').strip()
                break
        
        # Score based on URL hash (but realistic distribution)
        base_score = 45 + (url_hash % 50)  # Score between 45-95
        
        industries = [
            "B2B SaaS",
            "Enterprise Software",
            "Data Analytics",
            "Cybersecurity",
            "Marketing Technology",
            "Cloud Infrastructure",
            "AI/Machine Learning",
            "Customer Success"
        ]
        
        industry = industries[url_hash % len(industries)]
        
        # Determine qualification
        is_qualified = base_score >= 70
        action = "Qualified" if is_qualified else "Further Research" if base_score >= 60 else "Disqualified"
        
        fit_reasons = [
            "Strong alignment with our ICP in terms of company size and technology stack",
            "Excellent fit - they serve similar customer segments and face challenges we solve",
            "Good potential - their growth stage matches our ideal customer profile",
            "Moderate fit - some alignment but may need further qualification",
            "Limited alignment with our ICP, but worth exploring specific use cases"
        ]
        
        return {
            "lead_score": base_score,
            "score_rationale": f"Based on the website analysis, {company_name} scores {base_score}/100. They operate in {industry} which aligns with our target market. {fit_reasons[url_hash % len(fit_reasons)]}. The company demonstrates strong digital presence and appears to have the budget for enterprise solutions.",
            "company_name": company_name,
            "industry": industry,
            "key_insights": f"• {company_name} focuses on enterprise B2B solutions\n• Strong emphasis on innovation and modern technology stack\n• Active in the {industry} space with proven customer base\n• Website demonstrates professional brand positioning\n• Clear value proposition aligned with market needs",
            "fit_analysis": f"The company shows {'strong' if is_qualified else 'moderate'} alignment with our ICP. They operate in the {industry} sector and demonstrate characteristics of companies that benefit from our solution. {'Their technology-forward approach and enterprise focus make them an ideal prospect.' if is_qualified else 'Further research needed to validate budget authority and immediate need.'}",
            "personalized_email": f"""Subject: {company_name} + [Your Company]: Streamlining {industry} Operations

Hi [Name],

I came across {company_name} and was impressed by your work in {industry}. 

Many companies in your space face challenges with [relevant pain point]. We've helped similar organizations achieve [specific outcome].

Would you be open to a brief 15-minute call to explore if there's a fit?

Best regards,
[Your Name]""",
            "sms_draft": f"Hi! Saw {company_name}'s work in {industry}. We help similar companies [benefit]. Quick chat?",
            "recommended_action": action
        }
