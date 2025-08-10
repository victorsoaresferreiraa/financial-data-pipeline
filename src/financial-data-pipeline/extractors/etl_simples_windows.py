# etl_simples_windows.py - Versão que funciona 100% no Windows
import requests
import json
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os
import time

class ETLSimples:
    """ETL simplificado que realmente funciona"""
    
    def __init__(self):
        self.criar_pastas()
        self.criar_banco()
        print("Sistema ETL iniciado com sucesso!")
    
    def criar_pastas(self):
        """Cria estrutura de pastas"""
        os.makedirs('data', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        print("Pastas criadas: data/ e reports/")
    
    def criar_banco(self):
        """Cria banco SQLite simples"""
        conn = sqlite3.connect('data/acoes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS acoes (
                id INTEGER PRIMARY KEY,
                codigo TEXT,
                nome TEXT,
                preco REAL,
                volume INTEGER,
                data TEXT,
                variacao REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Banco de dados SQLite criado!")
    
    def extrair_yahoo_finance(self, symbol):
        """
        Extrai dados do Yahoo Finance (gratuito, sem API key)
        """
        try:
            print(f"Extraindo {symbol} do Yahoo Finance...")
            
            # Usando API pública do Yahoo Finance
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                quotes = result['indicators']['quote'][0]
                
                # Dados básicos
                dados_processados = {
                    'codigo': symbol,
                    'nome': meta.get('shortName', symbol),
                    'preco': meta.get('regularMarketPrice', 0),
                    'volume': meta.get('regularMarketVolume', 0),
                    'variacao': meta.get('regularMarketChangePercent', 0),
                    'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                print(f"SUCESSO: {symbol} - R$ {dados_processados['preco']:.2f}")
                return dados_processados
            
            print(f"ERRO: Dados não encontrados para {symbol}")
            return None
            
        except Exception as e:
            print(f"ERRO ao extrair {symbol}: {str(e)}")
            return None
    
    def salvar_no_banco(self, dados):
        """Salva dados no banco SQLite"""
        if not dados:
            return
            
        conn = sqlite3.connect('data/acoes.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO acoes 
            (codigo, nome, preco, volume, data, variacao)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            dados['codigo'],
            dados['nome'], 
            dados['preco'],
            dados['volume'],
            dados['data'],
            dados['variacao']
        ))
        
        conn.commit()
        conn.close()
        print(f"Dados de {dados['codigo']} salvos no banco!")
    
    def processar_portfolio(self, acoes):
        """Processa lista de ações"""
        print("=" * 50)
        print("INICIANDO PROCESSAMENTO DO PORTFOLIO")
        print("=" * 50)
        
        dados_portfolio = []
        sucessos = 0
        
        for i, acao in enumerate(acoes, 1):
            print(f"\n[{i}/{len(acoes)}] Processando {acao}...")
            
            # Extrair dados
            dados = self.extrair_yahoo_finance(acao)
            
            if dados:
                # Salvar no banco
                self.salvar_no_banco(dados)
                dados_portfolio.append(dados)
                sucessos += 1
            
            # Pequena pausa para não sobrecarregar
            time.sleep(1)
        
        print(f"\nRESULTADO: {sucessos}/{len(acoes)} ações processadas com sucesso!")
        return dados_portfolio
    
    def gerar_relatorio(self, dados_portfolio):
        """Gera relatório do portfolio"""
        if not dados_portfolio:
            print("Nenhum dado para gerar relatório")
            return
        
        print("\n" + "=" * 50)
        print("RELATÓRIO EXECUTIVO DO PORTFOLIO")
        print("=" * 50)
        
        # Converter para DataFrame para análises
        df = pd.DataFrame(dados_portfolio)
        
        # Estatísticas básicas
        total_acoes = len(df)
        preco_medio = df['preco'].mean()
        melhor_acao = df.loc[df['variacao'].idxmax()]
        pior_acao = df.loc[df['variacao'].idxmin()]
        
        print(f"Total de ações analisadas: {total_acoes}")
        print(f"Preço médio: R$ {preco_medio:.2f}")
        print(f"Melhor performance: {melhor_acao['codigo']} (+{melhor_acao['variacao']:.2f}%)")
        print(f"Pior performance: {pior_acao['codigo']} ({pior_acao['variacao']:.2f}%)")
        
        print(f"\nDETALHES POR AÇÃO:")
        for _, acao in df.iterrows():
            sinal = "+" if acao['variacao'] > 0 else ""
            print(f"{acao['codigo']}: R$ {acao['preco']:.2f} ({sinal}{acao['variacao']:.2f}%)")
        
        # Salvar relatório
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'total_acoes': total_acoes,
            'preco_medio': preco_medio,
            'melhor_acao': melhor_acao['codigo'],
            'pior_acao': pior_acao['codigo'],
            'dados_completos': dados_portfolio
        }
        
        with open('reports/relatorio_portfolio.json', 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        # Salvar Excel
        df.to_excel('reports/portfolio_analysis.xlsx', index=False)
        
        print(f"\nARQUIVOS GERADOS:")
        print(f"- Banco de dados: data/acoes.db")
        print(f"- Relatório JSON: reports/relatorio_portfolio.json") 
        print(f"- Análise Excel: reports/portfolio_analysis.xlsx")
    
    def consultar_banco(self):
        """Consulta dados do banco"""
        conn = sqlite3.connect('data/acoes.db')
        df = pd.read_sql_query("SELECT * FROM acoes ORDER BY variacao DESC", conn)
        conn.close()
        
        print("\nDADOS DO BANCO DE DADOS:")
        print(df.to_string(index=False))
        return df

def main():
    """Função principal"""
    
    # Lista de ações para processar
    acoes_portfolio = [
        'AAPL',    # Apple
        'MSFT',    # Microsoft
        'TSLA',    # Tesla
        'NVDA',    # NVIDIA
        'GOOGL'    # Google
    ]
    
    print("SISTEMA ETL FINANCEIRO - VERSÃO SIMPLIFICADA")
    print("Dados em tempo real via Yahoo Finance (gratuito)")
    
    # Inicializar ETL
    etl = ETLSimples()
    
    # Processar portfolio
    dados = etl.processar_portfolio(acoes_portfolio)
    
    # Gerar relatório
    etl.gerar_relatorio(dados)
    
    # Consultar banco
    etl.consultar_banco()
    
    print("\nSUCESSO! Todos os arquivos foram criados.")

if __name__ == "__main__":
    main()