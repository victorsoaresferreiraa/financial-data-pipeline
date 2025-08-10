# etl_api_real.py - ETL Profissional com APIs Reais + SQLite

import sqlite3
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional
import time

class ETLFinanceiroReal:
    """
    ETL Profissional que conecta com APIs reais e armazena em banco SQLite.
    
    Funcionalidades:
    - Extrai dados da API Alpha Vantage (gratuita)
    - Processa e limpa os dados
    - Armazena em banco SQLite  
    - Gera relatórios automáticos
    - Sistema de logs profissional
    """
    
    def __init__(self, api_key: Optional[str] = None):
        print("🚀 ETL Financeiro Real iniciado!")
        
        # Configuração da API Alpha Vantage (gratuita)
        self.api_key = "IJ3XCT1IXT7W5AL0"  # Use "demo" para teste
        self.base_url = "https://www.alphavantage.co/query"
        
        # Configuração do banco
        self.db_name = "data/portfolio_real.db"
        self._criar_estrutura()
        self._setup_database()
        
        # Controle de rate limiting (API gratuita tem limites)
        self.request_delay = 12  # 12 segundos entre requests (5 por minuto)
    
    def _criar_estrutura(self):
        """Cria estrutura de pastas"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/logs", exist_ok=True)
        print("📁 Estrutura criada")
    
    def _setup_database(self):
        """Configura banco SQLite com tabelas profissionais"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabela principal de cotações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                company_name TEXT,
                price REAL NOT NULL,
                volume INTEGER,
                change_percent REAL,
                timestamp TEXT NOT NULL,
                market_cap REAL,
                pe_ratio REAL,
                dividend_yield REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # Tabela de histórico diário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_diario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        ''')
        
        # Tabela de logs do ETL
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS etl_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_type TEXT NOT NULL,
                symbol TEXT,
                status TEXT NOT NULL,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("🗃️  Banco de dados configurado")
    
    def _log_processo(self, process_type: str, symbol: str = None, 
                     status: str = "SUCCESS", message: str = ""):
        """Sistema de logs profissional"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO etl_logs (process_type, symbol, status, message)
            VALUES (?, ?, ?, ?)
        ''', (process_type, symbol, status, message))
        
        conn.commit()
        conn.close()
        
        # Log também no terminal
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {process_type} - {symbol or 'GERAL'}: {status} - {message}")
    
    def extrair_cotacao_atual(self, symbol: str) -> Dict:
        """
        Extrai cotação atual de uma ação usando Alpha Vantage API
        
        Args:
            symbol: Símbolo da ação (ex: 'AAPL', 'MSFT')
            
        Returns:
            Dicionário com dados da cotação
        """
        try:
            # Parâmetros da API
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            print(f"📡 Buscando cotação atual de {symbol}...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Verifica se há dados válidos
            if 'Global Quote' not in data:
                if 'Note' in data:
                    raise Exception("Limite de requisições API atingido")
                raise Exception(f"Dados não encontrados para {symbol}")
            
            quote = data['Global Quote']
            
            # Processar dados
            cotacao = {
                'symbol': quote.get('01. symbol', symbol),
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                'timestamp': datetime.now().isoformat(),
                'high_day': float(quote.get('03. high', 0)),
                'low_day': float(quote.get('04. low', 0)),
                'open_price': float(quote.get('02. open', 0)),
                'previous_close': float(quote.get('08. previous close', 0))
            }
            
            self._log_processo("EXTRACT_QUOTE", symbol, "SUCCESS", 
                             f"Preço: ${cotacao['price']:.2f}")
            
            # Rate limiting
            time.sleep(self.request_delay)
            
            return cotacao
            
        except Exception as e:
            error_msg = f"Erro ao extrair {symbol}: {str(e)}"
            self._log_processo("EXTRACT_QUOTE", symbol, "ERROR", error_msg)
            return {}
    
    def extrair_dados_historicos(self, symbol: str, periodo: str = "compact") -> List[Dict]:
        """
        Extrai dados históricos diários
        
        Args:
            symbol: Símbolo da ação
            periodo: "compact" (100 dias) ou "full" (20 anos)
            
        Returns:
            Lista com dados históricos
        """
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': periodo,
                'apikey': self.api_key
            }
            
            print(f"📊 Buscando histórico de {symbol} ({periodo})...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                raise Exception("Dados históricos não encontrados")
            
            time_series = data['Time Series (Daily)']
            
            historico = []
            for date_str, values in time_series.items():
                historico.append({
                    'symbol': symbol,
                    'date': date_str,
                    'open_price': float(values['1. open']),
                    'high_price': float(values['2. high']),
                    'low_price': float(values['3. low']),
                    'close_price': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            self._log_processo("EXTRACT_HISTORY", symbol, "SUCCESS", 
                             f"{len(historico)} registros históricos")
            
            time.sleep(self.request_delay)
            return historico
            
        except Exception as e:
            error_msg = f"Erro histórico {symbol}: {str(e)}"
            self._log_processo("EXTRACT_HISTORY", symbol, "ERROR", error_msg)
            return []
    
    def carregar_cotacao_db(self, cotacao: Dict):
        """Carrega cotação no banco SQLite"""
        if not cotacao:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cotacoes 
                (symbol, price, volume, change_percent, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                cotacao['symbol'],
                cotacao['price'],
                cotacao['volume'],
                cotacao['change_percent'],
                cotacao['timestamp']
            ))
            
            conn.commit()
            conn.close()
            
            self._log_processo("LOAD_QUOTE", cotacao['symbol'], "SUCCESS", 
                             "Cotação salva no banco")
            
        except Exception as e:
            self._log_processo("LOAD_QUOTE", cotacao.get('symbol'), "ERROR", str(e))
    
    def carregar_historico_db(self, historico: List[Dict]):
        """Carrega histórico no banco SQLite"""
        if not historico:
            return
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            for registro in historico:
                cursor.execute('''
                    INSERT OR REPLACE INTO historico_diario 
                    (symbol, date, open_price, high_price, low_price, close_price, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    registro['symbol'],
                    registro['date'],
                    registro['open_price'],
                    registro['high_price'],
                    registro['low_price'],
                    registro['close_price'],
                    registro['volume']
                ))
            
            conn.commit()
            conn.close()
            
            symbol = historico[0]['symbol'] if historico else "UNKNOWN"
            self._log_processo("LOAD_HISTORY", symbol, "SUCCESS", 
                             f"{len(historico)} registros históricos salvos")
            
        except Exception as e:
            self._log_processo("LOAD_HISTORY", "ERROR", str(e))
    
    def executar_etl_completo(self, symbols: List[str], incluir_historico: bool = True):
        """
        Executa pipeline ETL completo
        
        Args:
            symbols: Lista de símbolos para extrair
            incluir_historico: Se deve extrair dados históricos
        """
        print("🔄 Iniciando ETL completo...")
        start_time = datetime.now()
        
        sucessos = 0
        erros = 0
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] Processando {symbol}...")
            
            # Extrair cotação atual
            cotacao = self.extrair_cotacao_atual(symbol)
            if cotacao:
                self.carregar_cotacao_db(cotacao)
                sucessos += 1
            else:
                erros += 1
                continue
            
            # Extrair histórico se solicitado
            if incluir_historico:
                historico = self.extrair_dados_historicos(symbol, "compact")
                if historico:
                    self.carregar_historico_db(historico)
        
        # Relatório final
        end_time = datetime.now()
        duracao = end_time - start_time
        
        print(f"\n🎉 ETL concluído!")
        print(f"⏱️  Duração: {duracao}")
        print(f"✅ Sucessos: {sucessos}")
        print(f"❌ Erros: {erros}")
        
        self._log_processo("ETL_COMPLETE", None, "SUCCESS", 
                          f"Processados {len(symbols)} símbolos em {duracao}")
    
    def gerar_relatorio_portfolio(self) -> pd.DataFrame:
        """Gera relatório do portfolio usando dados do banco"""
        try:
            conn = sqlite3.connect(self.db_name)
            
            # Query para pegar cotações mais recentes
            query = '''
                SELECT 
                    symbol,
                    price,
                    volume,
                    change_percent,
                    timestamp,
                    datetime(created_at) as ultima_atualizacao
                FROM cotacoes 
                WHERE (symbol, created_at) IN (
                    SELECT symbol, MAX(created_at) 
                    FROM cotacoes 
                    GROUP BY symbol
                )
                ORDER BY change_percent DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                print("⚠️ Nenhum dado encontrado no banco")
                return df
            
            # Análises
            print("\n📊 === RELATÓRIO DO PORTFOLIO (DADOS REAIS) ===")
            print("=" * 60)
            
            print(f"📅 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            print(f"📈 Total de ativos: {len(df)}")
            print(f"💰 Valor médio: ${df['price'].mean():.2f}")
            print(f"🎯 Variação média: {df['change_percent'].mean():+.2f}%")
            
            print("\n🏆 TOP PERFORMERS:")
            top_3 = df.head(3)
            for _, acao in top_3.iterrows():
                emoji = "🚀" if acao['change_percent'] > 5 else "📈"
                print(f"{emoji} {acao['symbol']:6} | ${acao['price']:8.2f} | {acao['change_percent']:+6.2f}%")
            
            print("\n📉 MAIORES QUEDAS:")
            bottom_3 = df.tail(3)
            for _, acao in bottom_3.iterrows():
                emoji = "💥" if acao['change_percent'] < -5 else "📉"
                print(f"{emoji} {acao['symbol']:6} | ${acao['price']:8.2f} | {acao['change_percent']:+6.2f}%")
            
            # Salvar relatório
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            df.to_csv(f"data/relatorio_real_{timestamp}.csv", index=False)
            print(f"\n💾 Relatório salvo: data/relatorio_real_{timestamp}.csv")
            
            return df
            
        except Exception as e:
            print(f"❌ Erro no relatório: {e}")
            return pd.DataFrame()


# === EXEMPLO DE USO COM DADOS REAIS ===

if __name__ == "__main__":
    # Inicializar ETL (use sua chave da Alpha Vantage se tiver)
    etl = ETLFinanceiroReal(api_key="demo")  # Substitua por sua chave real
    
    # Portfolio de ações americanas (Alpha Vantage funciona melhor com essas)
    portfolio_usa = [
        "AAPL",  # Apple
        "MSFT",  # Microsoft  
        "GOOGL", # Google
        "TSLA",  # Tesla
        "NVDA",  # NVIDIA
    ]
    
    print("🇺🇸 Executando ETL com dados reais de ações americanas...")
    print("⏰ ATENÇÃO: API gratuita tem limite de 5 requests/minuto")
    print("⏱️  Processo pode demorar alguns minutos devido aos delays necessários")
    
    # Executar ETL (apenas cotações atuais para demo)
    etl.executar_etl_completo(portfolio_usa, incluir_historico=False)
    
    # Gerar relatório
    df_portfolio = etl.gerar_relatorio_portfolio()
    
    print("\n🎉 ETL com dados REAIS concluído!")
    print("🗃️  Dados salvos em: data/portfolio_real.db")
    print("💡 Para usar com ações brasileiras, configure API da B3 ou Yahoo Finance")