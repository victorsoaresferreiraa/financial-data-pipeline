# .github/workflows/ci.yml - Pipeline CI/CD Profissional
name: 🚀 CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: 🧪 Tests & Quality
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
    - name: 📥 Checkout Code
      uses: actions/checkout@v4

    - name: 🐍 Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: 📦 Install Poetry
      uses: snok/install-poetry@v1
      with:
        version: latest
        virtualenvs-create: true
        virtualenvs-in-project: true

    - name: 🔧 Load cached dependencies
      uses: actions/cache@v3
      with:
        path: .venv
        key: venv-${{ runner.os }}-${{ matrix.python-version }}-${{ hashFiles('**/poetry.lock') }}

    - name: 📚 Install Dependencies
      run: poetry install --no-interaction --no-root

    - name: 🎯 Install Project
      run: poetry install --no-interaction

    - name: 🧹 Code Quality - Black
      run: poetry run black --check src/ tests/

    - name: 📏 Code Quality - isort
      run: poetry run isort --check-only src/ tests/

    - name: 🔍 Code Quality - flake8
      run: poetry run flake8 src/ tests/

    - name: 🧪 Run Tests
      run: |
        poetry run pytest tests/ -v --cov=src --cov-report=xml --cov-report=html

    - name: 📊 Upload Coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    name: 🛡️ Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout Code
      uses: actions/checkout@v4
      
    - name: 🔒 Run Bandit Security Scan
      uses: py-actions/bandit@v1
      with:
        path: src/

  docker:
    name: 🐳 Docker Build
    runs-on: ubuntu-latest
    needs: [test]
    
    steps:
    - name: 📥 Checkout Code
      uses: actions/checkout@v4
      
    - name: 🐳 Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: 🔨 Build Docker Image
      run: |
        docker build -t financial-pipeline:latest .
        docker run --rm financial-pipeline:latest python -c "import src.api_financeira; print('✅ Import test passed')"

  deploy:
    name: 🚀 Deploy to Production
    runs-on: ubuntu-latest
    needs: [test, security, docker]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: 📥 Checkout Code
      uses: actions/checkout@v4
      
    - name: 🎯 Deploy to Production
      run: |
        echo "🚀 Deploy seria executado aqui"
        echo "📊 Ambiente: Production"
        echo "🔗 URL: https://financial-api.exemplo.com"