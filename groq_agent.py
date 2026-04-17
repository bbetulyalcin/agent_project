import os
from groq import Groq
import requests
import json
import time
from dotenv import load_dotenv

api_key_degiskeni = os.getenv("api_key")
client = Groq(api_key=api_key_degiskeni)

def get_user_details(email: str):
    print(f"--- [API] Kullanıcı sorgulanıyor: {email} ---")
    response = requests.get(f"http://127.0.0.1:5000/api/user?email={email}")
    return response.json() if response.status_code == 200 else {"error": "Yok"}

def get_recent_transactions(user_id: str):
    print(f"--- [API] İşlemler çekiliyor: {user_id} ---")
    response = requests.get(f"http://127.0.0.1:5000/api/transactions/{user_id}")
    return response.json() if response.status_code == 200 else []

def check_fraud_reason(transaction_id: str):
    print(f"--- [API] Red sebebi sorgulanıyor: {transaction_id} ---")
    response = requests.get(f"http://127.0.0.1:5000/api/fraud-check/{transaction_id}")
    return response.json() if response.status_code == 200 else {"reason": "Bilinmiyor"}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_details",
            "description": "E-posta adresinden kullanıcı bilgilerini ve ID'sini getirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Kullanıcının e-posta adresi"}
                },
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_transactions",
            "description": "Kullanıcı ID'si ile son işlemleri listeler.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Kullanıcı ID'si"}
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_fraud_reason",
            "description": "İşlem ID'si ile reddedilme nedenini getirir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "string", "description": "İşlem (Transaction) ID'si"}
                },
                "required": ["transaction_id"],
            },
        },
    }
]

def run_agent(user_prompt):
    messages = [
        {"role": "system", "content": """
        Sen profesyonel bir veri asistanısın. KESİN KURALLAR:
        1. Araçları SADECE resmi JSON tool_calls mekanizmasıyla çağır. Ekrana <function> yazma.
        2. Bir işlemi bitirmeden asla pes etme. Kullanıcıyı bul, ID'yi al, sonra işlemleri sorgula, başarısız işlem varsa nedenini sorgula.
        3. Tüm veriler toplandığında net bir rapor sun.
        """},
        {"role": "user", "content": user_prompt}
    ]
    
    for step in range(10): 
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
       
        if not response_message.tool_calls:
            if "<function=" in (response_message.content or ""):
                return "Sistem Hatası: Model formatı bozdu. Lütfen soruyu farklı bir şekilde sorun."
            return response_message.content

        messages.append(response_message)
        
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_user_details":
                result = get_user_details(function_args.get("email"))
            elif function_name == "get_recent_transactions":
                result = get_recent_transactions(function_args.get("user_id"))
            elif function_name == "check_fraud_reason":
                result = check_fraud_reason(function_args.get("transaction_id"))
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": json.dumps(result),
            })
            
        
    return "Üzgünüm, sistem çok fazla adıma girdiği için işlemi durdurdum."

if __name__ == "__main__":
    print("--- Asistan Hazır! ---")
    while True:
        soru = input("\nSiz: ")
        if soru.lower() in ["exit", "quit"]: break
        
        try:
            cevap = run_agent(soru)
            print(f"\nAsistan: {cevap}")
        except Exception as e:
            print(f"Hata: {e}")