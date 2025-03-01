import pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.dom.minidom

# Nome do arquivo Excel
file_name = 'sample.xlsx'

# Lê o arquivo Excel
excel_file = pd.ExcelFile(file_name)

# Função para criar um elemento mxCell para uma tabela
def create_table_cell(root, table_id, table_name, x, y):
    table_cell = SubElement(
        root, 
        'mxCell', 
        id=table_id, 
        value=table_name,
        style='swimlane;fontStyle=0;childLayout=stackLayout;horizontal=1;startSize=26;fillColor=none;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;whiteSpace=wrap;html=1;',
        vertex="1",
        parent="1")
    
    geometry = SubElement(table_cell, 'mxGeometry', {
        'x': str(x), 'y': str(y), 'width': "160", 'height': "104", 'as': "geometry"
    })
    
    SubElement(geometry, 'mxRectangle', {
        'x': str(x+14), 'y': str(y+10), 'width': "70", 'height': "30", 'as': "alternateBounds"
    })

    return table_cell

# Função para criar um elemento mxCell para uma variável
def create_var_cell(root, var_id, var_value, parent_id, y_offset):
    var_cell = SubElement(
        root,
        'mxCell',
        id=var_id,
        value=var_value,
        style='text;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;whiteSpace=wrap;html=1;',
        vertex="1",
        parent=parent_id)
    
    SubElement(var_cell, 'mxGeometry', {
        'y': str(y_offset), 'width': "160", 'height': "26", 'as': "geometry"
    })

    return var_cell

# Função para criar um elemento mxCell para uma linha
def create_line_cell(root, line_id, source_id, target_id):
    line_cell = SubElement(
        root,
        'mxCell',
        id=line_id,
        style='edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;',
        edge="1",
        parent="1",
        source=source_id,
        target=target_id)
    
    SubElement(line_cell, 'mxGeometry', {'relative': "1", 'as': "geometry"})

    return line_cell

# Cria a estrutura XML básica
mxfile = Element(
    'mxfile',
    host="app.diagrams.net",
    modified="2024-08-04T03:43:21.921Z",
    agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/127.0.0.0 Safari/537.36",
    etag="ZdefrzVYWugYS7S8xtlY",
    version="24.6.5",
    type="device")

diagram = SubElement(
    mxfile,
    'diagram',
    name="Página-1",
    id="JH21Qx-s8GiAd0Xb08vd")

graph_model = SubElement(
    diagram,
    'mxGraphModel',
    dx="546",
    dy="532",
    grid="1",
    gridSize="10",
    guides="1",
    tooltips="1",
    connect="1",
    arrows="1",
    fold="1",
    page="1",
    pageScale="1",
    pageWidth="827",
    pageHeight="1169",
    math="0",
    shadow="0")

root = SubElement(graph_model, 'root')
SubElement(root, 'mxCell', id="0")
SubElement(root, 'mxCell', id="1", parent="0")

# Posicionamento inicial para as tabelas
x, y = 400, 440

# Dicionário para armazenar referências de variáveis
var_references = {}

# Itera sobre as planilhas no arquivo Excel
for i, sheet in enumerate(excel_file.sheet_names):
    # Lê os dados da planilha
    df = pd.read_excel(file_name, sheet_name=sheet)
    
    # Cria a tabela no XML
    table_id = f"{sheet}"
    table_cell = create_table_cell(root, table_id, sheet, x, y)
    
    # Cria as variáveis na tabela para cada linha da primeira coluna
    for j in range(df.shape[0]):
        var_id = f"{sheet}-{df.iloc[j, 0]}"
        var_value = df.iloc[j, 0]  # Assume que a primeira coluna é a coluna desejada
        create_var_cell(root, var_id, f"+ {var_value}", table_id, 26*(j+1))
        
    # Atualiza a posição X para a próxima tabela
    x += 200

# Conecta as variáveis de acordo com os dados da segunda coluna
for i, sheet in enumerate(excel_file.sheet_names):
    df = pd.read_excel(file_name, sheet_name=sheet)
    for j in range(df.shape[0]):
        if df.shape[1] > 1 and not pd.isna(df.iloc[j, 1]):
            source_id = f"{df.iloc[j, 1]}-{df.iloc[j, 0]}"
            target_id = f"{sheet}-{df.iloc[j, 0]}"
            line_id = f"line-{i+1}-{j+1}"
            create_line_cell(root, line_id, source_id, target_id)

# Converte o XML em uma string formatada
xml_str = xml.dom.minidom.parseString(tostring(mxfile)).toprettyxml(indent="  ")

# Salva o XML em um arquivo
with open("output.drawio", "w", encoding="utf-8") as f:
    f.write(xml_str)

import time
from functools import wraps

# Benchmarking utility
def benchmark(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        print(f"{func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper

@benchmark
def process_drawio_file(file_path):
    """Example processing workflow"""
    processor = DrawIOProcessor(file_path)
    
    # Example: Optimize structure
    processor.optimize_structure()
    
    # Example: Save optimized version
    processor.save(file_path.replace('.drawio', '_optimized.drawio'))

# Async example
async def async_process(file_path):
    """Async processing example"""
    # TODO: Implement async batch processing
    pass

print("Arquivo 'output.drawio' criado com sucesso.")