# extrator_simples.py - Versão bem fácil para começar

import json
from datetime import datetime
import random

class ExtratorFinanceiro:
    """Classe simples para extrair dados de ações"""
    
    def __init__(self):
        print("🚀 Extrator Financeiro iniciado!")
        self.dados_extraidos = []
    
    def simular_dados_acao(self, codigo_acao):
        """
        Simula dados de uma ação
        
        Parâmetros:
        codigo_acao (str): Código da ação (ex: "PETR4")
        
        Retorna:
        dict: Dados da ação
        """
        # Gerar dados aleatórios (simula API real)
        dados_acao = {
            "codigo": codigo_acao.upper(),
            "empresa": self._obter_nome_empresa(codigo_acao),
            "preco": round(random.uniform(20.0, 100.0), 2),
            "volume": random.randint(100000, 2000000),
            "variacao": round(random.uniform(-5.0, 5.0), 2),
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"📊 Dados extraídos para {codigo_acao}: R$ {dados_acao['preco']}")
        return dados_acao
    
    def _obter_nome_empresa(self, codigo):
        """Retorna nome da empresa baseado no código"""
        empresas = {
            "PETR4": "Petrobras",
            "VALE3": "Vale",
            "ITUB4": "Itaú",
            "BBDC4": "Bradesco",
            "ABEV3": "Ambev",
            "PVB11": "Papel"
        }
        return empresas.get(codigo.upper(), "Empresa Desconhecida")
    
    def extrair_multiplas_acoes(self, lista_acoes):
        """
        Extrai dados de várias ações
        
        Parâmetros:
        lista_acoes (list): Lista com códigos das ações
        
        Retorna:
        list: Lista com dados de todas as ações
        """
        print(f"🔄 Extraindo dados de {len(lista_acoes)} ações...")
        
        todas_acoes = []
        
        for codigo in lista_acoes:
            dados = self.simular_dados_acao(codigo)
            todas_acoes.append(dados)
            self.dados_extraidos.append(dados)
        
        print(f"✅ Extração concluída! {len(todas_acoes)} ações processadas")
        return todas_acoes
    
    def salvar_dados(self, dados, nome_arquivo="dados_acoes.json"):
        """
        Salva dados em arquivo JSON
        
        Parâmetros:
        dados (list): Lista com dados das ações
        nome_arquivo (str): Nome do arquivo para salvar
        """
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dados, arquivo, indent=2, ensure_ascii=False)
            
            print(f"💾 Dados salvos em '{nome_arquivo}'")
            
        except Exception as erro:
            print(f"❌ Erro ao salvar: {erro}")
    
    def mostrar_resumo(self, dados):
        """
        Mostra resumo dos dados extraídos
        
        Parâmetros:
        dados (list): Lista com dados das ações
        """
        if not dados:
            print("⚠️  Nenhum dado para mostrar")
            return
        
        print("\n📈 === RESUMO DOS DADOS ===")
        print(f"Total de ações: {len(dados)}")
        
        # Calcular estatísticas simples
        precos = [acao['preco'] for acao in dados]
        preco_medio = sum(precos) / len(precos)
        preco_maior = max(precos)
        preco_menor = min(precos)
        
        print(f"Preço médio: R$ {preco_medio:.2f}")
        print(f"Maior preço: R$ {preco_maior:.2f}")
        print(f"Menor preço: R$ {preco_menor:.2f}")
        
        print("\n📋 Detalhes por ação:")
        for acao in dados:
            variacao_emoji = "📈" if acao['variacao'] >= 0 else "📉"
            print(f"{variacao_emoji} {acao['codigo']} ({acao['empresa']}): R$ {acao['preco']} ({acao['variacao']:+.2f}%)")

    # Adicione esta função à sua classe:
    def analise_com_pandas(self, dados):
        """Análise profissional com pandas"""
        import pandas as pd
        
        # Converter dados para DataFrame
        df = pd.DataFrame(dados)
        
        print("\n📊 === ANÁLISE COM PANDAS ===")
        print("Estatísticas descritivas:")
        print(df[['preco', 'volume', 'variacao']].describe())
        
        # Ação com melhor performance
        melhor_acao = df.loc[df['variacao'].idxmax()]
        print(f"\n🥇 Melhor performance: {melhor_acao['codigo']} (+{melhor_acao['variacao']:.2f}%)")
        
        # Ação com maior volume
        maior_volume = df.loc[df['volume'].idxmax()]
        print(f"📊 Maior volume: {maior_volume['codigo']} ({maior_volume['volume']:,} ações)")

    def extrair_acao_especifica(self, codigo_acao):
        """
        Extrai dados de apenas uma ação específica
        
        Parâmetros:
        codigo_acao (str): Código da ação
        
        Retorna:
        dict: Dados da ação
        """
        print(f"🎯 Extraindo dados específicos de {codigo_acao}...")
        dados = self.simular_dados_acao(codigo_acao)
        
        # Salvar em arquivo separado
        nome_arquivo = f"{codigo_acao.lower()}_dados.json"
        self.salvar_dados([dados], nome_arquivo)
        
        return dados

# === EXEMPLO DE USO (PARTE PRINCIPAL) ===

if __name__ == "__main__":
    # Criar o extrator
    extrator = ExtratorFinanceiro()
    
    # Lista de ações brasileiras para extrair
    acoes_brasileiras = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", "PVB11"] 
    
    print("🇧🇷 Extraindo dados de ações brasileiras...\n")
    
    # Extrair dados de todas as ações
    dados_extraidos = extrator.extrair_multiplas_acoes(acoes_brasileiras)
    
    # Mostrar resumo
    extrator.mostrar_resumo(dados_extraidos)
    
    # Salvar dados em arquivo
    extrator.salvar_dados(dados_extraidos, "minhas_acoes.json")

    dados_vale = extrator.extrair_acao_especifica("VALE3")
    
    # Exemplo de como extrair apenas uma ação
    print("\n" + "="*50)
    print("🔍 Extraindo dados de uma ação específica...")
    
    dados_petrobras = extrator.simular_dados_acao("PETR4")
    print(f"Dados da Petrobras: {dados_petrobras}")
    
    print("\n🎉 Programa executado com sucesso!")
    print("📄 Verifique o arquivo 'portfolio_brasileiro.json' criado na pasta do projeto")