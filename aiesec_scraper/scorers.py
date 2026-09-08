"""AIESEC B2C Relevance Scoring, Parallel Org Detection, and Opportunity Engine."""

import re
from typing import Dict, List, Optional, Tuple


PARALLEL_ORG_PATTERNS = {
    "IEEE": [r"\bieee\b", r"ieee\s+student\s+branch", r"ieee\s+egypt"],
    "Enactus": [r"\benactus\b"],
    "Hult Prize": [r"\bhult\s+prize\b", r"\bhult\b"],
    "Toastmasters": [r"\btoastmasters\b", r"toastmasters\s+club"],
    "Google Developer Group (GDG)": [r"\bgdg\b", r"google\s+developer\s+groups?", r"\bgdsc\b"],
    "TEDx": [r"\btedx\b", r"tedx[a-z]+"],
    "Rotaract": [r"\brotaract\b", r"rotary\s+youth"],
    "Model United Nations (MUN)": [r"\bmun\b", r"model\s+united\s+nations", r"\bcairo\s+mun\b"],
}

# High Priority (>= 8.5): Flagship Summits, Career Fairs, Hackathons
SUMMIT_PATTERNS = [
    r"\btechne(\s+summit)?\b", r"\briseup(\s+summit)?\b", r"\begypt\s+career\s+summit\b",
    r"\byouth\s+speak(\s+forum)?\b", r"\bshe\s+can(\s+summit)?\b", r"\bieee.*congress\b",
    r"\benactus.*(expo|exposition|national)\b", r"\bcairo\s+ict\b", r"\bseamless\s+(north\s+africa|egypt)\b",
    r"\bdelta\s+youth\b", r"\bcampus\s+leadership\b", r"\bcareers\s+forum\b", r"\bstartup\s+expo\b",
    r"\binnovation\s+expo\b", r"\bdemo\s+day\b",
    r"\b\w+\s+summit\b", r"\bsummit\b", r"\bقمة\b", r"\bرايز\s+أب\b", r"\bتكني\b",
    r"\bconclave\b", r"\bnational\s+congress\b"
]

CAREER_PATTERNS = [
    r"\bcareer\s+(fair|day|expo|summit|fest)\b", r"\bjob\s+(fair|day|expo)\b", r"\bemployment\s+(fair|day|expo)\b",
    r"\bhiring\s+(day|fair|event)\b", r"\binternship\s+(fair|day)\b", r"\brecruitment\s+(fair|day)\b",
    r"\bcv\s+clinic\b", r"\bmeet\s+the\s+mentor\b", r"\bfresh\s+graduate\b",
    r"\bملتقى\s+التوظيف\b", r"\bمعرض\s+التوظيف\b", r"\bيوم\s+التوظيف\b", r"\bملتقى\s+توظيف\b",
    r"\bفرص\s+تدريب\s+وتوظيف\b", r"\bملتقى\s+التشغيل\b", r"\bوظائف\b"
]

HACKATHON_PATTERNS = [
    r"\bhackathon\b", r"\bdatathon\b", r"\bideathon\b", r"\bcode\s+(jam|challenge|camp)\b",
    r"\bspace\s+apps\b", r"\brobotics\s+challenge\b", r"\bهاكاثون\b", r"\bتحدي\s+البرمجة\b",
    r"\bمسابقة\s+برمجة\b", r"\bcompetitive\s+programming\b"
]

# Medium Priority (6.0 - 8.4): Student Orgs, Workshops, Tech Meetups, Culture, Volunteering
STUDENT_ORG_PATTERNS = [
    r"\btoastmasters\b", r"\bieee\b", r"\benactus\b", r"\bhult\s+prize\b",
    r"\bgdg\b", r"\bgdsc\b", r"\bgoogle\s+developer\b", r"\btedx\b",
    r"\brotaract\b", r"\bmun\b", r"\bmodel\s+united\s+nations\b", r"\bstudent\s+union\b",
    r"\bstudent\s+activit(y|ies)\b", r"\baiesec\b", r"\bأنشطة\s+طلابية\b", r"\bاتحاد\s+طلاب\b",
    r"\bأسرة\s+طلابية\b", r"\bنموذج\s+محاكاة\b", r"\bstudent\s+branch\b", r"\bstudent\s+chapter\b"
]

UNIVERSITY_ACADEMIC_PATTERNS = [
    r"\buniversity\b", r"\bجامعة\b", r"\bfaculty\b", r"\bكلية\b", r"\bcampus\b", r"\bحرم\b",
    r"\bacademic\b", r"\bأكاديمي\b", r"\bundergraduate\b", r"\bcollege\b",
    r"\bconference\s+of\s+.*university\b", r"\buniversity.*conference\b",
    r"\bannual\s+scientific\s+conference\b", r"\bannual\s+scientific\s+meeting\b",
    r"\binternational\s+conference\b", r"\bscientific\s+conference\b",
    r"\bsymposium\b", r"\bندوة\b", r"\bcolloquium\b", r"\bforum\b", r"\bمنتدى\b",
    r"\bsuez\s+canal\b", r"\bain\s+shams\b", r"\bcairo\s+university\b",
    r"\balexandria\s+university\b", r"\bmansoura\s+university\b", r"\bassiut\s+university\b",
    r"\btanta\s+university\b", r"\bhelwan\s+university\b", r"\bzagazig\s+university\b",
    r"\bbenha\s+university\b", r"\bmenoufia\s+university\b", r"\bfayoum\s+university\b",
    r"\bbeni\s+suef\b", r"\bminya\s+university\b", r"\bsohag\s+university\b",
    r"\bsouth\s+valley\b", r"\baswan\s+university\b", r"\bport\s+said\s+university\b",
    r"\bdamietta\s+university\b", r"\bkafr\s+el\s+sheikh\b", r"\bdamanhour\b",
    r"\bal-azhar\b", r"\bazhar\b", r"\bauc\b", r"\bguc\b", r"\bbue\b", r"\bgiu\b",
    r"\bmust\b", r"\bmsa\b", r"\bfue\b", r"\bo6u\b", r"\bejust\b", r"\bnile\s+university\b",
    r"\bzewail\b", r"\bgalala\b", r"\balamein\b", r"\bking\s+salman\b", r"\bsphinx\b",
    r"\bمؤتمر\s+علمي\b", r"\bمؤتمر\s+دولي\b", r"\bالمؤتمر\s+السنوي\b", r"\bكلية\s+الهندسة\b",
    r"\bكلية\s+التجارة\b", r"\bكلية\s+الحاسبات\b", r"\bكلية\s+العلوم\b", r"\bكلية\s+الألسن\b"
]

STUDENT_HEALTHCARE_PATTERNS = [
    r"\bstudent\b", r"\bطلاب\b", r"\bundergraduate\b", r"\buniversity\b", r"\bجامعة\b",
    r"\bfaculty\s+of\s+medicine\b", r"\bfaculty\s+of\s+pharmacy\b", r"\bfaculty\s+of\s+dentistry\b",
    r"\bfaculty\s+of\s+physical\s+therapy\b", r"\bfaculty\s+of\s+nursing\b",
    r"\bكلية\s+الطب\b", r"\bكلية\s+الصيدلة\b", r"\bكلية\s+طب\s+الأسنان\b", r"\bكلية\s+العلاج\s+الطبيعي\b",
    r"\bifmsa\b", r"\bepsf\b", r"\bmedical\s+student\b", r"\btraining\s+program\b",
    r"\bبرنامج\s+تدريب\b", r"\bkasr\s+al\s+ainy\b", r"\bain\s+shams\s+medicine\b",
    r"\bazhar\s+assiut\b", r"\bsphinx\b", r"\bpaces\b", r"\bawareness\b"
]

TRAINING_EDUCATION_PATTERNS = [
    r"\btraining\b", r"\bتدريب\b", r"\bdiploma\b", r"\bدبلومة\b", r"\bcertification\b",
    r"\bشهادة\b", r"\bcourse\b", r"\bكورس\b", r"\bmasterclass\b", r"\bcurriculum\b",
    r"\bمنهج\b", r"\bprogram\b", r"\bبرنامج\b", r"\bacademy\b", r"\bأكاديمية\b",
    r"\bconsultation\b", r"\beducation\b", r"\bتعليم\b", r"\bexecutive\s+education\b"
]

SKILL_WORKSHOP_PATTERNS = [
    r"\bworkshop\b", r"\bmasterclass\b", r"\bpublic\s+speaking\b", r"\bsoft\s+skills\b",
    r"\bstartup\b", r"\bentrepreneur(ship)?\b", r"\bbootcamp\b", r"\bwebinar\b",
    r"\bmentorship\b", r"\bcoaching\b", r"\bnetworking\b", r"\broundtable\b",
    r"\bpanel\s+discussion\b", r"\bcreative\s+minds\b", r"\bleadership\b",
    r"\bورشة\s+عمل\b", r"\bسيشن\b", r"\bندوة\b", r"\bجلسة\s+حوارية\b", r"\bريادة\s+الأعمال\b",
    r"\bريادة\s+أعمال\b", r"\bتدريب\b", r"\bمحاضرة\b", r"\btraining\s+program\b"
]

TECH_DEV_PATTERNS = [
    r"\bdeveloper\b", r"\bsoftware\b", r"\bartificial\s+intelligence\b", r"\bai\s+agent(s)?\b",
    r"\bmachine\s+learning\b", r"\bcloud-native\b", r"\bcybersecurity\b", r"\bdata\s+science\b",
    r"\bpython\b", r"\bjavascript\b", r"\bweb\s+development\b", r"\bfrontend\b", r"\bbackend\b",
    r"\bdeep\s+learning\b", r"\bprogramming\b", r"\bdevops\b", r"\bui/ux\b", r"\bبرمجة\b",
    r"\bذكاء\s+اصطناعي\b", r"\bkotlin\b", r"\bsecurity\s+conference\b", r"\btech\b",
    r"\bintelligent\s+cities\b"
]

CULTURE_VOLUNTEER_PATTERNS = [
    r"\bvolunteer(ing)?\b", r"\bsdg(s)?\b", r"\bsustainable\s+development\b",
    r"\blanguage\s+exchange\b", r"\bcross-cultural\b", r"\bstudy\s+abroad\b",
    r"\berasmus\b", r"\bcultural\s+palace\b", r"\bculturewheel\b", r"\bart\s+space\b",
    r"\bfilm\s+screening\b", r"\bfilm\s+challenge\b", r"\bmedfest\b",
    r"\bgerman\s+language\b", r"\benglish\s+(club|speaking|practice)\b", r"\bfrench\s+culture\b",
    r"\bspanish\s+practice\b", r"\blanguage\s+practice\b", r"\bfolklore\b",
    r"\barts\s+festival\b", r"\bculture\b", r"\bتطوع\b", r"\bتبادل\s+ثقافي\b",
    r"\bعمل\s+تطوعي\b", r"\bسينما\b", r"\bأفلام\b", r"\bثقافة\b"
]

# Negative Penalties (Low Priority < 6.0)
MEDICAL_PATTERNS = [
    r"\bonco\w*\b", r"\bcancer\b", r"\bgastro\w*\b", r"\bhepato\w*\b",
    r"\bcardio\w*\b", r"\bderma\w*\b", r"\btmj\b", r"\bdental\b", r"\bdentistry\b",
    r"\bsurg(ery|ical|eon)\w*\b", r"\borthopedic\b", r"\bpediatric\w*\b", r"\bclinical\b",
    r"\bmedical\s+(congress|conference|symposium|meeting|summit)\b", r"\bphysician\b",
    r"\bradiolog\w*\b", r"\bendocrin\w*\b", r"\bophthalmol\w*\b", r"\bgynecol\w*\b",
    r"\bnephrol\w*\b", r"\burolog\w*\b", r"\bpatholog\w*\b", r"\banaesthes\w*\b",
    r"\bmedicine\s+course\b", r"\batls\b", r"\bacls\b", r"\bobgyn\b", r"\bpharmac\w*\b",
    r"\bpharmaceutical\b", r"\bmedtech\s+b2b\b", r"\bnutriderma\b", r"\bendoegypt\b",
    r"\bendo\s+delta\b", r"\bueg\b", r"\bcamred\b", r"\bresuscitation\b", r"\bswallowing\b",
    r"\bcto\s+congress\b", r"\bespai\b", r"\bcardiology\b",
    r"\bطب\s+بشري\b", r"\bمؤتمر\s+طبي\b", r"\bجراحة\b", r"\bأورام\b", r"\bجلدية\b",
    r"\bأسنان\b", r"\bنساء\s+وتوليد\b", r"\bكبد\s+وجهاز\s+هضمي\b", r"\bعظام\b",
    r"\bقلب\s+وأوعية\b", r"\bعيون\b", r"\bأطفال\b", r"\bصيدلة\b"
]

INDUSTRIAL_B2B_PATTERNS = [
    r"\btextile\s+machiner\w*\b", r"\btrade\s+expo\b", r"\bindustrial\s+expo\b",
    r"\bbanking\s+summit\b", r"\bconnected\s+banking\b", r"\bcorporate\s+governance\b",
    r"\bpaper\s+(me|industry|manufacturing)\b", r"\bpackaging\b", r"\bheavy\s+machiner\w*\b",
    r"\bpetrochem\w*\b", r"\boil\s+(&|and)\s+gas\b", r"\bchemical\s+manufacturing\b",
    r"\bprocurement\b", r"\bchina\s+trade\b", r"\blogistics\s+(&|and)\s+freight\b",
    r"\bmaritime\s+trade\b", r"\bplastic\s+manufacturing\b", r"\baqua\s+energy\b",
    r"\bcteie\b", r"\bndix\b", r"\biex\s+egypt\b", r"\bautomotive\s+trade\b",
    r"\bcfo\s+summit\b", r"\bdenim\w*\b", r"\bbiodiesel\b", r"\bvendor\s+show\b",
    r"\bمعرض\s+صناعي\b", r"\bصناعات\s+ثقيلة\b", r"\bبترول\b", r"\bتغليف\b",
    r"\bتجارة\s+دولية\b"
]

ENTERTAINMENT_LEISURE_PATTERNS = [
    r"\bwedding\b", r"\bdisco\b", r"\bparty\b", r"\bnightclub\b", r"\bdj\s+night\b",
    r"\bcoffee\s+(morning|meetup|club)\b", r"\bstandup\s+comedy\b", r"\bcomedy\s+night\b",
    r"\bcomedy\s+show\b", r"\bconcert\b", r"\balbum\s+release\b", r"\bbeach\b",
    r"\bdesert\s+adventure\b", r"\bcamp\s+-\s+overnight\b", r"\bstargazing\b",
    r"\bpilates\b", r"\byoga\b", r"\bfitness\s+challenge\b", r"\bgame\s+night\b",
    r"\bحفل\s+زفاف\b", r"\bسهرة\b", r"\bحفلة\s+غنائية\b", r"\bستاند\s+آب\s+كوميدي\b",
    r"\bرحلة\b", r"\bكامب\b"
]


class B2CScorer:
    """
    Evaluates Egyptian events against AIESEC youth recruitment and partnership criteria.
    
    Calibrated Scoring Rubric:
    - HIGH Priority (>= 8.5): Top 15-20% tier. Official Flagship Summits, University Career Fairs,
      Student Hackathons, and Major Campus Congresses.
    - MEDIUM Priority (6.0 - 8.4): Student Org sessions (Toastmasters, IEEE, GDG), Youth Leadership Workshops,
      Developer Meetups, Volunteering, SDGs & Intercultural Exchanges.
    - LOW Priority (< 6.0): Specialized Clinical Medical Conferences, B2B Industrial Machinery Fairs,
      Nightlife / Entertainment / Weddings, Casual Coffee Meetups, and General Non-Youth Events.
    """

    def __init__(self, custom_rules: Optional[Dict] = None):
        self.rules = custom_rules

    def detect_parallel_org(self, text: str) -> Optional[str]:
        """Detects if an event is organized by or partnered with a known student/youth org."""
        lower_text = text.lower()
        for org_name, patterns in PARALLEL_ORG_PATTERNS.items():
            for p in patterns:
                if re.search(p, lower_text, re.IGNORECASE):
                    return org_name
        return None

    def evaluate(self, title: str, description: str = "", location: str = "") -> Tuple[float, str, str, List[str], str, Optional[str]]:
        """
        Calculates the calibrated B2C opportunity score and determines relevant tags.
        
        Returns:
            (b2c_score, b2c_priority, primary_category, tags, recommended_action, parallel_org)
        """
        t = (title or "").strip()
        d = (description or "").strip()
        loc = (location or "").strip()

        # Check for parallel youth organization
        combined_text = f"{t} {d} {loc}".lower()
        detected_org = self.detect_parallel_org(combined_text)

        full_text = f"{t} {d}".lower()
        t_lower = t.lower()

        # -------------------------------------------------------------
        # 1. Negative Filter Checks (Clinical, Industrial B2B, Nightlife/Leisure)
        # -------------------------------------------------------------
        # Medical / Clinical check
        for p in MEDICAL_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE) or re.search(p, full_text, re.IGNORECASE):
                # Distinguish student/university healthcare training from purely clinical adult surgeon congresses
                if any(re.search(sp, full_text, re.IGNORECASE) for sp in STUDENT_HEALTHCARE_PATTERNS):
                    tags = ["medical", "healthcare", "university", "student_training"]
                    if detected_org:
                        tags.insert(0, detected_org)
                    return (
                        7.2,
                        "MEDIUM",
                        "Healthcare & Medical Education",
                        tags,
                        "Target Medical, Dental & Pharmacy Undergraduates for AIESEC Global Volunteer Projects",
                        detected_org
                    )
                tags = ["medical", "clinical", "b2b"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    2.5,
                    "LOW",
                    "Medical & Clinical Congress",
                    tags,
                    "Do Not Deploy (Niche Clinical Target - Incompatible with Youth B2C)",
                    detected_org
                )

        # Industrial B2B check
        for p in INDUSTRIAL_B2B_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE) or re.search(p, full_text, re.IGNORECASE):
                tags = ["trade_expo", "b2b", "industry"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    3.0,
                    "LOW",
                    "B2B & Industrial Trade Expo",
                    tags,
                    "Low Priority B2C / Evaluate solely for B2B Corporate Sponsorship",
                    detected_org
                )

        # Entertainment / Private / Leisure check
        for p in ENTERTAINMENT_LEISURE_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE) or (
                re.search(p, full_text, re.IGNORECASE) and not any(re.search(s, t_lower) for s in SUMMIT_PATTERNS + CAREER_PATTERNS)
            ):
                tags = ["entertainment", "social", "leisure"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    2.8,
                    "LOW",
                    "Social & Entertainment",
                    tags,
                    "General Monitoring (Social / Leisure)",
                    detected_org
                )

        # -------------------------------------------------------------
        # 2. Positive Scoring Tiers (Title carries primary weight)
        # -------------------------------------------------------------
        # Check Flagship Summits in Title
        for p in SUMMIT_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE):
                tags = ["summit", "flagship", "youth", "leadership"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    9.8,
                    "HIGH",
                    "Flagship Summits",
                    tags,
                    "Major National Activation: Deploy LC Delegation, Booth Presence & Global Volunteer Recruitment",
                    detected_org
                )

        # Check Career & Job Fairs in Title
        for p in CAREER_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE):
                tags = ["career", "job fair", "student", "cv", "internship"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    9.2,
                    "HIGH",
                    "Career & Recruitment Fairs",
                    tags,
                    "Booth Booking & Direct Lead Generation for Global Talent / Teacher",
                    detected_org
                )

        # Check Hackathons in Title or Text
        for p in HACKATHON_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE) or re.search(p, full_text, re.IGNORECASE):
                tags = ["hackathon", "tech", "coding", "students"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    8.9,
                    "HIGH",
                    "Tech & Student Hackathons",
                    tags,
                    "Promote Global Talent IT & Tech Internship Opportunities",
                    detected_org
                )

        # Secondary Summit check in description
        for p in SUMMIT_PATTERNS:
            if re.search(p, full_text, re.IGNORECASE):
                tags = ["summit", "youth", "networking"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    9.2,
                    "HIGH",
                    "Flagship Summits",
                    tags,
                    "National Activation: Secondary Presence & Digital Lead Harvesting",
                    detected_org
                )

        # Secondary Career check in description
        for p in CAREER_PATTERNS:
            if re.search(p, full_text, re.IGNORECASE):
                tags = ["career", "job fair", "student", "cv", "internship"]
                if detected_org:
                    tags.insert(0, detected_org)
                return (
                    8.8,
                    "HIGH",
                    "Career & Recruitment Fairs",
                    tags,
                    "Campus Lead Generation: Distribute Global Talent flyers & recruit delegates",
                    detected_org
                )

        # Check Student Organizations & Campus Leadership
        if detected_org:
            is_major = any(w in t_lower or w in full_text for w in ["conference", "congress", "summit", "annual", "mega", "expo", "symposium", "national"])
            score = 9.0 if is_major else 8.0
            prio = "HIGH" if is_major else "MEDIUM"
            tags = [detected_org, "student", "campus", "youth", "leadership"]
            return (
                score,
                prio,
                "Student Orgs & Campus Leadership",
                tags,
                f"Partner Outreach with {detected_org}: Joint Activation / PR Collaboration",
                detected_org
            )

        # Check University & Academic Conferences (Major Campus Events)
        is_univ = any(re.search(p, t_lower, re.IGNORECASE) for p in UNIVERSITY_ACADEMIC_PATTERNS)
        is_conf = any(re.search(p, t_lower, re.IGNORECASE) for p in [
            r"\bconference\b", r"\bcongress\b", r"\bsymposium\b", r"\bforum\b",
            r"\binternational\b", r"\bannual\b", r"\bمؤتمر\b", r"\bندوة\b", r"\bمنتدى\b"
        ])
        if is_univ and is_conf:
            tags = ["university", "academic", "conference", "campus", "youth"]
            if detected_org:
                tags.insert(0, detected_org)
            return (
                8.7,
                "HIGH",
                "University Conferences & Academic Forums",
                tags,
                "Major Campus Activation: Deploy LC Delegation, Booth Presence & Recruit University Students",
                detected_org
            )
        elif is_univ or (is_conf and any(re.search(p, full_text, re.IGNORECASE) for p in UNIVERSITY_ACADEMIC_PATTERNS)):
            tags = ["campus", "students", "youth", "education"]
            if detected_org:
                tags.insert(0, detected_org)
            return (
                7.8,
                "MEDIUM",
                "Campus & Student Activities",
                tags,
                "Campus Outreach: Engage Student Attendees & Student Union Partners",
                detected_org
            )

        for p in STUDENT_ORG_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE) or re.search(p, full_text, re.IGNORECASE):
                tags = ["student_org", "campus", "youth", "leadership"]
                return (
                    7.8,
                    "MEDIUM",
                    "Student Orgs & Campus Leadership",
                    tags,
                    "Partner Outreach: Co-marketing, Joint Booth, or Workshop Collaboration",
                    detected_org
                )

        # Check Youth Leadership & Skills Workshops / Professional Training
        for p in SKILL_WORKSHOP_PATTERNS + TRAINING_EDUCATION_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE):
                tags = ["workshop", "skills", "leadership", "development"]
                return (
                    7.5,
                    "MEDIUM",
                    "Youth Leadership & Skills Workshops",
                    tags,
                    "Speaker Outreach, Workshop Co-hosting & AIESEC Presentation",
                    detected_org
                )
            elif re.search(p, full_text, re.IGNORECASE):
                tags = ["workshop", "training", "skills"]
                return (
                    6.8,
                    "MEDIUM",
                    "Youth Leadership & Skills Workshops",
                    tags,
                    "Workshop Attendee Outreach & Digital Flyer Drops",
                    detected_org
                )

        # Check Tech Communities & Meetups
        for p in TECH_DEV_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE):
                tags = ["tech", "developer", "software", "innovation"]
                return (
                    7.2,
                    "MEDIUM",
                    "Tech Communities & Innovation",
                    tags,
                    "Promote Global Talent IT Opportunities",
                    detected_org
                )
            elif re.search(p, full_text, re.IGNORECASE):
                tags = ["tech", "software", "meetup"]
                return (
                    6.5,
                    "MEDIUM",
                    "Tech Communities & Innovation",
                    tags,
                    "Tech Talent Sourcing for Global Talent",
                    detected_org
                )

        # Check Culture & Volunteering
        for p in CULTURE_VOLUNTEER_PATTERNS:
            if re.search(p, t_lower, re.IGNORECASE):
                tags = ["culture", "volunteering", "sdg", "exchange"]
                return (
                    7.0,
                    "MEDIUM",
                    "Volunteering, SDGs & Cultural Exchange",
                    tags,
                    "Promote Global Volunteer Projects & SDG Alignment",
                    detected_org
                )
            elif re.search(p, full_text, re.IGNORECASE):
                tags = ["cultural", "arts", "community"]
                return (
                    6.2,
                    "MEDIUM",
                    "Volunteering, SDGs & Cultural Exchange",
                    tags,
                    "Promote Cross-Cultural Exchange",
                    detected_org
                )

        # Default Neutral General Events
        tags = ["general"]
        return (
            4.0,
            "LOW",
            "General Event",
            tags,
            "General Monitoring for potential youth presence",
            detected_org
        )

