from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Libera o acesso para o seu HTML conseguir falar com o Python no Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou coloque o link exato do seu GitHub Pages / Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    acao: str

@app.post("/executar")
async def executar(dados: Payload):
    acao = dados.acao
    
    if acao == "senior":
        # Aqui você colocaria a lógica ou chamaria seu script Playwright
        return {"mensagem": "Comando recebido! O robô processou o Senior WMS com sucesso."}
    
    elif acao == "ics":
        return {"mensagem": "Busca no ICS Integrated realizada pelo Python!"}
        
    return {"mensagem": "Ação desconhecida."}

@app.get("/")
def home():
    return {"status": "API do Robô Total Express rodando com sucesso!"}
