FROM python:3.10
COPY chatbot.py HKBU_chatgpt.py requirements.txt  /app/  
WORKDIR /app  
RUN pip install --upgrade pip   
RUN pip install -r requirements.txt
  
CMD python chatbot.py