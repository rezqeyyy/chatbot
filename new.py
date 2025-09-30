import google.generativeai as genai
genai.configure(api_key="AIzaSyCddaaC0_q-Nf9UUcH-nvWqkzi0CS8k3lk")
for m in genai.list_models():
    print(m.name)
