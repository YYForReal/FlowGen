import asyncio
from typing import Tuple
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellTimeoutError, DeadKernelError
from nbformat.v4 import new_notebook, new_code_cell
import re

def remove_escape_and_color_codes(input_str: str) -> str:
    """
    使用正则表达式去除Jupyter Notebook输出结果中的转义字符和颜色代码。
    """
    pattern = re.compile(r"\x1b\[[0-9;]*[mK]")
    return pattern.sub("", input_str)

async def execute_code(code: str, timeout: int = 120, kernel_name: str = "python") -> Tuple[bool, str]:
    """
    执行传入的代码字符串，并返回执行是否成功以及输出结果或失败消息。

    参数：
        code (str): 要执行的代码字符串。
        timeout (int): 执行超时时间，默认120秒。
        kernel_name (str): 要使用的Jupyter内核名称，默认为"python"。

    返回：
        Tuple[bool, str]: 一个包含执行是否成功的布尔值和输出结果或错误消息的元组。
    """
    # 创建一个新的Notebook对象
    nb = new_notebook()
    nb.cells.append(new_code_cell(source=code))

    # 创建NotebookClient对象
    client = NotebookClient(nb, timeout=timeout, kernel_name=kernel_name)

    try:
        # 使用run_in_executor在后台线程中执行代码
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, client.execute)

        # 获取执行后的第一个单元格
        cell = nb.cells[0]
        if 'outputs' in cell:
            outputs = cell['outputs']
            output_text = ""
            is_success = True
            for output in outputs:
                if output['output_type'] == 'stream':
                    output_text += output.get('text', '')
                elif output['output_type'] == 'execute_result':
                    output_text += output['data'].get('text/plain', '')
                elif output['output_type'] == 'error':
                    output_text += "\n".join(output.get('traceback', []))
                    is_success = False
            # 清理输出中的转义字符和颜色代码
            output_text = remove_escape_and_color_codes(output_text)
            return is_success, output_text
        else:
            return True, "没有输出结果。"
    except CellTimeoutError:
        return False, "代码执行超时。"
    except DeadKernelError:
        return False, "内核在执行过程中意外终止。"
    except Exception as e:
        return False, f"执行出错: {str(e)}"


import asyncio

async def main():
    code = """
import math
print("The square root of 16 is", math.sqrt(16))
"""
    success, output = await execute_code(code)
    if success:
        print("执行成功，输出结果：")
        print(output)
    else:
        print("执行失败，错误信息：")
        print(output)

# 运行异步主函数
asyncio.run(main())
