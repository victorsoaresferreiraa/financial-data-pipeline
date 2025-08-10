# api_financeira.py - API REST Profissional com FastAPI
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import uvicorn
from contextlib import contextmanager
import os
import json

# Importar nosso ETL
from etl_robusto_windows import ETLFinanceiroRobusto

# === MODELOS PYDANTIC (VALIDAÇÃO AUTOMÁTICA) ===
class AcaoResponse(BaseModel):
    """Modelo para resposta de uma ação"""
    codigo: str = Field(..., description="Código da ação (ex: AAPL, PETR4.SA)")
    nome: str = Field(..., description="Nome da empresa")
    preco: float = Field(..., description="Preço atual em R$")
    volume: int = Field(..., description="Volume negociado")
    variacao: float = Field(..., description="Variação percentual do dia")
    data: str = Field(..., description="Data dos dados")
    fonte: str = Field(..., description="Fonte dos dados")

class PortfolioRequest(BaseModel):
    """Modelo para requisição de portfolio"""
    simbolos: List[str] = Field(..., min_items=1, max_items=20, description="Lista de códigos de ações")
    incluir_historico: bool = Field(default=False, description="Incluir dados históricos")

class AnaliseResponse(BaseModel):
    """Modelo para resposta de análise"""
    total_ativos: int
    preco_medio: float
    volume_total: int
    melhor_performance: Dict[str, Union[str, float]]
    pior_performance: Dict[str, Union[str, float]]
    recomendacoes: List[str]

# === CONFIGURAÇÃO DA API ===
app = FastAPI(
    title="🚀 Financial Data Pipeline API",
    description="API profissional para análise de dados financeiros em tempo real",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS para permitir acesso frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DEPENDÊNCIAS ===
@contextmanager
def get_db():
    """Context manager para conexão com banco"""
    conn = sqlite3.connect("data/portfolio.db")
    try:
        yield conn
    finally:
        conn.close()

def get_etl_instance():
    """Dependency injection do ETL"""
    return ETLFinanceiroRobusto()

# === ENDPOINTS DA API ===
@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raiz - Status da API"""
    return {
        "message": "🚀 Financial Data Pipeline API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """Health check para monitoramento"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM acoes")
            total_acoes = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_acoes_banco": total_acoes,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/acoes/{codigo}", response_model=AcaoResponse, tags=["Dados"])
async def obter_acao(codigo: str, etl: ETLFinanceiroRobusto = Depends(get_etl_instance)):
    """
    Obtém dados em tempo real de uma ação específica
    
    - **codigo**: Código da ação (ex: AAPL, PETR4.SA, VALE3.SA)
    """
    codigo = codigo.upper()
    
    try:
        # Extrair dados em tempo real
        dados = etl.extrair_dados_acao(codigo)
        
        if not dados:
            raise HTTPException(status_code=404, detail=f"Dados não encontrados para {codigo}")
        
        # Salvar no banco
        etl.salvar_no_banco(dados)
        
        return AcaoResponse(**dados)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar {codigo}: {str(e)}")

@app.post("/portfolio/analisar", response_model=Dict, tags=["Análise"])
async def analisar_portfolio(
    request: PortfolioRequest, 
    background_tasks: BackgroundTasks,
    etl: ETLFinanceiroRobusto = Depends(get_etl_instance)
):
    """
    Analisa um portfolio completo de ações
    
    - **simbolos**: Lista de códigos de ações para analisar
    - **incluir_historico**: Se deve incluir dados históricos
    """
    try:
        print(f"\n🔄 Processando portfolio de {len(request.simbolos)} ativos...")
        
        # Processar portfolio
        dados = etl.processar_portfolio(request.simbolos)
        
        if not dados:
            raise HTTPException(status_code=404, detail="Nenhum dado foi extraído")
        
        # Análise com pandas
        df = pd.DataFrame(dados)
        
        # Estatísticas
        analise = {
            "portfolio": dados,
            "estatisticas": {
                "total_ativos": len(df),
                "preco_medio": round(df['preco'].mean(), 2),
                "volume_total": int(df['volume'].sum()),
                "variacao_media": round(df['variacao'].mean(), 2),
                "valor_total_portfolio": round(df['preco'].sum(), 2)
            },
            "performance": {
                "melhor_acao": {
                    "codigo": df.loc[df['variacao'].idxmax(), 'codigo'],
                    "variacao": df['variacao'].max()
                },
                "pior_acao": {
                    "codigo": df.loc[df['variacao'].idxmin(), 'codigo'],
                    "variacao": df['variacao'].min()
                }
            },
            "recomendacoes": []
        }
        
        # Gerar recomendações automáticas
        for _, acao in df.iterrows():
            if acao['variacao'] > 2:
                analise['recomendacoes'].append(f"🚀 {acao['codigo']}: Forte alta (+{acao['variacao']:.2f}%) - Acompanhar tendência")
            elif acao['variacao'] < -2:
                analise['recomendacoes'].append(f"⚠️ {acao['codigo']}: Queda significativa ({acao['variacao']:.2f}%) - Avaliar compra")
        
        # Agendar geração de relatório em background
        background_tasks.add_task(gerar_relatorio_background, dados)
        
        return analise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.get("/portfolio/historico", tags=["Dados"])
async def historico_portfolio(limite: int = 50):
    """
    Retorna histórico de dados do banco
    
    - **limite**: Número máximo de registros (padrão: 50)
    """
    try:
        with get_db() as conn:
            query = """
            SELECT codigo, nome, preco, volume, variacao, data, fonte, created_at
            FROM acoes 
            ORDER BY created_at DESC 
            LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limite,))
            
            if df.empty:
                return {"message": "Nenhum dado histórico encontrado", "dados": []}
            
            return {
                "total_registros": len(df),
                "dados": df.to_dict('records'),
                "ultima_atualizacao": df.iloc[0]['created_at'] if not df.empty else None
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar histórico: {str(e)}")

@app.get("/portfolio/analise-rapida", tags=["Análise"])
async def analise_rapida():
    """Análise rápida dos dados mais recentes do banco"""
    try:
        with get_db() as conn:
            # Pegar dados mais recentes de cada ação
            query = """
            SELECT codigo, nome, preco, volume, variacao, data, fonte
            FROM acoes a1
            WHERE created_at = (
                SELECT MAX(created_at) 
                FROM acoes a2 
                WHERE a2.codigo = a1.codigo
            )
            ORDER BY variacao DESC
            """
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return {"message": "Nenhum dado para análise"}
            
            # Análise rápida
            return {
                "resumo": {
                    "total_ativos": len(df),
                    "valor_medio": round(df['preco'].mean(), 2),
                    "variacao_media": round(df['variacao'].mean(), 2)
                },
                "top_3_alta": df.nlargest(3, 'variacao')[['codigo', 'nome', 'variacao']].to_dict('records'),
                "top_3_baixa": df.nsmallest(3, 'variacao')[['codigo', 'nome', 'variacao']].to_dict('records'),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.post("/etl/executar", tags=["ETL"])
async def executar_etl(background_tasks: BackgroundTasks, simbolos: Optional[List[str]] = None):
    """
    Executa pipeline ETL completo em background
    
    - **simbolos**: Lista opcional de ações (usa padrão se não especificado)
    """
    if not simbolos:
        simbolos = ['AAPL', 'MSFT', 'GOOGL', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
    
    # Executar ETL em background
    background_tasks.add_task(executar_etl_background, simbolos)
    
    return {
        "message": "Pipeline ETL iniciado em background",
        "simbolos": simbolos,
        "status": "processando",
        "check_progress": "/portfolio/historico"
    }

# === FUNÇÕES BACKGROUND ===
async def gerar_relatorio_background(dados: List[Dict]):
    """Gera relatório em background"""
    try:
        etl = ETLFinanceiroRobusto()
        etl.gerar_relatorio_executivo(dados)
        print("📊 Relatório gerado em background com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")

async def executar_etl_background(simbolos: List[str]):
    """Executa ETL completo em background"""
    try:
        etl = ETLFinanceiroRobusto()
        dados = etl.processar_portfolio(simbolos)
        
        if dados:
            etl.gerar_relatorio_executivo(dados)
            print(f"✅ ETL concluído: {len(dados)} ativos processados")
        else:
            print("❌ ETL falhou: nenhum dado extraído")
            
    except Exception as e:
        print(f"Erro no ETL background: {str(e)}")

# === INICIALIZAÇÃO ===
if __name__ == "__main__":
    print("🚀 Iniciando API Financeira...")
    print("📊 Acesse: http://localhost:8000/docs")
    print("🔧 Documentação interativa disponível!")
    
    uvicorn.run(
        "api_financeira:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,  # Auto-reload durante desenvolvimento
        log_level="info"
    )