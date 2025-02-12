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
        # "user_prompt": "在流程图中添加评审环节，位于数据收集和数据分析之间",
        "user_prompt": "将图中的英文改成中文",
        "model_name": "glm",
        "current_drawio": """<mxfile host=\"localhost\" modified=\"2025-02-11T10:05:59.429Z\" agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36\" etag=\"SUPP3Dd8uJJ0l0Wf3-oK\" version=\"@DRAWIO-VERSION@\" type=\"device\">\n  <diagram id=\"C5RBs43oDa-KdzZeNtuy\" name=\"Page-1\">\n    <mxGraphModel dx=\"1017\" dy=\"655\" grid=\"1\" gridSize=\"10\" guides=\"1\" tooltips=\"1\" connect=\"1\" arrows=\"1\" fold=\"1\" page=\"1\" pageScale=\"1\" pageWidth=\"827\" pageHeight=\"1169\" math=\"0\" shadow=\"0\">\n      <root>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-0\" />\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-1\" parent=\"WIyWlLk6GJQsqaUBKTNV-0\" />\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-2\" value=\"\" style=\"rounded=0;html=1;jettySize=auto;orthogonalLoop=1;fontSize=11;endArrow=block;endFill=0;endSize=8;strokeWidth=1;shadow=0;labelBackgroundColor=none;edgeStyle=orthogonalEdgeStyle;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" source=\"WIyWlLk6GJQsqaUBKTNV-3\" target=\"WIyWlLk6GJQsqaUBKTNV-6\" edge=\"1\">\n          <mxGeometry relative=\"1\" as=\"geometry\" />\n        </mxCell>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-3\" value=\"Lamp doesn&#39;t work\" style=\"rounded=1;whiteSpace=wrap;html=1;fontSize=12;glass=0;strokeWidth=1;shadow=0;fillColor=#f5f5f5;fontColor=#333333;strokeColor=#666666;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" vertex=\"1\">\n          <mxGeometry x=\"180\" y=\"80\" width=\"120\" height=\"40\" as=\"geometry\" />\n        </mxCell>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-4\" value=\"Yes\" style=\"rounded=0;html=1;jettySize=auto;orthogonalLoop=1;fontSize=11;endArrow=block;endFill=0;endSize=8;strokeWidth=1;shadow=0;labelBackgroundColor=none;edgeStyle=orthogonalEdgeStyle;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" source=\"WIyWlLk6GJQsqaUBKTNV-6\" target=\"WIyWlLk6GJQsqaUBKTNV-10\" edge=\"1\">\n          <mxGeometry y=\"20\" relative=\"1\" as=\"geometry\">\n            <mxPoint as=\"offset\" />\n          </mxGeometry>\n        </mxCell>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-6\" value=\"Lamp&lt;br&gt;plugged in?\" style=\"rhombus;whiteSpace=wrap;html=1;shadow=0;fontFamily=Helvetica;fontSize=12;align=center;strokeWidth=1;spacing=6;spacingTop=-4;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" vertex=\"1\">\n          <mxGeometry x=\"190\" y=\"170\" width=\"100\" height=\"80\" as=\"geometry\" />\n        </mxCell>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-8\" value=\"No\" style=\"rounded=0;html=1;jettySize=auto;orthogonalLoop=1;fontSize=11;endArrow=block;endFill=0;endSize=8;strokeWidth=1;shadow=0;labelBackgroundColor=none;edgeStyle=orthogonalEdgeStyle;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" source=\"WIyWlLk6GJQsqaUBKTNV-10\" target=\"WIyWlLk6GJQsqaUBKTNV-11\" edge=\"1\">\n          <mxGeometry x=\"0.3333\" y=\"20\" relative=\"1\" as=\"geometry\">\n            <mxPoint as=\"offset\" />\n          </mxGeometry>\n        </mxCell>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-10\" value=\"Bulb&lt;br&gt;burned out?\" style=\"rhombus;whiteSpace=wrap;html=1;shadow=0;fontFamily=Helvetica;fontSize=12;align=center;strokeWidth=1;spacing=6;spacingTop=-4;fillColor=#e1d5e7;strokeColor=#9673a6;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" vertex=\"1\">\n          <mxGeometry x=\"190\" y=\"290\" width=\"100\" height=\"80\" as=\"geometry\" />\n        </mxCell>\n        <mxCell id=\"WIyWlLk6GJQsqaUBKTNV-11\" value=\"Repair Lamp\" style=\"rounded=1;whiteSpace=wrap;html=1;fontSize=12;glass=0;strokeWidth=1;shadow=0;fillColor=#f5f5f5;fontColor=#333333;strokeColor=#666666;\" parent=\"WIyWlLk6GJQsqaUBKTNV-1\" vertex=\"1\">\n          <mxGeometry x=\"180\" y=\"430\" width=\"120\" height=\"40\" as=\"geometry\" />\n        </mxCell>\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n"""
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