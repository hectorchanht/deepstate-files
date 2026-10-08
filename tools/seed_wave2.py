#!/usr/bin/env python3
"""Seed wave-2 records (from 2026-10-08 wave-2 research report) as src/records/*.json."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src")
REC = os.path.join(SRC, "records")
os.makedirs(REC, exist_ok=True)

NEW_TOPICS = [
    {"id": "vietnam-war", "title": "Vietnam-Era Files",
     "lede": "The Gulf of Tonkin deception and the Pentagon Papers — the declassified record of how America went to war in Vietnam.",
     "code": "DSF-10"},
    {"id": "surveillance", "title": "Mass Surveillance Files",
     "lede": "From Snowden's disclosures to the archives that hold them — the documented scale of NSA surveillance.",
     "code": "DSF-11"},
    {"id": "watergate", "title": "Watergate",
     "lede": "The tapes that ended a presidency — the 'smoking gun' and the cover-up, on the record.",
     "code": "DSF-12"},
    {"id": "rfk-mlk", "title": "RFK & MLK Files",
     "lede": "The 2025 releases under Executive Order 14176 — 230,000+ pages on the King assassination and new RFK tranches.",
     "code": "DSF-13"},
]

RECORDS = [
dict(id="mkultra-docs", topic="intel-abuses", title="MKUltra: The CIA's Declassified Files",
     date="1977-08-03", kind="document", status="verified",
     summary="CIA Director Helms ordered MKUltra files destroyed in 1973; a 1977 FOIA request surfaced ~20,000 misfiled records. At the Aug 3, 1977 Senate hearings, DCI Stansfield Turner testified on the finds: 149 subprojects across 80+ institutions (universities, hospitals, prisons, pharma companies); unwitting dosing of American and Canadian citizens with LSD and other drugs. Program closed 1964, some work continuing as MKSEARCH.",
     sources=[{"label": "CIA Reading Room doc 06760269 (archive.org mirror)", "url": "https://archive.org/details/cia-readingroom-document-06760269"},
              {"label": "DOE OpenNet summary (149 subprojects)", "url": "https://www.osti.gov/opennet/servlets/purl/16384504.pdf"},
              {"label": "CIA FOIA Reading Room", "url": "https://www.cia.gov/readingroom/"}],
     tags=["MKUltra", "CIA", "mind control"]),
dict(id="finders-file", topic="satanic-panic", title="FBI Vault: 'The Finders' File (324 pp.)",
     date="2019-11-01", kind="document", status="verified",
     summary="324-page FBI Vault file posted Nov 2019: Tallahassee PD 1987 arrest reports (two men with six children), DC Metro PD records, a 1987 U.S. Customs memo, FBI field reports, 1993 inquiry correspondence, news clippings. The investigation found no evidence of criminal activity; charges were dropped; no convictions resulted. The CIA-interference claim exists in the file only as an allegation (Martinez memo); the 1993–94 DOJ review did not substantiate it.",
     sources=[{"label": "FBI Vault: The Finders", "url": "https://vault.fbi.gov/the-finders"}],
     tags=["Finders", "FBI", "satanic panic"]),
dict(id="tuskegee-records", topic="intel-abuses", title="Tuskegee Syphilis Experiment: The Records",
     date="1997-05-16", kind="document", status="verified",
     summary="USPHS study in Macon County, Alabama (1932–1972): 399 Black men with syphilis observed without treatment; penicillin withheld after 1947; exposed by AP in 1972 (Peter Buxtun leak); terminated the same year. Class action Pollard v. United States settled 1974 (~$10M + lifetime medical benefits). President Clinton's formal apology, May 16, 1997, White House ceremony.",
     sources=[{"label": "CDC Tuskegee timeline", "url": "https://www.cdc.gov/tuskegee/index.html"},
              {"label": "NARA Tuskegee records", "url": "https://www.archives.gov/research/african-americans/individuals/tuskegee-study"}],
     tags=["Tuskegee", "medical abuse"]),
dict(id="tonkin-nsa", topic="vietnam-war", title="NSA 2005 Release: The Gulf of Tonkin Deception",
     date="2005-12-01", kind="document", status="verified",
     summary="On Dec 1, 2005 NSA declassified 140+ formerly top-secret documents including historian Robert J. Hanyok's SIGINT study. Conclusion: the Aug 2, 1964 engagement (USS Maddox) was real; the Aug 4, 1964 second attack did NOT happen — it rested on bad naval intelligence and misrepresented SIGINT. The Aug 4 incident was the basis for the Gulf of Tonkin Resolution (Aug 7, 1964) authorizing the war.",
     sources=[{"label": "National Security Archive press release", "url": "http://nsarchive.gwu.edu/NSAEBB/NSAEBB132/press20051201.htm"}],
     tags=["Vietnam", "NSA", "Gulf of Tonkin"]),
dict(id="pentagon-papers", topic="vietnam-war", title="The Pentagon Papers: NARA Full Release (2011)",
     date="2011-06-13", kind="document", status="verified",
     summary="'Report of the Office of the Secretary of Defense Vietnam Task Force,' commissioned by McNamara in 1967, leaked by Daniel Ellsberg in June 1971. Full official release June 13, 2011 (40th anniversary) by NARA with the Kennedy, Johnson and Nixon libraries — ~7,000 pages in 48 boxes, no redactions, ~2,384 pages newly available vs. the Gravel edition.",
     sources=[{"label": "NARA Pentagon Papers", "url": "https://www.archives.gov/research/pentagon-papers"},
              {"label": "NARA press release NR11-138", "url": "https://www.archives.gov/press/press-releases/2011/nr11-138.html"}],
     tags=["Vietnam", "Pentagon Papers", "NARA"]),
dict(id="snowden-archives", topic="surveillance", title="Snowden Disclosures: The Public Archives",
     date="2014-04-05", kind="document", status="verified",
     summary="Publicly documented collections of the 2013+ NSA disclosures: the ACLU NSA Documents Database (launched April 2014 — every document public since June 5, 2013, searchable); EFF's 'NSA Primary Sources' chronological list; The Guardian's 'The NSA Files'; National Security Archive holdings. (The exact current URL of the ACLU database was not captured in this research pass.)",
     sources=[{"label": "ACLU database launch report", "url": "https://www.theregister.com/security/2014/04/05/aclu-launches-user-friendly-database-of-every-snowden-doc/1007673"},
              {"label": "Global surveillance disclosures overview", "url": "https://en.wikipedia.org/wiki/Global_surveillance_disclosures_(2013–present)"}],
     tags=["Snowden", "NSA", "surveillance"]),
dict(id="rfk-files-2025", topic="rfk-mlk", title="RFK Assassination Files: 2025 Releases",
     date="2025-06-01", kind="document", status="verified",
     summary="Under EO 14176 (signed Jan 23, 2025), RFK assassination files were released in tranches April–June 2025 (FBI/CIA/LAPD-related records). No verified primary-document support for the major conspiracy claims (second gunman, CIA involvement) has been reported from these releases.",
     sources=[{"label": "EO 14176 text (Federal Register)", "url": "https://www.federalregister.gov/documents/full_text/html/2025/01/31/2025-02116.html"}],
     tags=["RFK", "NARA", "declassified"]),
dict(id="mlk-files-2025", topic="rfk-mlk", title="MLK Assassination Files: 230,000+ Pages (2025)",
     date="2025-07-21", kind="document", status="verified",
     summary="July 21, 2025 — 230,000+ pages released per EO 14176: the FBI MURKIN (Murder-King) investigation file; responsive CIA records; the State Department file on James Earl Ray's extradition from the UK; internal FBI memos and investigative leads. Per ODNI, unlike most JFK files these had never been digitized. Major claims (FBI/CIA conspiracy, Ray framed): no primary-document support reported.",
     sources=[{"label": "NARA MLK collection", "url": "https://www.archives.gov/research/mlk"},
              {"label": "NARA announcement", "url": "https://www.archives.gov/news/articles/nara-releases-230k-mlk-assassination-files"}],
     tags=["MLK", "NARA", "FBI", "declassified"]),
dict(id="watergate-tapes", topic="watergate", title="The 'Smoking Gun' Tape (June 23, 1972)",
     date="1974-08-05", kind="document", status="verified",
     summary="Oval Office conversation, Nixon–Haldeman, June 23, 1972, released Aug 5, 1974: Nixon and Haldeman plan to have the CIA tell the FBI to halt the Watergate investigation on false 'national security' grounds. It proved Nixon knew of the White House link to the burglaries within days and approved obstructing the FBI; congressional support collapsed; Nixon resigned Aug 8, 1974. Full tape portal at the Nixon Library.",
     sources=[{"label": "Nixon Library: White House Tapes", "url": "https://www.nixonlibrary.gov/white-house-tapes"},
              {"label": "Smoking gun tape transcript", "url": "https://watergate.info/1972/06/23/the-smoking-gun-tape.html/"}],
     tags=["Watergate", "Nixon"]),
dict(id="mockingbird-record", topic="intel-abuses", title="What the Church Committee Found on CIA & the Media",
     date="1976-04-26", kind="document", status="verified",
     summary="Church Committee Final Report, Book I (Apr 26, 1976): the CIA maintained covert relationships with ~50 American journalists/media figures; a network of several hundred foreign media individuals/assets for covert propaganda; 12+ U.S. news organizations provided cover for CIA officers abroad (some unwitting). The CIA refused to name names. Carl Bernstein (Rolling Stone, Oct 1977) separately reported ~400 U.S. journalists had worked with the CIA over 25 years.",
     sources=[{"label": "Church Committee findings on media (overview)", "url": "https://www.senate.gov/about/powers-procedures/investigations/church-committee.htm"}],
     tags=["Mockingbird", "CIA", "media"]),
dict(id="franklin-case", topic="satanic-panic", title="Franklin Credit Union Case: Court Records vs. Claims",
     date="1990-07-23", kind="document", status="verified",
     summary="What court records establish: Lawrence E. King Jr. convicted of financial crimes (fraud/embezzlement), pleaded guilty 1991, 15-year federal sentence. Vs. the claims: an elite child-trafficking/satanic ring reaching Washington was examined by the Douglas County Grand Jury (82 days, 395 exhibits, 76 witnesses; report July 23, 1990) — 'found no credible evidence' of abuse, interstate transport of minors, drug trafficking or a pornography ring. Key witnesses recanted (Troy Boner) or were convicted of perjury (Alisha Owen, 1991). No abuse-ring indictments or convictions resulted.",
     sources=[{"label": "Grand jury memorandum of decision (transcript)", "url": "https://www.scribd.com/document/138629079/Conspiracy-of-Silence-Memorandum-of-Decision-Transcript-4-Cv91-33037"}],
     tags=["Franklin", "court records"]),
dict(id="epstein-tranches", topic="epstein", title="Epstein Files: The 2025–2026 Tranches",
     date="2026-01-30", kind="document", status="verified",
     summary="Beyond the July 2025 DOJ/FBI memo: Feb 27, 2025 — AG Bondi 'Phase 1' (~100+ pages). Sept 2025 — House Oversight posted 33,295 pages from DOJ; Nov 2025 — ~20,000 pages from Epstein's estate. Nov 19, 2025 — Epstein Files Transparency Act signed (publish all unclassified DOJ Epstein records within 30 days). Dec 19, 2025 — first EFTA tranche (heavy redactions). Jan 30, 2026 — largest tranche: ~3–3.5M pages + 2,000+ videos + 180,000 images; DAG called it the 'final major disclosure.' Contents: flight logs, financial ledgers, interview transcripts, FBI memos, Maxwell-trial materials. No new criminal charges announced.",
     sources=[{"label": "Tranche-by-tranche fact check", "url": "https://factually.co/fact-checks/justice/released-jeffrey-epstein-files-by-administration-41dc56"},
              {"label": "DOJ Epstein disclosures", "url": "https://www.justice.gov/epstein/doj-disclosures"}],
     tags=["Epstein", "DOJ", "tranches"]),
# ---------------- claims ----------------
dict(id="claim-finders-cia", topic="satanic-panic", title="CLAIM: The Finders were a CIA child-trafficking front",
     date="1987-02-01", kind="claim", status="unproven",
     summary="Claims allege a CIA-front child-trafficking/satanic cult whose investigation was shut down as a 'CIA internal matter.' The 324-page FBI file shows the 1987 investigation found no evidence of criminal activity; charges were dropped; no convictions. The CIA-interference claim exists in the file only as an allegation in one Customs memo; the 1993–94 DOJ review did not substantiate it.",
     sources=[{"label": "FBI Vault: The Finders", "url": "https://vault.fbi.gov/the-finders"}],
     tags=["Finders", "claim"]),
dict(id="claim-mockingbird-name", topic="intel-abuses", title="CLAIM: A CIA program literally named 'Operation Mockingbird' ran the U.S. press",
     date="1979-01-01", kind="claim", status="unproven",
     summary="The NAME 'Operation Mockingbird' first appears in Deborah Davis's 1979 Katharine Graham biography and appears in NO released CIA or congressional document. Three real things get conflated: Frank Wisner's 'Mighty Wurlitzer' foreign propaganda network; the ~50 domestic journalist relationships documented by the Church Committee; and the real 'Project Mockingbird' — a narrow 1963 warrantless wiretap of two columnists (acknowledged in the CIA 'Family Jewels,' 2007).",
     sources=[{"label": "Church Committee (Senate)", "url": "https://www.senate.gov/about/powers-procedures/investigations/church-committee.htm"}],
     tags=["Mockingbird", "claim"]),
dict(id="claim-franklin-ring", topic="satanic-panic", title="CLAIM: Franklin was an elite satanic abuse ring reaching Washington",
     date="1990-07-23", kind="claim", status="unproven",
     summary="The Douglas County Grand Jury (76 witnesses, 395 exhibits) 'found no credible evidence' of child sexual abuse, interstate transport of minors, drug trafficking or a pornography ring by King or Franklin officials. Key witnesses recanted or were convicted of perjury. No abuse-ring indictments or convictions resulted; only King's financial-crimes conviction stands.",
     sources=[{"label": "Grand jury memorandum (transcript)", "url": "https://www.scribd.com/document/138629079/Conspiracy-of-Silence-Memorandum-of-Decision-Transcript-4-Cv91-33037"}],
     tags=["Franklin", "claim"]),
dict(id="claim-snowden-cia-plant", topic="surveillance", title="CLAIM: Snowden was a CIA plant running coded ops",
     date="2013-06-05", kind="claim", status="unproven",
     summary="Q-drop-era claim that the whistleblower was a CIA-planted operative. No primary source — no document, testimony or investigative file — supports it; the public record is the disclosure archive itself.",
     sources=[{"label": "Global surveillance disclosures overview", "url": "https://en.wikipedia.org/wiki/Global_surveillance_disclosures_(2013–present)"}],
     tags=["Snowden", "claim"]),
]

topics_path = os.path.join(SRC, "topics.json")
topics = json.load(open(topics_path))
have = {t["id"] for t in topics}
for t in NEW_TOPICS:
    if t["id"] not in have:
        topics.append(t)
with open(topics_path, "w") as f:
    json.dump(topics, f, indent=2, ensure_ascii=False)

for r in RECORDS:
    r["added"] = "2026-10-08"
    r["reviewed"] = True
    with open(os.path.join(REC, r["id"] + ".json"), "w") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)

print(f"topics now {len(topics)}, wrote {len(RECORDS)} wave-2 records")
