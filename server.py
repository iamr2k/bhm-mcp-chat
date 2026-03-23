import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# Load .env from the same directory as this script
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)

mcp = FastMCP("BharatMatrimony Search")

GRAPHQL_QUERY = """query getSearchMatches($listingInput: ListingInput!) {
  searchResult(criteria: $listingInput) {
    count
    profiles {
      ... on ProfileFull {
        profileCreatedBy
        id
        name
        lastActiveTime
        ageYear
        height
        education
        occupation
        income
        location {
          city
          state
          country
          __typename
        }
        photo(size: BIG)
        photoVisibility
        phoneVisibility
        photoCount
        profileVideoPreview
        isNewlyJoined
        isShortlistedByYou
        isPaid
        isAssisted
        isFeaturedProfile
        isPhotoVerified
        isIdVerified
        lastCommunication {
          type
          time
          content
          likeExpiresIn
          readStatus
          __typename
        }
        totalCommunicationCount
        onlineStatus
        caste
        subcaste
        __typename
      }
      __typename
    }
    __typename
  }
}"""


def _get_config():
    """Read current auth config from environment (reloads .env each time)."""
    load_dotenv(ENV_PATH, override=True)
    return {
        "user_id": os.environ.get("BHM_USER_ID", ""),
        "enc_id": os.environ.get("BHM_ENC_ID", ""),
        "bearer_token": os.environ.get("BHM_BEARER_TOKEN", ""),
        "session_id": os.environ.get("BHM_SESSION_ID", ""),
    }


def _build_headers(cfg: dict) -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Linux"',
        "Referer": "https://matches.keralamatrimony.com/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "src": cfg["enc_id"],
        "AppType": "300",
        "bearer": cfg["bearer_token"],
        "isprimetab": "0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "sessionId": cfg["session_id"],
    }


@mcp.tool()
def configure_auth(
    bearer_token: str,
    session_id: str,
    user_id: str = "",
    enc_id: str = "",
) -> str:
    """Configure authentication credentials for BharatMatrimony API.

    The user must provide their bearer token and session ID from the browser.
    To get these values:
    1. Log in to bharatmatrimony.com
    2. Open browser DevTools (F12) → Network tab
    3. Perform a search and find the GraphQL request
    4. Copy the 'bearer' and 'sessionId' header values

    Args:
        bearer_token: The JWT bearer token from the request headers.
        session_id: The session ID from the request headers.
        user_id: (Optional) Your matri ID, e.g. 'E9819315'. Read from existing .env if not provided.
        enc_id: (Optional) Your encrypted ID from the 'src' header. Read from existing .env if not provided.
    """
    # Read existing .env to preserve values not being updated
    existing = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()

    # Update with new values
    existing["BHM_BEARER_TOKEN"] = bearer_token
    existing["BHM_SESSION_ID"] = session_id
    if user_id:
        existing["BHM_USER_ID"] = user_id
    if enc_id:
        existing["BHM_ENC_ID"] = enc_id

    # Write back
    lines = [f"{k}={v}" for k, v in existing.items()]
    ENV_PATH.write_text("\n".join(lines) + "\n")

    # Reload into environment
    load_dotenv(ENV_PATH, override=True)

    return json.dumps({
        "status": "ok",
        "message": "Auth credentials saved to .env and loaded.",
        "user_id": existing.get("BHM_USER_ID", ""),
        "session_id_set": bool(session_id),
        "bearer_token_set": bool(bearer_token),
    })


@mcp.tool()
def get_auth_status() -> str:
    """Check whether BharatMatrimony auth credentials are configured.

    Returns the current user ID and whether bearer token / session ID are set.
    Does NOT reveal the actual token values.
    """
    cfg = _get_config()
    return json.dumps({
        "user_id": cfg["user_id"],
        "enc_id_set": bool(cfg["enc_id"]),
        "bearer_token_set": bool(cfg["bearer_token"]),
        "session_id_set": bool(cfg["session_id"]),
        "env_file_exists": ENV_PATH.exists(),
    })


def _build_criteria(
    age_min: int,
    age_max: int,
    height_min: str,
    height_max: str,
    religion: str,
    mother_tongue: list[str],
    marital_status: list[str],
    states: list[str],
    education_category: list[str],
    stars: list[str],
    drinking: list[str],
    smoking: list[str],
    caste: list[str],
    eating: list[str],
    physical_status: list[str],
) -> dict:
    return {
        "ageMin": age_min,
        "ageMax": age_max,
        "heightMin": height_min,
        "heightMax": height_max,
        "incomeMin": "ANY",
        "incomeMax": "ANY",
        "ancestralOrigin": [],
        "caste": caste,
        "citizenship": ["ANY"],
        "cityDistrict": [],
        "country": ["INDIA"],
        "createdBy": ["ANY"],
        "createdDate": "ALL",
        "dosham": ["ANY"],
        "doshamType": [],
        "drinking": drinking,
        "eating": eating,
        "educationCategory": education_category,
        "employmentType": ["ANY"],
        "excludeContacted": False,
        "excludeIgnored": True,
        "excludeShortlisted": True,
        "excludeViewed": False,
        "familyStatus": ["ANY"],
        "familyType": ["ANY"],
        "familyValue": ["ANY"],
        "gothram": ["ALL_EXCEPT_MY_GOTHRAM"],
        "haveChildren": [],
        "isRefine": True,
        "maritalStatus": marital_status,
        "motherTongue": mother_tongue,
        "occupation": ["ANY"],
        "physicalStatus": physical_status,
        "profileType": ["ANY"],
        "religion": religion,
        "residentStatus": ["ANY"],
        "institution": [],
        "organization": [],
        "smoking": smoking,
        "sort": None,
        "star": stars,
        "state": states,
        "subcaste": [],
        "sudhaJathakam": ["ANY"],
    }


@mcp.tool()
def search_profiles(
    age_min: int = 22,
    age_max: int = 29,
    height_min: str = "FT4_IN7_139CM",
    height_max: str = "FT5_IN9_175CM",
    religion: str = "HINDU",
    mother_tongue: list[str] = ["MALAYALAM"],
    marital_status: list[str] = ["NEVER_MARRIED"],
    states: list[str] = ["KERALA", "KARNATAKA"],
    education_category: list[str] = [
        "BACHELORS_ENGINEERING",
        "MASTERS_ENGINEERING",
        "BACHELORS_ARTS_SCIENCE_COMMERCE",
        "MASTERS_ARTS_SCIENCE_COMMERCE",
        "SERVICE_IAS_IPS_IRS_IES_IFS",
        "DOCTORATES",
        "FINANCE_ICWAI_CA_CS_CFA",
        "BACHELORS_LEGAL",
        "MASTERS_LEGAL",
        "BACHELORS_MANAGEMENT",
        "MASTERS_MANAGEMENT",
        "BACHELORS_MEDICINE_GENERAL",
        "MASTERS_MEDICINE_GENERAL",
        "BACHELORS_MEDICINE_OTHERS",
        "MASTERS_MEDICINE_OTHERS",
    ],
    stars: list[str] = [
        "ARDRA_THIRUVATHIRA",
        "ASHLESHA_AYILYAM",
        "HASTHA_ATHAM",
        "JYESTA_KETTAI_THRIKKETA",
        "KRITHIKA_KARTHIKA",
        "MAKHA_MAGAM",
        "MOOLAM_MOOLA",
        "POORVABADRAPADA_PURATATHI",
        "PUNARVASU_PUNARPUSAM",
        "REVATHI",
        "ROHINI",
        "SHATATARAKA_SADAYAM_SATABISHEK",
        "SHRAVAN_THIRUVONAM",
        "SWATI_CHOTHI",
        "UTTARAPALGUNI_UTHRAM",
        "UTTARASHADA_UTHRADAM",
        "VISHAKA_VISHAKAM",
    ],
    drinking: list[str] = ["NEVER", "NOT_SPECIFIED"],
    smoking: list[str] = ["NEVER", "NOT_SPECIFIED"],
    caste: list[str] = ["ANY"],
    eating: list[str] = ["ANY"],
    physical_status: list[str] = ["NORMAL"],
    page: int = 1,
    results_per_page: int = 20,
) -> str:
    """Search for matrimony profiles on BharatMatrimony with various filters.

    Returns matching profiles with details like name, age, education, occupation,
    income, location, caste, and online status.

    IMPORTANT: Before calling this tool, ensure auth is configured via configure_auth tool.

    Parameter reference:
    ---
    age_min / age_max: Integer age range (e.g. 22–35).

    height_min / height_max: Height codes. Common values:
      FT4_IN0_121CM, FT4_IN7_139CM, FT5_IN0_152CM, FT5_IN3_160CM,
      FT5_IN5_165CM, FT5_IN7_170CM, FT5_IN9_175CM, FT6_IN0_182CM,
      FT6_IN5_195CM, FT7_IN0_213CM

    religion: HINDU, MUSLIM, CHRISTIAN, SIKH, JAIN, BUDDHIST, PARSI, JEWISH, BAHAI, ANY

    mother_tongue: MALAYALAM, TAMIL, KANNADA, TELUGU, HINDI, MARATHI, BENGALI,
      GUJARATI, PUNJABI, ORIYA, URDU, etc.

    marital_status: NEVER_MARRIED, DIVORCED, WIDOWED, AWAITING_DIVORCE, ANNULLED

    states: KERALA, KARNATAKA, TAMIL_NADU, ANDHRA_PRADESH, TELANGANA, MAHARASHTRA,
      GOA, DELHI, UTTAR_PRADESH, WEST_BENGAL, RAJASTHAN, GUJARAT, etc.

    education_category: BACHELORS_ENGINEERING, MASTERS_ENGINEERING,
      BACHELORS_ARTS_SCIENCE_COMMERCE, MASTERS_ARTS_SCIENCE_COMMERCE,
      BACHELORS_MANAGEMENT, MASTERS_MANAGEMENT, BACHELORS_MEDICINE_GENERAL,
      MASTERS_MEDICINE_GENERAL, BACHELORS_MEDICINE_OTHERS, MASTERS_MEDICINE_OTHERS,
      BACHELORS_LEGAL, MASTERS_LEGAL, DOCTORATES, FINANCE_ICWAI_CA_CS_CFA,
      SERVICE_IAS_IPS_IRS_IES_IFS

    stars (nakshatras): ASHWINI, BHARANI, KRITHIKA_KARTHIKA, ROHINI,
      MRIGASHIRA_MAKAYIRAM, ARDRA_THIRUVATHIRA, PUNARVASU_PUNARPUSAM,
      PUSHYA_POOYAM, ASHLESHA_AYILYAM, MAKHA_MAGAM, POORVAPALGUNI_POORAM,
      UTTARAPALGUNI_UTHRAM, HASTHA_ATHAM, CHITRA_CHITHIRAI, SWATI_CHOTHI,
      VISHAKA_VISHAKAM, ANURADHA_ANIZHAM, JYESTA_KETTAI_THRIKKETA,
      MOOLAM_MOOLA, POORVASHADA_POORADAM, UTTARASHADA_UTHRADAM,
      SHRAVAN_THIRUVONAM, DHANISHTA_AVITTAM, SHATATARAKA_SADAYAM_SATABISHEK,
      POORVABADRAPADA_PURATATHI, UTTARABADRAPADA_UTHRATTATHI, REVATHI

    drinking: NEVER, OCCASIONALLY, NOT_SPECIFIED, ANY
    smoking: NEVER, OCCASIONALLY, NOT_SPECIFIED, ANY
    eating: VEGETARIAN, NON_VEGETARIAN, EGGETARIAN, ANY
    physical_status: NORMAL, PHYSICALLY_CHALLENGED, ANY
    caste: ANY, NAIR, EZHAVA, NAMBOOTHIRI, MENON, PILLAI, etc.
    """
    cfg = _get_config()
    if not cfg["bearer_token"]:
        return "Error: Bearer token not configured. Ask the user to provide their bearer token, then call configure_auth."
    if not cfg["session_id"]:
        return "Error: Session ID not configured. Ask the user to provide their session ID, then call configure_auth."
    if not cfg["user_id"]:
        return "Error: User ID not configured. Ask the user to provide their matri ID, then call configure_auth."

    headers = _build_headers(cfg)
    criteria = _build_criteria(
        age_min=age_min,
        age_max=age_max,
        height_min=height_min,
        height_max=height_max,
        religion=religion,
        mother_tongue=mother_tongue,
        marital_status=marital_status,
        states=states,
        education_category=education_category,
        stars=stars,
        drinking=drinking,
        smoking=smoking,
        caste=caste,
        eating=eating,
        physical_status=physical_status,
    )

    query_string = f"getSearchMatches-SearchResult-matches-300-{cfg['user_id']}"
    json_data = {
        "operationName": "getSearchMatches",
        "variables": {
            "listingInput": {
                "id": cfg["user_id"],
                "page": page,
                "resultsCount": results_per_page,
                "isPrime": False,
                "criteria": criteria,
            },
            "queryString": query_string,
        },
        "query": GRAPHQL_QUERY,
    }

    url = f"https://g.bharatmatrimony.com/?{query_string}"
    response = requests.post(url, headers=headers, json=json_data, timeout=30)
    response.raise_for_status()

    data = response.json()
    search_result = data.get("data", {}).get("searchResult", {})
    profiles = search_result.get("profiles", [])
    count = search_result.get("count", 0)

    # Format profiles for readable output
    output_profiles = []
    for p in profiles:
        loc = p.get("location", {})
        output_profiles.append({
            "id": p.get("id"),
            "name": p.get("name"),
            "age": p.get("ageYear"),
            "height": p.get("height"),
            "education": p.get("education"),
            "occupation": p.get("occupation"),
            "income": p.get("income"),
            "city": loc.get("city"),
            "state": loc.get("state"),
            "caste": p.get("caste"),
            "subcaste": p.get("subcaste"),
            "online_status": p.get("onlineStatus"),
            "last_active": p.get("lastActiveTime"),
            "created_by": p.get("profileCreatedBy"),
            "photo_count": p.get("photoCount"),
            "is_photo_verified": p.get("isPhotoVerified"),
            "is_id_verified": p.get("isIdVerified"),
        })

    result = {
        "total_count": count,
        "page": page,
        "profiles_returned": len(output_profiles),
        "profiles": output_profiles,
    }
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
