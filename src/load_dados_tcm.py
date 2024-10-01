# Importando as bibliotecas necessárias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
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
    windows = driver.window_handles
    driver.switch_to.window(windows[0])  # Sempre focar na primeira janela (original)


# Espera até que o seletor de ano esteja visível
try:
    select_ano = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ano"))
    )
    select_ano = Select(select_ano)
    select_ano.select_by_visible_text('2023')
except Exception as e:
    print(f"Erro ao encontrar o elemento de ano: {e}")
    driver.quit()

# Selecionar o município, ignorando a opção ":: SELECIONE ::"
try:
    select_municipio = Select(WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'municipio'))
    ))
    municipios = [option.text for option in select_municipio.options if option.text != ":: SELECIONE ::"]
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
        select_ano.select_by_visible_text('2023')

        # Selecionar o município
        select_municipio = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'municipio'))
        ))
        select_municipio.select_by_visible_text(municipio)
        print(f"Coletando dados do município: {municipio}")
        
        # Clicar no botão de buscar
        buscar_button = driver.find_element(By.NAME, 'pesquisar')
        actions = ActionChains(driver)
        actions.move_to_element(buscar_button).click().perform()
        #driver.execute_script("arguments[0].click();", buscar_button)
        #buscar_button.click()
        #buscar_button = WebDriverWait(driver, 10).until(
        #   EC.element_to_be_clickable((By.XPATH, '//input[@type="hidden" and @value="Pesquisar"]')))
        #buscar_button.click()
        
        # Esperar até que o botão de exportação "expCsv" esteja visível
        try:
            exp_csv_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'expCsv'))  # Verifique o ID correto do botão de exportação
            )
            exp_csv_button.click()  # Clique no botão de exportar CSV
            print(f"Exportando dados do município: {municipio}")
            
            # Nome do arquivo CSV esperado (verifique se o nome gerado pelo site segue um padrão)
            filename = f"receita_{municipio}.csv"
            print(f"Dados exportados com sucesso! ")
            
        except Exception as e:
            print(f"Erro ao exportar dados do município {municipio}")
            continue  # Pula para o próximo município se houver erro

    except Exception as e:
        print(f"Erro ao coletar dados do município {municipio}: {e}")
        continue  # Passa para o próximo município se houver erro

# Fechar o navegador
driver.quit()