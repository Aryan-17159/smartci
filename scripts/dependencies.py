"""Conservative AST import graph shared by build caching and test routing."""
import ast
from pathlib import Path


class UnsafeGraph(ValueError):
    pass


def import_graph(root):
    root = Path(root)
    files = sorted(p for folder in ('src', 'tests', 'scripts')
                   for p in (root / folder).rglob('*.py') if '__pycache__' not in p.parts)
    modules = {}
    for path in files:
        rel = path.relative_to(root).as_posix()
        module = rel[:-3].replace('/', '.')
        if module.endswith('.__init__'):
            module = module[:-9]
        modules[module] = rel
    graph = {path: set() for path in modules.values()}
    for module, rel in modules.items():
        try:
            tree = ast.parse((root / rel).read_text(encoding='utf-8'))
        except (SyntaxError, UnicodeError) as exc:
            raise UnsafeGraph(f'Cannot parse {rel}: {exc}') from exc
        package = module if rel.endswith('/__init__.py') else module.rpartition('.')[0]
        for i in range(1, len(module.split('.'))):
            ancestor = '.'.join(module.split('.')[:i])
            if ancestor in modules and modules[ancestor] != rel:
                graph[rel].add(modules[ancestor])
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = getattr(node.func, 'id', getattr(node.func, 'attr', ''))
                if (name in {'__import__', 'import_module'} or
                    isinstance(node.func, ast.Name) and name in {'exec', 'eval'} or
                    isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == 'builtins' and name in {'exec', 'eval'}):
                    raise UnsafeGraph(f'Dynamic code/import in {rel}; run all tests')
            targets = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ''
                if node.level:
                    parts = package.split('.')
                    if node.level > len(parts):
                        raise UnsafeGraph(f'Unresolved relative import in {rel}')
                    base = '.'.join(parts[:len(parts)-node.level+1] + ([base] if base else []))
                targets = [base] + [base + '.' + a.name for a in node.names
                                    if base + '.' + a.name in modules]
            for target in targets:
                if target in modules:
                    if modules[target] != rel:
                        graph[rel].add(modules[target])
                elif target.split('.')[0] in {'src', 'tests', 'scripts'}:
                    raise UnsafeGraph(f'Unresolved local import {target} in {rel}')
    return graph


def closure(graph, start):
    seen, pending = set(), [start]
    while pending:
        item = pending.pop()
        if item not in seen:
            seen.add(item)
            pending.extend(graph.get(item, ()))
    return seen
