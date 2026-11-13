import sys
import json
import time
import threading
from core.api_config import *
from core import cost_log

MAX_TRY = 5


class ThinkingBudgetExhaustedError(RuntimeError):
    """Raised when generation ends before producing final response content."""


_log_lock = threading.Lock()
_trace_lock = threading.Lock()
_token_lock = threading.Lock()

log_path = None
api_trace_json_path = None
total_prompt_tokens = 0
total_response_tokens = 0

# LLM 推理参数（可通过 init_llm_params 配置）
temperature = 0
max_tokens = 16384


def init_log_path(my_log_path):
    global total_prompt_tokens
    global total_response_tokens
    global log_path
    global api_trace_json_path
    log_path = my_log_path
    total_prompt_tokens = 0
    total_response_tokens = 0
    dir_name = os.path.dirname(log_path)
    os.makedirs(dir_name, exist_ok=True)

    # 另外一个记录api调用的文件
    api_trace_json_path = os.path.join(dir_name, 'api_trace.json')


def init_llm_params(my_temperature=None, my_max_tokens=None):
    """设置 LLM 推理参数 temperature 与 max_tokens。传入 None 则保持原值。"""
    global temperature
    global max_tokens
    if my_temperature is not None:
        temperature = my_temperature
    if my_max_tokens is not None:
        max_tokens = my_max_tokens
    print(f"LLM params -> temperature: {temperature}, max_tokens: {max_tokens}")


def api_func(prompt:str):
    global MODEL_NAME
    global temperature
    global max_tokens
    print(f"\nUse OpenAI model: {MODEL_NAME}\n")
    # 构造可选参数，max_tokens 为 None 时不传给 API
    optional_kwargs = {'temperature': temperature}
    if max_tokens is not None:
        optional_kwargs['max_tokens'] = max_tokens
    if 'Llama' in MODEL_NAME:
        openai.api_version = None
        openai.api_type = "open_ai"
        openai.api_key = "EMPTY"
        response = cost_log.request(openai.ChatCompletion.create,
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            **optional_kwargs
        )
    elif openai.api_type == "open_ai":
        openai.api_version = None
        response = cost_log.request(openai.ChatCompletion.create,
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            **optional_kwargs
        )
    else:
        response = cost_log.request(openai.ChatCompletion.create,
            engine=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            # temperature=0.1
            **optional_kwargs
        )
    choice = response['choices'][0]
    content = choice['message']['content']
    finish_reason = choice.get('finish_reason')
    if content is None or not content.strip():
        if finish_reason == 'length':
            raise ThinkingBudgetExhaustedError(
                f'Model exhausted max_tokens={max_tokens} before producing final response content.'
            )
        raise ValueError(f'LLM returned empty response content (finish_reason={finish_reason!r}).')
    text = content.strip()
    prompt_token = (response.get('usage') or {}).get('prompt_tokens')
    response_token = (response.get('usage') or {}).get('completion_tokens')
    return text, prompt_token, response_token


def safe_call_llm(input_prompt, **kwargs) -> str:
    """
    函数功能描述：输入 input_prompt ，返回 模型生成的内容（内部自动错误重试5次，5次错误抛异常）
    """
    global MODEL_NAME
    global log_path
    global api_trace_json_path
    global total_prompt_tokens
    global total_response_tokens

    cost_log.begin_call(kwargs)
    for i in range(5):
        try:
            if log_path is None:
                sys_response, prompt_token, response_token = api_func(input_prompt)
                print(f"\nsys_response: \n{sys_response}")
                print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n')
            else:
                if api_trace_json_path is None:
                    raise FileExistsError('api_trace_json_path is None, init_log_path first!')

                # Keep the network request outside locks so requests can run concurrently.
                sys_response, prompt_token, response_token = api_func(input_prompt)

                with _token_lock:
                    total_prompt_tokens += prompt_token or 0
                    total_response_tokens += response_token or 0
                    cur_total_prompt_tokens = total_prompt_tokens
                    cur_total_response_tokens = total_response_tokens

                trace_dict = dict(kwargs)
                trace_dict.update({
                    'response': '\n' + sys_response.strip() + '\n',
                    'input_prompt': input_prompt.strip() + '\n',
                    'prompt_token': prompt_token,
                    'response_token': response_token,
                    'cur_total_prompt_tokens': cur_total_prompt_tokens,
                    'cur_total_response_tokens': cur_total_response_tokens
                })
                with _trace_lock:
                    with open(api_trace_json_path, 'a+', encoding='utf8') as trace_json_fp:
                        print(json.dumps(trace_dict, ensure_ascii=False), file=trace_json_fp, flush=True)

                with _log_lock:
                    with open(log_path, 'a+', encoding='utf8') as log_fp:
                        print('\n' + f'*'*20 +'\n', file=log_fp)
                        print(input_prompt, file=log_fp)
                        print('\n' + f'='*20 +'\n', file=log_fp)
                        print(sys_response, file=log_fp)
                        print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n', file=log_fp)
                        print(f'\n total_prompt_tokens,total_response_tokens: {cur_total_prompt_tokens} {cur_total_response_tokens}\n', file=log_fp)

                print(f'\n prompt_token,response_token: {prompt_token} {response_token}\n')
                print(f'\n total_prompt_tokens,total_response_tokens: {cur_total_prompt_tokens} {cur_total_response_tokens}\n')
            return sys_response
        except ThinkingBudgetExhaustedError:
            raise
        except Exception as ex:
            print(type(ex).__name__)
            print(f'Request {MODEL_NAME} failed. try {i} times. Sleep 20 secs.')
            time.sleep(20)

    raise ValueError('safe_call_llm error!')


if __name__ == "__main__":
    res = safe_call_llm('我爸妈结婚为什么不邀请我？')
    print(res)
