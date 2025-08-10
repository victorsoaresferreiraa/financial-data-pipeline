# 🤝 Contribuindo para o Financial Data Pipeline

Obrigado pelo interesse em contribuir! Este documento explica como participar do desenvolvimento do projeto.

## 🚀 Quick Start para Contribuidores

### 1. **Fork e Clone**
```bash
# Fork no GitHub, depois:
git clone https://github.com/SEU-USUARIO/financial-data-pipeline.git
cd financial-data-pipeline
```

### 2. **Setup de Desenvolvimento**
```bash
# Instalar Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependências
poetry install

# Ativar ambiente
poetry shell

# Configurar hooks de qualidade
poetry run pre-commit install
```

### 3. **Executar Testes**
```bash
# Testes unitários
poetry run pytest

# Com coverage
poetry run pytest --cov=src

# Qualidade de código
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run flake8 src/ tests/
```

## 🌟 Como Contribuir

### **🐛 Reportar Bugs**
1. Verifique se o bug já foi reportado nas [Issues](../../issues)
2. Use o template de bug report
3. Inclua informações detalhadas:
   - Passos para reproduzir
   - Ambiente (OS, Python, versões)
   - Logs e screenshots

### **✨ Propor Funcionalidades**
1. Abra uma issue com o template de feature request
2. Descreva claramente:
   - Problema que resolve
   - Solução proposta
   - Impacto esperado

### **🔧 Enviar Código**
1. Crie uma branch a partir de `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/nome-da-feature
   ```

2. Implemente suas mudanças seguindo os padrões:
   - Code style: Black + isort
   - Linting: flake8
   - Type hints: mypy
   - Testes: pytest

3. Commit seguindo padrão conventional:
   ```bash
   git commit -m "feat: adicionar endpoint para análise de volatilidade"
   git commit -m "fix: corrigir rate limiting do Yahoo Finance"
   git commit -m "docs: atualizar documentação da API"
   ```

4. Push e abra Pull Request:
   ```bash
   git push origin feature/nome-da-feature
   ```

## 📏 Padrões de Código

### **🎨 Code Style**
- **Formatação:** Black (line-length=100)
- **Imports:** isort (perfil black)
- **Linting:** flake8 (max-line-length=100)
- **Type hints:** Obrigatório para funções públicas

### **📝 Convenções de Nomenclatura**
```python
# Variáveis e funções: snake_case
def processar_dados_acao():
    nome_empresa = "Petrobras"

# Classes: PascalCase  
class ETLFinanceiroRobusto:
    pass

# Constantes: UPPER_CASE
API_BASE_URL = "https://api.exemplo.com"

# Arquivos: snake_case.py
# financial_extractor.py ✅
# FinancialExtractor.py ❌
```

### **📚 Documentação**
```python
def processar_portfolio(simbolos: List[str]) -> List[Dict]:
    """
    Processa portfolio de ações extraindo dados atualizados.
    
    Args:
        simbolos: Lista de códigos de ações (ex: ['AAPL', 'PETR4.SA'])
        
    Returns:
        Lista de dicionários com dados processados
        
    Raises:
        ValueError: Se lista de símbolos estiver vazia
        APIError: Se todas as APIs falharem
    """
```

## 🧪 Testes

### **Cobertura Mínima:** 80%
- Testes unitários para todas as funções
- Testes de integração para endpoints
- Mocks para APIs externas

### **Exemplo de Teste:**
```python
def test_processar_dados_acao():
    """Testa processamento básico de dados"""
    dados_entrada = {
        "symbol": "AAPL",
        "price": "150.50",
        "volume": "1000000"
    }
    
    resultado = processar_dados_acao(dados_entrada)
    
    assert resultado["codigo"] == "AAPL"
    assert resultado["preco"] == 150.50
    assert resultado["volume"] == 1000000
```

## 🏗️ Arquitetura do Projeto

### **Princípios Seguidos:**
- **Single Responsibility:** Cada classe tem uma responsabilidade
- **Open/Closed:** Aberto para extensão, fechado para modificação
- **Dependency Injection:** Facilita testes e manutenção
- **Clean Code:** Código legível e bem documentado

### **Estrutura de Packages:**
```
src/
├── extractors/     # Extração de dados (APIs, files)
├── transformers/   # Transformação e limpeza
├── loaders/       # Carregamento em banco/arquivos
├── api/           # Endpoints FastAPI
├── models/        # Modelos Pydantic
├── utils/         # Utilitários compartilhados
└── config/        # Configurações e settings
```

## 🔄 Workflow de Desenvolvimento

### **Branches:**
- `main`: Código de produção (protegida)
- `develop`: Desenvolvimento ativo
- `feature/*`: Novas funcionalidades
- `hotfix/*`: Correções urgentes
- `release/*`: Preparação de releases

### **Processo de Review:**
1. **Automático:** CI/CD executa todos os checks
2. **Manual:** Code review obrigatório
3. **Aprovação:** Mínimo 1 aprovação para merge
4. **Merge:** Squash commits para histórico limpo

## 🏷️ Versionamento

Seguimos [Semantic Versioning](https://semver.org/):

- **MAJOR** (v2.0.0): Mudanças incompatíveis
- **MINOR** (v1.1.0): Novas funcionalidades compatíveis  
- **PATCH** (v1.0.1): Bug fixes compatíveis

### **Tags de Commit:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação de código
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

## 🎯 Roadmap de Contribuições

### **🥇 Alta Prioridade:**
- [ ] Testes de integração com APIs reais
- [ ] Dashboard web com Streamlit
- [ ] Autenticação JWT
- [ ] Métricas de monitoramento

### **🥈 Média Prioridade:**
- [ ] Suporte a PostgreSQL
- [ ] Cache com Redis
- [ ] Alertas por email
- [ ] Machine Learning para predições

### **🥉 Baixa Prioridade:**
- [ ] Interface mobile
- [ ] Exportação para outros formatos
- [ ] Integração com mais APIs
- [ ] Análises técnicas avançadas

## 💬 Comunicação

- **Issues:** Para bugs e feature requests
- **Discussions:** Para perguntas e ideias
- **Email:** Para questões privadas

## 🙏 Reconhecimento

Todos os contribuidores são reconhecidos no README.md e releases notes.

---

**Obrigado por contribuir! 🚀**