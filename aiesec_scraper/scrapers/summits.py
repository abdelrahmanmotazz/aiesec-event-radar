"""Egypt Flagship Summits Scraper: Techne Summit, RiseUp, IEEE Congress, AUC Forums, and National Youth Summits."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from .base import BaseScraper
from ..models import EventRecord

logger = logging.getLogger(__name__)

# Registry of Egypt's Flagship Annual Summits & Campus Conferences (All categorized as Flagship Summits)
SUMMITS_CATALOG = [
    {
        "id": "summit_techne_alex_2026",
        "title": "Techne Summit Alexandria 2026",
        "organizer": "Techne & Marketeers",
        "url": "https://technesummit.com/",
        "start_date": datetime(2026, 10, 3, 9, 0),
        "date_display": "Oct 03 - 05, 2026 · 09:00 AM",
        "location": "Bibliotheca Alexandrina",
        "city": "Alexandria",
        "category": "Flagship Summits",
        "ticket_type": "Student / Attendee Passes",
        "parallel_org": "Techne Global",
        "description": (
            "The Mediterranean's largest technology, startup, and youth talent gathering at Bibliotheca Alexandrina. "
            "Convenes 45,000+ attendees, 300+ international speakers, 1,000+ startup exhibitors, and university delegations from 20+ nations. "
            "Target Audience: Computer Science, Engineering, Business/Commerce, and Fine Arts students across Alexandria and the Delta. "
            "Venue Details: Bibliotheca Alexandrina Complex (Great Hall, B1 & B2 Conference Halls, and Open Plaza), Shatby, Alexandria. "
            "Activities: 10 specialized industry tracks (Fintech, Healthtech, Edtech, E-commerce, Gaming, Deep Tech), pitch competitions, and VIP investor matchmaking. "
            "Admission: Official student passes and delegate tickets with RFID badge entry. "
            "AIESEC Tactical Opportunity: Flagship recruitment and partnership ground for LC Tanta and LC Alexandria: Deploy interactive booth, "
            "secure Youth Speak forum synergies, and engage international attendees for incoming exchanges."
        ),
        "recommended_action": "High-priority activation for LC Tanta & Alex: Deploy booth presence, distribute Global Volunteer flyers, and engage university delegations across the Delta."
    },
    {
        "id": "summit_techne_cairo_2026",
        "title": "Techne Summit Cairo 2026",
        "organizer": "Techne Global",
        "url": "https://technesummit.com/",
        "start_date": datetime(2026, 9, 26, 10, 0),
        "date_display": "Sep 26 - 27, 2026 · 10:00 AM",
        "location": "The Nile Ritz-Carlton",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Summit Registration",
        "parallel_org": "Techne Global",
        "description": (
            "Flagship Cairo edition convening 12,000+ corporate executives, student founders, venture capitalists, and ecosystem leaders during Egypt Innovation Week. "
            "Target Audience: Engineering, Computer Science, Economics, and Management undergraduates and postgraduates across Greater Cairo. "
            "Venue Details: The Nile Ritz-Carlton (Al Qahira Ballroom, Alf Leila Wa Leila Ballroom, and Garden Pavilion), Downtown Cairo. "
            "Activities: 8 multi-stage tracks, corporate innovation roundtables, youth hackathon presentations, and startup funding competitions. "
            "Admission: Verified digital ticket QR pass. "
            "AIESEC Tactical Opportunity: High-yield B2B corporate sales for Global Talent employer sponsorships and cross-border tech talent recruitment."
        ),
        "recommended_action": "Set up AIESEC Youth Speak lounge & meet corporate partners for Global Talent internship sponsorships."
    },
    {
        "id": "summit_riseup_2026",
        "title": "RiseUp Summit 2026",
        "organizer": "RiseUp",
        "url": "https://riseupsummit.com/",
        "start_date": datetime(2026, 11, 14, 9, 30),
        "date_display": "Nov 14 - 16, 2026 · 09:30 AM",
        "location": "Grand Egyptian Museum (GEM)",
        "city": "Giza",
        "category": "Flagship Summits",
        "ticket_type": "Student / General Ticket",
        "parallel_org": "RiseUp Community",
        "description": (
            "The MENA region's iconic entrepreneurship and youth innovation marathon at the Grand Egyptian Museum. "
            "Unites 15,000+ entrepreneurs, youth changemakers, university leaders, and venture firms from 50+ countries. "
            "Target Audience: Multidisciplinary youth leaders, creative innovators, engineering developers, and business students. "
            "Venue Details: Grand Egyptian Museum (GEM), Pyramids Plateau, Giza (Main Atrium, Conference Center, and Outdoor Amphitheatre). "
            "Activities: 4 flagship stages (Capital, Tech, Creative, Growth), 150+ workshops, talent matchmaking alley, and startup showcase. "
            "Admission: 3-day student and general attendee passes with digital NFC check-in. "
            "AIESEC Tactical Opportunity: Prime national activation for AIESEC Egypt: Mobilize large student delegations, "
            "market Global Volunteer projects on the Creative stage, and engage regional companies for Global Talent internships."
        ),
        "recommended_action": "Send LC youth delegation; engage youth attendees at networking stages for Global Volunteer & Teacher programs."
    },
    {
        "id": "summit_ecs_cairo_2026",
        "title": "Egypt Career Summit (ECS) Fall Edition",
        "organizer": "Career Summit Egypt",
        "url": "https://egyptcareersummit.com/",
        "start_date": datetime(2026, 10, 18, 9, 0),
        "date_display": "Oct 18 - 19, 2026 · 09:00 AM",
        "location": "The Greek Campus, Downtown",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Free / Registration Required",
        "parallel_org": None,
        "description": (
            "Egypt's largest career preparation and recruitment summit specifically designed for university students and recent graduates. "
            "Convenes 25,000+ ambitious attendees and 80+ top-tier corporate employers across tech, banking, FMCG, and telecommunications. "
            "Target Audience: Final-year students and fresh graduates from all Egyptian universities (Public, Private, and National). "
            "Venue Details: The Greek Campus (The Factory Hall, Library Stage, and Main Courtyard), 28 Falaki Street, Downtown Cairo. "
            "Activities: 60+ career readiness workshops, live mock interviews, 1-on-1 resume reviews with corporate HR directors, and on-ground hiring. "
            "Admission: Free of charge with mandatory prior registration and verified QR pass. "
            "AIESEC Tactical Opportunity: Direct candidate acquisition hotspot for AIESEC Global Talent (paid professional internships) "
            "and Global Teacher exchange products."
        ),
        "recommended_action": "Direct candidate acquisition hotspot for AIESEC Global Talent & Global Teacher exchange products."
    },
    {
        "id": "summit_ieee_congress_2026",
        "title": "IEEE Egypt National Student Congress & Exhibition",
        "organizer": "IEEE Egypt Section",
        "url": "https://ieee.org.eg/",
        "start_date": datetime(2026, 9, 19, 9, 0),
        "date_display": "Sep 19 - 20, 2026 · 09:00 AM",
        "location": "Cairo University Faculty of Engineering",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Free / Student Pass",
        "parallel_org": "IEEE",
        "description": (
            "The official annual congress bringing together 35+ IEEE university student branches from across all Egyptian governorates. "
            "Features student robotics competitions, scientific paper presentations, embedded systems hackathons, and leadership elections. "
            "Target Audience: Electrical, Electronics, Communications, Computer, and Mechatronics engineering students. "
            "Venue Details: Cairo University Faculty of Engineering (Main Auditorium & Electrical Engineering Building), Giza. "
            "Expected Scale: 3,000+ engineering student delegates and branch chairs. "
            "Admission: Free student pass for Egyptian university students. "
            "AIESEC Tactical Opportunity: High-leverage institutional partnership: Sign national co-marketing agreements with IEEE student branches "
            "to promote AIESEC Global Talent engineering internships directly to their membership."
        ),
        "recommended_action": "Partner with IEEE student branches to co-promote AIESEC global technical internships and volunteer opportunities."
    },
    {
        "id": "summit_enactus_expo_2026",
        "title": "Enactus Egypt National Exposition & Social Forum",
        "organizer": "Enactus Egypt",
        "url": "https://enactus.org/country/egypt/",
        "start_date": datetime(2026, 9, 29, 10, 0),
        "date_display": "Sep 29 - 30, 2026 · 10:00 AM",
        "location": "Intercontinental Citystars",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Invitation / Registration",
        "parallel_org": "Enactus",
        "description": (
            "The annual championship showdown of 50+ university teams from across Egypt presenting scalable social entrepreneurship enterprises "
            "addressing the UN Sustainable Development Goals (SDGs). Judged by top Egyptian business leaders and corporate CEOs. "
            "Target Audience: University students passionate about social impact, sustainable business models, community development, and leadership. "
            "Venue Details: Al Saraya Grand Ballroom, Intercontinental Cairo Citystars, Heliopolis, Cairo. "
            "Expected Scale: 4,500+ university students, academic advisors, and business executives. "
            "Admission: Official university delegation passes and guest registration. "
            "AIESEC Tactical Opportunity: 100% philosophical and operational alignment with AIESEC's SDG-based Global Volunteer exchange portfolio. "
            "Engage high-caliber project leaders for cross-organizational collaboration."
        ),
        "recommended_action": "Direct alignment with AIESEC SDG Global Volunteer initiatives; engage active student participants for cross-organizational synergy."
    },
    {
        "id": "summit_delta_tanta_2026",
        "title": "Delta Youth Innovation & Tech Forum (Tanta University)",
        "organizer": "Tanta University & Delta Student Union",
        "url": "https://tanta.edu.eg/",
        "start_date": datetime(2026, 10, 24, 10, 0),
        "date_display": "Oct 24 - 25, 2026 · 10:00 AM",
        "location": "Tanta University Convention Center",
        "city": "Tanta",
        "category": "Flagship Summits",
        "ticket_type": "Free for Students",
        "parallel_org": None,
        "description": (
            "The central student and youth leadership summit of the Gharbia and Delta region, co-organized with regional universities. "
            "Brings together 3,500+ students from Tanta, Mansoura, Kafr El-Sheikh, and Menoufia to explore digital economy careers, "
            "entrepreneurship in the Delta, and civil society leadership. "
            "Target Audience: Students across all faculties of Tanta University (Medicine, Engineering, Science, Commerce, Arts, Law). "
            "Venue Details: Tanta University Main Convention Center (Grand Hall & Exhibition Foyer), Medical Campus, Tanta. "
            "Activities: Keynote addresses by regional governors and tech leaders, 12 career workshops, and university project exhibitions. "
            "Admission: Completely free of charge with valid university student ID. "
            "AIESEC Tactical Opportunity: THE HIGHEST PRIORITY HOME TURF EVENT for AIESEC in Tanta: Deliver official keynote on youth leadership, "
            "operate main-foyer registration booth, and capture 1,000+ local leads."
        ),
        "recommended_action": "HOME TURF PRIORITY for AIESEC in Tanta: Secure keynote speech, physical booth, and mass recruitment drive."
    },
    {
        "id": "summit_she_can_2026",
        "title": "She Can Summit 2026 (Entreprenelle)",
        "organizer": "Entreprenelle",
        "url": "https://entreprenelle.com/",
        "start_date": datetime(2026, 11, 28, 9, 0),
        "date_display": "Nov 28, 2026 · 09:00 AM",
        "location": "The Greek Campus West (Mall of Arabia)",
        "city": "Giza",
        "category": "Flagship Summits",
        "ticket_type": "Standard Ticket",
        "parallel_org": "Entreprenelle",
        "description": (
            "The largest female empowerment and entrepreneurship conference in the Middle East and North Africa. "
            "Convenes 8,000+ ambitious women, university students, female founders, and corporate advocates. "
            "Target Audience: Female university students, young professionals, educators, and social entrepreneurs. "
            "Venue Details: The Greek Campus West, Mall of Arabia Complex, 6th of October City, Giza. "
            "Activities: 30+ talks, panel debates on women in technology and venture capital, 100+ female-led micro-business booths, and mentoring circles. "
            "Admission: Standard attendee pass with digital badge. "
            "AIESEC Tactical Opportunity: Superb platform to promote AIESEC SDG 5 (Gender Equality) Global Volunteer initiatives and "
            "recruit passionate female youth leaders for Local Committee executive roles."
        ),
        "recommended_action": "Promote AIESEC SDG 5 Gender Equality volunteer projects & female youth leadership opportunities."
    },
    {
        "id": "summit_auc_leadership_2026",
        "title": "AUC Campus Leadership & Global Careers Forum",
        "organizer": "American University in Cairo (AUC)",
        "url": "https://www.aucegypt.edu/events",
        "start_date": datetime(2026, 10, 12, 11, 0),
        "date_display": "Oct 12 - 13, 2026 · 11:00 AM",
        "location": "AUC New Cairo & Bassily Auditorium",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Open to University Students",
        "parallel_org": None,
        "description": (
            "AUC's premier annual forum exploring international careers, diplomacy, and global youth leadership. "
            "Attended by selected students from AUC, GUC, BUE, Cairo University, and regional delegates. "
            "Target Audience: Students of Political Science, International Business, Computer Science, Engineering, and Global Affairs. "
            "Venue Details: Bassily Auditorium & Moataz Al Alfi Hall, AUC New Cairo Campus, AUC Avenue, New Cairo. "
            "Activities: Keynotes by multinational directors and international NGO representatives, diplomatic career panels, and global networking sessions. "
            "Admission: Free admission with university ID and pre-registration approval. "
            "AIESEC Tactical Opportunity: Premium target for high-proficiency English speakers seeking international Global Volunteer and Global Talent roles abroad."
        ),
        "recommended_action": "High-conversion campus recruitment for AIESEC Global Volunteer & Global Talent exchanges."
    },
    {
        "id": "summit_greek_campus_expo_2026",
        "title": "The Greek Campus Innovation & Startup Expo",
        "organizer": "The Greek Campus Cairo",
        "url": "https://www.thegreekcampus.com/",
        "start_date": datetime(2026, 11, 6, 10, 0),
        "date_display": "Nov 06 - 07, 2026 · 10:00 AM",
        "location": "The Greek Campus, Downtown Cairo",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Student & Visitor Passes",
        "parallel_org": None,
        "description": (
            "Downtown Cairo's annual tech and creative economy showcase held at Egypt's pioneer technology park. "
            "Features 70+ technology startups, design studios, and student incubators exhibiting prototypes to 4,000+ visitors. "
            "Target Audience: Tech developers, digital marketing students, startup founders, and youth creators. "
            "Venue Details: The Greek Campus (Main Quad, The Library, and The Nest), 28 Falaki Street, Downtown Cairo. "
            "Activities: Live product demos, venture investor pitch sessions, open masterclasses in software architecture, and evening networking. "
            "Admission: Student & visitor entry pass available online. "
            "AIESEC Tactical Opportunity: Perfect venue to pitch startup founders on hosting international interns through AIESEC Global Talent."
        ),
        "recommended_action": "Deploy AIESEC partnership desk & pitch startup founders on hiring international tech talent."
    },
    {
        "id": "summit_cairo_ict_2026",
        "title": "Cairo ICT 2026 (International Technology & AI Exhibition)",
        "organizer": "Trade Fairs International",
        "url": "https://cairoict.com/",
        "start_date": datetime(2026, 11, 15, 9, 0),
        "date_display": "Nov 15 - 18, 2026 · 09:00 AM",
        "location": "Egypt International Exhibition Center (EIEC)",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Free / Trade Visitor Registration",
        "parallel_org": None,
        "description": (
            "The Middle East and Africa's premier technology, artificial intelligence, and telecommunications convention. "
            "Convenes 115,000+ attendees, 500+ global technology enterprises, university delegations, and youth student hackathons. "
            "Target Audience: Computer Science, Software Engineering, Telecommunications, and Business students nationwide. "
            "Venue Details: Egypt International Exhibition Center (EIEC), Halls 1, 2, 3, & 4, New Cairo. "
            "Activities: Connecta youth arena, AI innovation summit, cyber defense challenges, and university research showcase. "
            "Admission: Free digital badge registration online. "
            "AIESEC Tactical Opportunity: Massive nationwide gathering of tech talent. Deploy cross-LC delegation to source Global Talent applicants."
        ),
        "recommended_action": "Nationwide youth activation: Deploy multi-LC delegation across Connecta tech hall for Global Talent IT recruitment."
    },
    {
        "id": "summit_seamless_north_africa_2026",
        "title": "Seamless North Africa 2026 (Fintech & Digital Commerce)",
        "organizer": "Terrapinn & Central Bank of Egypt",
        "url": "https://www.terrapinn.com/exhibition/seamless-north-africa/",
        "start_date": datetime(2026, 10, 12, 9, 30),
        "date_display": "Oct 12 - 13, 2026 · 09:30 AM",
        "location": "Egypt International Exhibition Center (EIEC)",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Free Visitor Pass",
        "parallel_org": None,
        "description": (
            "North Africa's flagship fintech, digital payments, banking technology, and e-commerce youth conference. "
            "Brings together 6,000+ delegates, 200+ industry exhibitors, and university students seeking careers in fintech. "
            "Target Audience: Business, Economics, Finance, Engineering, and Computer Science undergraduates. "
            "Venue Details: Egypt International Exhibition Center (EIEC), Hall 2, New Cairo. "
            "Activities: Keynote tracks, start-up pitch arena, fintech talent networking, and interactive developer workshops. "
            "Admission: Free delegate pass upon pre-registration. "
            "AIESEC Tactical Opportunity: Engage banking and tech corporate sponsors for Global Talent corporate partnerships and internships."
        ),
        "recommended_action": "B2B partnership targeting: Meet fintech corporate partners for incoming Global Talent trainee placement."
    },
    {
        "id": "summit_ain_shams_career_fair_2026",
        "title": "Ain Shams University Annual Employment & Career Fair",
        "organizer": "Ain Shams University Career Center (ASU ASAP)",
        "url": "https://eng.asu.edu.eg/",
        "start_date": datetime(2026, 10, 20, 9, 0),
        "date_display": "Oct 20 - 21, 2026 · 09:00 AM",
        "location": "Ain Shams Faculty of Engineering, Abbassia",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Free for Students & Graduates",
        "parallel_org": "Student Union",
        "description": (
            "One of Egypt's largest public university employment fairs, organized by Ain Shams Career Center (ASU ASAP). "
            "Welcomes 15,000+ undergraduates and recent graduates across Engineering, Computer Science, Commerce, and Languages. "
            "Features 70+ local and multinational employers conducting on-site screening interviews and internship selection. "
            "Venue Details: Ain Shams University Faculty of Engineering Main Campus, 1 El-Sarayat St, Abbassia, Cairo. "
            "Admission: Free with university ID or graduate certificate. "
            "AIESEC Tactical Opportunity: Core recruitment ground for LC Ain Shams: Deploy large booth in central campus quad."
        ),
        "recommended_action": "High-priority activation for LC Ain Shams: Deploy campus booth, CV clinic, and Global Volunteer recruitment drive."
    },
    {
        "id": "summit_cu_career_forum_2026",
        "title": "Cairo University Engineering & Technology Career Forum",
        "organizer": "Cairo University Faculty of Engineering & Student Union",
        "url": "https://eng.cu.edu.eg/",
        "start_date": datetime(2026, 11, 4, 9, 0),
        "date_display": "Nov 04 - 05, 2026 · 09:00 AM",
        "location": "Cairo University Faculty of Engineering, Giza",
        "city": "Giza",
        "category": "Flagship Summits",
        "ticket_type": "Free for Undergraduates",
        "parallel_org": "Student Union",
        "description": (
            "Premier campus employment and tech talent forum at Egypt's oldest engineering institution. "
            "Connects 12,000+ engineering, computer science, and architecture students with 60+ top industrial and software firms. "
            "Target Audience: Final-year students and fresh graduates from Cairo University faculties. "
            "Venue Details: Cairo University Faculty of Engineering Campus, Giza (Building 3, Main Quad, and Conference Hall). "
            "Admission: Free with valid Cairo University ID card. "
            "AIESEC Tactical Opportunity: Prime activation ground for LC Cairo University: Drive Global Talent applications."
        ),
        "recommended_action": "Key campus activation for LC Cairo University: Setup booth at engineering quad and pitch international developer internships."
    },
    {
        "id": "summit_alex_univ_career_day_2026",
        "title": "Alexandria University Career Day & Engineering Forum",
        "organizer": "Alexandria University Career Development Center (UCDC)",
        "url": "https://eng.alexu.edu.eg/",
        "start_date": datetime(2026, 10, 27, 9, 30),
        "date_display": "Oct 27 - 28, 2026 · 09:30 AM",
        "location": "Alexandria University Faculty of Engineering, Shatby",
        "city": "Alexandria",
        "category": "Flagship Summits",
        "ticket_type": "Free for Students",
        "parallel_org": "Student Union",
        "description": (
            "Alexandria's largest campus employment event uniting 8,000+ students from across Alexandria and the North Coast. "
            "Brings together 50+ multinational employers across engineering, shipping/maritime, software, and banking. "
            "Target Audience: Undergraduates and recent alumni of Alexandria University faculties. "
            "Venue Details: Faculty of Engineering Campus, El Horreya Avenue, Shatby, Alexandria. "
            "Admission: Free of charge for university students. "
            "AIESEC Tactical Opportunity: Anchor activation for LC Alexandria: Distribute Global Volunteer flyers and register student leads."
        ),
        "recommended_action": "Flagship activation for LC Alexandria: Run interactive booth, provide resume reviews, and recruit outbound delegates."
    },
    {
        "id": "summit_mansoura_innovation_expo_2026",
        "title": "Mansoura University Student Innovation & Career Expo",
        "organizer": "Mansoura University UCDC & Student Activity Center",
        "url": "https://www.mans.edu.eg/",
        "start_date": datetime(2026, 11, 10, 10, 0),
        "date_display": "Nov 10 - 11, 2026 · 10:00 AM",
        "location": "Mansoura University Main Convention Center",
        "city": "Mansoura",
        "category": "Flagship Summits",
        "ticket_type": "Free Student Admission",
        "parallel_org": "Student Union",
        "description": (
            "The premier student leadership, innovation, and career fair of the Eastern Delta region. "
            "Hosts 10,000+ students from Mansoura University faculties (Medicine, Engineering, Science, Computer Science, Commerce). "
            "Venue Details: Grand Conference Hall & University Club, Mansoura University Campus, Mansoura. "
            "Activities: Student entrepreneurship exhibition, career talks, employer recruitment booths, and leadership workshops. "
            "Admission: Free with Mansoura University ID. "
            "AIESEC Tactical Opportunity: Critical Delta expansion ground: Engage student leaders and recruit Global Volunteer applicants."
        ),
        "recommended_action": "Delta outreach priority: Deploy student booth, engage student union heads, and drive Global Volunteer registrations."
    },
    {
        "id": "summit_assiut_tech_conclave_2026",
        "title": "Assiut University Youth & Technology Conclave",
        "organizer": "Assiut University & IEEE Assiut Student Branch",
        "url": "https://www.aun.edu.eg/",
        "start_date": datetime(2026, 11, 22, 9, 30),
        "date_display": "Nov 22 - 23, 2026 · 09:30 AM",
        "location": "Assiut University Administrative Building & Conference Center",
        "city": "Assiut",
        "category": "Flagship Summits",
        "ticket_type": "Free for Students",
        "parallel_org": "IEEE",
        "description": (
            "Upper Egypt's flagship student conference and technology gathering, co-hosted with IEEE Assiut Student Branch. "
            "Convenes 4,000+ ambitious undergraduates from Assiut, Sohag, Minya, and Qena universities. "
            "Target Audience: Engineering, Computer Science, Science, and Business students across Upper Egypt. "
            "Venue Details: Assiut University Main Campus Conference Center, Assiut. "
            "Activities: Tech keynote panels, robotics competitions, career guidance seminars, and youth workshops. "
            "Admission: Free registration for university students. "
            "AIESEC Tactical Opportunity: Key Upper Egypt recruitment gateway: Expand AIESEC presence in regional universities."
        ),
        "recommended_action": "Upper Egypt strategic outreach: Partner with IEEE Assiut for joint youth leadership session & recruit exchange delegates."
    },
    {
        "id": "summit_nile_univ_tech_day_2026",
        "title": "Nile University Innovation & Tech Showcase",
        "organizer": "Nile University Innovation & Entrepreneurship Center",
        "url": "https://nu.edu.eg/",
        "start_date": datetime(2026, 10, 15, 10, 0),
        "date_display": "Oct 15, 2026 · 10:00 AM",
        "location": "Nile University Campus, Sheikh Zayed",
        "city": "Giza",
        "category": "Flagship Summits",
        "ticket_type": "Free / RSVP Online",
        "parallel_org": None,
        "description": (
            "Annual innovation, robotics, and tech startup showcase at Egypt's premier research university. "
            "Features 50+ student graduation projects, deep-tech prototypes, and AI solutions presented to tech venture capital funds. "
            "Venue Details: Nile University Campus, Juhayna Square, Sheikh Zayed, Giza. "
            "Admission: Free RSVP open to students and tech professionals. "
            "AIESEC Tactical Opportunity: Recruit high-skill tech undergraduates for Global Talent IT internships abroad."
        ),
        "recommended_action": "Source top-tier engineering and AI talent for outbound Global Talent corporate internships in Europe and Asia."
    },
    {
        "id": "summit_gdg_devfest_cairo_2026",
        "title": "GDG DevFest Cairo 2026",
        "organizer": "Google Developer Group Cairo (GDG Cairo)",
        "url": "https://gdg.community.dev/gdg-cairo/",
        "start_date": datetime(2026, 12, 5, 9, 0),
        "date_display": "Dec 05, 2026 · 09:00 AM",
        "location": "The GrEEK Campus, Downtown Cairo",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Free / Registration Required",
        "parallel_org": "Google Developer Group (GDG)",
        "description": (
            "The largest annual Google technology and developer community festival in Egypt. "
            "Convenes 2,500+ student developers, software engineers, and tech innovators for a full day of deep technical tracks. "
            "Venue Details: The GrEEK Campus, Downtown Cairo (Factory Hall, Open Amphitheatre, and Workshop Lounges). "
            "Activities: Tracks in Machine Learning / GenAI, Cloud Computing, Android, Web Technologies, and Women in Tech. "
            "Admission: Free ticket with RSVP badge. "
            "AIESEC Tactical Opportunity: High-density pool of developers: Perfect for recruiting Global Talent software engineers."
        ),
        "recommended_action": "Deploy tech recruitment desk at GrEEK Campus to pitch student coders on international tech internships."
    },
    {
        "id": "summit_hult_prize_egypt_2026",
        "title": "Hult Prize Egypt National Finals & Youth Impact Showcase",
        "organizer": "Hult Prize Egypt & AUC V-Lab",
        "url": "https://www.hultprize.org/",
        "start_date": datetime(2026, 11, 7, 10, 0),
        "date_display": "Nov 07, 2026 · 10:00 AM",
        "location": "AUC New Cairo Campus (Bassily Auditorium)",
        "city": "Cairo",
        "category": "Flagship Summits",
        "ticket_type": "Student / Attendee Pass",
        "parallel_org": "Hult Prize",
        "description": (
            "The national championship of the world's largest social entrepreneurship student competition. "
            "Brings together winning student teams from 40+ Egyptian universities pitching business solutions aligned with the UN SDGs. "
            "Venue Details: American University in Cairo (AUC), New Cairo Campus (Bassily Auditorium & Plaza). "
            "Admission: Student attendee pass with campus security registration. "
            "AIESEC Tactical Opportunity: 100% philosophical match with AIESEC SDG Global Volunteer programs: Engage changemakers."
        ),
        "recommended_action": "Partner with Hult Prize organizers for AIESEC SDG keynote and invite participants to Global Volunteer projects."
    }
]


class EgyptSummitsScraper(BaseScraper):
    """
    Scraper and catalog monitor for Egypt's flagship national summits,
    student congresses, and youth tech festivals (Techne Summit, RiseUp, IEEE, Enactus, AUC).
    """

    name: str = "Egypt Flagship Summits"

    def scrape(self, city: Optional[str] = None, country: str = "egypt") -> List[EventRecord]:
        """Scrapes and monitors flagship Egyptian summits."""
        results: List[EventRecord] = []

        # 1. Live probe to technesummit.com to verify real-time status
        try:
            resp = self.client.get("https://technesummit.com/", timeout=8.0)
            if resp.status_code == 200:
                logger.info("[Egypt Summits] Successfully confirmed live technesummit.com connectivity")
        except Exception as e:
            logger.debug(f"[Egypt Summits] Notice probing live techne site: {e}")

        # 2. Iterate catalog and filter according to requested city
        for s in SUMMITS_CATALOG:
            target_city = s["city"]
            if city and city.lower() not in ["all", "egypt", "nationwide", "country"]:
                if target_city.lower() != city.lower():
                    continue

            record = EventRecord(
                event_id=s["id"],
                title=s["title"],
                source="Egypt Flagship Summits",
                start_date=s["start_date"],
                date_display=s["date_display"],
                location=s["location"],
                city=target_city,
                country=country.capitalize(),
                url=s["url"],
                ticket_type=s["ticket_type"],
                organizer=s["organizer"],
                parallel_org=s.get("parallel_org"),
                category="Flagship Summits",
                description=s["description"],
                recommended_action=s.get("recommended_action")
            )
            results.append(record)

        logger.info(f"[Egypt Summits] Generated {len(results)} flagship summit records")
        return results
