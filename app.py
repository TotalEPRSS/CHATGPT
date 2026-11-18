import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from playwright.sync_api import sync_playwright, expect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    acao: str

def baixar_estoque_local(usuario: str = "540956", senha: str = "Batatinha123"):
    with sync_playwright() as p:
        # headless=True é obrigatório no Render (servidor Linux sem tela)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 650})
        page = context.new_page()

        # 1. Acessa o Senior WMS
        page.goto("https://texcoprd.seniorcloud.com.br/siltwms/")
        expect(page.get_by_role("img", name="senior-logo")).to_be_visible(timeout=20000)

        # 2. Preenche Login e Senha
        page.locator("#LoginDialog_loginText").click()
        page.locator("#LoginDialog_loginText").fill(usuario)
        page.locator("#LoginDialog_loginText").press("Tab")
        page.locator("#LoginDialog_passwordText").fill(senha)

        # 3. Seleciona Armazém Jundiaí
        page.locator("#LoginDialog_armazemComboBox").click()
        page.get_by_text("TOTAL EXPRESS - JUNDIAI").click()

        # 4. Clica em Entrar e aguarda carregar
        page.get_by_role("button", name="Entrar").click()
        expect(page.get_by_role("treeitem", name="Acompanhamento")).to_be_visible(timeout=30000)

        # 5. Pesquisa na barra de navegação lateral e abre Estoque Local Por Lote
        campo_navegacao = page.locator(".x-panel-tbar input[type='text']").first
        campo_navegacao.click()
        campo_navegacao.fill("Estoque local por lote")
        page.get_by_role("treeitem", name=re.compile(r"Estoque Local Por Lote", re.IGNORECASE)).click()

        # 6. Seleciona o Depositante
        page.locator("#SearchTriggerWindowRemote_searchTextField").fill("TEX COURIER S.A | DEVOLUÇÃO JDU")
        page.locator("#SearchTriggerWindowRemote_searchTextField").press("Enter")
        page.locator("#x-auto-980 div").filter(has_text=re.compile(r"^Localizar por:$")).click()
        page.get_by_text("Depositante", exact=True).click()
        page.locator("#SearchTriggerWindowRemote_searchTextField").click()
        page.locator("#SearchTriggerWindowRemote_searchTextField").press("Enter")

        # 7. Aguarda o gridcell 1063817 e dá duplo clique
        expect(page.get_by_role("gridcell", name="1063817")).to_be_visible(timeout=20000)
        page.get_by_role("link").dblclick()

        # 8. Exporta em .csv
        expect(page.get_by_role("button", name="Filtrando Depositante: TEX")).to_be_visible(timeout=15000)
        page.locator("#ExportGridPlugin_exportButton").click()
        expect(page.get_by_role("link", name="Excel (.xlsx)")).to_be_visible(timeout=10000)
        
        with page.expect_download() as download1_info:
            page.get_by_role("link", name="Separado por Vírgulas (\",\") .").click()
        download1 = download1_info.value
        download1.save_as("estoque_local_lote.csv")

        context.close()
        browser.close()

@app.get("/")
def home():
    return {"status": "online", "mensagem": "API Senior WMS rodando no Render!"}

@app.post("/executar")
def executar(dados: Payload):
    print(f"🤖 [AUTOMAÇÃO] Ação recebida: {dados.acao}")
    if dados.acao == "senior":
        try:
            baixar_estoque_local()
            print("✅ [AUTOMAÇÃO] Extração do CSV concluída no servidor!")
            return {"status": "ok", "mensagem": "Download concluído com sucesso!"}
        except Exception as e:
            print(f"❌ [ERRO] Falha no Playwright: {str(e)}")
            return {"status": "erro", "mensagem": str(e)}
            
    return {"status": "ignorado", "mensagem": "Ação não reconhecida."}
