## Installation

1. Clone the repository

```
git clone https://git.aggregatoricapaci.com/ai/dify_tool/virtual-teacher/ai-personal-assistant.git
```

2. Install all dependencies

```
pip install -r requirements.txt
cp .env.example .env
```

3. Run demo

*For api: Use api for full services* Enter the OPEN_AI_KEY in .env file

```
python -m web
```

4. Notice

*For api*

Some services has "session":"string" and "user_input":"string".

Enter the question then replace the string on user_input, replace the string on session to number or id.

Example:

{
    "session" : "123",
    "user_input":"Làm thế nào để bán được một tỷ gói mè?"
}

The result will be the response of api.

Chat history stored inside the data/folder in json format.
