import google.generativeai as genai
genai.configure(api_key="AIzaSyCv1CwT5pWAF-fkj5nHjIrryu6F2gZeL9c")
for m in genai.list_models():
    print(m.name)
