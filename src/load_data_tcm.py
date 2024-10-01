# Importando as bibliotecas necessárias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Caminho para a pasta "Documentos" do usuário
user_documents = os.path.join(os.path.expanduser("~"), "Documents")
download_dir = os.path.join(user_documents, "RelatoriosMunicipais")

# Verifica se o diretório existe, caso contrário, cria
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Configurações do Chrome para baixar arquivos diretamente no diretório desejado
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,  # Define o diretório de download
    "download.prompt_for_download": False,       # Não solicita confirmação de download
    "download.directory_upgrade": True,          # Permite atualizar o diretório de download
    "safebrowsing.enabled": True                 # Habilita navegação segura (necessário para alguns downloads)
})

# Configuração automática do Chromedriver usando o webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Acessar o site
driver.get("https://www.tcm.ba.gov.br/controle-social/consulta-de-receita/")

# Função para garantir que estamos na janela correta
def switch_to_main_window(driver):
    # Pega todas as janelas abertas
    windows = driver.window_handles
    driver.switch_to.window(windows[0])  # Sempre focar na primeira janela (original)

# Espera até que o seletor de ano esteja visível
try:
    select_ano = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ano"))
    )
    select_ano = Select(select_ano)
    select_ano.select_by_visible_text('2020')
except Exception as e:
    print(f"Erro ao encontrar o elemento de ano: {e}")
    driver.quit()

# Selecionar o município (aguardamos para garantir que o campo esteja disponível)
try:
    select_municipio = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'municipio'))
    ))
    municipios = [option.text for option in select_municipio.options if option.text != "Selecione"]
except Exception as e:
    print(f"Erro ao encontrar o seletor de município: {e}")
    driver.quit()

# Loop para coletar dados de todos os municípios
for municipio in municipios:
    try:
        # Sempre garantir que estamos na janela correta
        switch_to_main_window(driver)

        # Voltar para a página inicial antes de começar o loop para cada município
        driver.get("https://www.tcm.ba.gov.br/controle-social/consulta-de-receita/")
        
        # Selecionar o ano novamente
        select_ano = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ano"))
        )
        select_ano = Select(select_ano)
        select_ano.select_by_visible_text('2020')

        # Selecionar o município
        select_municipio = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'municipio'))
        ))

        # Aguarda a seleção automática da prefeitura
        time.sleep(5)
        
        select_municipio.select_by_visible_text(municipio)
        print(f"Coletando dados do município: {municipio}")
        
        # Clicar no botão de buscar
        buscar_button = driver.find_element(By.NAME, 'pesquisar')
        buscar_button.click()
        
        # Esperar até que o botão de exportação "expCsv" esteja visível
        try:
            exp_csv_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'expCsv'))  # Verifique o ID correto do botão de exportação
            )
            exp_csv_button.click()  # Clique no botão de exportar CSV
            print(f"Exportando dados do município: {municipio}")
            
            # Aguarda o término do download
            time.sleep(10)  # Pausa para garantir que o download seja concluído antes de continuar
            
        except Exception as e:
            print(f"Erro ao exportar dados do município {municipio}: {e}")
            continue  # Pula para o próximo município se houver erro

    except Exception as e:
        print(f"Erro ao coletar dados do município {municipio}: {e}")
        continue  # Passa para o próximo município se houver erro

# Fechar o navegador
driver.quit()