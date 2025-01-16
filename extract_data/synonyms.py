from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='llama3.1', messages=[
  {
    'role': 'user',
    'content': 'Compressed Natural Gas Compressed Natural Gas หาคำพ้องภาษาไทยและตัวย่อภาษาอังกฤษถ้ามี',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)



