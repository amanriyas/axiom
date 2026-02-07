"""Seed jurisdiction templates for multi-country onboarding support."""

import json
from sqlalchemy.orm import Session

from app.models import JurisdictionTemplate


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Jurisdiction Data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

JURISDICTIONS = {
    "US": {
        "name": "United States",
        "templates": {
            "employment_contract": {
                "content": """EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into as of {start_date}, by and between the Company and {name} ("Employee").

1. POSITION AND DUTIES
Employee is hired for the position of {role} in the {department} department. Employee shall report to {manager_email}.

2. AT-WILL EMPLOYMENT
Employment with the Company is at-will. Either party may terminate this relationship at any time, with or without cause or notice.

3. COMPENSATION
Employee shall receive a base salary as outlined in the attached compensation schedule, payable in accordance with the Company's standard payroll practices.

4. BENEFITS
Employee shall be entitled to participate in all benefit programs available to similarly situated employees, including health insurance, 401(k) retirement plan, and paid time off.

5. CONFIDENTIALITY
Employee agrees to maintain the confidentiality of all proprietary information and trade secrets of the Company.

6. INTELLECTUAL PROPERTY
All work product created by Employee during employment shall be the exclusive property of the Company.

7. NON-COMPETE
For a period of twelve (12) months following termination, Employee shall not engage in competitive activities within the Company's market.

8. GOVERNING LAW
This Agreement shall be governed by the laws of the State in which Employee is primarily based.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

Company: ________________________     Date: ________
Employee: {name}                       Date: ________""",
                "legal_requirements": json.dumps([
                    "At-will employment clause",
                    "Equal opportunity statement",
                    "FLSA compliance",
                    "I-9 employment verification reference",
                    "Workers' compensation notice",
                    "COBRA benefits reference",
                ]),
            },
            "nda": {
                "content": """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("NDA") is entered into as of {start_date}, by and between the Company ("Disclosing Party") and {name} ("Receiving Party").

1. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means any non-public information disclosed by the Company, including but not limited to business plans, source code, customer data, financial information, and trade secrets.

2. OBLIGATIONS OF RECEIVING PARTY
The Receiving Party agrees to:
a) Hold all Confidential Information in strict confidence
b) Not disclose Confidential Information to any third party without prior written consent
c) Use Confidential Information solely for employment purposes
d) Return all materials upon termination of employment

3. EXCLUSIONS
This NDA does not apply to information that:
a) Is or becomes publicly available through no fault of the Receiving Party
b) Was known to the Receiving Party prior to disclosure
c) Is independently developed without use of Confidential Information

4. TERM
This NDA shall remain in effect for two (2) years following termination of employment.

5. REMEDIES
The Receiving Party acknowledges that breach may cause irreparable harm and the Company may seek injunctive relief.

6. GOVERNING LAW
This NDA is governed by the laws of the applicable U.S. state.

Employee: {name}          Date: {start_date}
Position: {role}
Department: {department}""",
                "legal_requirements": json.dumps([
                    "Clear definition of confidential information",
                    "Duration of obligations",
                    "Permitted exceptions",
                    "Remedies for breach",
                    "DTSA compliance (Defend Trade Secrets Act)",
                ]),
            },
            "offer_letter": {
                "content": """OFFER OF EMPLOYMENT

Dear {name},

We are pleased to extend this offer of employment for the position of {role} within the {department} department.

START DATE: {start_date}
REPORTING TO: {manager_email}

COMPENSATION:
- Base salary as per the attached compensation schedule
- Eligible for annual performance bonus
- Stock options per the Company's equity incentive plan

BENEFITS:
- Comprehensive health, dental, and vision insurance
- 401(k) with company match up to 4%
- Unlimited PTO policy
- Parental leave (16 weeks)
- Annual learning & development budget: $2,000

EMPLOYMENT TERMS:
- Full-time, exempt position
- At-will employment
- Subject to background check and I-9 verification
- 90-day introductory period

This offer is contingent upon successful completion of a background check and verification of employment eligibility.

Please confirm your acceptance by signing below and returning this letter by [acceptance deadline].

Warm regards,
HR Team

I, {name}, accept this offer of employment.

Signature: ________________________     Date: ________""",
                "legal_requirements": json.dumps([
                    "At-will disclaimer",
                    "Contingency on background check",
                    "I-9 verification reference",
                    "EEO statement",
                    "Acceptance deadline",
                ]),
            },
        },
    },
    "UK": {
        "name": "United Kingdom",
        "templates": {
            "employment_contract": {
                "content": """CONTRACT OF EMPLOYMENT

This Contract of Employment is made between the Company and {name} ("Employee") in accordance with the Employment Rights Act 1996.

1. COMMENCEMENT
Your employment will commence on {start_date}. Your continuous period of employment begins on this date.

2. JOB TITLE AND DUTIES
You are employed as {role} in the {department} department, reporting to {manager_email}.

3. PLACE OF WORK
Your normal place of work shall be as notified by the Company. The Company reserves the right to require you to work at other locations.

4. HOURS OF WORK
Your normal working hours are 37.5 hours per week, Monday to Friday. Under the Working Time Regulations 1998, you have the right to opt out of the 48-hour weekly limit.

5. REMUNERATION
Your salary is payable monthly in arrears by bank transfer, subject to PAYE and National Insurance deductions.

6. HOLIDAY ENTITLEMENT
You are entitled to 25 days' paid annual leave plus 8 statutory bank holidays (pro rata). The holiday year runs from January to December.

7. SICK PAY
You are entitled to Statutory Sick Pay (SSP) and company sick pay as per the absence policy.

8. PENSION
You will be auto-enrolled in the Company's workplace pension scheme in accordance with the Pensions Act 2008.

9. NOTICE PERIOD
During the first two years: 1 month. Thereafter: 1 week per year of service up to 12 weeks.

10. RESTRICTIVE COVENANTS
Post-termination restrictions apply as set out in Schedule 1.

11. GOVERNING LAW
This contract is governed by the laws of England and Wales.

Signed by the Company: ________________________     Date: ________
Signed by the Employee: {name}                      Date: ________""",
                "legal_requirements": json.dumps([
                    "Written statement of employment under ERA 1996",
                    "Working Time Regulations 1998 compliance",
                    "National Minimum Wage compliance",
                    "Auto-enrolment pension (Pensions Act 2008)",
                    "GDPR data processing notice",
                    "Right to work in the UK verification",
                    "Statutory notice periods",
                ]),
            },
            "nda": {
                "content": """CONFIDENTIALITY AGREEMENT

This Confidentiality Agreement is entered into on {start_date} between the Company and {name} ("Employee").

1. DEFINITIONS
"Confidential Information" includes all information relating to the business, customers, finances, and operations of the Company that is not in the public domain.

2. OBLIGATIONS
The Employee shall:
a) Keep all Confidential Information strictly confidential
b) Not disclose to any third party without prior written consent
c) Use Confidential Information only for the purposes of employment
d) Take all reasonable steps to prevent unauthorised disclosure

3. EXCEPTIONS
Information shall not be considered Confidential if it:
a) Is or becomes publicly known other than through breach
b) Was already known to the Employee
c) Is required to be disclosed by law or regulation

4. DURATION
These obligations continue during employment and for 2 years following termination.

5. RETURN OF MATERIALS
Upon termination, all materials containing Confidential Information must be returned immediately.

6. DATA PROTECTION
Processing of personal data shall comply with the UK Data Protection Act 2018 and UK GDPR.

7. GOVERNING LAW
This Agreement is governed by the laws of England and Wales.

Employee: {name}
Position: {role} — {department}
Date: {start_date}""",
                "legal_requirements": json.dumps([
                    "UK GDPR and Data Protection Act 2018 compliance",
                    "Reasonable scope of restrictions",
                    "Garden leave provisions",
                    "Whistleblowing protection carve-out",
                ]),
            },
            "offer_letter": {
                "content": """OFFER OF EMPLOYMENT

Dear {name},

We are delighted to offer you the position of {role} within the {department} department.

START DATE: {start_date}
REPORTING TO: {manager_email}

COMPENSATION:
- Annual gross salary as per the attached schedule
- Annual performance review
- Company pension scheme with employer contribution

BENEFITS:
- 25 days annual leave plus bank holidays
- Private medical insurance
- Life assurance (4x salary)
- Cycle to work scheme
- Enhanced parental leave

EMPLOYMENT TERMS:
- Full-time, permanent position
- 37.5 hours per week
- Subject to right to work verification
- 6-month probationary period
- 1 month notice period (during probation: 1 week)

This offer is subject to satisfactory references, right to work verification, and DBS check (if applicable).

Please confirm your acceptance within 7 days.

Kind regards,
People Team

I, {name}, accept this offer of employment.

Signature: ________________________     Date: ________""",
                "legal_requirements": json.dumps([
                    "Right to work in UK verification",
                    "Statutory employment terms (ERA 1996 s.1)",
                    "Pension auto-enrolment details",
                    "Working hours and holiday entitlement",
                    "Probationary period terms",
                ]),
            },
        },
    },
    "AE": {
        "name": "United Arab Emirates",
        "templates": {
            "employment_contract": {
                "content": """EMPLOYMENT CONTRACT
(In accordance with UAE Federal Decree-Law No. 33 of 2021)

This Employment Contract is entered into between the Company ("Employer") and {name} ("Employee").

1. POSITION
Job Title: {role}
Department: {department}
Reports To: {manager_email}

2. CONTRACT TYPE AND DURATION
This is a limited/unlimited contract effective from {start_date}.

3. PROBATION PERIOD
The probationary period shall be six (6) months from the date of commencement. During this period, either party may terminate the contract with 14 days' written notice.

4. WORKING HOURS
Standard working hours: 8 hours per day, 48 hours per week (reduced during Ramadan to 6 hours per day).

5. SALARY AND BENEFITS
- Monthly basic salary as per the attached schedule (payable via WPS)
- Housing allowance
- Transportation allowance
- Annual air ticket to home country
- Medical insurance as per DHA/HAAD requirements

6. LEAVE ENTITLEMENTS
- Annual leave: 30 calendar days per year after one year of service
- Sick leave: 90 days per year (as per Article 31)
- Maternity leave: 60 days (as per Article 30)
- Public holidays: As per UAE Government announcements

7. END OF SERVICE GRATUITY
Employee is entitled to end-of-service gratuity as per Article 51 of the Labour Law.

8. VISA AND WORK PERMIT
The Employer shall sponsor the Employee's residence visa and work permit.

9. NON-COMPETE
Post-employment restrictions apply for 12 months within the UAE.

10. GOVERNING LAW
This contract is governed by UAE Federal Decree-Law No. 33 of 2021 and its amendments.

Employer: ________________________     Date: ________
Employee: {name}                       Date: ________""",
                "legal_requirements": json.dumps([
                    "UAE Federal Decree-Law No. 33 of 2021 compliance",
                    "MOHRE (Ministry of Human Resources) registration",
                    "Wage Protection System (WPS) compliance",
                    "Medical insurance as per emirate regulations",
                    "End-of-service gratuity provisions",
                    "Visa sponsorship terms",
                    "Arabic language version required",
                    "Ramadan working hours",
                ]),
            },
            "nda": {
                "content": """NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

This Agreement is entered into on {start_date} between the Company and {name} ("Employee"), position: {role}, department: {department}.

1. CONFIDENTIAL INFORMATION
Includes all business, technical, financial, and operational information of the Company and its clients in the UAE and internationally.

2. OBLIGATIONS
The Employee shall:
a) Maintain strict confidentiality of all proprietary information
b) Not disclose information to any third party
c) Use information solely for employment purposes
d) Comply with UAE data protection requirements (Federal Decree-Law No. 45 of 2021)

3. DURATION
Obligations survive termination for a period of two (2) years.

4. PENALTIES
Breach may result in disciplinary action, termination, and legal proceedings under UAE law.

5. GOVERNING LAW
This Agreement is governed by the laws of the United Arab Emirates.

Employee: {name}
Position: {role} — {department}
Date: {start_date}""",
                "legal_requirements": json.dumps([
                    "UAE Federal Decree-Law No. 45 of 2021 (Data Protection)",
                    "Reasonable scope under UAE Labour Law",
                    "Arabic translation may be required",
                    "DIFC/ADGM specific provisions if applicable",
                ]),
            },
            "offer_letter": {
                "content": """OFFER OF EMPLOYMENT

Dear {name},

We are pleased to offer you the position of {role} within the {department} department based in the United Arab Emirates.

START DATE: {start_date}
REPORTING TO: {manager_email}

COMPENSATION PACKAGE:
- Monthly basic salary as per attached schedule
- Housing allowance
- Transportation allowance
- Annual flight allowance (home country)
- Annual performance bonus (discretionary)

BENEFITS:
- Comprehensive medical insurance (employee + dependents)
- 30 calendar days annual leave
- End-of-service gratuity per UAE Labour Law
- Relocation assistance (if applicable)

EMPLOYMENT TERMS:
- Full-time position
- 6-month probationary period
- Company-sponsored residence visa and work permit
- Subject to medical fitness test and security clearance

This offer is contingent upon successful completion of medical examination and visa processing.

Please confirm your acceptance within 10 business days.

Best regards,
HR Department

I, {name}, accept this offer of employment.

Signature: ________________________     Date: ________""",
                "legal_requirements": json.dumps([
                    "MOHRE standard contract format",
                    "Medical fitness test requirement",
                    "Visa and work permit sponsorship",
                    "WPS salary payment compliance",
                    "End-of-service gratuity reference",
                ]),
            },
        },
    },
}


def seed_jurisdictions(db: Session) -> int:
    """Seed jurisdiction template data. Returns count of templates created."""
    count = 0

    for code, jurisdiction in JURISDICTIONS.items():
        # Check if templates already exist for this jurisdiction
        existing = (
            db.query(JurisdictionTemplate)
            .filter(JurisdictionTemplate.jurisdiction_code == code)
            .first()
        )
        if existing:
            continue

        for doc_type, template_data in jurisdiction["templates"].items():
            template = JurisdictionTemplate(
                jurisdiction_code=code,
                jurisdiction_name=jurisdiction["name"],
                document_type=doc_type,
                template_content=template_data["content"],
                legal_requirements=template_data["legal_requirements"],
            )
            db.add(template)
            count += 1

    db.commit()
    return count
