import yaml
import re
import os
import ast
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class Violation:
    rule: str
    severity: str
    line_number: int
    message: str
    code_snippet: str

class CodeReviewTool:
    def __init__(self, rules_file: str, debug: bool = False):
        """Initialize the tool with YAML rules"""
        self.debug = debug
        self.rules = self.load_rules(rules_file)
        self.violations: List[Violation] = []
        if self.debug:
            print(f"[DEBUG] Loaded rules from {rules_file}")
        
    def load_rules(self, rules_file: str) -> Dict:
        """Load rules from YAML file"""
        with open(rules_file, 'r') as f:
            return yaml.safe_load(f)
    
    def analyze_file(self, filepath: str) -> List[Violation]:
        """Analyze a Python file for violations"""
        self.violations = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
        
        if self.debug:
            print(f"[DEBUG] Analyzing {filepath} ({len(lines)} lines)")
        
        # Check all rule categories
        self.check_naming_conventions(lines)
        self.check_line_length(lines)
        self.check_duplicated_code(lines)
        self.check_complexity(filepath, lines)
        self.check_trailing_whitespace(lines)
        self.check_unused_imports(lines)
        self.check_security_issues(lines)
        self.check_bug_detection(lines, content)
        self.check_best_practices(lines)
        self.check_performance_issues(lines)
        
        if self.debug:
            print(f"[DEBUG] Found {len(self.violations)} violations")
        
        return self.violations
    
    def add_violation(self, rule: str, severity: str, line_num: int, 
                     message: str, code_snippet: str):
        """Add a violation to the list"""
        self.violations.append(Violation(
            rule=rule,
            severity=severity,
            line_number=line_num,
            message=message,
            code_snippet=code_snippet
        ))
        if self.debug:
            print(f"[DEBUG] Added violation: {rule} at line {line_num}")
    
    def check_naming_conventions(self, lines: List[str]):
        """Check naming conventions (PEP 8)"""
        rule_config = self.get_rule_config('naming_conventions')
        if not rule_config or not rule_config.get('enabled'):
            return
        
        for i, line in enumerate(lines, 1):
            # Check for CamelCase variables (should be snake_case)
            if re.search(r'^\s*[a-z]+[A-Z]\w*\s*=', line):
                self.add_violation(
                    'naming_conventions', 'info', i,
                    "Variable should use snake_case naming",
                    line.strip()
                )
    
    def check_line_length(self, lines: List[str]):
        """Check line length (max 120 characters)"""
        rule_config = self.get_rule_config('line_length')
        if not rule_config or not rule_config.get('enabled'):
            return
        
        threshold = rule_config.get('threshold', 120)
        for i, line in enumerate(lines, 1):
            if len(line.rstrip()) > threshold:
                self.add_violation(
                    'line_length', 'info', i,
                    f"Line exceeds {threshold} characters (length: {len(line.rstrip())})",
                    line.rstrip()[:80] + "..."
                )
    
    def check_duplicated_code(self, lines: List[str]):
        """Check for duplicated code blocks"""
        rule_config = self.get_rule_config('duplicated_code')
        if not rule_config or not rule_config.get('enabled'):
            return
        
        threshold = rule_config.get('threshold', 3)
        seen_blocks = {}
        
        for i in range(len(lines) - threshold + 1):
            block = tuple(lines[i:i+threshold])
            block_str = ''.join(block).strip()
            
            if block_str and not block_str.startswith('#'):
                if block_str in seen_blocks:
                    self.add_violation(
                        'duplicated_code', 'major', i+1,
                        f"Duplicated code block (first occurrence at line {seen_blocks[block_str]})",
                        block_str[:80]
                    )
                else:
                    seen_blocks[block_str] = i+1
    
    def check_complexity(self, filepath: str, lines: List[str]):
        """Check cyclomatic complexity"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self.calculate_complexity(node)
                    threshold = self.get_rule_config('cyclomatic_complexity', {}).get('threshold', 10)
                    
                    if complexity > threshold:
                        self.add_violation(
                            'cyclomatic_complexity', 'major', node.lineno,
                            f"Function '{node.name}' has cyclomatic complexity {complexity} (threshold: {threshold})",
                            f"def {node.name}(...)"
                        )
        except SyntaxError as e:
            print(f"[WARNING] Syntax error in {filepath}: {e}")
    
    def calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
        return complexity
    
    def check_trailing_whitespace(self, lines: List[str]):
        """Check for trailing whitespace"""
        rule_config = self.get_rule_config('trailing_whitespace')
        if not rule_config or not rule_config.get('enabled'):
            return
        
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip('\n'):
                self.add_violation(
                    'trailing_whitespace', 'minor', i,
                    "Line has trailing whitespace",
                    line.rstrip()
                )
    
    def check_unused_imports(self, lines: List[str]):
        """Check for unused imports"""
        rule_config = self.get_rule_config('unused_imports')
        if not rule_config or not rule_config.get('enabled'):
            return
        
        import_pattern = r'^\s*(from\s+\w+\s+import\s+\*|import\s+\w+)'
        for i, line in enumerate(lines, 1):
            if re.match(import_pattern, line):
                # Simple check for star imports or unused imports
                if 'import *' in line:
                    self.add_violation(
                        'star_imports', 'major', i,
                        "Avoid using 'from module import *'",
                        line.strip()
                    )
    
    def check_security_issues(self, lines: List[str]):
        """Check for security vulnerabilities"""
        # Hardcoded credentials
        credentials_pattern = r'(password|api_key|secret|token|pwd)\s*=\s*["\']'
        for i, line in enumerate(lines, 1):
            if re.search(credentials_pattern, line, re.IGNORECASE):
                self.add_violation(
                    'hardcoded_credentials', 'critical', i,
                    "Hardcoded credentials found",
                    line.strip()
                )
        
        # SQL injection - more flexible matching
        for i, line in enumerate(lines, 1):
            if ('SELECT' in line.upper() or 'INSERT' in line.upper()) and ('+' in line or 'f"' in line or "f'" in line):
                self.add_violation(
                    'sql_injection', 'critical', i,
                    "Potential SQL injection vulnerability",
                    line.strip()
                )
        
        # eval/exec usage
        for i, line in enumerate(lines, 1):
            if re.search(r'\b(eval|exec)\s*\(', line):
                self.add_violation(
                    'eval_exec_usage', 'critical', i,
                    "Avoid using eval() or exec()",
                    line.strip()
                )
        
        # pickle usage
        for i, line in enumerate(lines, 1):
            if re.search(r'pickle\.(loads|dumps)', line):
                self.add_violation(
                    'pickle_usage', 'major', i,
                    "Pickle may be unsafe with untrusted data",
                    line.strip()
                )
    
    def check_bug_detection(self, lines: List[str], content: str):
        """Check for common bugs"""
        # Comparison with None
        for i, line in enumerate(lines, 1):
            if re.search(r'==\s*None|None\s*==', line):
                self.add_violation(
                    'comparison_with_none', 'major', i,
                    "Use 'is None' instead of '== None'",
                    line.strip()
                )
            
            # Comparison with True/False
            if re.search(r'==\s*(True|False)|if .* == (True|False)', line):
                self.add_violation(
                    'comparison_with_true_false', 'minor', i,
                    "Use 'if x:' or 'if not x:' instead of '== True/False'",
                    line.strip()
                )
        
        # Bare except
        for i, line in enumerate(lines, 1):
            if re.search(r'except\s*:', line):
                self.add_violation(
                    'bare_except', 'major', i,
                    "Avoid bare 'except:' - specify exception types",
                    line.strip()
                )
        
        # Mutable default arguments
        for i, line in enumerate(lines, 1):
            if re.search(r'def\s+\w+\s*\([^)]*=\s*(\[|\{)', line):
                self.add_violation(
                    'mutable_default_arguments', 'major', i,
                    "Avoid mutable default arguments (list, dict, set)",
                    line.strip()
                )
    
    def check_best_practices(self, lines: List[str]):
        """Check best practices"""
        # Print statements - FIX: Check each print separately, not just if __main__ exists
        for i, line in enumerate(lines, 1):
            if re.search(r'\bprint\s*\(', line) and not line.strip().startswith('#'):
                # Only skip print if it's inside if __name__ == "__main__" block
                in_main_block = False
                for j in range(i-1, -1, -1):
                    if '__name__' in lines[j]:
                        in_main_block = True
                        break
                    if lines[j].strip() and not lines[j].startswith(' ' * 4) and j < i-1:
                        break
                
                if not in_main_block:
                    self.add_violation(
                        'print_statements', 'minor', i,
                        "Use logging instead of print() in production code",
                        line.strip()
                    )
        
        # TODO/FIXME comments
        for i, line in enumerate(lines, 1):
            if re.search(r'#\s*(TODO|FIXME|XXX)', line):
                self.add_violation(
                    'todo_comments', 'info', i,
                    "TODO/FIXME comment found",
                    line.strip()
                )
        
        # Commented code
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith('#') and any(kw in stripped for kw in ['def ', 'class ', 'import ', 'return ']):
                self.add_violation(
                    'commented_code', 'info', i,
                    "Remove or fix commented-out code",
                    line.strip()
                )
    
    def check_performance_issues(self, lines: List[str]):
        """Check performance issues"""
        # String concatenation in loops
        for i, line in enumerate(lines, 1):
            if '+=' in line and ('"' in line or "'" in line):
                # Check if inside a for loop
                for j in range(max(0, i-20), i):
                    if 'for ' in lines[j]:
                        self.add_violation(
                            'string_concatenation', 'minor', i,
                            "Use ''.join() for string concatenation in loops",
                            line.strip()
                        )
                        break
    
    def get_rule_config(self, rule_name: str, default=None) -> Dict:
        """Get configuration for a specific rule"""
        all_rules = self.rules.get('staticCodeReviewRules', {})
        for category in all_rules.values():
            if isinstance(category, list):
                for rule in category:
                    if rule.get('rule') == rule_name:
                        return rule
        return default or {}
    
    def generate_report(self, violations: List[Violation]) -> str:
        """Generate a formatted report"""
        if not violations:
            return "✓ No violations found!"
        
        # Group by severity
        by_severity = {}
        for v in violations:
            if v.severity not in by_severity:
                by_severity[v.severity] = []
            by_severity[v.severity].append(v)
        
        severity_order = ['critical', 'major', 'minor', 'info']
        report = f"\n{'='*80}\n"
        report += f"CODE REVIEW REPORT - {len(violations)} violations found\n"
        report += f"{'='*80}\n\n"
        
        for severity in severity_order:
            if severity in by_severity:
                report += f"\n[{severity.upper()}] - {len(by_severity[severity])} issue(s)\n"
                report += "-" * 80 + "\n"
                for v in by_severity[severity]:
                    report += f"Line {v.line_number}: {v.rule}\n"
                    report += f"  Message: {v.message}\n"
                    report += f"  Code: {v.code_snippet}\n\n"
        
        return report

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python code_review_tool.py <python_file> [rules_file] [--debug]")
        print("Example: python code_review_tool.py test_violations.py code-review-rules.yaml --debug")
        return
    
    test_file = sys.argv[1]
    rules_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'code-review-rules.yaml'
    debug = '--debug' in sys.argv
    
    if not os.path.exists(test_file):
        print(f"Error: File '{test_file}' not found")
        return
    
    if not os.path.exists(rules_file):
        print(f"Error: Rules file '{rules_file}' not found")
        return
    
    tool = CodeReviewTool(rules_file, debug=debug)
    violations = tool.analyze_file(test_file)
    report = tool.generate_report(violations)
    print(report)

if __name__ == '__main__':
    main()