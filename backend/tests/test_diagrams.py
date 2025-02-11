import requests
import pytest
from typing import Dict, Any
# python backend/tests/test_diagrams.py

BASE_URL = "http://localhost:8000"

def test_generate_diagram():
    """测试生成图表接口"""
    url = f"{BASE_URL}/generate-diagram"
    
    # 测试数据
    payload = {
        "type": "flowchart",  # 假设type字段是必需的，根据实际情况修改
        "user_prompt": "在流程图中添加评审环节，位于数据收集和数据分析之间",
        "current_drawio": "<mxfile>...</mxfile>"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 如果响应状态码不是200，将引发异常
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()

        print(data)

        # 验证响应数据结构
        assert isinstance(data, dict)
        assert "success" in data  # 假设响应中包含drawio字段，根据实际情况修改
        assert "analysis" in data
        assert "content" in data

        assert data["success"] == True        
        
        print("测试成功!")
        print("响应数据:", data)
        
    except requests.exceptions.RequestException as e:
        pytest.fail(f"请求失败: {str(e)}")
    except AssertionError as e:
        pytest.fail(f"响应验证失败: {str(e)}")
    except Exception as e:
        pytest.fail(f"测试过程中出现未知错误: {str(e)}")

if __name__ == "__main__":
    test_generate_diagram() 