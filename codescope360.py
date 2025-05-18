#!/usr/bin/env python3
"""
CodeScope 360 - Analisador estruturado de projetos Python

Este script analisa recursivamente um projeto Python e gera um relatório detalhado
em formato Markdown, descrevendo a estrutura, classes, funções, importações e 
relacionamentos entre os arquivos do projeto.

Uso:
    python codescope360.py [caminho_do_projeto]

Se o caminho não for fornecido, o diretório atual será usado.
"""

import os
import sys
import ast
import re
from datetime import datetime
import importlib.util

def get_project_path():
    """Obtém o caminho do projeto a ser analisado"""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if not os.path.isdir(path):
            print(f"Erro: O caminho '{path}' não é um diretório válido.")
            sys.exit(1)
        return path
    return os.getcwd()

def find_python_files(project_path):
    """Encontra recursivamente todos os arquivos .py no projeto"""
    python_files = []
    
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                # Caminho relativo para melhor legibilidade
                rel_path = os.path.relpath(full_path, project_path)
                python_files.append(rel_path)
    
    # Organizar arquivos pelo caminho para melhor estrutura no relatório
    python_files.sort()
    return python_files

def find_requirements_file(project_path):
    """Localiza o arquivo requirements.txt se existir"""
    req_path = os.path.join(project_path, 'requirements.txt')
    if os.path.isfile(req_path):
        return req_path
    return None

def parse_requirements(req_path):
    """Analisa o arquivo requirements.txt e extrai informações relevantes"""
    if not req_path:
        return None
    
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair dependências usando regex para lidar com formatos variados
        dependencies = []
        for line in content.splitlines():
            line = line.strip()
            # Ignorar comentários e linhas vazias
            if not line or line.startswith('#'):
                continue
            
            # Lidar com formatos de requisitos comuns
            # Exemplo: package==1.0.0, package>=1.0.0, package
            match = re.match(r'^([a-zA-Z0-9_.-]+)(?:[=<>!~]+([a-zA-Z0-9_.-]+))?', line)
            if match:
                package = match.group(1)
                version = match.group(2) if len(match.groups()) > 1 else None
                
                if version:
                    dependencies.append(f"{package} ({version})")
                else:
                    dependencies.append(package)
        
        return dependencies
    except Exception as e:
        return [f"Erro ao analisar requirements.txt: {str(e)}"]

def categorize_dependencies(dependencies):
    """Categoriza as dependências em frameworks e áreas do projeto"""
    if not dependencies:
        return {}
    
    categories = {
        "Web": ["flask", "django", "fastapi", "pyramid", "bottle", "cherrypy", "tornado", "aiohttp"],
        "Análise de Dados": ["pandas", "numpy", "scipy", "matplotlib", "seaborn", "scikit-learn", "sklearn", "tensorflow", "pytorch", "keras"],
        "Banco de Dados": ["sqlalchemy", "pymongo", "psycopg2", "mysql-connector", "pymysql", "redis", "sqlmodel"],
        "API/Requisições": ["requests", "httpx", "urllib3", "aiohttp"],
        "CLI": ["typer", "click", "argparse", "rich", "prompt-toolkit"],
        "Automação": ["selenium", "beautifulsoup4", "bs4", "scrapy", "playwright"],
        "Testes": ["pytest", "unittest", "nose", "coverage", "behave", "robot"],
        "Documentação": ["sphinx", "mkdocs", "pdoc", "pydoctor"],
        "Utilitários": ["dotenv", "pydantic", "attrs", "dataclasses"]
    }
    
    project_categories = {}
    
    # Limpar versões para comparação
    clean_deps = []
    for dep in dependencies:
        if " (" in dep:
            clean_deps.append(dep.split(" (")[0].lower())
        else:
            clean_deps.append(dep.lower())
    
    for category, frameworks in categories.items():
        matched = [dep for dep in clean_deps if any(fw.lower() in dep.lower() for fw in frameworks)]
        if matched:
            project_categories[category] = matched
    
    return project_categories

def extract_docstring(node):
    """Extrai a docstring de um nó AST, se existir"""
    if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
        return None
    
    try:
        # Em Python 3.8+, os docstrings podem ser tanto ast.Str quanto ast.Constant
        if node.body and isinstance(node.body[0], ast.Expr):
            if hasattr(node.body[0].value, 's'):  # ast.Str
                return node.body[0].value.s.strip()
            elif isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                return node.body[0].value.value.strip()
        return None
    except Exception:
        return None

def get_significant_comments(source_code):
    """Extrai comentários importantes no início do arquivo ou blocos"""
    lines = source_code.splitlines()
    significant_comments = []
    comment_block = []
    
    # Pegar comentários no início do arquivo
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            comment_block.append(line[1:].strip())
        elif not line:
            continue
        else:
            break
    
    if comment_block:
        significant_comments.append(" ".join(comment_block))
    
    # Procurar por blocos de comentários significativos (3+ linhas consecutivas)
    comment_block = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            comment_block.append(line[1:].strip())
        else:
            if len(comment_block) >= 3:
                significant_comments.append(" ".join(comment_block))
            comment_block = []
    
    # Verificar o último bloco
    if len(comment_block) >= 3:
        significant_comments.append(" ".join(comment_block))
    
    return significant_comments

def analyze_imports(tree):
    """Analisa as importações de um arquivo Python"""
    imports = {
        "standard_lib": [],
        "third_party": [],
        "project": []
    }
    
    standard_libs = [
        "abc", "argparse", "ast", "asyncio", "base64", "collections", "configparser", 
        "contextlib", "copy", "csv", "datetime", "decimal", "difflib", "enum", 
        "functools", "glob", "hashlib", "io", "itertools", "json", "logging", 
        "math", "multiprocessing", "os", "pathlib", "pickle", "random", "re", 
        "shutil", "socket", "sqlite3", "statistics", "string", "subprocess", 
        "sys", "tempfile", "threading", "time", "timeit", "traceback", "typing", 
        "unittest", "uuid", "warnings", "xml", "zipfile"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                module = name.name.split('.')[0]
                if module in standard_libs:
                    imports["standard_lib"].append(name.name)
                else:
                    # Usamos uma abordagem mais simples para determinar se é third_party ou projeto
                    try:
                        if module in sys.modules or importlib.util.find_spec(module) is not None:
                            imports["third_party"].append(name.name)
                        else:
                            imports["project"].append(name.name)
                    except (ImportError, ValueError):
                        imports["project"].append(name.name)
                        
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split('.')[0]
                import_names = [f"{node.module}.{n.name}" for n in node.names]
                
                if module in standard_libs:
                    imports["standard_lib"].extend(import_names)
                else:
                    try:
                        if module in sys.modules or importlib.util.find_spec(module) is not None:
                            imports["third_party"].extend(import_names)
                        else:
                            imports["project"].extend(import_names)
                    except (ImportError, ValueError):
                        imports["project"].extend(import_names)
    
    # Remover duplicados e ordenar
    for key in imports:
        imports[key] = sorted(list(set(imports[key])))
    
    return imports

def analyze_main_block(source_code):
    """Analisa o bloco if __name__ == "__main__" se existir"""
    main_match = re.search(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:', source_code)
    if main_match:
        # Encontrar o bloco main e extrair uma versão resumida
        main_start = main_match.start()
        lines = source_code[main_start:].splitlines()
        
        # Pegar as primeiras 5 linhas significativas (não vazias) do bloco main
        significant_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                significant_lines.append(stripped)
            if len(significant_lines) >= 5:
                break
        
        if significant_lines:
            return significant_lines
    
    return None

def analyze_python_file(file_path, project_path):
    """Analisa um arquivo Python e extrai suas características principais"""
    full_path = os.path.join(project_path, file_path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        
        # Informações básicas
        result = {
            "path": file_path,
            "classes": [],
            "functions": [],
            "docstring": extract_docstring(tree),
            "comments": get_significant_comments(source_code),
            "imports": analyze_imports(tree),
            "main_block": analyze_main_block(source_code)
        }
        
        # Extrair classes e métodos
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": extract_docstring(node),
                    "methods": []
                }
                
                # Extrair métodos da classe
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        method_info = {
                            "name": sub_node.name,
                            "docstring": extract_docstring(sub_node)
                        }
                        class_info["methods"].append(method_info)
                
                result["classes"].append(class_info)
        
        # Funções fora de classes (no nível do módulo)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                function_info = {
                    "name": node.name,
                    "docstring": extract_docstring(node)
                }
                result["functions"].append(function_info)
        
        return result
    
    except Exception as e:
        return {
            "path": file_path,
            "error": f"Erro ao analisar arquivo: {str(e)}"
        }

def infer_file_purpose(file_info):
    """Infere o propósito de um arquivo com base em seu conteúdo"""
    # Se houver erro de análise, informar
    if "error" in file_info:
        return f"Arquivo com erro de análise: {file_info['error']}"
    
    # Verificar docstring do arquivo
    if file_info.get("docstring"):
        first_line = file_info["docstring"].splitlines()[0]
        return first_line
    
    # Verificar padrões no nome do arquivo
    filename = os.path.basename(file_info["path"])
    if filename == "__init__.py":
        return "Arquivo de inicialização de pacote Python"
    elif filename == "setup.py":
        return "Script de configuração e instalação do pacote"
    elif "test" in filename.lower():
        return "Arquivo de teste"
    elif "config" in filename.lower():
        return "Arquivo de configuração"
    elif "util" in filename.lower():
        return "Utilitários e funções auxiliares"
    elif "model" in filename.lower():
        return "Definição de modelos de dados"
    elif "view" in filename.lower():
        return "Componente de visualização/interface"
    elif "controller" in filename.lower():
        return "Controlador para lógica de negócios"
    
    # Inferir pelo conteúdo
    classes = [c["name"] for c in file_info.get("classes", [])]
    functions = [f["name"] for f in file_info.get("functions", [])]
    
    # Verificar padrões específicos
    if classes:
        class_pattern = ", ".join(classes[:3])
        if len(classes) > 3:
            class_pattern += "..."
        purpose = f"Define classes: {class_pattern}"
    elif functions:
        func_pattern = ", ".join(functions[:3])
        if len(functions) > 3:
            func_pattern += "..."
        purpose = f"Implementa funções: {func_pattern}"
    elif file_info.get("main_block"):
        purpose = "Script executável com ponto de entrada principal"
    else:
        purpose = "Arquivo Python auxiliar"
    
    # Adicionar contexto com base nas importações
    imports = file_info.get("imports", {})
    if imports.get("third_party"):
        key_libs = []
        for lib in imports["third_party"]:
            if '.' in lib:
                key_libs.append(lib.split('.')[0])
            else:
                key_libs.append(lib)
                
        if "flask" in key_libs or "django" in key_libs:
            purpose += " (componente web)"
        elif "pandas" in key_libs or "numpy" in key_libs:
            purpose += " (processamento de dados)"
        elif "sqlite" in key_libs or "sqlalchemy" in key_libs:
            purpose += " (acesso a banco de dados)"
    
    return purpose

def identify_entry_points(files_info):
    """Identifica possíveis pontos de entrada do projeto"""
    entry_points = []
    
    for file_info in files_info:
        # Verificar arquivos que têm bloco main
        if file_info.get("main_block"):
            entry_points.append({
                "path": file_info["path"],
                "type": "Script executável"
            })
        
        # Verificar setup.py
        if os.path.basename(file_info["path"]) == "setup.py":
            entry_points.append({
                "path": file_info["path"],
                "type": "Instalação do pacote"
            })
        
        # Verificar scripts/cli/app no nome
        filename = os.path.basename(file_info["path"])
        if any(pattern in filename.lower() for pattern in ["app.py", "cli.py", "main.py", "run.py", "server.py"]):
            entry_points.append({
                "path": file_info["path"],
                "type": "Aplicação principal"
            })
    
    return entry_points

def map_import_relationships(files_info):
    """Mapeia as relações de importação entre os arquivos do projeto"""
    relationships = {}
    project_files = [f["path"] for f in files_info]
    
    for file_info in files_info:
        file_path = file_info["path"]
        relationships[file_path] = {"imports": [], "imported_by": []}
        
        # Converter imports do projeto para comparação de arquivos
        project_imports = file_info.get("imports", {}).get("project", [])
        for imp in project_imports:
            # Converter formato de import para formato de arquivo
            imp_parts = imp.split('.')
            possible_paths = []
            
            # Construir possíveis caminhos de arquivo
            for i in range(1, len(imp_parts) + 1):
                module_path = os.path.join(*imp_parts[:i])
                possible_paths.append(f"{module_path}.py")
                possible_paths.append(os.path.join(module_path, "__init__.py"))
            
            # Verificar se algum caminho possível está nos arquivos do projeto
            for path in possible_paths:
                if path in project_files:
                    relationships[file_path]["imports"].append(path)
                    break
    
    # Calcular "imported_by"
    for file_path, rel in relationships.items():
        for imported in rel["imports"]:
            if imported in relationships:
                relationships[imported]["imported_by"].append(file_path)
    
    return relationships

def generate_report(project_path, files_info, req_info, relationships):
    """Gera o relatório completo do projeto"""
    # Criar nome do arquivo de relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_name = os.path.basename(os.path.abspath(project_path))
    report_file = f"codescope_{project_name}_{timestamp}.md"
    
    # Identificar pontos de entrada
    entry_points = identify_entry_points(files_info)
    
    # Organizar arquivos por diretório para melhor visibilidade
    dir_structure = {}
    for file_info in files_info:
        path = file_info["path"]
        directory = os.path.dirname(path)
        if directory not in dir_structure:
            dir_structure[directory] = []
        dir_structure[directory].append(file_info)
    
    # Verificar erros de análise
    files_with_errors = [f for f in files_info if "error" in f]
    
    with open(report_file, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write(f"# Relatório de Análise do Projeto: {project_name}\n\n")
        f.write(f"*Gerado por CodeScope 360 em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n\n")
        f.write(f"**Caminho do projeto:** `{os.path.abspath(project_path)}`\n")
        f.write(f"**Total de arquivos Python:** {len(files_info)}\n\n")
        
        # Aviso de erros, se houver
        if files_with_errors:
            f.write("⚠️ **Atenção**: Encontramos problemas ao analisar alguns arquivos:\n\n")
            for file in files_with_errors:
                f.write(f"- `{file['path']}`: {file.get('error', 'Erro desconhecido')}\n")
            f.write("\n")
        
        # Dependências
        if req_info:
            f.write("## Dependências do Projeto\n\n")
            
            # Categorias de dependências
            categories = categorize_dependencies(req_info)
            if categories:
                f.write("### Categorias de dependências\n\n")
                for category, deps in categories.items():
                    f.write(f"- **{category}**: {', '.join(deps)}\n")
                f.write("\n")
            
            f.write("### Lista de dependências\n\n")
            for dep in req_info:
                f.write(f"- {dep}\n")
            f.write("\n")
        
        # Pontos de entrada
        if entry_points:
            f.write("## Pontos de Entrada do Projeto\n\n")
            for ep in entry_points:
                f.write(f"- **{ep['path']}** - {ep['type']}\n")
            f.write("\n")
        
        # Estrutura do projeto
        f.write("## Estrutura do Projeto\n\n")
        
        # Listar diretórios e arquivos
        directories = sorted(dir_structure.keys())
        for directory in directories:
            if directory:
                f.write(f"### 📁 {directory}\n\n")
            else:
                f.write("### 📁 Diretório Raiz\n\n")
            
            for file_info in dir_structure[directory]:
                basename = os.path.basename(file_info["path"])
                purpose = infer_file_purpose(file_info)
                f.write(f"- **{basename}** - {purpose}\n")
            f.write("\n")
        
        # Detalhes de cada arquivo
        f.write("## Detalhes dos Arquivos\n\n")
        
        for file_info in files_info:
            f.write(f"### 📄 {file_info['path']}\n\n")
            
            # Verificar erro
            if "error" in file_info:
                f.write(f"**⚠️ Erro:** {file_info['error']}\n\n")
                continue
            
            # Propósito
            purpose = infer_file_purpose(file_info)
            f.write(f"**Propósito:** {purpose}\n\n")
            
            # Docstring
            if file_info.get("docstring"):
                f.write("**Descrição:**\n")
                f.write(f"```\n{file_info['docstring']}\n```\n\n")
            
            # Comentários relevantes
            if file_info.get("comments"):
                f.write("**Comentários Importantes:**\n")
                for comment in file_info["comments"]:
                    f.write(f"- {comment}\n")
                f.write("\n")
            
            # Classes
            if file_info.get("classes"):
                f.write("**Classes:**\n\n")
                for cls in file_info["classes"]:
                    f.write(f"- **{cls['name']}**\n")
                    if cls.get("docstring"):
                        # Pegar apenas a primeira linha da docstring para manter o relatório conciso
                        first_line = cls["docstring"].splitlines()[0]
                        f.write(f"  - Descrição: {first_line}\n")
                    
                    if cls.get("methods"):
                        f.write("  - Métodos:\n")
                        for method in cls["methods"]:
                            f.write(f"    - `{method['name']}()`")
                            if method.get("docstring"):
                                first_line = method["docstring"].splitlines()[0]
                                f.write(f": {first_line}")
                            f.write("\n")
                f.write("\n")
            
            # Funções
            if file_info.get("functions"):
                f.write("**Funções:**\n\n")
                for func in file_info["functions"]:
                    f.write(f"- **{func['name']}()**")
                    if func.get("docstring"):
                        first_line = func["docstring"].splitlines()[0]
                        f.write(f": {first_line}")
                    f.write("\n")
                f.write("\n")
            
            # Importações
            imports = file_info.get("imports", {})
            if any(imports.values()):
                f.write("**Importações:**\n\n")
                
                if imports.get("project"):
                    f.write("- **Do projeto:**\n")
                    for imp in imports["project"]:
                        f.write(f"  - {imp}\n")
                
                if imports.get("third_party"):
                    f.write("- **Bibliotecas externas:**\n")
                    for imp in imports["third_party"]:
                        f.write(f"  - {imp}\n")
                
                if imports.get("standard_lib"):
                    f.write("- **Biblioteca padrão:**\n")
                    for imp in imports["standard_lib"][:5]:  # Limitar para economia de espaço
                        f.write(f"  - {imp}\n")
                    if len(imports["standard_lib"]) > 5:
                        f.write(f"  - ... e mais {len(imports['standard_lib'])-5} importações\n")
                f.write("\n")
            
            # Bloco Main
            if file_info.get("main_block"):
                f.write("**Bloco Principal:**\n")
                f.write("```python\n")
                f.write("if __name__ == \"__main__\":\n")
                for line in file_info["main_block"]:
                    f.write(f"    {line}\n")
                f.write("```\n\n")
            
            # Relações de importação
            if file_info["path"] in relationships:
                rel = relationships[file_info["path"]]
                
                if rel["imports"]:
                    f.write("**Importa arquivos:**\n")
                    for imp in rel["imports"]:
                        f.write(f"- {imp}\n")
                    f.write("\n")
                
                if rel["imported_by"]:
                    f.write("**Importado por:**\n")
                    for imp in rel["imported_by"]:
                        f.write(f"- {imp}\n")
                    f.write("\n")
            
            f.write("---\n\n")
        
        # Visão geral do projeto
        f.write("## Visão Geral do Projeto\n\n")
        
        # Arquivos mais importados (nós centrais)
        central_files = []
        for file_path, rel in relationships.items():
            if len(rel["imported_by"]) > 1:
                central_files.append({
                    "path": file_path,
                    "importers": len(rel["imported_by"])
                })
        
        central_files.sort(key=lambda x: x["importers"], reverse=True)
        
        if central_files:
            f.write("### Arquivos Centrais\n\n")
            f.write("Estes arquivos são importados por vários outros, indicando que são componentes centrais:\n\n")
            
            for cf in central_files[:5]:  # Top 5
                f.write(f"- **{cf['path']}** - Importado por {cf['importers']} arquivos\n")
            f.write("\n")
        
        # Conclusão
        f.write("## Conclusão\n\n")
        
        # Framework principal
        categories = categorize_dependencies(req_info) if req_info else {}
        if categories:
            main_categories = list(categories.keys())
            if main_categories:
                f.write(f"Este projeto parece ser um **aplicativo de {', '.join(main_categories)}**. ")
        
        # Tamanho do projeto
        if len(files_info) <= 5:
            f.write("É um projeto pequeno com poucos arquivos. ")
        elif len(files_info) <= 15:
            f.write("É um projeto de tamanho médio. ")
        else:
            f.write("É um projeto grande com muitos arquivos e componentes. ")
        
        # Organização
        if len(directories) > 3:
            f.write("O código está organizado em múltiplos diretórios, sugerindo uma boa separação de componentes.")
        else:
            f.write("O código está organizado em poucos diretórios.")
        
        f.write("\n\n---\n\n")
        f.write("*Relatório gerado por CodeScope 360 - Análise estruturada de projetos Python*")
    
    return report_file

def main():
    """Função principal do programa"""
    print("CodeScope 360 - Análise Estruturada de Projetos Python")
    print("-" * 60)
    
    # Obter caminho do projeto
    project_path = get_project_path()
    print(f"Analisando projeto em: {project_path}")
    
    # Encontrar arquivos Python
    python_files = find_python_files(project_path)
    if not python_files:
        print("Nenhum arquivo Python encontrado no projeto!")
        sys.exit(1)
    
    print(f"Encontrados {len(python_files)} arquivos Python.")
    
    # Analisar requirements.txt
    req_path = find_requirements_file(project_path)
    req_info = None
    if req_path:
        print("Analisando requirements.txt...")
        req_info = parse_requirements(req_path)
    
    # Analisar cada arquivo Python
    print("Analisando arquivos Python...")
    files_info = []
    for i, file_path in enumerate(python_files):
        print(f"  [{i+1}/{len(python_files)}] {file_path}")
        file_info = analyze_python_file(file_path, project_path)
        files_info.append(file_info)
    
    # Mapear relacionamentos entre arquivos
    print("Mapeando relacionamentos entre arquivos...")
    relationships = map_import_relationships(files_info)
    
    # Gerar relatório
    print("Gerando relatório...")
    report_file = generate_report(project_path, files_info, req_info, relationships)
    
    print("-" * 60)
    print(f"Análise concluída! Relatório salvo em: {report_file}")

if __name__ == "__main__":
    main()