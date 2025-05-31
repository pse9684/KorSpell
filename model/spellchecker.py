import os
import json
from dotenv import load_dotenv

# Add OpenAI import
from openai import AzureOpenAI

def main(): 
        
    try:
        # Flag to show citations
        show_citations = False

        # Get configuration settings 
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        azure_search_key = os.getenv("AZURE_SEARCH_KEY")
        azure_search_index = os.getenv("AZURE_SEARCH_INDEX")

        # Load system prompt from file
        with open("model/system.txt", "r", encoding="utf-8") as f:
            system_prompt = f.read()
        
        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            base_url=f"{azure_oai_endpoint}/openai/deployments/{azure_oai_deployment}",
            api_key=azure_oai_key,
            api_version="2023-09-01-preview")

        # Get the prompt
        text = input('\n문장을 입력하세요: \n')

        # Configure your data source
        extension_config = dict(dataSources = [
            {
                "type": "AzureCognitiveSearch",
                "parameters": {
                    "endpoint": azure_search_endpoint,
                    "key": azure_search_key,
                    "indexName": azure_search_index
                }
            }
        ])

        # Send request to Azure OpenAI model
        print("Azure OpenAI로 요청 중...\n")

        response = client.chat.completions.create(
            model = azure_oai_deployment,
            temperature = 0.5,
            max_tokens = 1000,
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )

        # Print response
        print("교정 결과: " + response.choices[0].message.content + "\n")

        if (show_citations):
            # Print citations
            print("Citations:")
            citations = response.choices[0].message.context["messages"][0]["content"]
            citation_json = json.loads(citations)
                
        
    except Exception as ex:
        print(ex)


if __name__ == '__main__': 
    main()