import os
import json
import http.client

class Issue:
    number = -1
    title = ''
    body = ''
    repoName = ''

def gemini(prompt: str, api_key: str):
    conn = http.client.HTTPSConnection("generativelanguage.googleapis.com")

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }

    conn.request(
        "POST",
        "/v1beta/models/gemini-2.0-flash:generateContent",
        body=json.dumps(payload),
        headers=headers
    )

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    result = json.loads(data)

    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        print("Gemini response:", result)
        return ""


def use_prompt(issue: Issue, api_type: str, api_key: str):
    if issue.number == -1:
        raise ValueError('Issue number is required')

    branch_name = f'ai/issue-{issue.number}'
    # Create a new branch
    os.system(f'git checkout -b {branch_name}')

    prompt = f'''
    Please review the following issue:
    Title: {issue.title}
    Body: {issue.body}
    '''

    data = ''

    if api_type == 'gemini':
        data = gemini(
            prompt,
            api_key
        )

    else:
        raise ValueError(f'API type {api_type} is not supported')

    # print(f"data: \n{data}")

    if data == '':
        raise ValueError('AI response is empty')

    with open("AI_REVIEW.md", "w", encoding="utf-8") as f:
        f.write(data)

    # Add all changes to the branch
    os.system('git add .')
    # git commit
    os.system('git commit -m "AI: Review issue"')
    # git push
    os.system(f'git push origin {branch_name}')


def main():
    # handle environment variables
    issue_number = os.environ.get('ISSUE_NUMBER', '-1')
    issue_title = os.environ.get('ISSUE_TITLE', '')
    issue_body = os.environ.get('ISSUE_BODY', '')
    repo_name = os.environ.get('REPO_NAME', '')
    api_type = os.environ.get('API_TYPE', '').lower()
    api_key = os.environ.get('API_KEY', '')

    issue = Issue()
    issue.number = int(issue_number)
    issue.title = issue_title
    issue.body = issue_body
    issue.repoName = repo_name

    use_prompt(issue, api_type, api_key)

if __name__ == "__main__":
    main()
