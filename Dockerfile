FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# If using pdfkit, install wkhtmltopdf
RUN apt-get update && apt-get install -y wkhtmltopdf
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.enableCORS=false"]