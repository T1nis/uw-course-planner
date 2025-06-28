import requests
import json
import time

SCHOOL_ID = "U2Nob29sLTE4NDE4"  # UW–Madison RMP School ID
BASE_URL = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://www.ratemyprofessors.com/search/professors/18418",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Origin": "https://www.ratemyprofessors.com",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}

def fetch_professors(cursor=None):
    query = """
    query SearchTeachers($schoolID: ID!, $query: String, $first: Int, $after: ID) {
      search: searchTeachers(
        schoolID: $schoolID
        query: $query
        first: $first
        after: $after
      ) {
        edges {
          cursor
          node {
            id
            firstName
            lastName
            department
            avgRating
            numRatings
            wouldTakeAgainPercent
            avgDifficulty
            legacyId
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    variables = {
        "schoolID": SCHOOL_ID,
        "query": "",
        "first": 50,
        "after": cursor
    }
    response = requests.post(
        BASE_URL,
        headers=HEADERS,
        json={"query": query, "variables": variables}
    )
    try:
        return response.json()
    except Exception:
        print("Non-JSON response received from RMP API:")
        print("=" * 60)
        print(response.text)
        print("=" * 60)
        raise

def fetch_comments(prof_id):
    query = """
    query TeacherRatingsPageQuery($id: ID!, $first: Int, $after: ID) {
      node(id: $id) {
        ... on Teacher {
          id
          firstName
          lastName
          department
          avgRating
          numRatings
          wouldTakeAgainPercent
          avgDifficulty
          ratings(first: $first, after: $after) {
            edges {
              node {
                id
                date
                comment
                clarityRating
                difficultyRating
                grade
                isForOnlineClass
                ratingTags
                attendanceMandatory
                wouldTakeAgain
                grade
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    }
    """
    all_comments = []
    cursor = None
    while True:
        variables = {
            "id": prof_id,
            "first": 50,
            "after": cursor
        }
        response = requests.post(
            BASE_URL,
            headers=HEADERS,
            json={"query": query, "variables": variables}
        )
        try:
            resp = response.json()
        except Exception:
            print("Non-JSON response received while fetching comments for professor ID", prof_id)
            print("=" * 60)
            print(response.text)
            print("=" * 60)
            raise
        ratings = resp["data"]["node"]["ratings"]
        edges = ratings["edges"]
        for edge in edges:
            all_comments.append(edge["node"])
        page_info = ratings["pageInfo"]
        if page_info["hasNextPage"]:
            cursor = page_info["endCursor"]
            time.sleep(0.5)
        else:
            break
    return all_comments

# ----------- MAIN SCRIPT ----------- #

all_data = []
cursor = None

print("Fetching professor list...")
while True:
    result = fetch_professors(cursor)
    print("Full response from RMP API:", result)
    edges = result["data"]["search"]["edges"]
    if not edges:
        break
    for edge in edges:
        prof = edge["node"]
        print(f"Fetching comments for {prof['firstName']} {prof['lastName']}...")
        prof["comments"] = fetch_comments(prof["id"])
        all_data.append(prof)
        time.sleep(1)  # Be polite!
    page_info = result["data"]["search"]["pageInfo"]
    if page_info["hasNextPage"]:
        cursor = page_info["endCursor"]
    else:
        break

with open("ratemyprofessors_uwmadison_data.json", "w") as f:
    json.dump(all_data, f, indent=2)

print(f"Scraped {len(all_data)} professors with comments!")
