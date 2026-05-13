from datetime import datetime, timezone
import json


def demo_cvss_decoder():
    print("\n--- DEMO 2: CVSS Vector Decoder ---")

    vector = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H"

    attack_vector     = {"N": "Network", "A": "Adjacent", "L": "Local", "P": "Physical"}
    attack_complexity = {"L": "Low", "H": "High"}
    privileges        = {"N": "None", "L": "Low", "H": "High"}
    user_interaction  = {"N": "None", "R": "Required"}
    scope             = {"U": "Unchanged", "C": "Changed"}
    impact            = {"N": "None", "L": "Low", "H": "High"}

    parts = vector.split("/")[1:]
    parsed = {}

    for part in parts:
        key, val = part.split(":")
        parsed[key] = val

    print(f"Vector: {vector}\n")
    print(f"Attack Vector:      {attack_vector[parsed['AV']]}")
    print(f"Attack Complexity:  {attack_complexity[parsed['AC']]}")
    print(f"Privileges Required:{privileges[parsed['PR']]}")
    print(f"User Interaction:   {user_interaction[parsed['UI']]}")
    print(f"Scope:              {scope[parsed['S']]}")
    print(f"Confidentiality:    {impact[parsed['C']]}")
    print(f"Integrity:          {impact[parsed['I']]}")
    print(f"Availability:       {impact[parsed['A']]}")

    is_critical = (
        parsed['AV'] == 'N' and
        parsed['PR'] == 'N' and
        parsed['UI'] == 'N'
    )

    print(f"\nRemote No-Auth Exploitable: {is_critical}")
    print("→ PATCH IMMEDIATELY" if is_critical else "→ Schedule patching")


def demo_sbom_structure():
    print("\n--- DEMO 3: SBOM Structure (CycloneDX format) ---")

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "name": "firmware-nav-system",
                "version": "2.3.1",
                "type": "firmware"
            }
        },
        "components": [
            {
                "type": "library",
                "name": "openssl",
                "version": "1.1.1t",
                "purl": "pkg:generic/openssl@1.1.1t",
                "licenses": [{"id": "OpenSSL"}],
                "hashes": [{"alg": "SHA-256", "content": "a1b2c3..."}]
            },
            {
                "type": "library",
                "name": "libcurl",
                "version": "7.88.1",
                "purl": "pkg:generic/libcurl@7.88.1",
                "licenses": [{"id": "MIT"}],
                "hashes": [{"alg": "SHA-256", "content": "d4e5f6..."}]
            },
            {
                "type": "library",
                "name": "zlib",
                "version": "1.2.11",
                "purl": "pkg:generic/zlib@1.2.11",
                "licenses": [{"id": "Zlib"}],
                "hashes": [{"alg": "SHA-256", "content": "g7h8i9..."}]
            }
        ]
    }

    components = sbom["components"]

    print(f"Firmware: {sbom['metadata']['component']['name']} "
          f"v{sbom['metadata']['component']['version']}")
    print(f"Total components: {len(components)}\n")

    vulnerable_versions = {
        "openssl": ["1.1.1t", "1.1.1s", "3.0.0", "3.0.1"],
        "libcurl": ["7.88.0"],
        "zlib": ["1.2.11"]
    }

    print("Vulnerability Scan:")
    for component in components:
        name = component["name"]
        version = component["version"]
        is_vulnerable = version in vulnerable_versions.get(name, [])
        status = "⚠️  VULNERABLE" if is_vulnerable else "✅ OK"
        print(f"  {name} {version} — {status}")


def demo_osint_sources():
    print("\n--- DEMO 4: OSINT Source Classification ---")

    osint_sources = [
        {
            "name": "NVD (National Vulnerability Database)",
            "url": "https://nvd.nist.gov",
            "reliability": 1,
            "type": "government",
            "update_frequency": "daily",
            "data_format": "JSON/CVE",
            "relevance_to_defense": "Critical — official CVE scores and patch info",
            "already_scraping": True
        },
        {
            "name": "CISA KEV (Known Exploited Vulnerabilities)",
            "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            "reliability": 1,
            "type": "government",
            "update_frequency": "daily",
            "data_format": "JSON/CSV",
            "relevance_to_defense": "Critical — actively exploited vulnerabilities",
            "already_scraping": False
        },
        {
            "name": "The Hacker News",
            "url": "https://thehackernews.com",
            "reliability": 2,
            "type": "media",
            "update_frequency": "hourly",
            "data_format": "HTML/RSS",
            "relevance_to_defense": "High — fast reporting",
            "already_scraping": True
        },
        {
            "name": "BleepingComputer",
            "url": "https://bleepingcomputer.com",
            "reliability": 2,
            "type": "media",
            "update_frequency": "hourly",
            "data_format": "HTML",
            "relevance_to_defense": "High — technical analysis",
            "already_scraping": True
        },
        {
            "name": "Krebs on Security",
            "url": "https://krebsonsecurity.com",
            "reliability": 2,
            "type": "independent",
            "update_frequency": "daily",
            "data_format": "HTML",
            "relevance_to_defense": "Medium — investigative reporting",
            "already_scraping": True
        },
        {
            "name": "MITRE ATT&CK",
            "url": "https://attack.mitre.org",
            "reliability": 1,
            "type": "framework",
            "update_frequency": "quarterly",
            "data_format": "JSON/STIX",
            "relevance_to_defense": "Critical — adversary techniques",
            "already_scraping": False
        }
    ]

    sorted_sources = sorted(osint_sources, key=lambda x: x["reliability"])

    print(f"{'Source':<35} {'Type':<12} {'Reliability':<12} {'Scraping?'}")
    print("-" * 75)

    for s in sorted_sources:
        scraping = "✅ Yes" if s["already_scraping"] else "➕ Add to capstone"
        print(f"{s['name']:<35} {s['type']:<12} {s['reliability']:<12} {scraping}")

    print("\n💡 CISA KEV is reliability-1 and you're NOT scraping it yet.")
    print("   Adding it would strengthen your capstone.")


def demo_threat_report_schema():
    print("\n--- DEMO 5: Threat Intelligence Report Schema ---")

    sample_report = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline_version": "1.0.0",
            "sources_scraped": [
                "thehackernews.com",
                "bleepingcomputer.com",
                "krebsonsecurity.com"
            ],
            "articles_analyzed": 33
        },
        "summary": {
            "critical_count": 4,
            "high_count": 8,
            "medium_count": 12,
            "low_count": 9,
            "top_attack_vectors": ["Phishing", "RCE", "Supply Chain"],
            "most_affected_sectors": ["Defense", "Finance", "Healthcare"]
        },
        "articles": [
            {
                "title": "Critical RCE in Palo Alto GlobalProtect",
                "source": "thehackernews.com",
                "url": "https://thehackernews.com/...",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "analysis": {
                    "threat_level": "Critical",
                    "cve_ids": ["CVE-2024-3400"],
                    "affected_systems": ["PAN-OS < 11.1.2-h3"],
                    "attack_vector": "Remote Network Exploitation",
                    "affected_sectors": ["Defense", "Government"],
                    "recommended_action": "Apply patch immediately",
                    "relevance_to_defense": "Critical exposure in DOD environments"
                }
            }
        ]
    }

    print(json.dumps(sample_report, indent=2))
    print("\nThis schema represents your CyberPulse output format.")


def demo_cve_structure():
    print("\n--- DEMO 1: CVE Data Structure ---")

    cve_record = {
        "id": "CVE-2024-3400",
        "published": "2024-04-12T00:00:00Z",
        "lastModified": "2024-04-15T00:00:00Z",
        "vulnStatus": "Analyzed",
        "descriptions": [
            {
                "lang": "en",
                "value": "A command injection vulnerability in Palo Alto Networks PAN-OS "
                         "allows an unauthenticated attacker to execute arbitrary code "
                         "with root privileges via the GlobalProtect feature."
            }
        ],
        "metrics": {
            "cvssMetricV31": {
                "cvssData": {
                    "version": "3.1",
                    "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                    "baseScore": 10.0,
                    "baseSeverity": "CRITICAL",
                    "attackVector": "NETWORK",
                    "attackComplexity": "LOW",
                    "privilegesRequired": "NONE",
                    "userInteraction": "NONE",
                    "scope": "CHANGED",
                    "confidentialityImpact": "HIGH",
                    "integrityImpact": "HIGH",
                    "availabilityImpact": "HIGH"
                }
            }
        },
        "weaknesses": [
            {"description": [{"lang": "en", "value": "CWE-77"}]}
        ],
        "configurations": [
            {"software": "Palo Alto PAN-OS", "versions_affected": ["< 11.1.2-h3"]}
        ],
        "references": [
            {"url": "https://security.paloaltonetworks.com/CVE-2024-3400", "source": "vendor"}
        ]
    }

    cvss = cve_record["metrics"]["cvssMetricV31"]["cvssData"]

    print(f"CVE ID:         {cve_record['id']}")
    print(f"Severity:       {cvss['baseSeverity']} ({cvss['baseScore']})")
    print(f"Attack Vector:  {cvss['attackVector']}")
    print(f"No Auth Needed: {cvss['privilegesRequired'] == 'NONE'}")
    print(f"Description:    {cve_record['descriptions'][0]['value'][:80]}...")


def run_demos():
    demo_cve_structure()
    demo_cvss_decoder()
    demo_sbom_structure()
    demo_osint_sources()
    demo_threat_report_schema()

    print("\n✅ Security context complete! Ready for CyberPulse capstone.")


if __name__ == "__main__":
    run_demos()