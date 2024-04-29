
FROM python:3.12


WORKDIR /app


COPY . /app


RUN if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi


CMD ["python", "lesson7_ht1.py"]