# extrator_pandas.py - Versão profissional com Pandas e análises avançadas

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

class ExtratorFinanceiroProfissional:
    """
    Extrator financeiro com análises profissionais usando Pandas.
    Ideal para impressionar recrutadores!
    """
    
    def __init__(self):
        print("🚀 Extrator Financeiro Profissional iniciado!")
        print("📊 Powered by Pandas - Análises de nível empresarial")
        self.dados_extraidos = []
        self.df_portfolio = None
        
        # Criar pastas para organização
        self._criar_estrutura_pastas()
    
    def _criar_estrutura_pastas(self):
        """Cria estrutura de pastas profissional"""
        pastas = ['data/raw', 'data/processed', 'data/reports', 'data/charts']
        for pasta in pastas:
            os.makedirs(pasta, exist_ok=True)
        print("📁 Estrutura de pastas criada")
    
    def simular_dados_historicos(self, codigo_acao, dias=30):
        """
        Simula dados históricos de uma ação (útil para análises de tendência)
        
        Parâmetros:
        codigo_acao (str): Código da ação
        dias (int): Número de dias de histórico
        
        Retorna:
        list: Lista com dados históricos
        """
        print(f"📈 Simulando {dias} dias de histórico para {codigo_acao}")
        
        historico = []
        preco_base = random.uniform(30.0, 100.0)
        
        for i in range(dias):
            # Simula variação diária realista
            variacao_dia = random.uniform(-0.05, 0.05)  # -5% a +5%
            preco_base = preco_base * (1 + variacao_dia)
            
            data = datetime.now() - timedelta(days=dias-i-1)
            
            dados_dia = {
                'codigo': codigo_acao.upper(),
                'empresa': self._obter_nome_empresa(codigo_acao),
                'data': data.strftime('%Y-%m-%d'),
                'preco_abertura': round(preco_base * random.uniform(0.98, 1.02), 2),
                'preco_fechamento': round(preco_base, 2),
                'preco_maximo': round(preco_base * random.uniform(1.00, 1.05), 2),
                'preco_minimo': round(preco_base * random.uniform(0.95, 1.00), 2),
                'volume': random.randint(100000, 3000000),
                'variacao_dia': round(variacao_dia * 100, 2)
            }
            
            historico.append(dados_dia)
        
        return historico
    
    def _obter_nome_empresa(self, codigo):
        """Retorna nome da empresa com setor"""
        empresas = {
            "PETR4": {"nome": "Petrobras", "setor": "Petróleo e Gás"},
            "VALE3": {"nome": "Vale", "setor": "Mineração"},
            "ITUB4": {"nome": "Itaú Unibanco", "setor": "Bancos"},
            "BBDC4": {"nome": "Bradesco", "setor": "Bancos"},
            "ABEV3": {"nome": "Ambev", "setor": "Bebidas"},
            "PVB11": {"nome": "Vanguard Value ETF", "setor": "ETF"},
            "MGLU3": {"nome": "Magazine Luiza", "setor": "Varejo"},
            "WEGE3": {"nome": "WEG", "setor": "Máquinas e Equipamentos"}
        }
        
        info = empresas.get(codigo.upper(), {"nome": "Empresa Desconhecida", "setor": "Diversos"})
        return info["nome"]
    
    def extrair_portfolio_completo(self, lista_acoes, incluir_historico=True):
        """
        Extrai dados completos do portfolio com análises profissionais
        
        Parâmetros:
        lista_acoes (list): Lista de códigos das ações
        incluir_historico (bool): Se deve incluir dados históricos
        
        Retorna:
        pandas.DataFrame: DataFrame com todos os dados
        """
        print(f"🔄 Extraindo portfolio completo de {len(lista_acoes)} ações...")
        
        todos_dados = []
        
        for codigo in lista_acoes:
            if incluir_historico:
                # Dados históricos dos últimos 30 dias
                historico = self.simular_dados_historicos(codigo, 30)
                todos_dados.extend(historico)
            else:
                # Apenas dados do dia atual
                dados_hoje = self.simular_dados_historicos(codigo, 1)[0]
                todos_dados.append(dados_hoje)
        
        # Converter para DataFrame do pandas
        self.df_portfolio = pd.DataFrame(todos_dados)
        
        # Conversões de tipos (importante para análises)
        self.df_portfolio['data'] = pd.to_datetime(self.df_portfolio['data'])
        colunas_numericas = ['preco_abertura', 'preco_fechamento', 'preco_maximo', 
                           'preco_minimo', 'volume', 'variacao_dia']
        
        for coluna in colunas_numericas:
            self.df_portfolio[coluna] = pd.to_numeric(self.df_portfolio[coluna])
        
        print(f"✅ Portfolio extraído: {len(self.df_portfolio)} registros")
        return self.df_portfolio
    
    def analises_estatisticas_avancadas(self):
        """
        Realiza análises estatísticas profissionais
        Tipo de análise que empresas fazem!
        """
        if self.df_portfolio is None:
            print("⚠️ Execute extrair_portfolio_completo() primeiro")
            return
        
        print("\n" + "="*60)
        print("📊 === ANÁLISES ESTATÍSTICAS PROFISSIONAIS ===")
        print("="*60)
        
        # Análise por ação (dados mais recentes)
        df_atual = self.df_portfolio.groupby('codigo').tail(1)
        
        print("\n🎯 PERFORMANCE ATUAL POR AÇÃO:")
        print("-" * 50)
        
        for _, acao in df_atual.iterrows():
            emoji = "📈" if acao['variacao_dia'] >= 0 else "📉"
            print(f"{emoji} {acao['codigo']:6} | {acao['empresa']:20} | "
                  f"R$ {acao['preco_fechamento']:7.2f} | {acao['variacao_dia']:+6.2f}%")
        
        # Estatísticas descritivas
        print("\n📈 ESTATÍSTICAS DESCRITIVAS (30 dias):")
        print("-" * 50)
        stats = self.df_portfolio.groupby('codigo')['preco_fechamento'].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).round(2)
        stats.columns = ['Preço_Médio', 'Desvio_Padrão', 'Mínimo', 'Máximo', 'Dias']
        print(stats)
        
        # Análise de volatilidade
        print("\n⚡ ANÁLISE DE VOLATILIDADE:")
        print("-" * 50)
        volatilidade = self.df_portfolio.groupby('codigo')['variacao_dia'].std().sort_values(ascending=False)
        
        print("Ranking de volatilidade (maior = mais arriscada):")
        for i, (codigo, vol) in enumerate(volatilidade.items(), 1):
            risco = "🔴 ALTO" if vol > 3 else "🟡 MÉDIO" if vol > 2 else "🟢 BAIXO"
            print(f"{i}º {codigo}: {vol:.2f}% {risco}")
        
        # Análise de volume
        print("\n📊 ANÁLISE DE LIQUIDEZ (Volume médio):")
        print("-" * 50)
        volume_medio = self.df_portfolio.groupby('codigo')['volume'].mean().sort_values(ascending=False)
        
        for i, (codigo, volume) in enumerate(volume_medio.items(), 1):
            liquidez = "🟢 ALTA" if volume > 2000000 else "🟡 MÉDIA" if volume > 1000000 else "🔴 BAIXA"
            print(f"{i}º {codigo}: {volume:,.0f} ações/dia {liquidez}")
    
    def detectar_tendencias(self):
        """
        Detecta tendências usando médias móveis (análise técnica profissional)
        """
        if self.df_portfolio is None:
            print("⚠️ Execute extrair_portfolio_completo() primeiro")
            return
        
        print("\n" + "="*60)
        print("📈 === ANÁLISE DE TENDÊNCIAS (Médias Móveis) ===")
        print("="*60)
        
        resultados_tendencia = []
        
        for codigo in self.df_portfolio['codigo'].unique():
            df_acao = self.df_portfolio[self.df_portfolio['codigo'] == codigo].copy()
            df_acao = df_acao.sort_values('data')
            
            # Calcular médias móveis
            df_acao['MA_7'] = df_acao['preco_fechamento'].rolling(window=7).mean()
            df_acao['MA_21'] = df_acao['preco_fechamento'].rolling(window=21).mean()
            
            # Últimos valores
            preco_atual = df_acao['preco_fechamento'].iloc[-1]
            ma_7 = df_acao['MA_7'].iloc[-1]
            ma_21 = df_acao['MA_21'].iloc[-1]
            
            # Determinar tendência
            if pd.notna(ma_7) and pd.notna(ma_21):
                if preco_atual > ma_7 > ma_21:
                    tendencia = "🚀 ALTA FORTE"
                    sinal = "COMPRA"
                elif preco_atual > ma_7 and ma_7 < ma_21:
                    tendencia = "📈 ALTA MODERADA"
                    sinal = "COMPRA"
                elif preco_atual < ma_7 < ma_21:
                    tendencia = "📉 BAIXA FORTE"
                    sinal = "VENDA"
                elif preco_atual < ma_7 and ma_7 > ma_21:
                    tendencia = "📉 BAIXA MODERADA"
                    sinal = "VENDA"
                else:
                    tendencia = "➡️  LATERAL"
                    sinal = "AGUARDAR"
            else:
                tendencia = "❓ DADOS INSUFICIENTES"
                sinal = "AGUARDAR"
            
            resultados_tendencia.append({
                'codigo': codigo,
                'preco_atual': preco_atual,
                'ma_7_dias': ma_7,
                'ma_21_dias': ma_21,
                'tendencia': tendencia,
                'sinal': sinal
            })
        
        # Mostrar resultados
        print("\n🎯 SINAIS DE TRADING:")
        print("-" * 70)
        
        for resultado in resultados_tendencia:
            print(f"{resultado['codigo']:6} | R$ {resultado['preco_atual']:7.2f} | "
                  f"MA7: {resultado['ma_7_dias']:7.2f} | MA21: {resultado['ma_21_dias']:7.2f} | "
                  f"{resultado['tendencia']:15} | 🎯 {resultado['sinal']}")
    
    def gerar_relatorio_executivo(self):
        """
        Gera relatório executivo completo (tipo que CEOs recebem)
        """
        if self.df_portfolio is None:
            print("⚠️ Execute extrair_portfolio_completo() primeiro")
            return
        
        print("\n" + "="*80)
        print("🏢 === RELATÓRIO EXECUTIVO DO PORTFOLIO ===")
        print("="*80)
        
        # Dados atuais
        df_atual = self.df_portfolio.groupby('codigo').tail(1)
        
        # Métricas principais
        valor_total = (df_atual['preco_fechamento'] * 100).sum()  # Assumindo 100 ações de cada
        melhor_performance = df_atual.loc[df_atual['variacao_dia'].idxmax()]
        pior_performance = df_atual.loc[df_atual['variacao_dia'].idxmin()]
        
        print(f"📅 Data do relatório: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"💰 Valor estimado do portfolio: R$ {valor_total:,.2f}")
        print(f"📊 Número de ativos: {len(df_atual)}")
        print(f"🎯 Variação média do dia: {df_atual['variacao_dia'].mean():+.2f}%")
        
        print(f"\n🏆 DESTAQUE POSITIVO:")
        print(f"   {melhor_performance['codigo']} ({melhor_performance['empresa']})")
        print(f"   R$ {melhor_performance['preco_fechamento']:.2f} ({melhor_performance['variacao_dia']:+.2f}%)")
        
        print(f"\n⚠️  ATENÇÃO REQUERIDA:")
        print(f"   {pior_performance['codigo']} ({pior_performance['empresa']})")
        print(f"   R$ {pior_performance['preco_fechamento']:.2f} ({pior_performance['variacao_dia']:+.2f}%)")
        
        # Salvar relatório
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_relatorio = f"data/reports/relatorio_executivo_{timestamp}.txt"
        
        with open(nome_relatorio, 'w', encoding='utf-8') as f:
            f.write(f"RELATÓRIO EXECUTIVO - {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write("="*50 + "\n\n")
            f.write(f"Valor total estimado: R$ {valor_total:,.2f}\n")
            f.write(f"Número de ativos: {len(df_atual)}\n")
            f.write(f"Variação média: {df_atual['variacao_dia'].mean():+.2f}%\n")
        
        print(f"\n💾 Relatório salvo em: {nome_relatorio}")
    
    def exportar_para_excel(self):
        """
        Exporta dados para Excel (formato que empresas adoram)
        """
        if self.df_portfolio is None:
            print("⚠️ Execute extrair_portfolio_completo() primeiro")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_arquivo = f"data/processed/portfolio_completo_{timestamp}.xlsx"
            
            # Criar arquivo Excel com múltiplas abas
            with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
                # Aba 1: Dados completos
                self.df_portfolio.to_excel(writer, sheet_name='Dados_Completos', index=False)
                
                # Aba 2: Resumo por ação
                resumo = self.df_portfolio.groupby(['codigo', 'empresa']).agg({
                    'preco_fechamento': ['mean', 'min', 'max', 'std'],
                    'volume': 'mean',
                    'variacao_dia': 'mean'
                }).round(2)
                resumo.to_excel(writer, sheet_name='Resumo_Por_Acao')
                
                # Aba 3: Dados atuais
                df_atual = self.df_portfolio.groupby('codigo').tail(1)
                df_atual.to_excel(writer, sheet_name='Posicao_Atual', index=False)
            
            print(f"📋 Dados exportados para Excel: {nome_arquivo}")
            
        except ImportError:
            print("⚠️ Para exportar Excel, instale: pip install openpyxl")


# === EXEMPLO DE USO PROFISSIONAL ===

if __name__ == "__main__":
    # Inicializar extrator profissional
    extrator = ExtratorFinanceiroProfissional()
    
    # Portfolio diversificado brasileiro
    portfolio_br = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", "PVB11", "MGLU3", "WEGE3"]
    
    print(f"\n🇧🇷 Analisando portfolio brasileiro de {len(portfolio_br)} ativos...")
    
    # Extrair dados completos (histórico de 30 dias)
    df_portfolio = extrator.extrair_portfolio_completo(portfolio_br, incluir_historico=True)
    
    # Executar todas as análises profissionais
    extrator.analises_estatisticas_avancadas()
    extrator.detectar_tendencias()
    extrator.gerar_relatorio_executivo()
    
    # Exportar para Excel (se disponível)
    extrator.exportar_para_excel()
    
    print("\n" + "="*80)
    print("🎉 ANÁLISE COMPLETA FINALIZADA!")
    print("📁 Verifique a pasta 'data/' para todos os arquivos gerados")
    print("🚀 Portfolio profissional pronto para impressionar recrutadores!")
    print("="*80)