import os
import json
import requests
from dotenv import load_dotenv

def search_azure_cognitive_search(query, endpoint, key, index):
    search_url = f"{endpoint}/indexes/{index}/docs/search?api-version=2021-04-30-Preview"
    headers = {
        "api-key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "search": query,
        #"top": 3,           # 상위 3개 문서 검색, 필요시 조정
        "queryType": "simple"
    }

    response = requests.post(search_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    load_dotenv()

    # 환경변수 로드
    azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key = os.getenv("AZURE_OAI_KEY")
    azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
    azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    azure_search_key = os.getenv("AZURE_SEARCH_KEY")
    azure_search_index = os.getenv("AZURE_SEARCH_INDEX")

    # system prompt 불러오기
    with open("model/system.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # 사용자 입력
    user_input = input("\n문장을 입력하세요:\n")

    # 1) Azure Cognitive Search 호출
    search_results = search_azure_cognitive_search(
        user_input, azure_search_endpoint, azure_search_key, azure_search_index
    )

    # 검색 결과에서 필드 추출
    documents = [doc.get("input_text", "") for doc in search_results.get("corrected_text", [])]
    context_text = "\n\n".join(documents)

    # 2) Chat Completion 호출 시 검색 결과를 컨텍스트로 포함
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"참고 문서 내용:\n{context_text}"},
        {"role": "user", "content": user_input}
    ]

    url = f"{azure_oai_endpoint}/openai/deployments/{azure_oai_deployment}/chat/completions?api-version=2024-02-15-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_oai_key
    }
    body = {
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 1000
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        result = response.json() # 반환된 결과값
        print("교정 결과:\n" + result["choices"][0]["message"]["content"] + "\n")
    else:
        print(f"\n오류 발생: {response.status_code} - {response.text}\n")

if __name__ == "__main__":
    main()
