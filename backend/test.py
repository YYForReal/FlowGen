# pip install plantuml-creator

# 编写一个简单的示例代码，用于渲染plantuml的代码成为图片

from plantuml_creator import PlantUML

uml_code = """
@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi
@enduml
"""


def test_plantuml():
    plantuml = PlantUML()
    png = plantuml.generate_png(uml_code)
    with open('diagram.png', 'wb') as f:
        f.write(png)

test_plantuml()
