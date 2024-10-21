from datetime import datetime

import yaml
import boto3
import openai

from utils import Utils
from prompt import base_prompt


class SQLGenerator(Utils):
    def __init__(self):
        # 필요한 key 읽기
        self.__read_config()

        # (api doc) https://github.com/openai/openai-python
        self.client = openai.OpenAI(
            api_key=self.__config["openai_api_key"],
        )

        # 로그 적재를 위한 s3 세션
        session = boto3.Session(
            aws_access_key_id=self.__config["aws_access_key_id"],
            aws_secret_access_key=self.__config["aws_secret_access_key"],
        )
        self.s3 = session.client("s3")
        # 로그에 남길 시간
        self.log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def main(self, question: str):
        """메인 실행 함수"""
        # prompt 생성
        prompt = self.create_prompt()
        # 질문 할당
        query_answer = self.generate_sql(question=question, prompt=prompt)
        return query_answer

    def generate_sql(self, question: str, prompt: str) -> str:
        """api 호출해서 응답받고 로그를 남기는 함수"""
        # 호출
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": f"Translate the following question into SQL based on the given schema,table usages and question history info:\nQuestion: {question}\n",
                },
            ],
        )

        # log
        try:
            query_answer = response.choices[0].message.content.strip()
            status = "SUCCESS"
        except:
            query_answer = response
            status = "FAIL"

        response_log = self._generate_log(question, query_answer, status)
        self._write_log(log=response_log, path="response")
        return query_answer

    def create_prompt(self) -> str:
        """스키마 정보와 함께 질문을 포함한 프롬프트 생성하는 함수"""
        schema = self._read_schema_file()
        question_history = self._read_question_file()
        prompt = f"""{base_prompt} : \nSchema: {schema}\nQuestion_history: {question_history}"""
        self._write_log(schema, path="prompt/schema")
        self._write_log(question_history, path="prompt/question_history")
        return prompt

    def __read_config(self) -> None:
        """설정값 읽어오는 함수"""
        with open("src/conf.yaml", "r") as f:
            self.__config = yaml.load(f, Loader=yaml.FullLoader)


if __name__ == "__main__":
    sql_generator = SQLGenerator()
    # question = "How many loan account did each user have? Use the lastest loan_id per each user."
    # question = "How many loan account did each user have? Use the lastest loan_id per each user. Period after 2024-08-01."
    # question = "2024-08-01 이후, mydata 기준으로 유저별로 가지고 있는 대출계좌 수를 확인해줘"
    # question = "Check the number of loan accounts per user based on mydata after August 1, 2024."
    # question = "유저별 최신 신용점수를 알고 싶어"
    # question = "유저아이디 1903978가 2024년 8월에 LM_schedule_view로그가 있는지 알려줘. mixpanel_id로 확인해줘"
    # question = "check if there is user logs record named LM_schedule_view for the user with user ID 1903978 in 2024/08."
    # question = "마수동 알람 설정한 유저 중에 유저 최신 신용점수를 알고 싶어"
    question = "유저 아이디 3324539인 유저가 mixpanel에 LM_schedule_view 이벤트 로그가 없어. appsflyer에 로그가 있는지 확인해줘. "
    sql_query = sql_generator.main(question)
    print(f"""Generated SQL Query:\n{sql_query}""")
