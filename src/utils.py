import json
import yaml
from typing import List

class Utils:
    def __init__(self):
        pass 
    
    def _generate_log(self, question:str, query_answer:str, status:str) -> None:
        """포멧에 맞는 로그 생성하는 함수"""
        ## log
        log = {
            'timestamp': self.log_time,
            'question': None,
            'response': None,
            'status': None
        }
        log['question'] = question
        log['response'] = query_answer
        log['status'] = status
        log['env'] = 'dajeong-test'
        # print(log)
        return json.dumps(log, ensure_ascii=False)
    
    def _write_log(self, log:str, path:str='response') -> None:
        self.__read_config()
        bucket_name = self.__config['bucket_name']
        current_time = self.log_time
        file_name = f'{current_time}.json'
        object_key = f'text2query/logs/{current_time}/{path}/{file_name}'
        # s3://dajeong-test/text2query/logs/{current_time}/

        self.s3.put_object(Body=log, Bucket=bucket_name, Key=object_key)

    def _read_schema_file(self) -> str:
        """작성된 테이블 schema 파일을 읽어오는 함수"""
        with open('src/schema.json', 'r' , encoding='utf-8') as f:
            schema_json = json.load(f)
        json_string = json.dumps(schema_json, indent=4, ensure_ascii=False)
        return json_string
    
    def _read_question_file(self) -> str:
        """작성된 테이블 question set 파일을 읽어오는 함수"""
        with open('src/questions.json', 'r' , encoding='utf-8') as f:
            question_json = json.load(f)
        json_string = json.dumps(question_json, indent=4, ensure_ascii=False)
        return json_string

    def _select_tables(self) -> List:
        """테이블이 많을 경우에 연관 테이블 스키마만 가져와서 schema에 전달하기 위함"""
        table_list = []
        return table_list
    
    def __read_config(self) -> None:
        """설정값 읽어오는 함수"""
        with open('src/conf.yaml', 'r') as f:
            self.__config = yaml.load(f, Loader=yaml.FullLoader)