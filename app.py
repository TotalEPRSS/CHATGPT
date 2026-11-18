from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Libera o acesso para o seu HTML conseguir falar com o Python no Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    acao: str

# 1. Rota raiz para testar se o Python está vivo
@app.get("/")
def home():
    return {"status": "online", "mensagem": "O Python no Render está rodando perfeitamente!"}

# 2. Rota que o seu chat chama ao clicar nos botões
@app.post("/executar")
async def executar(dados: Payload):
    acao = dados.acao
    
    # Isso vai aparecer nos Logs do Render em tempo real quando você clicar no chat!
    print(f"🤖 [AUTOMAÇÃO] Ação recebida do chat: {acao}")
    
    if acao == "senior":
        # Aqui depois você coloca o seu código Playwright para o Senior WMS
        return {"mensagem": "Python recebeu com sucesso! Robô do Senior WMS foi acionado."}
    
    elif acao == "ics":
        # Aqui depois você coloca a automação do ICS
        return {"mensagem": "Python recebeu com sucesso! Robô do ICS Integrated foi acionado."}
        
    return {"mensagem": f"Ação '{acao}' recebida, mas não reconhecida."}
