from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LEETCODE_GRAPHQL = "https://leetcode.com/graphql/"


@app.get("/api/tag/{tag}")
async def get_questions_by_tag(tag: str, type:str):
    print(tag + " "+ type)
    query = None
    variable = None
    if type == 'topic':
        query = """
        query problemsetQuestionList(
          $categorySlug: String,
          $limit: Int,
          $skip: Int,
          $filters: QuestionListFilterInput
        ) {
          problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
          ) {
            total: totalNum
            questions: data {
              difficulty
              title
              titleSlug
              paidOnly: isPaidOnly
            }
          }
        }
        """
        variables = {
                "categorySlug": "",
                "skip": 0,
                "limit": 4000,
                "filters": {
                    "tags": [tag]
                }
            }
    elif type == 'pattern':
        query = """
                query favoriteQuestionList(
                  $favoriteSlug: String!,
                  $limit: Int,
                  $skip: Int,
                  $filter: FavoriteQuestionFilterInput
                ) {
                  problemsetQuestionList: favoriteQuestionList(
                    favoriteSlug: $favoriteSlug
                    limit: $limit
                    skip: $skip
                    filter: $filter
                  ) {
                    total: totalLength
                    questions: questions {
                      difficulty
                      paidOnly: paidOnly
                      title
                      titleSlug
                    }
                  }
                  }
                """
        variables = {
            "favoriteSlug": tag,
            "skip": 0,
            "limit": 4000,
            "filters": {}
        }

    async with httpx.AsyncClient() as client:
        #print(variables)
        response = await client.post(
            LEETCODE_GRAPHQL,
            json={
                "query": query,
                "variables": variables
            },
            headers={
                "Content-Type": "application/json"
            }
        )
    #print(response)
    data = response.json()
    #print(data)
    questions = data["data"]["problemsetQuestionList"]["questions"]
    #print(questions)

    # Remove paid questions
    questions = [
        q for q in questions
        if not q["paidOnly"]
    ]

    customData = {}
    data["data"]["problemsetQuestionList"]["questions"] = questions
    data["data"]["problemsetQuestionList"]["total"] = len(questions)
    questions = data["data"]["problemsetQuestionList"]["questions"]

    #print(questions)
    customQuestions = [{
     "difficulty": q['difficulty'],
     "paidOnly": q['paidOnly'],
     "title": q['title'],
     "titleSlug" : q['titleSlug']
    }
    for q in questions
    ]
    data["data"]["problemsetQuestionList"]["questions"] = customQuestions
    print(data["data"]["problemsetQuestionList"]["questions"])
    return data